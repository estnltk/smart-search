#!/usr/bin/python3

"""
Sisse:
koondbaas.sqlite:
{   "indeks_vormid":[(VORM, DOCID, START, END, LIITSÕNA_OSA)],
    "indeks_lemmad":[(LEMMA, DOCID, START, END, LIITSÕNA_OSA)],
    "liitsõnad":[(OSALEMMA, LIITLEMMA)],
    "lemma_kõik_vormid":[(VORM, KAAL, LEMMA)],
    "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)],
    "kirjavead":[(VIGANE_VORM, VORM)],
    "allikad":[(DOCID, CONTENT)],
}

    json_io (Dict): 
        {   "content": str // päringustring
        }

Returns:
    Dict:
    {   TOKEN: // päringusõne
        {   LEMMA: // päringusõne lemma
            {   "type": str, // "suggestion"|"word"|"compound"
                "confidence:NUMBER // suuremat numbrit esineb rohkem
            }
        }
    }
 
Code (silumiseks):
    {
        "name": "api_sl_lemmatiser",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/ea_paring_sl/",
        "program": "./api_ea_paring_sl.py",
        "env": {},
        "args": [ \
            "--baas=../ea_jsoncontent_2_jsontabelid/1024-koond.sqlite" \
            "--json={\"tss\":\"presidendiga\\tpalk\"}",
        ]
    },
    
    {
        "name": "api_sl_lemmatiser (-llitsõnad)",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/ea_paring_sl/",
        "program": "./api_ea_paring_sl.py",
        "env": {},
        "args": [ \
            "--baas=../ea_jsoncontent_2_jsontabelid/1024-koond.sqlite" \
            "--json={\"params\":{\"otsi_liitsõnadest\":false}, \"tss\":\"presidendiga\\tpalk\"}",
        ]
    },

Käsurealt:
$ venv/bin/python3 api_ea_paring_sl.py \
    --baas=./1024-koond.sqlite \
    --json='{"tss":"presidendiga\tpalk"}'

$ venv/bin/python3 api_ea_paring_sl.py \
    --baas=./1024-koond.sqlite \
    --json='{"params":{"otsi_liitsõnadest":false}, "tss":"presidendiga\tpalk"}'
 
"""

import os
import sys
import json
import sqlite3
from typing import Dict, List, Union
from inspect import currentframe, getframeinfo

class PARING_SONED:
    def __init__(self, baas:Union[str,None], csthread=True):
        """Initsialiseerime versioonumbri, avame andmebaasi

        Args:

        db_lemmatiseerija (Union[str,None]): Andmebaasi nimi, None korral võta keskkonnamuutujast DB_LEMATISEERIJA
        csthread (bool): Falskist kasutamisel False, kui me midagi andmebaasi ei kirjuta, ei tohiks asjad pekki minna.
        
        Returns:

        * self.self.con_lemmatiseerija
        * self.cur_lemmatiseerija
        """
        # https://stackoverflow.com/questions/48218065/objects-created-in-a-thread-can-only-be-used-in-that-same-thread
        # kui me midagi andmebaasi ei kirjuta, ei tohiks csthread=False asju pekki keerata
        self.VERSION="2023.10.14"
        self.json_io = {}
        self.con_paring = None

        self.db_paring = baas

        if baas is None and (baas := os.environ.get('DB_PARING')) is None:
            sys.stdout.write('{"error": "Ei leidnud andmebaasi nime"}')
            exit()

        self.db_paring = baas
        self.con_paring = sqlite3.connect(self.db_paring, check_same_thread=csthread)
        self.cur_paring = self.con_paring.cursor()

    def __del__(self)->None:
        """Sulgeme avatud andmebaasid
        """
        if self.con_paring is not None:
            self.con_paring.close()

    def string2json(self, str:str)->None:
        """JSONis sisendstring "päris" JSONiks

        Args:
            str (str): päringusõned, tühikuga eraldud

        Raises:
            Exception: Exception({"error": "JSON parse error"})

        Returns:
            self.json_io (Dict): 
        """
        try:
            self.json_io = json.loads(str)
        except Exception as e:
            raise e
        
    def paring_tsv(self) -> None:
        """
        {   "tss": str, // Tab Separated Strings (tokens)
            "params":{"otsi_liitsõnadest":bool} // optional
        }

        (location, input, lemma, type, confidence, wordform)
            location    järjekorranr 0, 1, 2, ...
            input       päringusõne
            lemma       lemma 
            type        suggestion|word|compound
            confidence  mitu korda esines
            wordform    sõnavorm
        """ 
        otsi_liitsõnadest = True
        if "params" in self.json_io and "otsi_liitsõnadest" in self.json_io["params"]:
            otsi_liitsõnadest = self.json_io["params"]["otsi_liitsõnadest"]
        self.response_table = []
        self.response_table.append(("location", "input", "lemma", "type", "confidence", "wordform")) # veerunimed
        self.response_json = {}
        paring = self.json_io["tss"].split('\t') # ei kasuta sõnestamist, näit "Sarved&Sõrad" tüüpi asjad lähevad pekkiven
        self.json_out = [("location", "input", "lemma", "type", "confidence", "wordform")]
        for location, sone in enumerate(paring):
            # leiame päringusõne korpuses esinenud vormid
            # "lemma_kõik_vormid":[(VORM, KAAL, LEMMA)],
            # "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)],
            res_fetchall = []
            res = self.cur_paring.execute(f"""
                SELECT 
                    lemma_kõik_vormid.vorm, 
                    lemma_korpuse_vormid.lemma,         
                    lemma_korpuse_vormid.kaal,
                    lemma_korpuse_vormid.vorm         
                FROM lemma_kõik_vormid
                INNER JOIN lemma_korpuse_vormid ON lemma_kõik_vormid.lemma = lemma_korpuse_vormid.lemma 
                WHERE lemma_kõik_vormid.vorm = '{sone}'
            """)
            res_fetchall=res.fetchall()
            for input, lemma, confidence, wordform in res_fetchall:
                self.response_table.append((location, input, lemma, "word", confidence, wordform))
                self.append_2_json(input, lemma, "word", confidence, wordform)

            # vaatame kirjavigade loendit
            # "kirjavead":[(VIGANE_VORM, VORM)]
            # "lemma_kõik_vormid":[(VORM, KAAL, LEMMA)],
            # "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)],
            res_fetchall = []
            res = self.cur_paring.execute(f"""
                SELECT
                    kirjavead.vigane_vorm,
                    lemma_korpuse_vormid.lemma,         
                    lemma_korpuse_vormid.kaal,
                    lemma_korpuse_vormid.vorm                                                                              
                FROM kirjavead
                INNER JOIN lemma_kõik_vormid ON kirjavead.vorm=lemma_kõik_vormid.vorm
                INNER JOIN lemma_korpuse_vormid ON lemma_kõik_vormid.lemma = lemma_korpuse_vormid.lemma 
                WHERE vigane_vorm='{sone}'
            """)
            res_fetchall=res.fetchall()
            for input, lemma, confidence, wordform in res_fetchall:
                self.response_table.append((location, input, lemma, "suggestion",  confidence, wordform))
                self.append_2_json(input, lemma, "suggestion", confidence, wordform)

            # Liitsõnandus
            # "lemma_kõik_vormid":[(VORM, 0, LEMMA)]
            # "liitsõnad":[(OSALEMMA, LIITLEMMA)]
            # "lemma_korpuse_vormid":[(LEMMA,VORM)]
            if otsi_liitsõnadest:
                res_fetchall = []
                res = self.cur_paring.execute(f"""
                    SELECT
                        lemma_kõik_vormid.vorm, 
                        liitsõnad.osalemma,         
                        lemma_korpuse_vormid.kaal,
                        lemma_korpuse_vormid.vorm 
                    FROM lemma_kõik_vormid
                    INNER JOIN liitsõnad ON lemma_kõik_vormid.lemma = liitsõnad.osalemma
                    INNER JOIN lemma_korpuse_vormid ON liitsõnad.liitlemma=lemma_korpuse_vormid.lemma
                    WHERE lemma_kõik_vormid.vorm='{sone}'
                """)
                res_fetchall = res.fetchall()
            for input, lemma, confidence, wordform in res_fetchall:
                self.response_table.append((location, input, lemma, "compound",  confidence, wordform))
                self.append_2_json(input, lemma, "suggestion", confidence, wordform)  
        pass #DB

    def append_2_json(self, input, lemma, type, confidence, wordform):
        if input not in self.response_json:
            self.response_json[input] = {}
        if lemma not in self.response_json[input]:
            self.response_json[input][lemma] = {}
        if wordform not in self.response_json[input][lemma]:
            self.response_json[input][lemma][wordform] = {"type":type, "confidence":confidence}
                

    def version_json(self) -> Dict:
        """Versiooninfo

        Returns:
            Dict: {"version": self.VERSION}
        """
        return {"version": self.VERSION, "DB_LEMATISEERIJA": self.db_paring}
        
if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-b', '--baas', type=str, help='andmebaasi nimi')
    argparser.add_argument('-j', '--json', type=str, help='json input')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    args = argparser.parse_args()

    prng = PARING_SONED(args.baas)
    if args.json is not None:
        prng.string2json(args.json)
        prng.paring_tsv()
        for location, input, lemma, type, confidence, wordform in prng.response_table:
            sys.stdout.write(f'{location}\t{input}\t{lemma}\t{type}\t{confidence}\t{wordform}\n')
        #json.dump(prng.response_json, sys.stdout, indent=args.indent, ensure_ascii=False)
        #sys.stdout.write('\n')

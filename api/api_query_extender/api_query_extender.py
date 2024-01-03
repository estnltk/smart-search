#!/usr/bin/python3

"""
Mida uut:
2024.01.03
* Kasutame vabomorfi spellerit kui kirjaviga ei leitud ettegenereeritud kirjavigade tabelis

---------------------------------------
Sisse:
    Amdmebaas 3 tabeliga

    * lemma_kõik_vormid(
            vorm TEXT NOT NULL,         -- lemma kõikvõimalikud vormid genereerijast
            paritolu INT NOT NULL,      -- 0-lemma on leitud jooksvas dokumendis olevast sõnavormist; 1-vorm on lemma sünonüüm
            lemma TEXT NOT NULL,        -- korpuses esinenud sõnavormi lemma
            PRIMARY KEY(vorm, lemma)

    * lemma_kõik_vormid( 
            lemma TEXT NOT NULL,        -- korpuses esinenud sõnavormi lemma
            kaal INT NOT NULL,          -- suurem number on sagedasem
            vorm TEXT NOT NULL,         -- lemma kõikvõimalikud vormid genereerijast
            PRIMARY KEY(lemma, vorm))

    * kirjavead(
                vigane_vorm TEXT NOT NULL,  -- sõnavormi vigane versioon
                vorm TEXT NOT NULL,         -- korpuses esinenud sõnavorm
                kaal INT,                   -- sagedasemad vms võiksid olla suurema kaaluga
                PRIMARY KEY(vigane_vorm, vorm)

    * ignoreeritavad_vormid(
                ignoreeritav_vorm TEXT NOT NULL,  -- sellist sõnavormi ignoreerime päringus                       
                PRIMARY KEY(ignoreeritav_vorm)

    * liitsõnad( 
            osalemma TEXT NOT NULL,     -- liitsõna osasõna lemma
            liitlemma TEXT NOT NULL,    -- liitsõna osasõna lemmat sisaldav liitsõna lemma
            PRIMARY KEY(osalemma, liitlemma))

    json_io (Dict): 
        {   "content": str // päringustring
        }

Returns (üks alljärgnevatest):
    SL väljund TSV kujul: # TSV kujul JSON kuju
        (location, input, lemma, type, confidence, wordform)
        location    järjekorranr 0, 1, 2, ...
        input       päringusõne
        lemma       lemma 
        type        suggestion|speller_suggestion|word|compound|ignore
        confidence  mitu korda esines
        wordform    sõnavorm

    SL väljund JSON kujul # JSON kujul TSV kuju 
    {   INPUT:
        {   LEMMA:
            {   WORDFORM:
                {   "type": suggestion|speller_suggestion|word|compound|ignore,
                    "confidence": int
                }
            }
        }
    }

    Dict:
    {   "content": str // päringustring,
        "annotatsions":
        {   "query":                        # [[str]]: päringusõnedel vastavate lemmade massiiv
            [   [LEMMA11, LEMMA12, ...],    # [str]: 1. päringusõnele vastavad LEMMAD
                [LEMMA21, LEMMA22, ...],    # [str]: 2. päringusõnele vastavad LEMMAD
                ...                         
            ],
            "typos" # kui see olemas tuleb tegeleda kirjavigade parandamisega, mitte päringuga 
            {   TYPO:                   # [[str,int]]: kirjavigaste sõnede massiiv
                {   "suggestions": [SUGGESTED_WORDFORM]   # str: soovitus
                }
            },
            "ignore": [IGNOREERITAV_PÄRINGUSÕNE],
            "not indexed": [VORM] # pole indeksis    
        }
    }

Kasutusnäited:

Code:

        {
            "name": "api_query_extender_content",
            "type": "python",
            "request": "launch",
            "cwd": "${workspaceFolder}/api/api_query_extender/",
            "program": "./api_query_extender.py",
            "args": [\
                "--dbase=../../demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts/koond.sqlite", \
                "--json={\"content\":\"hapikurgiga lai presidendi ja presitendi\"}"],
        },
        {
            "name": "api_query_extender_tss2json",
            "type": "python",
            "request": "launch",
            "cwd": "${workspaceFolder}/api/api_query_extender/",
            "program": "./api_query_extender.py",
            "args": [\
                "--dbase=../../demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts/koond.sqlite", \
                "--indent=4", \
                "--json={\"tss\":\"ignotestsõne\\tlai\\tpresidendi\\tja\\tpresitendi\"}"],
        },
        {
            "name": "api_query_extender_tss2tsv",
            "type": "python",
            "request": "launch",
            "cwd": "${workspaceFolder}/api/api_query_extender/",
            "program": "./api_query_extender.py",
            "args": [\
                "--dbase=../../demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts/koond.sqlite", \
                "--tsv", \
                "--json={\"tss\":\"ignotestsõne\\tlaix\\tpresidendi\\tja\\tpresitendiga\"}"],
        },
    
Käsurealt:
    $ cd ~/git/smart-search_github/api/api_query_extender

    $ ./venv/bin/python3 ./api_query_extender.py  \
        --tsv \
        --dbase=../../demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts/koond.sqlite \
        --json="{\"content\":\"presidemdiga pidi laia ignotestsõne presidendi ja ning\"}" | jq

    $ SMART_SEARCH_QE_DBASE="../../demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts/koond.sqlite" \
        ./venv/bin/python3 ./api_query_extender.py  \
        --json="{\"content\":\"presitendi ja  polekorpuses kantseleis\"}"| jq
        
    $ ./venv/bin/python3 ./api_query_extender.py  \
        --tsv \
        --dbase=../../demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts/koond.sqlite \
        --json="{\"tss\":\"presitendiga\\tpresidemdigas\\tpresidendiga\", \"params\":{\"otsi_liitsõnadest\":\"false\"}}" 

    $ ./venv/bin/python3 ./api_query_extender.py  \
        --tsv \
        --dbase=../../demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts/koond.sqlite \
        --json="{\"tss\":\"presidendiga\", \"params\":{\"otsi_liitsõnadest\":\"true\"}}"
"""

import os
import sys
import json
import sqlite3
from typing import Dict, List, Union
import subprocess

proc_stlspellerjson = subprocess.Popen(['./stlspellerjson', '--path=.'],  
                            universal_newlines=True, 
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)

class Q_EXTENDER:
    def __init__(self, dbase:str, csthread=True):
        """Initsialiseerime versioonumbri, avame andmebaasi

        Args:

        db_lemmatiseerija (Union[str,None]): Andmebaasi nimi, None korral võta keskkonnamuutujast DB_LEMATISEERIJA
        csthread (bool): Falskist kasutamisel False, kui me midagi andmebaasi ei kirjuta, ei tohiks asjad pekki minna.
        
        Returns:

        * self.self.con_dbase
        * self.cur_dbase
        """
        # https://stackoverflow.com/questions/48218065/objects-created-in-a-thread-can-only-be-used-in-that-same-thread
        # kui me midagi andmebaasi ei kirjuta, ei tohiks csthread=False asju pekki keerata
        self.VERSION="2024.01.03"
        self.response_json = {}
        self.con_dbase = None
        self.dbase = dbase

        if self.dbase == "":
            self.dbase = os.environ.get('SMART_SEARCH_QE_DBASE') # veebiteenus sõnestamiseks

        self.con_dbase = sqlite3.connect(self.dbase, check_same_thread=csthread)
        self.cur_dbase = self.con_dbase.cursor()

    def __del__(self)->None:
        """Sulgeme avatud andmebaasid
        """
        if self.con_dbase is not None:
            self.con_dbase.close()

    def run_subprocess(self, proc, json_in:Dict) -> Dict:
        try:
            proc.stdin.write(f'{json.dumps(json_in)}\n')
            proc.stdin.flush()
            json_out = json.loads(proc.stdout.readline())
        except Exception as e: 
            raise            
        return json_out

    def string2json(self, str:str)->None:
        """JSONis sisendstring "päris" JSONiks

        Args:
            str (str): päringusõned, tühikuga eraldud

        Raises:
            Exception: Exception({"error": "JSON parse error"})

        Returns:
            self.response_json (Dict): 
        """
        try:
            self.response_json = json.loads(str)
        except:
            raise Exception({"error": "JSON parse error"})
        
    def paring_process(self) -> None:
        """Päringusõnedest päringu koostamine

        Args:

        * self.response_json -- päringut sisaldav JSON
        * self.cur_dbase -- andmebaas

        Returns:

        * self.response_json -- Lisatud päringutulemused, vt kommentaari programmi alguses

        """
        paring = self.response_json["content"].split() # ei kasuta sõnestamist, näit "Sarved&Sõrad" tüüpi asjad lähevad pekki

        self.response_json["annotations"] = {"query":[], "typos": {}, "ignore":[], "not indexed": []}
        for sone in paring:
            # vaatame kas jooksev päringusõne on ignoreeritavate loendis
            res = self.cur_dbase.execute(f'''
                SELECT ignoreeritav_vorm FROM ignoreeritavad_vormid 
                WHERE ignoreeritav_vorm = "{sone}"
                ''')
            if len(res_fetchall:=res.fetchall()) > 0:
                # seda päringusõne ignoreerime
                self.response_json["annotations"]["ignore"].append(res_fetchall[0][0])
                continue # kui on ignereeritav, siis teisi tabeleid ei vaata

            # vaatame kas leiame jooksvale päringusõnele vastava korpuselemma
            res = self.cur_dbase.execute(f'''
                SELECT vorm, lemma FROM lemma_kõik_vormid 
                WHERE vorm = "{sone}"
                ''')
            if len(res_fetchall:=res.fetchall()) > 0:
                vormid = []
                for res in res_fetchall:
                    vormid.append(res[1])
                self.response_json["annotations"]["query"].append(vormid)
                korpuselemma_või_kirjaviga = True
                continue # kui misiganes kujul leidsime korpusest, kirjavigasid ei vaata
           
            # ei leidnud indeksist
            self.response_json["annotations"]["not indexed"].append(sone)

            # vaatame kas jooksev päringusesõne on ettearvutatud kirjavigade loendis
            res = self.cur_dbase.execute(f"""
                SELECT 
                    kirjavead.vigane_vorm,
                    lemma_kõik_vormid.vorm
                FROM kirjavead
                INNER JOIN lemma_kõik_vormid ON kirjavead.vorm = lemma_kõik_vormid.vorm
                WHERE kirjavead.vigane_vorm = '{sone}'
            """)
            if len(res_fetchall:=res.fetchall()) > 0:
                self.response_json["annotations"]["typos"][sone] =  {"suggestions":[]}
                for typo in res_fetchall:
                    self.response_json["annotations"]["typos"][sone]["suggestions"].append(typo[1])
                continue # oli ettearvutatud kirjavigade hulgas, piirdume sellega

            # polnud ettearvutatud kirjavigade hulgas, küsime "päris" spellerilt
            # sisse: {"annotations":{"tokens":[{"features":{"token": string}}]}}
            '''
            {   "annotations":
                {   "tokens":
                    [   {   "features":
                            {   "token": string,  /* kontrollitav sõne */
                                "suggestions":["sooovitus1",...] /* võimaliku kirjavea korral soovitavad parandatud variandid */
                            }
                        }
                    ]
                }
            }
            '''
            speller_json_out = self.run_subprocess(proc_stlspellerjson, {"annotations":{"tokens":[{"features":{"token": sone}}]}})
            for token in speller_json_out["annotations"]["tokens"]:
                if "suggestions" in token["features"]:
                    for suggestion in token["features"]["suggestions"]:
                        res_fetchall = []
                        res = self.cur_dbase.execute(f"""
                            SELECT lemma                       
                            FROM lemma_kõik_vormid
                            WHERE vorm='{suggestion}'
                        """)
                        if len(res_fetchall:=res.fetchall()) > 0:
                            self.response_json["annotations"]["typos"][sone] =  {"suggestions":[]}
                            for lemma in res_fetchall:
                                self.response_json["annotations"]["typos"][sone]["suggestions"].append(lemma[0])
                            
    def paring_jsontsv(self) -> None:
        """
        {   "tss": str, // Tab Separated Strings (tokens)
            "params":{"otsi_liitsõnadest":bool} // optional
        }

        Teeb tsv ja json kujul väljundi
        tsv: 
        (location, input, lemma, type, confidence, wordform)
            location    järjekorranr 0, 1, 2, ...
            input       päringusõne
            lemma       lemma 
            type        suggestion|speller_suggestion|word|compound|ignore
            confidence  mitu korda esines
            wordform    sõnavorm

        json
        {   INPUT:
            {   LEMMA:
                {   WORDFORM:
                    {   "type": suggestion|speller_suggestion|word|compound|ignore,
                        "confidence": int
                    }
                }
            }
        }    
        """
        oli_liitsõnas = False
        oli_indeksis = False 
        
        otsi_liitsõnadest = True
        if "params" in self.response_json and "otsi_liitsõnadest" in self.response_json ["params"]:
            otsi_liitsõnadest = self.response_json["params"]["otsi_liitsõnadest"].upper() == "TRUE"

        self.response_table = []
        self.response_table.append(("location", "input", "lemma", "type", "confidence", "wordform")) # veerunimed
        paring = self.response_json["tss"].split('\t') # ei kasuta sõnestamist, näit "Sarved&Sõrad" tüüpi asjad lähevad pekkiven
        self.json_out = [("location", "input", "lemma", "type", "confidence", "wordform")]

        for location, sone in enumerate(paring):
            # vaatame kas jooksev päringusõne on ignoreeritavate loendis
            res = self.cur_dbase.execute(f'''
                SELECT ignoreeritav_vorm FROM ignoreeritavad_vormid 
                WHERE ignoreeritav_vorm = "{sone}"
                ''')
            res_fetchall=res.fetchall()
            if len(res_fetchall) > 0:
                assert len(res_fetchall)==1 and res_fetchall[0][0]==sone
                self.response_table.append((location, sone, sone, "ignore", -1, sone))
                self.append_2_json(sone, sone, "ignore", -1, sone)
                continue # kui oli ignoreeritav, siis rohkem selle sõnega ei tegele
            
            # Liitsõnandus
            # "lemma_kõik_vormid":[(VORM, 0, LEMMA)]
            # "liitsõnad":[(OSALEMMA, LIITLEMMA)]
            # "lemma_korpuse_vormid":[(LEMMA,VORM)]
            if otsi_liitsõnadest:
                res_fetchall = []
                res = self.cur_dbase.execute(f"""
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
                if len(res_fetchall) > 0:
                    oli_liitsõnas = True
                    for input, lemma, confidence, wordform in res_fetchall:
                        self.response_table.append((location, input, lemma, "compound",  confidence, wordform))
                        self.append_2_json(input, lemma, "compound", confidence, wordform)  

            # leiame päringusõne korpuses esinenud vormid
            # "lemma_kõik_vormid":[(VORM, KAAL, LEMMA)],
            # "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)],
            res_fetchall = []
            res = self.cur_dbase.execute(f"""
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
            if len(res_fetchall) > 0:
                oli_indeksis = True
                for input, lemma, confidence, wordform in res_fetchall:
                    self.response_table.append((location, input, lemma, "word", confidence, wordform))
                    self.append_2_json(input, lemma, "word", confidence, wordform)
            if oli_liitsõnas is True or oli_indeksis is True:
                continue # kui terviksõnena või liitsõna osana oli indeksid ära kirjavigasid vaata

            self.response_table.append((location, sone, sone, "not_indexed",  -1, sone))
            self.append_2_json(sone, sone, "not_indexed", -1, sone)

            # vaatame kirjavigade loendit
            # "kirjavead":[(VIGANE_VORM, VORM)]
            # "lemma_kõik_vormid":[(VORM, KAAL, LEMMA)],
            # "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)],
            res_fetchall = []
            res = self.cur_dbase.execute(f"""
                SELECT
                    kirjavead.vigane_vorm,
                    lemma_korpuse_vormid.lemma,         
                    lemma_korpuse_vormid.kaal,
                    lemma_korpuse_vormid.vorm                                                                              
                FROM kirjavead
                INNER JOIN lemma_kõik_vormid ON kirjavead.vorm = lemma_kõik_vormid.vorm
                INNER JOIN lemma_korpuse_vormid ON lemma_kõik_vormid.lemma = lemma_korpuse_vormid.lemma 
                WHERE vigane_vorm='{sone}'
            """)
            res_fetchall=res.fetchall()
            if len(res_fetchall) > 0:
                for input, lemma, confidence, wordform in res_fetchall:
                    self.response_table.append((location, input, lemma, "suggestion",  confidence, wordform))
                    self.append_2_json(input, lemma, "suggestion", confidence, wordform)
            else:
                # polnud ettearvutatud kirjavigade hulgas, küsime "päris" spellerilt
                # sisse: {"annotations":{"tokens":[{"features":{"token": string}}]}}
                '''
                {   "annotations":
                    {   "tokens":
                        [   {   "features":
                                {   "token": string,  /* kontrollitav sõne */
                                    "suggestions":["sooovitus1",...] /* võimaliku kirjavea korral soovitavad parandatud variandid */
                                }
                            }
                        ]
                    }
                }
                '''
                speller_json_out = self.run_subprocess(proc_stlspellerjson, {"annotations":{"tokens":[{"features":{"token": sone}}]}})
                for token in speller_json_out["annotations"]["tokens"]:
                    if "suggestions" in token["features"]:
                        for suggestion in token["features"]["suggestions"]:
                            res_fetchall = []
                            res = self.cur_dbase.execute(f"""
                                SELECT 
                                    lemma_korpuse_vormid.lemma,
                                    lemma_korpuse_vormid.kaal,
                                    lemma_korpuse_vormid.vorm                                               
                                FROM lemma_kõik_vormid
                                INNER JOIN lemma_korpuse_vormid ON lemma_kõik_vormid.lemma = lemma_korpuse_vormid.lemma
                                WHERE lemma_kõik_vormid.vorm ='{suggestion}'
                            """)
                            res_fetchall=res.fetchall()
                            for lemma, confidence, wordform in res_fetchall:
                                self.response_table.append((location, sone, lemma, "speller_suggestion",  confidence, wordform))
                                self.append_2_json(sone, lemma, "speller_suggestion", confidence, wordform)
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
        try:
            res_fetchall = []
            res = self.cur_dbase.execute('SELECT version FROM version')
            db_version = res.fetchall()[0]
        except:
            db_version = "not present"
        return {"VERSION_API": self.VERSION, "SMART_SEARCH_QE_DBASE": self.dbase, "DBASE_VERSION": db_version}
        
if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-b', '--dbase', type=str, help='database')
    argparser.add_argument('-j', '--json', type=str, help='json input')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for JSON output, None=all in one line')
    argparser.add_argument('-c', '--tsv',  action="store_true", help='CSV output')
    args = argparser.parse_args()

    prng = Q_EXTENDER(args.dbase)
    if args.json is not None:
        prng.string2json(args.json)
        if "content" in prng.response_json:
            prng.paring_process()
            json.dump(prng.response_json, sys.stdout, indent=args.indent, ensure_ascii=False)
        elif "tss" in prng.response_json:
            prng.paring_jsontsv()
            if args.tsv is True:
                for rec in prng.response_table:
                    print(f'{rec[0]}\t{rec[1]}\t{rec[2]}\t{rec[3]}\t{rec[4]}\t{rec[5]}')
            else:
                json.dump(prng.response_json, sys.stdout, indent=args.indent, ensure_ascii=False)
        sys.stdout.write('\n')
        
    #json.dump(prng.version_json(), sys.stdout, indent=args.indent, ensure_ascii=False)
    
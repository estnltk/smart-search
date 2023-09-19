#!/usr/bin/python3

"""
Sisse:
    Amdmebaas 3 tabeliga

    * lemma_kõik_vormid(
            vorm TEXT NOT NULL,         -- lemma kõikvõimalikud vormid genereerijast
            paritolu INT NOT NULL,      -- 0-lemma on leitud jooksvas dokumendis olevast sõnavormist; 1-vorm on lemma sünonüüm
            lemma TEXT NOT NULL,        -- korpuses esinenud sõnavormi lemma
            PRIMARY KEY(vorm, lemma)

    * kirjavead(
                vigane_vorm TEXT NOT NULL,  -- sõnavormi vigane versioon
                vorm TEXT NOT NULL,         -- korpuses esinenud sõnavorm
                kaal INT,                   -- sagedasemad vms võiksid olla suurema kaaluga
                PRIMARY KEY(vigane_vorm, vorm)

    * ignoreeritavad_vormid(
                ignoreeritav_vorm TEXT NOT NULL,  -- sellist sõnavormi ignoreerime päringus
                paritolu INT NOT NULL,            -- 0:korpusest tuletatud, 1:etteantud vorm                       
                PRIMARY KEY(ignoreeritav_vorm)

    json_io (Dict): 
        {   "content": str // päringustring
        }

Returns:
    Dict:
    {   "content": str // päringustring,
        "annotatsions":
        {   "query":                        # [[str]]: päringusõnedel vastavate lemmade massiiv
            [   [LEMMA11, LEMMA12, ...],    # [str]: 1. päringusõnele vastavad LEMMAD
                [LEMMA21, LEMMA22, ...],    # [str]: 2. päringusõnele vastavad LEMMAD
                ...                         
            ]
            "typos" # kui see olemas tuleb tegeleda kirjavigade parandamisega, mitte päringuga 
            {   TYPO:                   # [[str,int]]: kirjavigaste sõnede massiiv
                [   {   "suggestion": SUGGESTED_WORDFORM,   # str: soovitus
                        "weight": WEIGHT                    # int: kaal
                    }
                ]
            }
            "unknown": [VORM] # täiesti käsitlematu päringusõne, sellise päringuga pole midagi peale hakata    
        }
    }

Kasutusnäited:

Code:

    {
        "name": "api_ea_paring_A",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/ea_paring/",
        "program": "./api_ea_paring.py",
        "args": [\
            "--lemmatiseerija=./lemmataja.db", \
            "--json={\"content\":\"presitendi ja  polekorpuses kantseleis\"}"],
    }

    {
        "name": "api_ea_paring_B",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/ea_paring/",
        "program": "./api_ea_paring.py",
        "args": ["--json={\"content\":\"presitendi ja  polekorpuses kantseleis\"}"],
        "env": {"DB_LEMATISEERIJA":"./lemmataja.db"},
    }
    
Käsurealt:

    $ ./venv/bin/python3 ./api_ea_paring.py  \
        --lemmatiseerija=./lemmataja.db \
        --json="{\"content\":\"presitendi ja  polekorpuses kantseleis\"}"

    $ DB_LEMATISEERIJA="./lemmataja.db" \
        ./venv/bin/python3 ./api_ea_paring.py  \
        --json="{\"content\":\"presitendi ja  polekorpuses kantseleis\"}"

"""

import os
import sys
import json
import sqlite3
from typing import Dict, List, Union

class PARING_SONED:
    def __init__(self, db_lemmatiseerija:Union[str,None], csthread=True):
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
        self.VERSION="2023.09.16"
        self.json_io = {}
        self.con_lemmatiseerija = None
        self.lemmatiseerija = db_lemmatiseerija

        if self.lemmatiseerija == None:
            self.lemmatiseerija = os.environ.get('DB_LEMATISEERIJA') # veebiteenus sõnestamiseks

        self.con_lemmatiseerija = sqlite3.connect(self.lemmatiseerija, check_same_thread=csthread)
        self.cur_lemmatiseerija = self.con_lemmatiseerija.cursor()

    def __del__(self)->None:
        """Sulgeme avatud andmebaasid
        """
        if self.con_lemmatiseerija is not None:
            self.con_lemmatiseerija.close()

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
        except:
            raise Exception({"error": "JSON parse error"})
        
    def paring_json(self) -> None:
        """Päringusõnedest päringu koostamine

        Args:

        * self.json_io -- päringut sisaldav JSON
        * self.cur_lemmatiseerija -- andmebaas

        Returns:

        * self.json_io -- Lisatud päringutulemused, vt kommentaari programmi alguses

        """
        paring = self.json_io["content"].split() # ei kasuta sõnestamist, näit "Sarved&Sõrad" tüüpi asjad lähevad pekki

        
        self.json_io["annotations"] = {"query":[], "typos": {}, "unknown": []}
        for sone in paring:

            # vaatame kas jooksev päringusõne on ignoreeritavate loendis
            res = self.cur_lemmatiseerija.execute(f'''
                SELECT ignoreeritav_vorm FROM ignoreeritavad_vormid 
                WHERE ignoreeritav_vorm = "{sone}"
                ''')
            if len(res_fetchall:=res.fetchall()) > 0:
                continue # seda päringusõne ignoreerime

            # vaatame kas leiame jooksvale päringusõnele vastava korpuselemma
            res = self.cur_lemmatiseerija.execute(f'''
                SELECT vorm, lemma FROM lemma_kõik_vormid 
                WHERE vorm = "{sone}"
                ''')
            if len(res_fetchall:=res.fetchall()) > 0:
                vormid = []
                for res in res_fetchall:
                    vormid.append(res[1])
                self.json_io["annotations"]["query"].append(vormid)
                continue # leidsime päringusõne lemma korpusest
            
            # vaatame kas jooksev korpusesõne on kirjavigade loendis
            res = self.cur_lemmatiseerija.execute(f'''
                SELECT vigane_vorm, vorm, kaal FROM kirjavead 
                WHERE vigane_vorm = "{sone}"
                ''')
            if len(res_fetchall:=res.fetchall()) > 0:
                self.json_io["annotations"]["typos"][sone] = []
                for typo in res_fetchall:
                    self.json_io["annotations"]["typos"][sone].append({"suggestion":typo[1], "weight":typo[2]})
                continue # kirjaviga

            # mingi täielik kamarajura
            self.json_io["annotations"]["unknown"].append(sone)

    
    def version_json(self) -> Dict:
        """Versiooninfo

        Returns:
            Dict: {"version": self.VERSION}
        """
        return {"version": self.VERSION}
        
if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-l', '--lemmatiseerija', type=str, help='json input')
    argparser.add_argument('-j', '--json', type=str, help='json input')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    args = argparser.parse_args()

    prng = PARING_SONED(args.lemmatiseerija)
    if args.json is not None:
        prng.string2json(args.json)
        prng.paring_json()
        json.dump(prng.json_io, sys.stdout, indent=args.indent, ensure_ascii=False)
        sys.stdout.write('\n')

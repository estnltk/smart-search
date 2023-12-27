#!/usr/bin/python3

'''
Kasutamine:
Code:

    {
        "name": "query_extender_setup",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/scripts/query_extender_setup/example_make_based_workflow",
        "program": "./query_extender_setup.py",
        "args": [\
            "--verbose", \
            "--db_name=test-tmp.sqlite", \
            "--tables=lemma_kõik_vormid:lemma_korpuse_vormid:indeks_vormid:indeks_lemmad:liitsõnad:allikad", \
            "/home/tarmo/git/smart-search_github/demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts/government_orders.csv.json",
            "/home/tarmo/git/smart-search_github/demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts/government_regulations.csv.json",  \
            ],
        "env": {}
    }

Käsurealt:
$ cd ~/git/smart-search_github/api/ea_jsontabelid_2_db
$ export PREFIKS=1019- # kasuta sama prefiksit, millega tegid JSON failid
$ ./create_venv.sh
$ ./venv/bin/python3 ./api_jsontabelid_2_db.py \
    --verbose --db_name=${PREFIKS}baas.sqlite \
    --tables=indeks_vormid:indeks_lemmad:liitsõnad:lemma_kõik_vormid:lemma_korpuse_vormid:kirjavead:kirjavead_2:allikad:ignoreeritavad_vormid \
    ../ea_jsoncontent_2_jsontabelid/${PREFIKS}*.json 

SisendJson:
        {   "indeks_vormid":[(VORM, DOCID, START, END, LIITSÕNA_OSA)],
            "indeks_lemmad":[(LEMMA, DOCID, START, END, LIITSÕNA_OSA)],
            "liitsõnad":[(OSALEMMA, LIITLEMMA)],
            "lemma_kõik_vormid":[(VORM, KAAL, LEMMA)],
            "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)],
            "kirjavead":[(VIGANE_VORM, VORM)],
            "allikad":[(DOCID, CONTENT)],
        }
 '''
import os
import sys
import json
import sqlite3
from tqdm import tqdm
from typing import Dict, List, Tuple
from inspect import currentframe, getframeinfo

class DB:
    def __init__(self, append:bool, db_name:str, tables:List, verbose:bool)->None:
        self.verbose = verbose
        self.db_name = db_name
        self.tables = tables

        if append is False and os.path.isfile(self.db_name):
            if self.verbose:
                sys.stdout.write(f"# kustutame andmebaasi {self.db_name}\n")
            os.remove(self.db_name)

        if self.verbose:
            sys.stdout.write(f"# teeme/avame andmebaasi {self.db_name}\n")

        # loome/avame andmebaasi
        self.con_baas = sqlite3.connect(self.db_name)
        self.cur_baas = self.con_baas.cursor()

        # "indeks_vormid":[(VORM, DOCID, START, END, LIITSÕNA_OSA)]
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS indeks_vormid(
                vorm  TEXT NOT NULL,          -- (jooksvas) dokumendis esinenud sõnavorm
                docid TEXT NOT NULL,          -- dokumendi id
                start INT,                    -- vormi alguspositsioon tekstis
                end INT,                      -- vormi lõpupositsioon tekstis
                liitsona_osa INT,             -- 0: pole liitsõna osa; 1: on liitsõna osa
                PRIMARY KEY(vorm, docid, start, end)
                )
        ''')

        # "indeks_lemmad":[(LEMMA, DOCID, START, END, LIITSÕNA_OSA)]
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS indeks_lemmad(
                lemma  TEXT NOT NULL,         -- (jooksvas) dokumendis esinenud sõna lemma
                docid TEXT NOT NULL,          -- dokumendi id
                start INT,                    -- lemmale vastava vormi alguspositsioon tekstis
                end INT,                      -- lemmale vastava vormi lõpupositsioon tekstis
                liitsona_osa INT,             -- 0: pole liitsõna osa; 1: on liitsõna osa
                PRIMARY KEY(lemma, docid, start, end)
                )
        ''')

        # "liitsõnad":[(OSALEMMA, LIITLEMMA)]
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS liitsõnad( 
            osalemma TEXT NOT NULL,     -- liitsõna osasõna lemma
            liitlemma TEXT NOT NULL,    -- liitsõna osasõna lemmat sisaldav liitsõna lemma
            PRIMARY KEY(osalemma, liitlemma)
        )''')

        # "lemma_kõik_vormid":[(LEMMA, KAAL, VORM)],
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS lemma_kõik_vormid( 
            lemma TEXT NOT NULL,        -- korpuses esinenud sõnavormi lemma
            kaal INT NOT NULL,          -- suurem number on sagedasem
            vorm TEXT NOT NULL,         -- lemma kõikvõimalikud vormid genereerijast
            PRIMARY KEY(lemma, vorm)
        )''')
        
        # "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)]
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS lemma_korpuse_vormid(
            lemma TEXT NOT NULL,        -- dokumendis esinenud sõnavormi lemma
            kaal INT NOT NULL,          -- suurem number on sagedasem            
            vorm TEXT NOT NULL,         -- lemma need sõnavormid, mis on mingis dokumendis dokumendis esinenud
            PRIMARY KEY(vorm, lemma)
        )''')

        # {"tabelid":{ "kirjavead":[[VIGANE_VORM, VORM, KAAL]] }
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS kirjavead(
            vigane_vorm TEXT NOT NULL,  -- sõnavormi vigane versioon
            vorm TEXT NOT NULL,         -- korpuses esinenud sõnavorm
            kaal REAL,                  -- kaal vahemikus [0.0,1.0]
            PRIMARY KEY(vigane_vorm, vorm)
        )''')


        # ["tabelid"]["allikad"]:[(DOCID, CONTENT)]
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS allikad(
                docid TEXT NOT NULL,        -- dokumendi id
                content TEXT NOT NULL,      -- dokumendi text
                PRIMARY KEY(docid)
                )
        ''')  

        self.json_in = {}
        if self.verbose:
            sys.stdout.write("\n")

    def __del__(self)->None:
        if self.con_baas is not None:
            self.con_baas.close()
            if self.verbose is True:
                print(f"# Suletud andmebaas {self.db_name}")  
                     
    def toimeta(self, file:str)->None:
        print("# -----")
        with open(file) as f:
            for line in f:
                self.json_in = self.string2json(line)
                self.täienda_tabelid(file)
 
    def täienda_tabelid(self, file:str)->None:
        """Kanna self.json_in'ist info andmbeaaaside tabelitesse
        """
        for table in self.tables:
            pass #DB
            if table == "lemma_kõik_vormid":
                # "lemma_kõik_vormid":[(VORM, KAAL, LEMMA)],
                pbar = tqdm(self.json_in["tabelid"][table], desc=f'# {file} : {table} :', disable=(not self.verbose))
                for lemma, kaal, vorm in pbar:
                    res = self.cur_baas.execute(f"SELECT lemma, kaal, vorm FROM {table} WHERE lemma='{lemma}' and vorm='{vorm}'")
                    if len(res_fetchall:=res.fetchall()) == 0:
                        # sellist kirjet polnud, lisame uue
                        rec = (lemma, kaal, vorm)
                        self.cur_baas.execute(f"INSERT INTO {table} VALUES {rec}")
                    elif len(res_fetchall) == 1:
                        #selline kirje oli, liidame kaalud kokku, vajadusel uuendame kaalu
                        vana_kaal = res_fetchall[0][1]
                        uus_kaal = vana_kaal + kaal
                        if vana_kaal != uus_kaal: # kaal muutus, uuendame kaalu
                            self.cur_baas.execute(f"UPDATE {table} SET kaal='{uus_kaal}'  WHERE lemma='{lemma}' and vorm='{vorm}'")
                    else:
                        # midagi väga valesti sest PRIMARY KEY(vorm, lemma)
                        raise ValueError(f"Viga tabelis {table}: mitu rida vorm='{vorm}' and lemma='{lemma}'")
            elif table == "lemma_korpuse_vormid":
                # "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)]
                pbar = tqdm(self.json_in["tabelid"][table], desc=f'# {file} : {table} :', disable=(not self.verbose))
                for lemma, kaal, vorm in pbar:
                    res = self.cur_baas.execute(f"SELECT lemma, kaal, vorm FROM {table} WHERE lemma='{lemma}' and vorm='{vorm}'")
                    if len(res_fetchall:=res.fetchall()) == 0:
                        # sellist kirjet polnud, lisame uue
                        rec = (lemma, kaal, vorm)
                        self.cur_baas.execute(f"INSERT INTO {table} VALUES {rec}")
                    elif len(res_fetchall) == 1:
                        #selline kirje oli, liidame kaalud kokku, vajadusel uuendame kaalu
                        vana_kaal = res_fetchall[0][1]
                        uus_kaal = vana_kaal + kaal
                        if vana_kaal != uus_kaal: # kaal muutus, uuendame kaalu
                            self.cur_baas.execute(f"UPDATE {table} SET kaal='{uus_kaal}' WHERE lemma='{lemma}' and vorm='{vorm}'")
                    else:
                        # midagi väga valesti sest PRIMARY KEY(vorm, lemma)
                        raise ValueError(f"Viga tabelis {table}: mitu rida vorm='{vorm}' and lemma='{lemma}'")
            else:
                pbar = tqdm(self.json_in["tabelid"][table], desc=f'# {file} : {table} :', disable=(not self.verbose))
                for rec in pbar:
                    try:
                        self.cur_baas.execute(f"INSERT INTO {table} VALUES {tuple(rec)}")
                    except Exception as e:
                        # assert False, f'assert {getframeinfo(currentframe()).filename}:{getframeinfo(currentframe()).lineno}'  #DB
                        continue # selline juba oli, ignoreerime kordusi
            self.con_baas.commit()         
        
    def string2json(self, str:str)->Dict:
        """PRIVATE:String sisendJSONiga DICTiks

        Args:
            str (str): String sisendJSONiga

        Raises:
            Exception: Exception({"warning":"JSON parse error"})

        Returns:
            Dict: DICTiks tehtud sisendJSON
        """
        json_in = {}
        try:
            return json.loads(str.replace('\n', ' '))
        except:
            raise Exception({"warning":"JSON parse error"})



if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-v', '--verbose',  action="store_true", help='kuva rohkem infot')
    argparser.add_argument('-a', '--append',  action="store_true", help='lisa tabelid andmebaasi, ei kustata baasi varasemat sisu')
    argparser.add_argument('-b', '--db_name', type=str, help='väljundandmebaasi nimi')
    argparser.add_argument('-t', '--tables', type=str, help='kooloniga eraldatult tabelite nimed')
    argparser.add_argument('file', type=argparse.FileType('r'), nargs='+')
    args = argparser.parse_args()

    try:
        tables = args.tables.split(":")
        db = DB(args.append, args.db_name, tables, args.verbose)
        for f  in args.file:
            db.toimeta(f.name)
    except Exception as e:
        print(f"\n\n\nAn exception occurred: {str(e)}")
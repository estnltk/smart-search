#!/usr/bin/python3

'''
Kasutamine:
Code:

    {
        "name": "api_lisa_andmebaasidesse",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/ea_jsontabelid_2_db/",
        "program": "./api_jsontabelid_2_db.py",
        "args": [\
            "--verbose", \
            "--db_name=test.sqlite", \
            "--tables=ignoreeritavad_vormid:lemma_korpuse_vormid:lemma_kõik_vormid:liitsõnad:indeks_vormid:indeks_lemmad", \
            "../ea_jsoncontent_2_jsontabelid/1017-government_orders.json" \
            ],
        "env": {}
    }

Käsurealt:
$ cd ~/git/smart-search_github/api/ea_jsontabelid_2_db
$ ./create_venv.sh
$ ./venv/bin/python3 ./api_jsontabelid_2_db.py \
    --verbose --db_name=1017-baas_sl.sqlite \
    --tables=kirjavead_2:kirjavead:ignoreeritavad_vormid:lemma_korpuse_vormid:lemma_kõik_vormid:liitsõnad:indeks_vormid:indeks_lemmad \
    ../ea_jsoncontent_2_jsontabelid/1017-*.json 

SisendJson:
    {"tabelid":{ "kirjavead":[[VIGANE_VORM, VORM, KAAL]] }
    {"tabelid":{ "kirjavead_2": [[typo, lemma, correct_wordform, confidence]] }
    {"tabelid":{ "ignoreeritavad_vormid":[VORM] }
    {"tabelid":{ "lemma_korpuse_vormid":[(VORM, LEMMA)] }
    {"tabelid":{ "lemma_kõik_vormid":[(VORM, 0, LEMMA)] }
    {"tabelid":{ "liitsõnad":[(OSALEMMA, LIITLEMMA)] }
    {"tabelid":{ "indeks_vormid":[(VORM, DOCID, START, END, LIITSÕNA_OSA)] }
    {"tabelid":{ "indeks_lemmad":[(LEMMA, DOCID, START, END, LIITSÕNA_OSA)] }

 '''
import os
import sys
import json
import sqlite3
from tqdm import tqdm
from typing import Dict, List, Tuple
from inspect import currentframe, getframeinfo

class DB:
    def __init__(self, db_name:str, tables:List, verbose:bool)->None:
        self.verbose = verbose
        self.db_name = db_name
        self.tables = tables

        if self.verbose:
            sys.stdout.write("# teeme/avame andmebaasi ja tabelid")

        # päringu normaliseerimine: päringusõned -> lemmad
        # loome/avame andmebaasi
        if os.path.isfile(self.db_name):
            os.remove(self.db_name)
        self.con_baas = sqlite3.connect(self.db_name)
        self.cur_baas = self.con_baas.cursor()

        # {"tabelid":{ "kirjavead":[[VIGANE_VORM, VORM, KAAL]] }
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS kirjavead(
            vigane_vorm TEXT NOT NULL,  -- sõnavormi vigane versioon
            vorm TEXT NOT NULL,         -- korpuses esinenud sõnavorm
            kaal INT,                   -- sagedasemad vms võiksid olla suurema kaaluga
            PRIMARY KEY(vigane_vorm, vorm)
        )''')
        
        # {"tabelid":{ "kirjavead_2": [[typo, lemma, correct_wordform, confidence]] }
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS kirjavead_2(
            typo TEXT NOT NULL,              -- vigane versioon korrektsest sõnavormist
            lemma TEXT NOT NULL,             -- lemma
            correct_wordform TEXT NOT NULL,  -- korrektne sõnavorm            
            confidence INT,                  -- korrektse sõnavormi esinemiste arv
            PRIMARY KEY(typo, lemma, correct_wordform)
        )''')       
        
        # {"tabelid":{ "ignoreeritavad_vormid":[VORM] }
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS ignoreeritavad_vormid(
            ignoreeritav_vorm TEXT NOT NULL,  -- sellist sõnavormi ignoreerime päringus
            paritolu INT NOT NULL,            -- ignoreerimise põhjus int'iks kodeerituna                       
            PRIMARY KEY(ignoreeritav_vorm)
        )''')       

        # {"tabelid":{ "lemma_korpuse_vormid":[(VORM, LEMMA)] }
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS lemma_korpuse_vormid(
            lemma TEXT NOT NULL,        -- dokumendis esinenud sõnavormi lemma
            vorm TEXT NOT NULL,         -- lemma need sõnavormid, mis on mingis dokumendis dokumendis esinenud
            PRIMARY KEY(lemma, vorm)
        )''')

        # {"tabelid":{ "lemma_kõik_vormid":[(VORM, 0, LEMMA)] }
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS lemma_kõik_vormid( 
            vorm TEXT NOT NULL,         -- lemma kõikvõimalikud vormid genereerijast
            paritolu INT NOT NULL,      -- 0-lemma on leitud jooksvas dokumendis olevst sõnavormist; 1-vorm on lemma sünonüüm
            lemma TEXT NOT NULL,        -- korpuses esinenud sõnavormi lemma
            PRIMARY KEY(vorm, lemma)
        )''')

        # {"tabelid":{ "liitsõnad":[(OSALEMMA, LIITLEMMA)] }
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS liitsõnad( 
            osalemma TEXT NOT NULL,     -- liitsõna osasõna lemma
            liitlemma TEXT NOT NULL,    -- liitsõna osasõna lemmat sisaldav liitsõna lemma
            PRIMARY KEY(osalemma, liitlemma)
        )''')

        # {"tabelid":{ "indeks_vormid":[(VORM, DOCID, START, END, LIITSÕNA_OSA)] }
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS indeks_vormid(
                vorm  TEXT NOT NULL,          -- (jooksvas) dokumendis esinenud sõnavorm
                docid TEXT NOT NULL,          -- dokumendi id
                start INT,                    -- vormi alguspositsioon tekstis
                end INT,                      -- vormi lõpupositsioon tekstis
                liitsona_osa,                 -- 0: pole liitsõna osa; 1: on liitsõna osa
                PRIMARY KEY(vorm, docid, start, end)
                )
        ''')

        # {"tabelid":{ "indeks_lemmad":[(LEMMA, DOCID, START, END, LIITSÕNA_OSA)] }
        self.cur_baas.execute('''CREATE TABLE IF NOT EXISTS indeks_lemmad(
                lemma  TEXT NOT NULL,         -- (jooksvas) dokumendis esinenud sõna lemma
                docid TEXT NOT NULL,          -- dokumendi id
                start INT,                    -- lemmale vastava vormi alguspositsioon tekstis
                end INT,                      -- lemmale vastava vormi lõpupositsioon tekstis
                liitsona_osa,                 -- 0: pole liitsõna osa; 1: on liitsõna osa
                PRIMARY KEY(lemma, docid, start, end)
                )
        ''')

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
        print("-----")
        with open(file) as f:
            for line in f:
                self.json_in = self.string2json(line)
                self.täienda_tabelid(file)
 
    def täienda_tabelid(self, file:str)->None:
        """Kanna self.json_in'ist info andmbeaaaside tabelitesse
        """
        for table in self.tables:
            pass
            if table == "kirjavead":
                # {"tabelid":{ "kirjavead":[[VIGANE_VORM, VORM, KAAL]] }
                pbar = tqdm(self.json_in["tabelid"][table], desc=f'# {file} : {table} :', disable=(not self.verbose))
                for vigane_vorm, vorm, kaal in pbar:
                    res = self.cur_baas.execute(f"SELECT * FROM {table} WHERE vigane_vorm='{vigane_vorm}' and vorm='{vorm}'")
                    if len(res_fetchall:=res.fetchall()) > 0:
                        #selline juba oli, liidame kokku
                        if kaal > 0: # kaal muutub
                            for ret_vigane_vorm, ret_vorm, ret_kaal in res_fetchall:
                                uus_kaal = kaal + ret_kaal
                                self.cur_baas.execute(f"UPDATE {table} SET kaal='{uus_kaal}' WHERE vigane_vorm='{vigane_vorm}' and vorm='{vorm}'")
                    else:
                        # polnud, lisame uue
                        self.cur_baas.execute(f"INSERT INTO {table} VALUES('{vigane_vorm}','{vorm}',{kaal})")
            elif table == "kirjavead_2":
                # {"tabelid":{ "kirjavead_2": [[typo, lemma, correct_wordform, confidence]] }
                pbar = tqdm(self.json_in["tabelid"][table], desc=f'# {file} : {table} :', disable=(not self.verbose))
                for typo, lemma, correct_wordform, confidence in pbar:     
                    if typo == "EEesti": #DB
                        pass  #DB
                    res = self.cur_baas.execute(f"SELECT typo, lemma, correct_wordform, confidence FROM {table} WHERE typo='{typo}' and lemma='{lemma}' and correct_wordform ='{correct_wordform}'")
                    res_fetchall = res.fetchall()
                    if len(res_fetchall) > 0:
                        #selline juba oli, liidame kokku
                        assert len(res_fetchall) == 1, f'assert {getframeinfo(currentframe()).filename}:{getframeinfo(currentframe()).lineno}'  #DB
                        if confidence > 0: # kaal muutub
                            ret_typo, ret_lemma, ret_correct_wordform, ret_confidence = res_fetchall[0]
                            new_confidence = confidence + ret_confidence
                            self.cur_baas.execute(f"UPDATE {table} SET confidence='{new_confidence}' WHERE typo='{typo}' and lemma='{lemma}' and correct_wordform ='{correct_wordform}'")
                    else: # polnud, lisame uue
                        try:
                            self.cur_baas.execute(f"INSERT INTO {table} VALUES('{typo}','{lemma}','{correct_wordform}', '{confidence}')")
                            self.con_baas.commit()
                        except Exception as e:
                            assert False, f'assert {getframeinfo(currentframe()).filename}:{getframeinfo(currentframe()).lineno}'  #DB
            else:
                pbar = tqdm(self.json_in["tabelid"][table], desc=f'# {file} : {table} :', disable=(not self.verbose))
                for rec in pbar:
                    try:
                        #self.cur_baas.execute(f'INSERT INTO {table} VALUES({values_pattern})', rec)
                        test = f"INSERT INTO {table} VALUES{tuple(rec)}"
                        self.cur_baas.execute(f"INSERT INTO {table} VALUES{tuple(rec)}")
                    except Exception as e:
                        assert False, f'assert {getframeinfo(currentframe()).filename}:{getframeinfo(currentframe()).lineno}'  #DB
                        #continue # selline juba oli
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
    argparser.add_argument('-v', '--verbose',  action="store_true", help='tulemus CSV vormingus std väljundisse')
    argparser.add_argument('-b', '--db_name', type=str, help='väljundandmebaasi nimi')
    argparser.add_argument('-t', '--tables', type=str, help='kooloniga eraldatul tabelite nimed')
    argparser.add_argument('file', type=argparse.FileType('r'), nargs='+')
    args = argparser.parse_args()

    try:
        tables = args.tables.split(":")
        db = DB(args.db_name, tables, args.verbose)
        for f  in args.file:
            db.toimeta(f.name)
    except Exception as e:
        print(f"\n\n\nAn exception occurred: {str(e)}")
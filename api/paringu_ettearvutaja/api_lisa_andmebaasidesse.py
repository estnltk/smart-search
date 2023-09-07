#!/usr/bin/python3

import os
import sys
import json
import requests
import sqlite3
from typing import Dict, List, Tuple

class DB:
    def __init__(self, lemmatiseerija:str, indeks, verbose:bool)->None:
        self.verbose = verbose
        self.lemmatiseerija = lemmatiseerija
        self.indeks = indeks

        if self.verbose:
            sys.stdout.write("# teeme/avame andmebaasi ja tabelid")

        # päringu normaliseerimine: päringusõned -> lemmad
        # loome/avame andmebaasi
        self.con_lemmatiseerija = sqlite3.connect(self.lemmatiseerija)
        self.cur_lemmatiseerija = self.con_lemmatiseerija.cursor()

        # lisame puuduvad tabelid, kui nood puudusid
        # ["annotations"]["generator"]["tabelid"]["vorm_lemmaks"]:[(VORM,PARITOLU,LEMMA)]
        self.cur_lemmatiseerija.execute('''
            CREATE TABLE IF NOT EXISTS vorm_lemmaks( 
                vorm TEXT NOT NULL,         -- lemma kõikvõimalikud vormid genereerijast
                paritolu INT NOT NULL,      -- 0-lemma on leitud jooksvas dokumendis olevst sõnavormist; 1-vorm on lemma sünonüüm
                lemma TEXT NOT NULL,        -- korpuses esinenud sõnavormi lemma
                PRIMARY KEY(vorm, lemma)
            )
        ''')

        # ["annotations"]["generator"]["tabelid"]["kirjavead"]:[(VIGANE_VORM, VORM, KAAL)]
        self.cur_lemmatiseerija.execute('''
            CREATE TABLE IF NOT EXISTS kirjavead(
                vigane_vorm TEXT NOT NULL,  -- sõnavormi vigane versioon
                vorm TEXT NOT NULL,         -- korpuses esinenud sõnavorm
                kaal INT,                   -- sagedasemad vms võiksid olla suurema kaaluga
                PRIMARY KEY(vigane_vorm, vorm)
            )
        ''')
        
        # päringule vastamine : lemma -> sõnavormid korpuses -> indeksist esinemiskohad dokumentides
        # loome/avame andmebaasi
        self.con_indeks = sqlite3.connect(self.indeks)
        self.cur_indeks = self.con_indeks.cursor()       

        # lisame puuduvad tabelid, kui nood puudusid

        # ["annotations"]["generator"]["tabelid"]["lemma_korpuse_vormid"]:[(LEMMA, VORM)]
        self.cur_indeks.execute('''
            CREATE TABLE IF NOT EXISTS lemma_paradigma_korpuses(
                lemma TEXT NOT NULL,        -- dokumendis esinenud sõnavormi lemma
                vorm TEXT NOT NULL,         -- lemma need sõnavormid, mis on mingis dokumendis dokumendis esinenud
                PRIMARY KEY(lemma, vorm)
                )
        ''')

        #  ["annotations"]["indeks"]["sonavormid"]:[(TOKEN,DOCID,START,END,LIITSÕNA_OSA)]
        self.cur_indeks.execute('''    
            CREATE TABLE IF NOT EXISTS sonavormid(
                vorm  TEXT NOT NULL,          -- (jooksvas) dokumendis esinenud sõnavorm
                docid TEXT NOT NULL,          -- dokumendi id
                start INT,                    -- vormi alguspositsioon tekstis
                end INT,                      -- vormi lõpupositsioon tekstis
                liitsona_osa,                 -- 0: pole liitsõna osa; 1: on liitsõna osa
                PRIMARY KEY(vorm, docid, start, end)
                )
        ''')

        # ["sources"][DOCID]["content"]:DOKUMENDI_TEXT
        self.cur_indeks.execute('''    
            CREATE TABLE IF NOT EXISTS sources(
                docid TEXT NOT NULL,        -- dokumendi id
                content TEXT NOT NULL,      -- dokumendi text
                PRIMARY KEY(docid)
                )
        ''')  

        self.json_in = {}
        if self.verbose:
            sys.stdout.write("\n")

    def __del__(self)->None:
        if self.con_lemmatiseerija is not None:
            self.con_lemmatiseerija.close()
            if self.verbose is True:
                print(f"# Suletud andmebaas {self.lemmatiseerija}")  
        if self.con_indeks is not None:
            self.con_indeks.close()
            if self.verbose is True:
                print(f"# Suletud andmebaas {self.indeks}")                          

    def toimeta(self, file:str)->None:
        with open(file) as f:
            for line in f:
                self.json_in = self.string2json(line)
                self.täienda_vorm_lemmaks()

    def täienda_vorm_lemmaks(self)->None:
        """
        
        Kasutame:
        * self.json_in["annotations"]["generator"]["tabelid"]["vorm_lemmaks"]:[(VORM,PARITOLU,LEMMA)]

        Tulemus: täiendatud:
        * self.cur_lemmatiseerija.vorm_lemmaks(
            vorm TEXT NOT NULL,         -- lemma kõikvõimalikud vormid genereerijast
            paritolu INT NOT NULL,      -- 0-lemma on leitud jooksvas dokumendis olevst sõnavormist; 1-vorm on lemma sünonüüm; 2-kirjavigane vorm
            lemma TEXT NOT NULL,        -- korpuses esinenud sõnavormi lemma
            PRIMARY KEY(vorm, lemma)
        )
        """
        if self.verbose:
            sys.stdout.write("#                         Täiendame tabelit lemmatiseerija.vorm_lemmaks\r")
        for idx, rec in enumerate(self.json_in["annotations"]["generator"]["tabelid"]["vorm_lemmaks"]):
            if self.verbose:
                sys.stdout.write(f'{idx+1}/{len(self.json_in["annotations"]["generator"]["tabelid"]["vorm_lemmaks"])}\r')
            try:
                self.cur_lemmatiseerija.execute("INSERT INTO vorm_lemmaks VALUES(?, ?, ?)", rec)
            except:
                continue # selline juba oli
        self.con_lemmatiseerija.commit()
        if self.verbose:
            sys.stdout.write('\n')        

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
    argparser.add_argument('-l', '--lemmatiseerija', type=str, help='väljundandmebaasi nimi')
    argparser.add_argument('-i', '--indeks', type=str, help='väljundandmebaasi nimi')
    argparser.add_argument('file', type=argparse.FileType('r'), nargs='+')
    args = argparser.parse_args()

    try:
        db = DB(args.lemmatiseerija, args.indeks, args.verbose)

        for f  in args.file:
            if db.verbose:
                sys.stdout.write(f'\n# sisendfail: {f.name}\n')
                db.toimeta(f.name)
            pass    
            

    except Exception as e:
        print(f"\n\n\nAn exception occurred: {str(e)}")
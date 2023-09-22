#!/usr/bin/python3

'''
Silumine:
Code:
    {
        "name": "rt_web_crawler_csv_2_db",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/rt_web_crawler/rt_web_crawler_csv_2_db/",
        "program": "./rt_web_crawler_csv_2_db.py",
        "args": [   \
            "--verbose", \
            "--lemma_inf=../results/caption_index/state_laws.csv", \
            "--all_wordforms=../results/caption_index/state_laws_all_wordforms.csv", \
            "--normalisation_dictionary=../results/caption_index/state_laws_normalisation_dictionary.csv", \
            "--db=hl_normalization.db"
        ],
    }
    
Kasutamine (ei vaja virtuaalkeskkonda):
    ./rt_web_crawler_csv_2_db.py --verbose \
        --lemma_inf=../results/caption_index/state_laws.csv \
        --all_wordforms=../results/caption_index/state_laws_all_wordforms.csv \
        --normalisation_dictionary=../results/caption_index/state_laws_normalisation_dictionary.csv \
        --db=hl_normalization.db.db 
'''
import inspect
import csv
import sys
import sqlite3
from typing import Dict, List, Tuple

class DB:
    def __init__(self, db_name:str, verbose:bool)->None:
        self.verbose = verbose
        self.db_name = db_name

        if self.verbose:
            sys.stdout.write(f"# teeme/avame andmebaasi ja tabelid: {self.db_name}")

        # loome/avame andmebaasi
        self.con_db = sqlite3.connect(self.db_name)
        self.cur_db = self.con_db.cursor()

        # lemma_inf (state_laws.csv): (sublemma:bool,lemma:str,occurence_count:int,document_count:int)
        self.cur_db.execute('''
            CREATE TABLE IF NOT EXISTS lemma_inf( 
                sublemma INT NOT NULL,          -- 0:sublemma, 1:full lemma
                lemma TEXT NOT NULL,
                occurence_count INT NOT NULL,
                document_count INT NOT NULL,
                PRIMARY KEY(sublemma, lemma))
        ''')

        # all_wordforms(lemma:str, wordforms:str)
        self.cur_db.execute('''
            CREATE TABLE IF NOT EXISTS all_wordforms(
                lemma TEXT NOT NULL,
                wordform  TEXT NOT NULL,
                PRIMARY KEY(lemma, wordform))
        ''')

        # normalisation_dictionary (misspelling:bool, search_string:str, lemma:str)
        self.cur_db.execute('''
            CREATE TABLE IF NOT EXISTS normalisation_dictionary(
                misspelling INT NOT NULL, -- 1: misspelling, 0: correct wordform  
                search_string TEXT NOT NULL,
                lemma TEXT NOT NULL,
                PRIMARY KEY(misspelling, search_string, lemma))
        ''')

        self.json_in = {}
        if self.verbose:
            sys.stdout.write("\n")

    def __del__(self)->None:
        if self.con_db is not None:
            self.con_db.close()
            if self.verbose is True:
                print(f"# Suletud andmebaas {self.db_name}")  
                       
    def load_csv_2_db(self, table, pattern, csv_file)->None:
        if self.verbose:
            sys.stdout.write(f'# {inspect.currentframe().f_code.co_name}({table})...')
        my_csv = csv.reader(csv_file, delimiter=',')
        # normalisation_dictionary (misspelling:bool, search_string:str, lemma:str)
        insert_cmd = f"INSERT OR IGNORE INTO {table} VALUES({pattern})"
        self.cur_db.executemany(insert_cmd, my_csv)
        self.con_db.commit()  
        if self.verbose:
            sys.stdout.write('ok\n')

if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-v', '--verbose',  action="store_true", help='tulemus CSV vormingus std väljundisse')
    argparser.add_argument('-l', '--lemma_inf', type=argparse.FileType('r'), help='CSV faili nimi')
    argparser.add_argument('-a', '--all_wordforms', type=argparse.FileType('r'), help='CSV faili nimi')
    argparser.add_argument('-b', '--normalisation_dictionary', type=argparse.FileType('r'), help='CSV faili nimi')
    argparser.add_argument('-d', '--db', type=str, help='andmebaasi nimi')
    args = argparser.parse_args()

    try:
        db = DB(args.db, args.verbose)
        db.load_csv_2_db("lemma_inf", "?, ?, ?, ?", args.lemma_inf)
        db.load_csv_2_db("all_wordforms", "?, ?", args.all_wordforms)
        db.load_csv_2_db("normalisation_dictionary", "?, ?, ?", args.normalisation_dictionary)

    except Exception as e:
        print(f"\n\nAn exception occurred: {str(e)}")
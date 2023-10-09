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
            "--paring=päring.sqlite", \
            "--indeks=index.sqlite", \
            "../ea_jsoncontent_2_jsontabelid/table_government_orders.json", \
            "../ea_jsoncontent_2_jsontabelid/table_government_regulations.json" \
            "../ea_jsoncontent_2_jsontabelid/table_local_government_acts.json", \
            "../ea_jsoncontent_2_jsontabelid/table_state_laws.json", \
            ],
        "env": {}
    }

Käsurealt:
$ cd ~/git/smart-search_github/api/ea_jsontabelid_2_db
$ ./create_venv.sh
$ ./venv/bin/python3 ./api_jsontabelid_2_db.py \
    --verbose --paring=paring.sqlite --indeks=index.sqlite \
    ../ea_jsoncontent_2_jsontabelid/table_government_orders.json \
    ../ea_jsoncontent_2_jsontabelid/table_government_regulations.json \
    ../ea_jsoncontent_2_jsontabelid/table_local_government_acts.json \
    ../ea_jsoncontent_2_jsontabelid/table_state_laws.json

lemmataja
    "lemma_kõik_vormid": [(VORM, PARITOLU, LEMMA)],     # (LEMMA_kõik_vormid, 0:korpusest|1:abisõnastikust, sisendkorpuses_esinenud_sõnavormi_LEMMA)
    "ignoreeritavad_vormid": [(VORM, 0)],               # tee_ignoreeritavad_vormid(), 0:vorm on genereeritud etteantud lemmast
    "kirjavead": [(VIGANE_VORM, VORM, KAAL)]            # (kõikvõimalikud_VORMi_kirjavigased_variandid, sisendkorpuses_esinenud_sõnaVORM, kaal_hetkel_alati_0)

indeks
    "lemma_korpuse_vormid": [(LEMMA, VORM)],             # (sisendkorpuses_esinenud_sõnavormi_LEMMA, kõik_LEMMA_vormid_mis_sisendkorpuses_esinesid)
    "indeks": [(VORM, DOCID, START, END, LIITSÕNA_OSA)] # (sisendkorpuses_esinenud_sõnaVORM, dokumendi_id, alguspos, lõpupos, True:liitsõna_osa|False:terviksõna)
    "allikad": [(DOCID, CONTENT)]                       # (docid, dokumendi_"plain_text"_mille_suhtes_on_arvutatud_START_ja_END)
'''

import sys
import json
import sqlite3
from tqdm import tqdm
from typing import Dict, List, Tuple

class DB:
    def __init__(self, paring:str, indeks:str, verbose:bool)->None:
        self.verbose = verbose
        self.paring = paring
        self.indeks = indeks

        if self.verbose:
            sys.stdout.write("# teeme/avame andmebaasi ja tabelid")

        # päringu normaliseerimine: päringusõned -> lemmad
        # loome/avame andmebaasi
        self.con_paring = sqlite3.connect(self.paring)
        self.cur_paring = self.con_paring.cursor()

        # lisame puuduvad tabelid, kui nood puudusid
        # ["tabelid"]["lemma_kõik_vormid"]:[(VORM,PARITOLU,LEMMA)]
        self.cur_paring.execute('''
            CREATE TABLE IF NOT EXISTS lemma_kõik_vormid( 
                vorm TEXT NOT NULL,         -- lemma kõikvõimalikud vormid genereerijast
                paritolu INT NOT NULL,      -- 0-lemma on leitud jooksvas dokumendis olevst sõnavormist; 1-vorm on lemma sünonüüm
                lemma TEXT NOT NULL,        -- korpuses esinenud sõnavormi lemma
                PRIMARY KEY(vorm, lemma)
            )
        ''')

        # ["tabelid"]["kirjavead"]:[(VIGANE_VORM, VORM, KAAL)]
        self.cur_paring.execute('''
            CREATE TABLE IF NOT EXISTS kirjavead(
                vigane_vorm TEXT NOT NULL,  -- sõnavormi vigane versioon
                vorm TEXT NOT NULL,         -- korpuses esinenud sõnavorm
                kaal INT,                   -- sagedasemad vms võiksid olla suurema kaaluga
                PRIMARY KEY(vigane_vorm, vorm)
            )
        ''')
        
        # ["tabelid"]["ignoreeritavad_vormid"]:[VORM]
        self.cur_paring.execute('''
            CREATE TABLE IF NOT EXISTS ignoreeritavad_vormid(
                ignoreeritav_vorm TEXT NOT NULL,  -- sellist sõnavormi ignoreerime päringus
                paritolu INT NOT NULL,            -- 0:etteantud lemmast genreeritud                       
                PRIMARY KEY(ignoreeritav_vorm)
            )
        ''')       

        # päringule vastamine : lemma -> sõnavormid korpuses -> indeksist esinemiskohad dokumentides
        # loome/avame andmebaasi
        self.con_indeks = sqlite3.connect(self.indeks)
        self.cur_indeks = self.con_indeks.cursor()       

        # lisame puuduvad tabelid, kui nood puudusid

        # ["tabelid"]["lemma_korpuse_vormid"]:[(LEMMA, VORM)]
        self.cur_indeks.execute('''
            CREATE TABLE IF NOT EXISTS lemma_korpuse_vormid(
                lemma TEXT NOT NULL,        -- dokumendis esinenud sõnavormi lemma
                vorm TEXT NOT NULL,         -- lemma need sõnavormid, mis on mingis dokumendis dokumendis esinenud
                PRIMARY KEY(lemma, vorm)
                )
        ''')

        #  ["tabelid"]["indeks"][(TOKEN,DOCID,START,END,LIITSÕNA_OSA)]
        self.cur_indeks.execute('''    
            CREATE TABLE IF NOT EXISTS indeks(
                vorm  TEXT NOT NULL,          -- (jooksvas) dokumendis esinenud sõnavorm
                docid TEXT NOT NULL,          -- dokumendi id
                start INT,                    -- vormi alguspositsioon tekstis
                end INT,                      -- vormi lõpupositsioon tekstis
                liitsona_osa,                 -- 0: pole liitsõna osa; 1: on liitsõna osa
                PRIMARY KEY(vorm, docid, start, end)
                )
        ''')

        # ["tabelid"]["allikad"]:[(DOCID, CONTENT)]
        self.cur_indeks.execute('''    
            CREATE TABLE IF NOT EXISTS allikad(
                docid TEXT NOT NULL,        -- dokumendi id
                content TEXT NOT NULL,      -- dokumendi text
                PRIMARY KEY(docid)
                )
        ''')  

        self.json_in = {}
        if self.verbose:
            sys.stdout.write("\n")

    def __del__(self)->None:
        if self.con_paring is not None:
            self.con_paring.close()
            if self.verbose is True:
                print(f"# Suletud andmebaas {self.paring}")  
        if self.con_indeks is not None:
            self.con_indeks.close()
            if self.verbose is True:
                print(f"# Suletud andmebaas {self.indeks}")                          

    def toimeta(self, file:str)->None:
        if self.verbose:
            sys.stdout.write(f'# sisendfail: {file}\n') 
        with open(file) as f:
            for line in f:
                self.json_in = self.string2json(line)
                self.täienda_tabelid()
 
    def täienda_tabelid(self)->None:
        """Kanna self.json_in'ist info andmbeaaaside tabelitesse
        """
        
        """
        * self.json_in["tabelid"]["lemma_kõik_vormid"]:[(VORM,PARITOLU,LEMMA)]
        * self.cur_paring.lemma_kõik_vormid(
            vorm TEXT NOT NULL,         -- lemma kõikvõimalikud vormid genereerijast
            paritolu INT NOT NULL,      -- 0-lemma on leitud jooksvas dokumendis olevast sõnavormist; 1-vorm on lemma sünonüüm
            lemma TEXT NOT NULL,        -- korpuses esinenud sõnavormi lemma
            PRIMARY KEY(vorm, lemma)

        """
        self.täienda_tabel(self.con_paring, self.cur_paring, "paring", "lemma_kõik_vormid", "?, ?, ?")
        
        """
        * self.json_in["tabelid"]["lemma_korpuse_vormid"]:[(LEMMA, VORM)]
        * self.cur_indeks.lemma_korpuse_vormid(
                lemma TEXT NOT NULL,        -- dokumendis esinenud sõnavormi lemma
                vorm TEXT NOT NULL,         -- lemma need sõnavormid, mis on mingis dokumendis dokumendis esinenud
                PRIMARY KEY(lemma, vorm)
        """
        self.täienda_tabel(self.con_paring, self.cur_paring, "paring", "lemma_korpuse_vormid", "?, ?")


        """
        * self.json_in["tabelid"]["kirjavead"]:[(VIGANE_VORM, VORM, KAAL)]
        * self.cur_paring.kirjavead(
                vigane_vorm TEXT NOT NULL,  -- sõnavormi vigane versioon
                vorm TEXT NOT NULL,         -- korpuses esinenud sõnavorm
                kaal INT,                   -- sagedasemad vms võiksid olla suurema kaaluga
                PRIMARY KEY(vigane_vorm, vorm)
        """
        self.täienda_tabel(self.con_paring, self.cur_paring, "paring", "kirjavead", "?, ?, ?")
        
        """
        # self.json_in["tabelid"]["ignoreeritavad_vormid"]:[VORM]
        self.cur_paring.ignoreeritavad_vormid(
                ignoreeritav_vorm TEXT NOT NULL,  -- sellist sõnavormi ignoreerime päringus
                paritolu INT NOT NULL,            -- 0:korpusest tuletatud, 1:etteantud vorm                       
                PRIMARY KEY(ignoreeritav_vorm)
        """
        if "ignoreeritavad_vormid" in self.json_in["tabelid"]:
            self.täienda_tabel(self.con_paring, self.cur_paring, "paring", "ignoreeritavad_vormid", "?, ?")

        """
        * self.json_in["tabelid"]["lemma_korpuse_vormid"]:[(LEMMA, VORM)]
        * self.cur_indeks.lemma_korpuse_vormid(
                lemma TEXT NOT NULL,        -- dokumendis esinenud sõnavormi lemma
                vorm TEXT NOT NULL,         -- lemma need sõnavormid, mis on mingis dokumendis dokumendis esinenud
                PRIMARY KEY(lemma, vorm)
        """
        self.täienda_tabel(self.con_indeks, self.cur_indeks, "indeks", "lemma_korpuse_vormid", "?, ?")
        
        """
        * self.json_in["indeks"]:[(TOKEN,DOCID,START,END,LIITSÕNA_OSA)]
        * self.cur_indeks.indeks(
                vorm  TEXT NOT NULL,          -- (jooksvas) dokumendis esinenud sõnavorm
                docid TEXT NOT NULL,          -- dokumendi id
                start INT,                    -- vormi alguspositsioon tekstis
                end INT,                      -- vormi lõpupositsioon tekstis
                liitsona_osa,                 -- 0: pole liitsõna osa; 1: on liitsõna osa
                PRIMARY KEY(vorm, docid, start, end)
        """
        self.täienda_tabel(self.con_indeks, self.cur_indeks, "indeks","indeks", "?, ?, ?, ?, ?")
        
        """
        * self.json_in["annotations"]["generator"]["tabelid"]["allikad"]:[(DOCID, CONTENT)]
        * self.cur_indeks.allikad(
                docid TEXT NOT NULL,        -- dokumendi id
                content TEXT NOT NULL,      -- dokumendi text
                PRIMARY KEY(docid)
        """
        self.täienda_tabel(self.con_indeks, self.cur_indeks, "indeks","allikad", "?, ?")
        
    def täienda_tabel(self, connection, cursor, prefstr:str, table:str, values_pattern:str)->None: 
        """Täiendame andmebaasi uute kirjetaga
        
        Args:
            values (List): Selle massiivi elemendid lisame vastavasse andmebaasi tabelisse
            cursor: andmebaasi kursor
            table (str): andmebaasi tabeli nimi
            values_pattern (str): lisatava kirje muster
        )
        """
        if self.verbose:
            sys.stdout.write(f'#                         Täiendame tabelit {table}\r')
        pbar = tqdm(self.json_in["tabelid"][table], desc=f'# {prefstr} {table}')
        #pbar.set_description(f'# {table}')
        for rec in pbar:
            try:
                cursor.execute(f'INSERT INTO {table} VALUES({values_pattern})', rec)
            except:
                continue # selline juba oli
        connection.commit()
   
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
    argparser.add_argument('-p', '--päring', type=str, help='väljundandmebaasi nimi')
    argparser.add_argument('-i', '--indeks', type=str, help='väljundandmebaasi nimi')
    argparser.add_argument('file', type=argparse.FileType('r'), nargs='+')
    args = argparser.parse_args()

    try:
        db = DB(args.päring, args.indeks, args.verbose)
        for f  in args.file:
            db.toimeta(f.name)
    except Exception as e:
        print(f"\n\n\nAn exception occurred: {str(e)}")
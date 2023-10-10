#!/usr/bin/python3

import sys
import json
import sqlite3
from tqdm import tqdm
from typing import Dict, List, Tuple

'''
cd ~/git/smart-search_github/api/ea_jsontabelid_2_db

Silumiseks
    {
        "name": "arvuta_juurde",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/ea_jsontabelid_2_db/",
        "program": "./api_arvuta_juurde.py",
        "env": {},
        "args": ["--verbose", "--db_name=koondbaas.sqlite"]
    },


    {   "location": int,  // sõne nr päringus
        "input":str,      // päringusõne
        "inf":
        [   {   "lemma": str,       // päringusõne lemma
                "suggestion":
                [   {   "vorm": str, // soovitatud "õige" sõnavorm päringusõnest
                        "confidence": float 
                    }
                ],
                "lemma_all_forms": [str], // lemma/päringusõne kõikvõimalikud vormid, mida otsida
                "lemma_corp_forms": [str] // lemma korpuses esinenud vormid - või jätame selle ära?
            }
        ]
    }

koond:
    "lemma_kõik_vormid": [(VORM, PARITOLU, LEMMA)],     # (LEMMA_kõik_vormid, 0:korpusest|1:abisõnastikust, sisendkorpuses_esinenud_sõnavormi_LEMMA)
    "lemma_korpuse_vormid": [(LEMMA, VORM)],            # (sisendkorpuses_esinenud_sõnavormi_LEMMA, kõik_LEMMA_vormid_mis_sisendkorpuses_esinesid)
    "ignoreeritavad_vormid": [(VORM, 0)],               # tee_ignoreeritavad_vormid(), 0:vorm on genereeritud etteantud lemmast
    "kirjavead": [(VIGANE_VORM, VORM, KAAL)]            # (kõikvõimalikud_VORMi_kirjavigased_variandid, sisendkorpuses_esinenud_sõnaVORM, kaal_hetkel_alati_0)
    "kirjavead_2": [(typo, lemma, correct_wordform, confidence)]
    "indeks": [(VORM, DOCID, START, END, LIITSÕNA_OSA)] # (sisendkorpuses_esinenud_sõnaVORM, dokumendi_id, alguspos, lõpupos, True:liitsõna_osa|False:terviksõna)
    "allikad": [(DOCID, CONTENT)]                       # (docid, dokumendi_"plain_text"_mille_suhtes_on_arvutatud_START_ja_END)

'''

class DB:
    def __init__(self, db_name:str, verbose:bool)->None:
        self.verbose = verbose
        self.db_name = db_name

        if self.verbose:
            sys.stdout.write("# teeme/avame andmebaasi ja tabelid")

        # loome/avame andmebaasi
        self.con_baas = sqlite3.connect(self.db_name)
        self.cur_baas = self.con_baas.cursor()

        self.cur_baas.execute('''
            CREATE TABLE IF NOT EXISTS kirjavead_2( 
                typo TEXT NOT NULL,
                lemma TEXT NOT NULL,
                correct_wordform TEXT NOT NULL,
                confidence INT,
                PRIMARY KEY(typo, lemma, correct_wordform)                       
            )
        ''')

    def __del__(self)->None:
        if self.con_baas is not None:
            self.con_baas.close()
            if self.verbose is True:
                print(f"# Suletud andmebaas {self.db_name}")  

    def toimeta(self):
        res_fetchall = []
        try:
            res = self.cur_baas.execute(f'''
                SELECT
                    vigane_vorm,
                    vorm
                    FROM kirjavead                         
                ''')
            res_fetchall = res.fetchall()
        except:
            pass
        pbar = tqdm(res_fetchall)
        for idx, (vigane_vorm, korrektne_vorm) in enumerate(pbar):
            res2_fetchall = []
            try:
                res2 = self.cur_baas.execute(f"""
                    SELECT
                        kirjavead.vigane_vorm,   -- 0
                        lemma_kõik_vormid.lemma, -- 1
                        lemma_kõik_vormid.vorm,  -- 2
                        indeks.docid,            -- 3
                        indeks.start             -- 4
                    FROM kirjavead 
                    INNER JOIN lemma_kõik_vormid ON kirjavead.vorm = lemma_kõik_vormid.vorm
                    INNER JOIN indeks ON indeks.vorm = lemma_kõik_vormid.vorm
                    WHERE kirjavead.vigane_vorm = '{vigane_vorm}' AND lemma_kõik_vormid.vorm = '{korrektne_vorm}'                                      
                """)
                                                #  0     1      2          3      4
                res2_fetchall = res2.fetchall() # (typo, lemma, õige_vorm, docid, start)
            except:
                pass

            '''
              0       1        2                 3      4
            { typo: { lemma: { õige_sõnavorm: [ (docid, start) ] } } } }
            '''
            if len(res2_fetchall) > 0:
                inf = {}
                for rec in res2_fetchall:
                    if rec[0] not in inf: # typo
                        inf[rec[0]] = {}
                    if rec[1] not in inf[rec[0]]: # lemma
                        inf[rec[0]][rec[1]] = {}
                    if rec[2] not in inf[rec[0]][rec[1]]:
                        inf[rec[0]][rec[1]][rec[2]] = [] # õige_vorm
                    inf[rec[0]][rec[1]][rec[2]].append((rec[3], rec[4]))

                pass
                for typo, lemmas in inf.items():
                    for lemma, õiged_vormid in inf[typo].items():
                        for õige_vorm, esinemised in inf[typo][lemma].items():
                            try:
                                self.cur_baas.execute(
                                    'INSERT INTO kirjavead_2 VALUES(?, ?, ?, ?)',
                                    (typo, lemma, õige_vorm, len(esinemised)))
                            except:
                                pass
            else:
                res3_fetchall = []
                try:

                    res3 = self.cur_baas.execute(f"""
                        SELECT
                            kirjavead.vigane_vorm,
                            lemma_kõik_vormid.lemma,
                            lemma_kõik_vormid.vorm
                        FROM kirjavead 
                        INNER JOIN lemma_kõik_vormid ON kirjavead.vorm = lemma_kõik_vormid.vorm
                        WHERE kirjavead.vigane_vorm = '{vigane_vorm}' AND lemma_kõik_vormid.vorm = '{korrektne_vorm}'                                    
                    """)
                                                    #  0     1      2
                    res3_fetchall = res3.fetchall() # (typo, lemma, õige_vorm)
                except:
                    pass
                '''
                  0       1        2
                { typo: { lemma: [ õige_sõnavorm ] } } }
                '''
                inf = {}
                for rec in res2_fetchall:
                    if rec[0] not in inf: # typo
                        inf[rec[0]] = {}
                    if rec[1] not in inf[rec[0]]: # lemma
                        inf[rec[0]][rec[1]] = []
                    if rec[2] not in inf[rec[0]][rec[1]]:
                        inf[rec[0]][rec[1]].append(rec[2])

                for typo, lemmas in inf.items():
                    for lemma, õiged_vormid in inf[typo].items():
                        for õige_vorm in inf[typo][lemma]:
                            try:
                                self.cur_baas.execute(
                                    'INSERT INTO kirjavead_2 VALUES(?, ?, ?, ?)',
                                    (typo, lemma, õige_vorm, 0))
                            except:
                                pass
        self.con_baas.commit()




if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-v', '--verbose',  action="store_true", help='tulemus CSV vormingus std väljundisse')
    argparser.add_argument('-b', '--db_name', type=str, help='sisendandmebaasi nimi')
    args = argparser.parse_args()

    try:
        db = DB(args.db_name, args.verbose)
        db.toimeta()
    except Exception as e:
        print(f"\n\n\nAn exception occurred: {str(e)}")
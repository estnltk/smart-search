#!/usr/bin/python3

"""
Silumiseks:

    {
        "name": "api-paringu-ettearvutaja",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/paringu_ettearvutaja/",
        "program": "./api_paringu_ettearvutaja.py",
        // "args": ["--json", "--indent=4", "microcorpus2.json", "microcorpus3.json", "microcorpus1.json"]
        //"args": ["--csv", "microcorpus2.json", "microcorpus3.json", "microcorpus1.json"]
        "args": ["--db=../../testkorpused/microcorpus/ettervutaja.db", \
            "../../testkorpused/microcorpus/microcorpus2.json", \
            "../../testkorpused/microcorpus/microcorpus3.json", \
            "../../testkorpused/microcorpus/microcorpus1.json"]
        "env": {\
            "OTSING_SONED": "https://smart-search.tartunlp.ai/api/sonede-indeks/check", \
            "GENERATOR": "https://smart-search.tartunlp.ai/api/generator/process", \
            "INDEKSEERIJA_LEMMAD": "https://smart-search.tartunlp.ai/api/lemmade-indekseerija", \
            "TOKENIZER": "https://smart-search.tartunlp.ai/api/tokenizer/process", \
            "ANALYSER": "https://smart-search.tartunlp.ai/api/analyser/process" \
        }
    }

"""


import os
import sys
import json
import requests
#import subprocess
import json
import argparse
#from flask import Flask, request, jsonify, make_response
from typing import Dict, List, Tuple
from collections import OrderedDict
import sqlite3
import csv
import io

class ETTEARVUTAJA:
    def __init__(self, db:str, verbose:bool)->None:
        """Initsialiseerime muutujad: versiooninumber,kasutatavate veebiteenuste URLid, andmebaasi nimi jne

        Args:
            db (str): andmebaasi nimi, eelistame seda keskkonnamuutujaga määratule
            verbose (bool): kuva tööjärjega seotud infot
        """
        self.verbose = verbose

        self.VERSION="2023.08.22"

        self.otsing = os.environ.get('OTSING_SONED') # veebiteenus sõnavormide indeksis olemise kontrollimiseks
        if self.otsing is None: 
            self.OTSING_SONED_IP=os.environ.get('OTSING_SONED_IP') if os.environ.get('OTSING_SONED_IP') != None else 'localhost'
            self.OTSING_SONED_PORT=os.environ.get('OTSING_SONED_PORT') if os.environ.get('OTSING_SONED_PORT') != None else '7007'
            self.otsing = f'http://{self.OTSING_SONED_IP}:{self.OTSING_SONED_PORT}/api/sonede-indeks/check'

        self.tokenizer = os.environ.get('TOKENIZER') # veebiteenus sõnestamiseks
        if self.tokenizer is None:
            self.TOKENIZER_IP=os.environ.get('TOKENIZER_IP') if os.environ.get('TOKENIZER_IP') != None else 'localhost'
            self.TOKENIZER_PORT=os.environ.get('TOKENIZER_PORT') if os.environ.get('TOKENIZER_PORT') != None else '6000'
            self.tokenizer = f'http://{self.TOKENIZER_IP}:{self.TOKENIZER_PORT}/api/tokenizer/process'

        self.analyser = os.environ.get('ANALYSER')  # veebiteenus morf analüüsiks
        if self.analyser is None:
            self.ANALYSER_IP=os.environ.get('ANALYSER_IP') if os.environ.get('ANALYSER_IP') != None else 'localhost'
            self.ANALYSER_PORT=os.environ.get('ANALYSER_PORT') if os.environ.get('ANALYSER_PORT') != None else '7007'
            self.analyser = f'http://{self.ANALYSER_IP}:{self.ANALYSER_PORT}/api/analyser/process'

        self.generator = os.environ.get('GENERATOR') # veebiteenus morf genemiseks
        if self.generator is None:
            self.GENERATOR_IP=os.environ.get('GENERATOR_IP') if os.environ.get('GENERATOR_IP') != None else 'localhost'
            self.GENERATOR_PORT=os.environ.get('GENERATOR_PORT') if os.environ.get('GENERATOR_PORT') != None else '7000'
            self.generator = f'http://{self.GENERATOR_IP}:{self.GENERATOR_PORT}/process' # NB! generaator ei ole selle koha peal analoogiline teiste teenustega
        
        self.db_ettarvutatud_generaator = os.environ.get('DB_ETTEARVUTATUD_GENRAATOR')
        if db is not None:
            self.db_ettarvutatud_generaator = db # eelistame käsurealt antud andmebaasi nime

        self.ignore_pos = "PZJ" # ignoreerime lemmasid, mille sõnaliik on: Z=kirjavahemärk, J=sidesõna, P=asesõna

        self.con = None
        if self.db_ettarvutatud_generaator is not None:
            if os.path.isfile(db) is False:
                # andmebaasi veel pole, teeme tühja andmebaasi ja tabelid
                self.con = sqlite3.connect(db)
                self.cur = self.con.cursor()

                self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS vorm_lemmaks(
                        vorm TEXT NOT NULL,
                        lemma TEXT NOT NULL,
                        PRIMARY KEY(vorm, lemma)
                        )
                ''')
                self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS lemma_paradigma_korpuses(
                        lemma TEXT NOT NULL,
                        vorm TEXT NOT NULL,
                        PRIMARY KEY(lemma, vorm)
                        )
                ''')  
                if self.verbose is True:
                    print(f"Loodud andmebaas {self.db_ettarvutatud_generaator} ja tabelid (vorm_lemmaks, lemma_paradigma_korpuses)")           
            else:
                self.con = sqlite3.connect(db)
                self.cur = self.con.cursor()
                if self.verbose is True:
                    print(f"Avatud andmebaas {self.db_ettarvutatud_generaator}")           


    def __del__(self)->None:
        """Sulgeb avatud andmebaasi (kui oli avatud).
        """
        if self.con is not None:
            self.con.close()
            if self.verbose is True:
                print(f"Suletud andmebaas {self.db_ettarvutatud_generaator}")           
  

    def string2json(self, str:str)->Dict:
        """String sisendJSONiga DICTiks

        Args:
            str (str): String sisendJSONiga

        Raises:
            Exception: Exception({"warning":"JSON parse error"})

        Returns:
            Dict: Sõnastikuks tehtud sisendJSON
        """
        json_in = {}
        try:
            return json.loads(str.replace('\n', ' '))
        except:
            raise Exception({"warning":"JSON parse error"})

    def morfi(self)->None:
        """Morfime sõnestatud sisendkorpused

        Kasutame: 
            self.json_io; morf analüüsi veebiteenust.

        Raises:
            Exception: Exception({"warning":'Probleemid veebiteenusega: {self.analyser}'})

        Returns:
            None, lisab self.json_io'sse morf analüüsid
        """

        for docid in self.json_io["sources"]:
            self.json_io["sources"][docid]["params"] = {"vmetajson":["--guess"]}
            try:
                doc = json.loads(requests.post(self.analyser, json=self.json_io["sources"][docid]).text)
            except:
                raise Exception({"warning":'Probleemid veebiteenusega: {self.analyser}'})
            for idx_token, token in enumerate(doc["annotations"]["tokens"]):        # tsükkel üle sõnede (ainult üks sõne meil antud juhul on)
                tokens = []                                                             # siia korjame erinevad lemma-stringid
                for mrf in token["features"]["mrf"]:                                    # tsükkel üle sama sõne alüüsivariantide (neid võib olla mitu)
                    if self.ignore_pos.find(mrf["pos"]) != -1:                              # selle sõnaliiiga lemmasid...
                        continue                                                                # ...ignoreerime, neid ei indekseeri
                    if mrf["lemma_ma"] not in tokens:                                                   # sõne morf analüüside hulgas võib sama kujuga lemma erineda ainult käände/põõrde poolest
                        tokens.append( mrf["lemma_ma"])                                                      # lisame uue lemma-stringi, kui sellist veel polnud
                self.json_io["sources"][docid]["annotations"]["tokens"][idx_token]["features"]["tokens"] = tokens # lisame leitud lemmad tulemusse
    
    def tee_paradigmad(self, lemma:str)-> (List[str], List[str]):
        """Leiame sisendlemma kõik vormid ja nende hulgast need mis tegelikult korpuses esinesid

        Args:
            lemma (str): lemma

        Kasutame: 
            Sõnavormide genereerimise veebiteenust; veebiteenust mis ütleb millised sõnavormid tegelikult korpuses esinesid.


        Raises:
            Exception: Exception({"warning":'Probleemid veebiteenusega: {self.generator}'})
            Exception: Exception({"warning":f'Probleemid veebiteenusega: {self.paring}'})

        Returns:
            List, List: paradigma_täielik -- lemma kõik vormid, paradigma_korpuses -- lemma korpuses esinevad vormid
        """
        # gene selle lemma kõik vormid
        try:
            generator_out = json.loads(requests.post(self.generator, json={"type":"text", "content": lemma}).text)
        except:
            raise Exception({"warning":'Probleemid veebiteenusega: {self.generator}'})
        # lisa saadud vormid päringusse
        paradigma_täielik = []
        for text in generator_out["response"]["texts"]:
            for generated_form in text["features"]["generated_forms"]:
                paradigma_täielik.append(generated_form["token"].replace("_", "").replace("=", "").replace("+", ""))
        
        # leiame lemma kõigi vormide hulgast need, mis esinesid korpuses
        paradigma_korpuses = []
        if len(paradigma_täielik) > 0:
            try:
                paradigma_korpuses = json.loads(requests.post(self.otsing, json=paradigma_täielik).text)
            except:
                raise Exception({"warning":f'Probleemid veebiteenusega: {self.otsing}'})
        return paradigma_täielik, paradigma_korpuses

    def tee_lemmade_indeks(self, json_in:Dict) -> None:
        """Tekitab lemmade indeksi

        Args:
            json_in (Dict): SisendJSON, sisaldab korpusetekste

            json_in
            {   "sources":
                {   DOCID:              // dokumendi ID
                    {   "content": str  // dokumendi tekst ("plain text", märgendus vms teraldi tõstetud)
                                        // dokumendi kohta käiv lisainfo pane siia...
                    }
                }
            }

        Raises:
            Exception: Exception({"warning":f'Probleemid veebiteenusega: {self.tokenizer}'})

        Returns: 
            self.json_io:
            
            {   "index":
                {   "lemma_paradigma_korpuses":
                    {   LEMMA: [VORM] # LEMMA esines korpuses VORMides
                    }
                    "lemma_paradigma_täielik":
                    {   LEMMA: [VORM] # LEMMA kõikvõimalikud VORMid
                    }
                }
            }
        """
        self.json_io = json_in
        if self.verbose is True:
            print(f"Teeme lemmade indeksi")
            for docid in self.json_io["sources"]:
                print(f"  {docid}")
        for docid in self.json_io["sources"]:
            try:                                                # sõnestame kõik dokumendid
                self.json_io["sources"][docid] = json.loads(requests.post(self.tokenizer, json=self.json_io["sources"][docid]).text)
            except:                                             # sõnestamine äpardus
                raise Exception({"warning":f'Probleemid veebiteenusega: {self.tokenizer}'})
        self.morfi()                                            # leiame iga tekstisõne võimalikud sobiva sõnaliigiga tüvi+lõpud (liitsõnapiir='_', järelliite eraldaja='=')   
        if "index" not in self.json_io:                         # geneme iga lemma kõik vormid
            self.json_io["index"] = {"lemma_paradigma_korpuses":{},"lemma_paradigma_täielik":{}}
        for docid in self.json_io["sources"]:                   # tsükkel üle tekstide
            for token in self.json_io["sources"][docid]["annotations"]["tokens"]: # tsükkel üle lemmade
                if len(token["features"]["tokens"])==0:             # kui pole ühtegi meid huvitava sõnaliigiga...
                    continue                                            # ...laseme üle
                for tkn in token["features"]["tokens"]:             # tsükkel üle leitud liitsõnapiiridega lemmade
                    puhas_tkn = tkn.replace('_', '').replace('=', '')   # terviklemma lisamine...
                    if puhas_tkn not in self.json_io["index"]["lemma_paradigma_korpuses"]:
                        # sellist lemmat meil veel polnud, lisame genetud/korpuse vormid
                        paradigma_täielik, paradigma_korpuses = self.tee_paradigmad(puhas_tkn) # leiame lemma kõik vormid ja korpuses esinenud vormid
                        assert puhas_tkn in paradigma_täielik, "Lemma ei sisaldu täisparadigmas"
                        if len(paradigma_korpuses) > 0: # ainult siis, kui päriselt korpuses esines
                            self.json_io["index"]["lemma_paradigma_korpuses"][puhas_tkn] = paradigma_korpuses
                            self.json_io["index"]["lemma_paradigma_täielik"][puhas_tkn]  = paradigma_täielik

            del self.json_io["sources"][docid]["annotations"]["sentences"] # kustutame sõnaestajast ja morf analüüsist järgi jäänud mudru
            del self.json_io["sources"][docid]["annotations"]["tokens"]
            if len(self.json_io["sources"][docid]["annotations"]) == 0:
                del self.json_io["sources"][docid]["annotations"]
            del self.json_io["sources"][docid]["params"]
        del self.json_io["sources"]                                        # kustutame algdsed dokumendid

    def tee_json(self)->None:
        """Teeme valmis lõpliku väljundJSONi

        Args: 
            self.json_io:

            {   "index":
                {   "lemma_paradigma_korpuses":
                    {   LEMMA: [VORM] # LEMMA esines korpuses VORMides
                    }
                    "lemma_paradigma_täielik":
                    {   LEMMA: [VORM] # LEMMA kõikvõimalikud VORMid
                    }
                }
            }

        Returns:
            self.json_io:

            {   "index":
                {   "lemma_paradigma_korpuses": # järjestatud LEMMA järgi
                    {   LEMMA: [VORM] # LEMMA esines korpuses VORMides
                    }
                    "vorm_lemmaks":     # täisparadigma vorm lemmaks, järjestatud VORMi järgi
                    {   VORM: [LEMMA]   # LEMMA ∈ self.json_io["index"]["lemma_paradigma_korpuses"]
                                        # VORM  ⊆ self.json_io["index"]["lemma_paradigma_täielik"][LEMMA]
                                        
                    }
                }
            }        
        """
        self.json_io["index"]["vorm_lemmaks"] = {}
        for lemma in self.json_io["index"]["lemma_paradigma_täielik"]:
            lemma_paradigma_täielik = self.json_io["index"]["lemma_paradigma_täielik"][lemma]
            for vorm in lemma_paradigma_täielik:
                if vorm not in self.json_io["index"]["vorm_lemmaks"]:
                    self.json_io["index"]["vorm_lemmaks"][vorm] = [lemma]
                elif lemma not in self.json_io["index"]["vorm_lemmaks"][vorm]:
                    self.json_io["index"]["vorm_lemmaks"][vorm].append(lemma)
        del self.json_io["index"]["lemma_paradigma_täielik"]
        self.json_io["index"]["vorm_lemmaks"            ] = dict(sorted(self.json_io["index"]["vorm_lemmaks"            ].items()))
        self.json_io["index"]["lemma_paradigma_korpuses"] = dict(sorted(self.json_io["index"]["lemma_paradigma_korpuses"].items()))
        pass
        
    def tee_data4sql_csv(self):
        """Teeme massiivid CSV ja SQL-i jaoks

        Args:
            self.json_io:

            {   "index":
                {   "lemma_paradigma_korpuses": # järjestatud LEMMA järgi
                    {   LEMMA: [VORM] # LEMMA esines korpuses VORMides
                    }
                    "vorm_lemmaks":
                    {   VORM: [LEMMA]   # sõnavormile vastavad lemmad, järjestatud VORMi järgi
                    }
                }
            }

        Returns:
            self.data_lemma_paradigma_korpuses (list[])

            self.data_vorm_lemmaks (list[])
        """            
        self.data_lemma_paradigma_korpuses = [("lemma", "sõnavorm_korpuses")]
        for lemma in self.json_io["index"]["lemma_paradigma_korpuses"]:
            for vorm in self.json_io["index"]["lemma_paradigma_korpuses"][lemma]:
                self.data_lemma_paradigma_korpuses.append( (lemma, vorm) )
        
        self.data_vorm_lemmaks = [("täisparadigma_sõnavorm", "lemma")]
        for vorm in self.json_io["index"]["vorm_lemmaks"]:
            for lemma in self.json_io["index"]["vorm_lemmaks"][vorm]:
                self.data_vorm_lemmaks.append((vorm, lemma))
        pass

    def tee_csv(self)->Tuple[str, str]:
        """_summary_

        Args:
            self.data_lemma_paradigma_korpuses (list[])

            self.data_vorm_lemmaks (list[])
        
        Returns:
            str, str: csv_vorm_lemmaks, csv_lemma_paradigma_korpuses
        """
        output = io.StringIO()
        #writer = csv.writer(output, doublequote=False, escapechar='\\', quoting=csv.QUOTE_NONNUMERIC)
        writer = csv.writer(output, dialect='excel')
        writer.writerows(self.data_lemma_paradigma_korpuses)
        csv_lemma_paradigma_korpuses = output.getvalue()

        output = io.StringIO()
        #writer = csv.writer(output, doublequote=False, escapechar='\\', quoting=csv.QUOTE_NONNUMERIC)
        writer = csv.writer(output, dialect='excel')
        writer.writerows(self.data_vorm_lemmaks)
        csv_vorm_lemmaks = output.getvalue()       

        return csv_vorm_lemmaks, csv_lemma_paradigma_korpuses
    
    def lisa_andmebaasi(self):
        """Lisame ettervutatud generaatori andmebaasi

        Args:
            self.data_lemma_paradigma_korpuses (list[])

            self.data_vorm_lemmaks (list[])

        Returns
            Täiendatud andmebaas kettal 

        """
        for d in self.data_vorm_lemmaks[1:]: # self.data_vorm_lemmaks[0] on veerunimed
            try:
                self.cur.execute("INSERT INTO vorm_lemmaks VALUES(?, ?)", d)
            except:
                continue # selline juba oli 
        for d in self.data_lemma_paradigma_korpuses[1:]:  # self.data_vorm_lemmaks[0] on veerunimed
            try:
                self.cur.execute("INSERT INTO lemma_paradigma_korpuses VALUES(?, ?)", d)
            except:
                continue # selline juba oli 
        self.con.commit()

    def version_json(self) -> Dict:
        """Kuva JSONkujul versiooniinfot ja kasutatavate veebiteenuste URLe

        Returns:
            Dict: versiooninfo ja URLid
        """
        return  {"ettearvutaja.version": self.VERSION, "otsing": self.otsing  , "tokenizer": self.tokenizer, "analyser": self.analyser,  "generator:": self.generator}


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-v', '--verbose',  action="store_true", help='tulemus CSV vormingus std väljundisse')
    argparser.add_argument('-c', '--csv',  action="store_true", help='tulemus CSV vormingus std väljundisse')
    argparser.add_argument('-j', '--json', action="store_true", help='tulemus JSON vormingus std väljundisse')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    argparser.add_argument('-d', '--db', type=str, help='väljundandmebaasi nimi')
    argparser.add_argument('file', type=argparse.FileType('r'), nargs='+')
    args = argparser.parse_args()

    try:
        ettearvutaja = ETTEARVUTAJA(args.db, args.verbose)
        for f  in args.file:
            ettearvutaja.tee_lemmade_indeks(ettearvutaja.string2json(f.read()))
            ettearvutaja.tee_json()
            if args.json is True:
                json.dump(ettearvutaja.json_io, sys.stdout, indent=args.indent, ensure_ascii=False)
                continue
            ettearvutaja.tee_data4sql_csv()
            if args.csv is True:
                csv_vorm_lemmaks, csv_lemma_paradigma_korpuses = ettearvutaja.tee_csv()
                print(f'{csv_vorm_lemmaks}\n\n{csv_lemma_paradigma_korpuses}\n--------')
                continue
            if args.db is not None:
                ettearvutaja.lisa_andmebaasi()
                continue
    except Exception as e:
        print(f"An exception occurred: {str(e)}")
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


    self.json_io:
            
    {   "sources":
        {   DOCID:              // algne sisend: dokumendi ID -- lõpptulemuses
            {   "content": str  // algne sisend: dokumendi tekst ("plain text") -- lõpptulemuses
                "annotations":
                {   "tokens":                               // tee_sõnestamine(): sõnede massiiv 
                    [   {   "start": number,                // tee_sõnestamine(): sõne alguspositsioon algses tekstis 
                            "end": number,                  // tee_sõnestamine(): sõne lõpupositsioon algses tekstis 
                            "features":
                            {   "token": string,            // tee_sõnestamine(): sõne
                                "tokens_stem": [string]     // tee_sõnede_ja_osaõnede_indeks.morfi_sõned(): liitsõnapiiriga sõnevariandid
                                "tokens_lemma": [string]    // tee_generator.morfi_lemmadeks(): liitsõnapiiriga lemmavariandid
                            }
                        }
                    ],          
                }
            }
        "annotations":
        {   "indeks":
            {   "indeksjson":   {TOKEN: {DOCID: [{'start': int, 'end': int, 'liitsõna_osa': bool}]}} # tee_sõnede_ja_osaõnede_indeks()
                "sonavormid": [(TOKEN,  DOCID,    START,        END,        LIITSÕNAOSA)]            # tee_sõnede_ja_osaõnede_indeks() -- lõpptulemuses
            }
            "generator":
            {   "lemma_paradigmad":
                {   LEMMA:
                    {   "lemma_korpuse_vormid": [string],       # tee_generator()
                        "lemma_kõik_vomid": [string]            # tee_generator()
                    }
                },
                "tabelid":
                {   "vorm_lemmaks": [(VORM, PARITOLU, LEMMA)],  # tee_generator() -- lõpptulemuses
                    "lemma_korpuse_vormid": [(LEMMA, VORM)]     # tee_generator() -- lõpptulemuses
                }
            }
        }
    }    


"""

import fractions
import os
import sys
import json
import requests
import json
import argparse
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
        
        self.ignore_pos = "PZJ" # ignoreerime lemmasid, mille sõnaliik on: Z=kirjavahemärk, J=sidesõna, P=asesõna
        """
        self.con = None
        if self.db_ettarvutatud_generaator is not None:
            if os.path.isfile(db) is False:
                # andmebaasi veel pole, teeme tühja andmebaasi ja tabelid
                self.con = sqlite3.connect(db)
                self.cur = self.con.cursor()

                self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS vorm_lemmaks(
                        vorm TEXT NOT NULL,         -- lemma kõikvõimalikud vormid genereerijast
                        paritolu INT NOT NULL,      -- 0-lemma on leitud jooksvas dokumendis olevst sõnavormist; 1-vorm on lemma sünonüüm; 2-kirjavigane vorm
                        lemma TEXT NOT NULL,        -- korpuses esinenud sõnavormi lemma
                        PRIMARY KEY(vorm, lemma)
                        )
                ''')
                self.cur.execute('''
                    CREATE TABLE IF NOT EXISTS lemma_paradigma_korpuses(
                        lemma TEXT NOT NULL,        -- (jooksvas) dokumendis esinenud sõnavormi lemma
                        vorm TEXT NOT NULL,         -- lemma need sõnavormid, mis jooksvas dokumendis esinesid
                        PRIMARY KEY(lemma, vorm)
                        )
                ''') 
                self.cur.execute('''    
                    CREATE TABLE IF NOT EXISTS index(
                        vorm  TEXT NOT NULL,        -- (jooksvas) dokumendis esinenud sõnavorm
                        docid TEXT NOT NULL,        -- dokumendi id
                        start INT,                  -- vormi alguspositsioon tekstis
                        end INT,                    -- vormi lõpupositsioon tekstis
                        liitsona_osa,               -- 0: pole liitsõna osa; 1: on liitsõna osa
                        PRIMARY KEY(vorm, docid, start, end)
                        )
                ''')
                self.cur.execute('''    
                    CREATE TABLE IF NOT EXISTS sources(
                        docid TEXT NOT NULL,        -- dokumendi id
                        content TEXT NOT NULL,      -- dokumendi text
                        PRIMARY KEY(docid)
                        )
                ''')                
                if self.verbose is True:
                    print(f"# Loodud andmebaas {self.db_ettarvutatud_generaator} ja tabelid (vorm_lemmaks, lemma_paradigma_korpuses)")           
            else:
                self.con = sqlite3.connect(db)
                self.cur = self.con.cursor()
                if self.verbose is True:
                    print(f"# Avatud andmebaas {self.db_ettarvutatud_generaator}")   
        """

    
    def __del__(self)->None:
        """Sulgeb avatud andmebaasi (kui oli avatud).

        if self.con is not None:
            self.con.close()
            if self.verbose is True:
                print(f"# Suletud andmebaas {self.db_ettarvutatud_generaator}")           
        """
        pass

    def tee_sõnestamine(self) -> None:
        """Tekitab lemmade indeksi

        Args:
            json_in (Dict): SisendJSON, sisaldab korpusetekste

        Raises:
            Exception: Exception({"warning":f'Probleemid veebiteenusega: {self.tokenizer}'})

        Returns: 
            self.json_io: sõnestame dokumendid, lisame

            * ["sources"][DOCID]["annotations"]["tokens"][N]["start"]
            * ["sources"][DOCID]["annotations"]["tokens"][N]["end"]
            * ["sources"][DOCID]["annotations"]["tokens"][N]["features"]["token"]
        """
        if self.verbose is True:
            sys.stdout.write("# sõnestamine:")
        for docid in self.json_io["sources"]:
            try:
                if self.verbose is True:  
                    sys.stdout.write(f" {docid}")           # sõnestame kõik dokumendid
                self.json_io["sources"][docid] = json.loads(requests.post(self.tokenizer, json=self.json_io["sources"][docid]).text)
                del self.json_io["sources"][docid]["annotations"]["sentences"]
            except:                                     # sõnestamine äpardus
                raise Exception({"warning":f'Probleemid veebiteenusega: {self.tokenizer}'})
        if self.verbose is True:
            sys.stdout.write("\n")

    def string2json(self, str:str)->Dict:
        """String sisendJSONiga DICTiks

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

    def tee_sõnede_ja_osaõnede_indeks(self) -> None:
        """Tekitab indeksi

        Args:
            self.json_io: sõnestatud dokumendid, kasutame:
            * ["sources"][DOCID]["annotations"]["tokens"][N]["features"][token]

        Returns:
            self.json_io (Dict): lisame:
            * ["sources"][DOCID]["annotations"]["tokens"][N]["features"]["tokens_stem"]
            * ["annotations"]["indeks"]["indeksjson"]
            * ["annotations"]["indeks"]["sonavormid"] -- lõpptulemuses
        """
        if self.verbose:
            sys.stdout.write("# tee_sõnede_ja_osaõnede_indeks: ")
        self.morfi_sõned() # leiame iga tekstisõne võimalikud sobiva sõnaliigiga tüvi+lõpud (liitsõnapiir='_', järelliite eraldaja='=')   
        self.json_io["annotations"] = {"indeks":{"indeksjson":{}, "sonavormid":{}}}
        # teeme self.json_io["annotations"]["indeks"]["indeksjson"]
        for docid in self.json_io["sources"]:                   # tsükkel üle tekstide
            if self.verbose:
                sys.stdout.write(f" {docid}")
            if self.verbose:
                sys.stdout.write(f' {docid}')
            for token in self.json_io["sources"][docid]["annotations"]["tokens"]: # tsükkel üle sõnede
                if len(token["features"]["tokens_stem"])==0:            # kui pole ühtegi meid huvitava sõnaliigiga...
                    continue                                            # ...laseme üle
                for tkn in token["features"]["tokens_stem"]:             # tsükkel üle leitud liitsõnapiiridega sõnede
                    puhas_tkn = tkn.replace('_', '').replace('=', '')
                    if puhas_tkn in self.json_io["annotations"]["indeks"]["indeksjson"]:              # kui selline sõne juba oli...
                        if docid in self.json_io["annotations"]["indeks"]["indeksjson"][puhas_tkn]:       # ...selles dokumendis
                            self.json_io["annotations"]["indeks"]["indeksjson"][puhas_tkn][docid].append({"liitsõna_osa":False, "start": token["start"], "end":token["end"]})
                        else:                                               # ...polnud selles dokumendis
                            self.json_io["annotations"]["indeks"]["indeksjson"][puhas_tkn][docid] = [{"liitsõna_osa":False, "start": token["start"], "end":token["end"]}]
                    else:                                               # ...polnud seni üheski dokumendis                               
                        self.json_io["annotations"]["indeks"]["indeksjson"][puhas_tkn] = {docid:[{"liitsõna_osa":False, "start": token["start"], "end":token["end"]}]}

                    osasonad = tkn.replace('=', '').split('_')          # tükeldame liitsõna piirilt
                    if len(osasonad) <= 1:                              # kui pole liitsõna...
                        continue                                            # ...laseme üle
                    fragmendid = []                                     # siia hakkame korjame liitsõna tükikesi
                    # Suure tõenäosusega oleks mõistlik võtta ainult
                    # liitsõna viimane komponent.
                    for idx, osasona in enumerate(osasonad):            # tsükkel ole liitsõna osasõnade
                        if idx == 0:                                    # algab esimese osasõnaga
                            sona = osasonad[idx]
                            fragmendid.append(sona)                                                           
                            for idx2 in range(idx+1, len(osasonad)-1):
                                sona += osasonad[idx2]
                                fragmendid.append(sona)
                        elif idx == len(osasonad)-1:                    # lõppeb viimase osasõnaga
                            fragmendid.append(osasona)
                        else:                                           # vahepealsed jupid (kui liitsõnas 3 või enam komponenti)
                            fragmendid.append(osasona)
                            sona = osasonad[idx]
                            for idx2 in range(idx+1, len(osasonad)):
                                sona += osasonad[idx2]
                                if idx2 < len(osasonad)-1:
                                    fragmendid.append(sona)
                                else:
                                    fragmendid.append(sona)
                    for puhas_tkn in fragmendid:                        # lisame leitud osasõnad indeksisse 
                        if puhas_tkn in self.json_io["annotations"]["indeks"]["indeksjson"]:          # kui selline sõne juba oli...
                            if docid in self.json_io["annotations"]["indeks"]["indeksjson"][puhas_tkn]:   # ...selles dokumendis
                                    self.json_io["annotations"]["indeks"]["indeksjson"][puhas_tkn][docid].append({"liitsõna_osa":False, "start": token["start"], "end":token["end"]})
                            else:                                           # ...polnud selles dokumendis
                                self.json_io["annotations"]["indeks"]["indeksjson"][puhas_tkn][docid]= [{"liitsõna_osa":True, "start": token["start"], "end":token["end"]}]
                        else:                                           # ...polnud seni üheski dokumendis                               
                            self.json_io["annotations"]["indeks"]["indeksjson"][puhas_tkn] = {docid:[{"liitsõna_osa":True, "start": token["start"], "end":token["end"]}]}
        if self.verbose:
            sys.stdout.write(' | järjestame...')
        # järjestame vastavalt etteantud parameetritele
        self.json_io["annotations"]["indeks"]["indeksjson"] = dict(sorted(self.json_io["annotations"]["indeks"]["indeksjson"].items()))

        # teeme tabeli self.json_io["annotations"]["indeks"]["sonavormid"]
        self.json_io["annotations"]["indeks"]["sonavormid"] = []
        for token in self.json_io["annotations"]["indeks"]["indeksjson"]:
            for docid in self.json_io["annotations"]["indeks"]["indeksjson"][token]:
                for inf in self.json_io["annotations"]["indeks"]["indeksjson"][token][docid]:
                    self.json_io["annotations"]["indeks"]["sonavormid"].append((token, docid, inf["start"], inf["end"], int(inf["liitsõna_osa"])))
        if self.verbose:
            sys.stdout.write('\n')

    def morfi_sõned(self)->None:
        """Paneme sõnedesse liitsõna- ja järeliitepiirid sisse

        Args:
            self.json_io: kasutame
            * ["sources"][DOCID]["annotations"]["tokens"][N]["features"][token]

        Raises:
            Exception: Exception({"warning":f'Probleemid veebiteenusega {self.analyser}'})
            
        Returns:
            self.json_io: lisame 
            * ["sources"][DOCID]["annotations"]["tokens"][IDX]["features"]["tokens_stem"]
        """

        if self.verbose:
            sys.stdout.write("(morfi_sõned:")
        for docid in self.json_io["sources"]:
            if self.verbose:
                sys.stdout.write(f" {docid}")
            self.json_io["sources"][docid]["params"] = {"vmetajson":["--stem", "--guess"]}
            try:
                doc = json.loads(requests.post(self.analyser, json=self.json_io["sources"][docid]).text)
            except:
                raise Exception({"warning":f'Probleemid veebiteenusega {self.analyser}'})
            for token_idx, token in enumerate(doc["annotations"]["tokens"]):    # tsükkel üle sõnede 
                tokens_stem = []                                                    # siia korjame erinevad tüvi+lõpp stringid
                for mrf in token["features"]["mrf"]:                                    # tsükkel üle sama sõne alüüsivariantide (neid võib olla mitu)
                    if self.ignore_pos.find(mrf["pos"]) != -1:                              # selle sõnaliiiga tüvesid...
                        continue                                                                # ...ignoreerime, neid ei indekseeri
                    tkn = mrf["stem"]+mrf["ending"] if mrf["ending"] != '0' else mrf["stem"]# tüvi+lõpp
                    if tkn not in tokens_stem:                                                      # sõne morf analüüside hulgas võib sama kujuga tüvi erineda ainult käände/põõrde poolest
                        tokens_stem.append(tkn)                                                         # lisame uue tüvi+lõpp stringi, kui sellist veel polnud
                self.json_io["sources"][docid]["annotations"]["tokens"][token_idx]["features"]["tokens_stem"] = tokens_stem # lisame tulemusse
        if self.verbose:
            sys.stdout.write(") ")

    def morfi_lemmadeks(self)->None:
        """Morfime sõnestatud sisendteksti(d)

        Args:
            self.json_io: kasutame:
            * ["sources"][DOCID]["annotations"]["tokens"][N]["features"][token]


        Raises:
            Exception: Exception({"warning":f'Probleemid veebiteenusega {self.analyser}'})
            
        Returns:
            self.json_io: lisame:
            * ["sources"][docid]["annotations"]["tokens"][idx_token]["features"]["tokens_lemma"]
        """
        if self.verbose:
            sys.stdout.write("(morfime lemmadeks:")
        for docid in self.json_io["sources"]:
            if self.verbose:
                sys.stdout.write(f" {docid}")
            self.json_io["sources"][docid]["params"] = {"vmetajson":["--guess"]}
            try:
                doc = json.loads(requests.post(self.analyser, json=self.json_io["sources"][docid]).text)
            except:
                raise Exception({"warning":f'Probleemid veebiteenusega {self.analyser}'})
            for idx_token, token in enumerate(doc["annotations"]["tokens"]):        # tsükkel üle sõnede (ainult üks sõne meil antud juhul on)
                tokens_lemma = []                                                             # siia korjame erinevad tüvi+lõpp stringid
                for mrf in token["features"]["mrf"]:                                    # tsükkel üle sama sõne alüüsivariantide (neid võib olla mitu)
                    if self.ignore_pos.find(mrf["pos"]) != -1:                              # selle sõnaliiiga tüvesid...
                        continue                                                                # ...ignoreerime, neid ei indekseeri
                    if mrf["lemma_ma"] not in tokens_lemma:                                                   # sõne morf analüüside hulgas võib sama kujuga lemma erineda ainult käände/põõrde poolest
                        tokens_lemma.append( mrf["lemma_ma"])                                                        # lisame uue tüvi+lõpp stringi, kui sellist veel polnud
                self.json_io["sources"][docid]["annotations"]["tokens"][idx_token]["features"]["tokens_lemma"] = tokens_lemma # lisame tulemusse
        if self.verbose:
            sys.stdout.write(') ')

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
            List, List: paradigma_täielik -- lemma kõik vormid; paradigma_korpuses -- lemma sisendtekstides esinevad vormid
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
                puhas_vorm = generated_form["token"].replace("_", "").replace("=", "").replace("+", "")
                if puhas_vorm not in paradigma_täielik:
                    paradigma_täielik.append(puhas_vorm)
        
        # leiame lemma kõigi vormide hulgast need, mis esinesid korpuses
        paradigma_korpuses = []
        if len(paradigma_täielik) > 0:
            for vorm in paradigma_täielik:
                if vorm in self.json_io["annotations"]["indeks"]["indeksjson"]:
                   paradigma_korpuses.append(vorm) 
            #try:
            #    paradigma_korpuses = json.loads(requests.post(self.otsing, json=paradigma_täielik).text)
            #except:
            #    raise Exception({"warning":f'Probleemid veebiteenusega: {self.otsing}'})
        return paradigma_täielik, paradigma_korpuses

    def tee_generator(self) -> None:
        """Tekitab lemmade indeksi

        Args:
            self.json_in (Dict): Kasutame
            * ["sources"][docid]["annotations"]["tokens"][N]["features"]["tokens_lemma"]
            * ["annotations"]["indeks"]["indeksjson"]

        Returns: 
            self.json_io: lisame:
            * ["annotations"]["indeks"]["generator"]["lemma_paradigmad"][LEMMA]["lemma_korpuse_vormid"]
            * ["annotations"]["indeks"]["generator"]["lemma_paradigmad"][LEMMA]["lemma_kõik_vomid"]
            s
            * ["annotations"]["generator"]["tabelid"]["lemma_korpuse_vormid"][(lemma, vorm)] -- lõpptulemuses
            * ["annotations"]["generator"]["tabelid"]["vorm_lemmaks"][(vorm, 0,lemma)] -- lõpptulemuses
        """
        if self.verbose is True:
            sys.stdout.write(f"# teeme generaatori:")

        self.morfi_lemmadeks()                                          # leiame iga tekstisõne võimalikud sobiva sõnaliigiga tüvi+lõpud (liitsõnapiir='_', järelliite eraldaja='=')   
        self.json_io["annotations"]["generator"] = \
            {   "lemma_paradigmad":{},
                "tabelid":
                {   "vorm_lemmaks":[], 
                    "lemma_korpuse_vormid":[]
                }
            }
        for docid in self.json_io["sources"]:                   # tsükkel üle tekstide
            if self.verbose is True:
                sys.stdout.write(f' {docid}')
            for token in self.json_io["sources"][docid]["annotations"]["tokens"]: # tsükkel üle sõnede
                if len(token["features"]["tokens_lemma"])==0:           # kui pole ühtegi meid huvitava sõnaliigiga lemmat...
                    continue                                            # ...laseme üle
                for tkn in token["features"]["tokens_lemma"]:           # tsükkel üle leitud liitsõnapiiridega lemmade
                    puhas_tkn = tkn.replace('_', '').replace('=', '')   # terviklemma lisamine...
                    if puhas_tkn not in self.json_io["annotations"]["generator"]["lemma_paradigmad"]:
                        # sellist lemmat meil veel polnud, lisame genetud/korpuse vormid
                        paradigma_täielik, paradigma_korpuses = self.tee_paradigmad(puhas_tkn) # leiame lemma kõik vormid ja korpuses esinenud vormid
                        assert puhas_tkn in paradigma_täielik, "Lemma ei sisaldu täisparadigmas"
                        if len(paradigma_korpuses) > 0: # ainult siis, kui päriselt korpuses esines
                            self.json_io["annotations"]["generator"]["lemma_paradigmad"][puhas_tkn] = \
                                {"lemma_korpuse_vormid":paradigma_korpuses, 
                                 "lemma_kõik_vomid" :paradigma_täielik}

        if self.verbose is True:
            sys.stdout.write(' | Teeme tabelid...')
        for lemma in self.json_io["annotations"]["generator"]["lemma_paradigmad"]:
            lemma_inf = self.json_io["annotations"]["generator"]["lemma_paradigmad"][lemma]
            for vorm in lemma_inf["lemma_kõik_vomid"]:
                self.json_io["annotations"]["generator"]["tabelid"]["vorm_lemmaks"].append( (vorm, 0,lemma) )
            for vorm in lemma_inf["lemma_korpuse_vormid"]:
                self.json_io["annotations"]["generator"]["tabelid"]["lemma_korpuse_vormid"].append( (lemma, vorm) )


        if self.verbose is True:
            sys.stdout.write('\n')


    def kuva_tabelid(self, indent)-> None:
        """Lõpptulemus JSON kujul std väljundisse
        """

        for docid in self.json_io["sources"]:
            del self.json_io["sources"][docid]["annotations"]
            del self.json_io["sources"][docid]["params"]
        del self.json_io["annotations"]["indeks"]["indeksjson"]
        del self.json_io["annotations"]["generator"]["lemma_paradigmad"]

        json.dump(self.json_io, sys.stdout, indent=indent, ensure_ascii=False)
        sys.stdout.write('\n')
   
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
                self.cur.execute("INSERT INTO vorm_lemmaks VALUES(?, ?, ?)", d)
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
            if ettearvutaja.verbose:
                sys.stdout.write(f'\n# sisendfail: {f.name}\n')
            ettearvutaja.json_io = ettearvutaja.string2json(f.read())
            ettearvutaja.tee_sõnestamine()
            ettearvutaja.tee_sõnede_ja_osaõnede_indeks()
            ettearvutaja.tee_generator()
            ettearvutaja.kuva_tabelid(args.indent)

    except Exception as e:
        print(f"An exception occurred: {str(e)}")
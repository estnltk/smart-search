#!/usr/bin/python3

"""
Silumiseks (code):

    {
        "name": "api_ea_paring_A",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/ea_paring/",
        "program": "./api_ea_paring.py",
        "args": [\
            "--lemmatiseerija=../../testkorpused/riigiteataja/lemmataja.db", \
            "--json={\"content\":\"presitendi ja  polekorpuses kantseleis\"}"],
    }

    {
        "name": "api_ea_paring_B",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/ea_paring/",
        "program": "./api_ea_paring.py",
        "args": ["--json={\"content\":\"presitendi ja  polekorpuses kantseleis\"}"],
        "env": {"DB_LEMATISEERIJA":"../../testkorpused/riigiteataja/lemmataja.db"},
    }

Käsurealt:
    GENERATOR=https://smart-search.tartunlp.ai/api/generator/process \
    TOKENIZER=https://smart-search.tartunlp.ai/api/tokenizer/process \
    ANALYSER=https://smart-search.tartunlp.ai/api/analyser/process  \
        ./api_ettearvutaja.py  \
            ../../testkorpused/riigiteataja/riigiteataja.json > tabelid.json
    
JSON sees- ja välispidiseks kasutamiseks:
    self.json_io:
            
    {   "sources":
        {   DOCID:                  # (string) algne sisend: dokumendi unikaalne ID 
            {   "content": string   # algne sisend: dokumendi tekst ("plain text")
                "annotations":
                {   "tokens":                                  # tee_sõnestamine(): sõnede massiiv 
                    [   {   "start": number,                   # tee_sõnestamine(): sõne alguspositsioon algses tekstis 
                            "end": number,                     # tee_sõnestamine(): sõne lõpupositsioon algses tekstis 
                            "features":
                            {   "token": string,               # tee_sõnestamine(): sõne
                                "tokens_stem": [string],       # tee_sõnede_ja_osaõnede_indeks.morfi_sõned(): liitsõnapiiriga sõnevariandid
                                "tokens_lemma": [string],      # tee_generator.morfi_lemmadeks(): liitsõnapiiriga lemmavariandid
                            }
                        }
                    ],          
                }
            }
        "indeks":    # tee_sõnede_ja_osaõnede_indeks()
        {   TOKEN: 
            {   DOCID: 
                [   {   'start': number, 
                        'end': number, 
                        'liitsõna_osa': bool
                    }
                ]
            }
        }   
        "generator":
        {   LEMMA:
            {   "lemma_korpuse_vormid": [string],       # tee_generator()
                "lemma_kõik_vormid": [string]           # tee_generator()
            }
        }
        "lemmas_2_ignore": 
        {   "lemmas": [string], # tee_generator.morfi_lemmadeks(): ingoreeritavad lemmad (sidesõnad jms)
        }

        "tabelid":  # lõpptulemus
        {   "lemma_kõik_vormid": [(VORM, PARITOLU, LEMMA)],         # tee_generator()
            "lemma_korpuse_vormid": [(LEMMA, VORM)],                # tee_generator()
            "ignoreeritavad_vormid": [(VORM, 0)],                   # tee_ignoreeritavad_vormid(), 0:vorm tuleneb korpusest
            "indeks": [(VORM, DOCID, START, END, LIITSÕNA_OSA)]     # tee_sõnede_ja_osaõnede_indeks()
            "kirjavead": [(VIGANE_VORM, VORM, KAAL)]                # tee_kirjavead()
            "allikad": [(DOCID, CONTENT)]                           # tee_sources_tabeliks() 
        }
    }    
"""

import csv
import os
import sys
import json
import requests
from tqdm import tqdm
from typing import Dict, List, Tuple

import kirjavigastaja

class ETTEARVUTAJA:
    def __init__(self, verbose:bool)->None:
        """Initsialiseerime muutujad: versiooninumber,kasutatavate veebiteenuste URLid, jne

        Args:
            verbose (bool): kuva tööjärjega seotud infot
        """
        self.verbose = verbose

        self.VERSION="2023.09.06"

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
 
    def string2json(self, str:str)->None:
        """PUBLIC:String sisendJSONiga DICTiks

        Args:
            str (str): String sisendJSONiga

        Raises:
            Exception: Exception({"warning":"JSON parse error"})

        Returns:
            self.json_io (Dict): DICTiks tehtud sisendJSON
        """
        try:
            self.json_io = json.loads(str.replace('\n', ' '))
        except:
            raise Exception({"warning":"JSON parse error"})

    def csvpealkrjadest(self, f)->None:
        """_summary_

        Args:
            f : CSV faili read

        Returns:

            self.json_io (Dict): DICTiks tehtud sisendCSV

            {   "sources":
                {   DOCID: // "pk"+globaalID+liik
                    {   "content": str,
                        "globaalID": str,   # praegu pealkirja korral
                        "liik": str,        # praegu pealkirja korral
                        "url": str          # praegu pealkirja korral - vist ei paku huvi?
                    }
                }
            }
        """
        data = list(csv.reader(f, delimiter=","))
        self.json_io = {"sources": {}}
        for d in data:
            assert len(d)==5
            self.json_io["sources"][f'pk{d[1]}_{d[2]}'] = {
                    "content" : d[3],
                    "globaalID": d[1],
                    "liik": d[2],
                    "url": d[4]
                }

    def tee_sõnestamine(self)->None:
        """PUBLIC:Sõnestame sisendtekstid

        Args:
            json_in (Dict): kasutab:
            * ["sources"][DOCID]["content"]

        Raises:
            Exception: Exception({"warning":f'Probleemid veebiteenusega: {self.tokenizer}'})

        Returns: 
            self.json_io: sõnestame dokumendid, lisame

            * ["sources"][DOCID]["annotations"]["tokens"][N]["start"]:NUMBER
            * ["sources"][DOCID]["annotations"]["tokens"][N]["end"]:NUMBER
            * ["sources"][DOCID]["annotations"]["tokens"][N]["features"]["token"]:VORM
        """
        pbar = tqdm(self.json_io["sources"].keys(), disable=(not self.verbose))
        for docid in pbar:
            try:
                pbar.set_description(f"sõnestamine: {docid}")
                self.json_io["sources"][docid] = json.loads(requests.post(self.tokenizer, json=self.json_io["sources"][docid]).text)
                del self.json_io["sources"][docid]["annotations"]["sentences"]
                pbar.set_description(f"sõnestamine")
            except:                                     # sõnestamine äpardus
                raise Exception({"warning":f'Probleemid veebiteenusega: {self.tokenizer}'})
    


    def tee_sõnede_ja_osaõnede_indeks(self) -> None:
        """PUBLIC:Tekitab indeksi

        Args:
            self.json_io: sõnestatud dokumendid, kasutame:
            * ["sources"][DOCID]["annotations"]["tokens"][N]["features"][token]:VORM

        Returns:
            self.json_io (Dict): lisame:
            * ["sources"][DOCID]["annotations"]["tokens"][N]["features"]["tokens_stem"]:[VORM]
            * ["indeks"]:{TOKEN: {DOCID: [{'start': int, 'end': int, 'liitsõna_osa': bool}]}}
            * ["tabelid"]["indeks"]:[(TOKEN, DOCID, START, END, LIITSÕNAOSA)] -- lõpptulemuses
        """
        self.morfi_sõned() # leiame iga tekstisõne võimalikud sobiva sõnaliigiga tüvi+lõpud (liitsõnapiir='_', järelliite eraldaja='=') 

        if "indeks" not in self.json_io:
            self.json_io["indeks"] = {}

        # teeme self.json_io["indeks"]
        pbar = tqdm(self.json_io["sources"].keys(), disable=(not self.verbose))
        for docid in pbar:                   # tsükkel üle tekstide
            pbar.set_description(f"tee_sõnede_ja_osaõnede_indeks: {docid}")
            for token in self.json_io["sources"][docid]["annotations"]["tokens"]: # tsükkel üle sõnede
                if len(token["features"]["tokens_stem"])==0:            # kui pole ühtegi meid huvitava sõnaliigiga...
                    continue                                            # ...laseme üle
                for tkn in token["features"]["tokens_stem"]:             # tsükkel üle leitud liitsõnapiiridega sõnede
                    puhas_tkn = tkn.replace('_', '').replace('=', '')
                    if puhas_tkn in self.json_io["indeks"]:              # kui selline sõne juba oli...
                        if docid in self.json_io["indeks"][puhas_tkn]:       # ...selles dokumendis
                            self.json_io["indeks"][puhas_tkn][docid].append({"liitsõna_osa":False, "start": token["start"], "end":token["end"]})
                        else:                                               # ...polnud selles dokumendis
                            self.json_io["indeks"][puhas_tkn][docid] = [{"liitsõna_osa":False, "start": token["start"], "end":token["end"]}]
                    else:                                               # ...polnud seni üheski dokumendis                               
                        self.json_io["indeks"][puhas_tkn] = {docid:[{"liitsõna_osa":False, "start": token["start"], "end":token["end"]}]}

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
                        if puhas_tkn in self.json_io["indeks"]:          # kui selline sõne juba oli...
                            if docid in self.json_io["indeks"][puhas_tkn]:   # ...selles dokumendis
                                    self.json_io["indeks"][puhas_tkn][docid].append({"liitsõna_osa":False, "start": token["start"], "end":token["end"]})
                            else:                                           # ...polnud selles dokumendis
                                self.json_io["indeks"][puhas_tkn][docid]= [{"liitsõna_osa":True, "start": token["start"], "end":token["end"]}]
                        else:                                           # ...polnud seni üheski dokumendis                               
                            self.json_io["indeks"][puhas_tkn] = {docid:[{"liitsõna_osa":True, "start": token["start"], "end":token["end"]}]}
            pbar.set_description(f"tee_sõnede_ja_osaõnede_indeks")                
        if self.verbose:
            sys.stdout.write('järjestame ja teeme tabelid...')
        # järjestame vastavalt etteantud parameetritele
        self.json_io["indeks"] = dict(sorted(self.json_io["indeks"].items()))

        # teeme tabeli self.json_io["annotations"]["tabelid"]["indeks"]:[(TOKEN, DOCID, START, END, LIITSÕNAOSA)] -- lõpptulemuses
        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "indeks" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["indeks"] = []

        for token in self.json_io["indeks"]:
            for docid in self.json_io["indeks"][token]:
                for inf in self.json_io["indeks"][token][docid]:
                    self.json_io["tabelid"]["indeks"].append((token, docid, inf["start"], inf["end"], int(inf["liitsõna_osa"])))
        if self.verbose:
            sys.stdout.write('\n')

    def tee_generator(self) -> None:
        """PUBLIC:Tekitab lemmade indeksi

        Args:
            self.json_in (Dict): kasutame
            * ["sources"][DOCID]["annotations"]["tokens"][N]["features"]["token"]:VORM  

        Returns: 
            self.json_io: lisame:
            * ["sources"][docid]["annotations"]["tokens"][idx_token]["features"]["tokens_lemma"]:[LEMMA] -- morfi_lemmadeks()

            * ["generator"][LEMMA]["lemma_kõik_vormid"]:[VORM]
            * ["generator"][LEMMA]["lemma_korpuse_vormid"]:[VORM]
            
            * ["tabelid"]["lemma_kõik_vormid"]:[(vorm, 0,lemma)] -- lõpptulemuses, lemma kõik vormid, 0:lemma jooksvas sisendkorpuses
            * ["tabelid"]["lemma_korpuse_vormid"]:[(lemma, vorm)] -- lõpptulemuses, ainult jooksvas sisendkorpuses esinenud vormid
        """

        self.morfi_lemmadeks() 
        if "generator" not in self.json_io:
            self.json_io["generator"] ={}

        # leiame iga tekstisõne võimalikud sobiva sõnaliigiga tüvi+lõpud (liitsõnapiir='_', järelliite eraldaja='=')   
        pbar = tqdm(self.json_io["sources"].keys(), disable=(not self.verbose), desc="tee_generator")
        for docid in pbar:                   # tsükkel üle tekstide
            pbar.set_description(f"tee_generator: {docid}")    
            for token in self.json_io["sources"][docid]["annotations"]["tokens"]: # tsükkel üle sõnede
                if len(token["features"]["tokens_lemma"])==0:           # kui pole ühtegi meid huvitava sõnaliigiga lemmat...
                    continue                                            # ...laseme üle
                for tkn in token["features"]["tokens_lemma"]:           # tsükkel üle leitud liitsõnapiiridega lemmade
                    puhas_tkn = tkn.replace('_', '').replace('=', '')   # terviklemma lisamine...
                    if puhas_tkn not in self.json_io["generator"]:
                        # sellist lemmat meil veel polnud, lisame genetud/korpuse vormid
                        #if puhas_tkn == 'salastatu':
                        #    pass
                        paradigma_täielik, paradigma_korpuses = self.tee_paradigmad(puhas_tkn) # leiame lemma kõik vormid ja korpuses esinenud vormid
                        if len(paradigma_korpuses) > 0: # ainult siis, kui päriselt korpuses esines
                            self.json_io["generator"][puhas_tkn] = \
                                { "lemma_korpuse_vormid":paradigma_korpuses, 
                                  "lemma_kõik_vormid" :paradigma_täielik
                                }

        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "lemma_kõik_vormid" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["lemma_kõik_vormid"] = []
        if "lemma_korpuse_vormid" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["lemma_korpuse_vormid"] = []
        pbar = tqdm(self.json_io["generator"].keys(), disable=(not self.verbose), desc="tee_generator: tabelite genereerimine")
        for lemma in pbar:
            lemma_inf = self.json_io["generator"][lemma]
            for vorm in lemma_inf["lemma_kõik_vormid"]:
                self.json_io["tabelid"]["lemma_kõik_vormid"].append( (vorm, 0,lemma) )
            for vorm in lemma_inf["lemma_korpuse_vormid"]:
                self.json_io["tabelid"]["lemma_korpuse_vormid"].append( (lemma, vorm) )


    def tee_ignoreeritavad_vormid(self)->None:
        """Genereerime ignoreeritavad vormid

        Args:
            * self.json_io["sources"][docid]["annotations"]["tokens"][idx_token]["features"]["tokens_lemma_igno"]:[LEMMA]


        Return
            * self.json_io["tabelid"]["ignoreeritavad_vormid"]: [vorm]
        """

        ignoreeritavad_vormid = []
        pbar = tqdm(self.json_io["lemmas_2_ignore"]["lemmad"], disable=(not self.verbose), desc="tee_ignoreeritavad_vormid")
        for lemma in pbar:
            try:
                generator_out = json.loads(requests.post(self.generator, json={"type":"text", "content": lemma}).text)
            except:
                raise Exception({"warning":'Probleemid veebiteenusega: {self.generator}'})
            # lisa saadud vormid ignoreeritavate vormide loendisse
            for text in generator_out["response"]["texts"]:
                for generated_form in text["features"]["generated_forms"]:
                    puhas_vorm = generated_form["token"].replace("_", "").replace("=", "").replace("+", "")
                    if puhas_vorm not in ignoreeritavad_vormid:
                        ignoreeritavad_vormid.append((puhas_vorm, 0))
        del self.json_io["lemmas_2_ignore"]["lemmad"]
        self.json_io["tabelid"]["ignoreeritavad_vormid"] = ignoreeritavad_vormid


    def tee_kirjavead(self)->None:
        """PUBLIC:Lisame kirjavead parandamiseks vajaliku tabeli

        Args:
            self.json_io: kasutame:
            * ["indeks"]

        Returns:
            self.json_io: lisame:
            * ["tabelid"]["kirjavead"][(VIGANE_VORM, VORM, KAAL)]
        """
        kv = kirjavigastaja.KIRJAVIGASTAJA(self.verbose, self.analyser)
        if "kirjavead" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["kirjavead"] = []
        pbar = tqdm(self.json_io["indeks"].keys(), disable=(not self.verbose), desc="tee_kirjavead")
        for token in pbar:
            if any(char.isdigit() for char in token) is False:
                self.json_io["tabelid"]["kirjavead"] += kv.kirjavigur(token)
                #pbar.set_description(f"tee_kirjavead")


    def tee_sources_tabeliks(self)->None:
        """

        Args:
            self.json_io: kasutame:
            * ["sources"][DOCID]["content"]:string 
        
        Returns:
            self.json_io: lisame:
            * ["tabelid"]["allikad"]:[(DOCID, CONTENT)]            # tee_sources_tabeliks() -- lõpptulemuses
        """
        if self.verbose:
            sys.stdout.write("tee_sources_tabeliks...")
        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "allikad" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["allikad"] = []
        pbar = tqdm(self.json_io["sources"].keys(), disable=(not self.verbose))
        for docid in pbar:
            pbar.set_description(f"tee_sources_tabeliks: {docid}")
            self.json_io["tabelid"]["allikad"].append((docid, self.json_io["sources"][docid]["content"]))
            del self.json_io["sources"][docid]["content"]
            pbar.set_description(f"tee_sources_tabeliks")
        if self.verbose:
            sys.stdout.write('kustutame sortsud...')
        del self.json_io["sources"]
        if self.verbose:
            sys.stdout.write('\n')

    def kustuta_vahetulemused(self)->None:
        del self.json_io["indeks"]
        del self.json_io["generator"]

    def kuva_tabelid(self, indent)-> None:
        """PUBLIC:Lõpptulemus JSON kujul std väljundisse

        Args:
            indent (int): taande pikkus JSON väljundis, None korral kõik ühel real
            self.json_io["indeks"]
            self.json_io["generator"]
            
        Std väljundisse:    
            * ["tabelid"]["vorm_lemmaks"]:[(VORM, 0,LEMMA)] -- lemma kõik vormid, 0:lemma jooksvas sisendkorpuses
            * ["tabelid"]["lemma_korpuse_vormid"]:[(LEMMA, VORM)] -- ainult jooksvas sisendkorpuses esinenud vormid
            * ["tabelid"]["kirjavead"]:[(VIGANE_VORM, VORM, KAAL)] -- ainult jooksvas sisendkorpuses esinenud vormid
            * ["tabelid"]["allikad"]:[(DOCID,CONTENT)]
        """
        json.dump(self.json_io, sys.stdout, indent=indent, ensure_ascii=False)
        sys.stdout.write('\n')
   
    def morfi_sõned(self)->None:
        """PRIVATE:Paneme sõnedesse liitsõna- ja järeliitepiirid sisse

        Args:
            self.json_io: kasutame
            * ["sources"][DOCID]["annotations"]["tokens"][N]["features"][token]

        Raises:
            Exception: Exception({"warning":f'Probleemid veebiteenusega {self.analyser}'})
            
        Returns:
            self.json_io: lisame 
            * ["sources"][DOCID]["annotations"]["tokens"][IDX]["features"]["tokens_stem"]
        """
        pbar = tqdm(self.json_io["sources"].keys(), disable=(not self.verbose))
        for docid in pbar:
            pbar.set_description(f"morfi_sõned: {docid}")

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


    def morfi_lemmadeks(self)->None:
        """PRIVATE:Morfime sõnestatud sisendteksti(d)

        Args:
            self.json_io: kasutame:
            * ["sources"][DOCID]["annotations"]["tokens"][N]["features"]["token"]:VORM


        Raises:
            Exception: Exception({"warning":f'Probleemid veebiteenusega {self.analyser}'})
            
        Returns:
            self.json_io: lisame:
            * ["sources"][docid]["annotations"]["tokens"][idx_token]["features"]["tokens_lemma"]:[LEMMA]
            * ["sources"][docid]["annotations"]["tokens"][idx_token]["features"]["tokens_lemma_igno"]:[LEMMA]
        """

        if "lemmas_2_ignore" not in self.json_io:
            self.json_io["lemmas_2_ignore"] = {"lemmad":[]}
        pbar = tqdm(self.json_io["sources"].keys(), disable=(not self.verbose))
        for docid in pbar:
            pbar.set_description(f"morfi_lemmadeks: {docid}")
            self.json_io["sources"][docid]["params"] = {"vmetajson":["--guess"]}
            try:
                doc = json.loads(requests.post(self.analyser, json=self.json_io["sources"][docid]).text)
            except:
                raise Exception({"warning":f'Probleemid veebiteenusega {self.analyser}'})
            for idx_token, token in enumerate(doc["annotations"]["tokens"]):        # tsükkel üle sõnede (ainult üks sõne meil antud juhul on)
                tokens_lemma = []                                                   # siia korjame erinevad tüvi+lõpp stringid
                                                           
                for mrf in token["features"]["mrf"]:                                    # tsükkel üle sama sõne alüüsivariantide (neid võib olla mitu)
                    if self.ignore_pos.find(mrf["pos"]) != -1:                              # selle sõnaliiiga tüvesid...
                        if mrf["pos"] != "Z" and mrf["lemma_ma"] not in self.json_io["lemmas_2_ignore"]["lemmad"]:
                            self.json_io["lemmas_2_ignore"]["lemmad"].append( mrf["lemma_ma"])                                                              # ...ignoreerime, neid ei indekseeri                            
                    elif mrf["lemma_ma"] not in tokens_lemma:                                                  # sõne morf analüüside hulgas võib sama kujuga lemma erineda ainult käände/põõrde poolest
                        tokens_lemma.append( mrf["lemma_ma"])                                                        # lisame uue tüvi+lõpp stringi, kui sellist veel polnud
                self.json_io["sources"][docid]["annotations"]["tokens"][idx_token]["features"]["tokens_lemma"] = tokens_lemma # lisame tulemusse

    def tee_paradigmad(self, lemma:str)-> (List[str], List[str]):
        """PRIVATE:Leiame sisendlemma kõik vormid ja nende hulgast need mis tegelikult jooksvas sisendkorpuses esinesid

        Args:
            lemma (str): lemma

        Raises:
            Exception: Exception({"warning":'Probleemid veebiteenusega: {self.generator}'})

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
        if len(paradigma_täielik) == 0:
            paradigma_täielik.append(lemma)
        
        # leiame lemma kõigi vormide hulgast need, mis esinesid korpuses
        paradigma_korpuses = []
        if len(paradigma_täielik) > 0:
            for vorm in paradigma_täielik:
                if vorm in self.json_io["indeks"]:
                   paradigma_korpuses.append(vorm) 
        return paradigma_täielik, paradigma_korpuses


    def version_json(self) -> Dict:
        """PUBLIC:Kuva JSONkujul versiooniinfot ja kasutatavate veebiteenuste URLe

        Returns:
            Dict: versiooninfo ja URLid
        """
        return  {"ettearvutaja.version": self.VERSION, "tokenizer": self.tokenizer, "analyser": self.analyser,  "generator:": self.generator}


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-p', '--csvpealkirjad',  action="store_true", help='sisendfaili formaat')
    argparser.add_argument('-v', '--verbose',  action="store_true", help='kuva rohkem infot tööjärje kohta')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    argparser.add_argument('file', type=argparse.FileType('r'), nargs='+')
    args = argparser.parse_args()

    try:
        ettearvutaja = ETTEARVUTAJA(args.verbose)

        for f  in args.file:
            if ettearvutaja.verbose:
                sys.stdout.write(f'\n# sisendfail: {f.name}\n')
            if args.csvpealkirjad:
                ettearvutaja.csvpealkrjadest(f.readlines())
            else:
                ettearvutaja.string2json(f.read())
            ettearvutaja.tee_sõnestamine()
            ettearvutaja.tee_sõnede_ja_osaõnede_indeks()
            ettearvutaja.tee_generator()
            ettearvutaja.tee_ignoreeritavad_vormid()
            ettearvutaja.tee_kirjavead()
            ettearvutaja.tee_sources_tabeliks()
            ettearvutaja.kustuta_vahetulemused()
            ettearvutaja.kuva_tabelid(args.indent)

    except Exception as e:
        print(f"An exception occurred: {str(e)}")
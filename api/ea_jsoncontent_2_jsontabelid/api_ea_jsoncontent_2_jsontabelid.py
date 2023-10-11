#!/usr/bin/python3

"""
Silumiseks:
    {
        "name": "content_2_tabelid_DB",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/ea_jsoncontent_2_jsontabelid/",
        "program": "./api_ea_jsoncontent_2_jsontabelid.py",
        "env": {\
            "GENERATOR": "http://localhost:7008/api/vm/generator/process", \
            "TOKENIZER": "http://localhost:6000/api/tokenizer/process", \
            "ANALYSER": "http://localhost:7007/api/analyser/process" \
        },
        "args": ["--verbose", "--csvpealkirjad", \
            "../../rt_web_crawler/results/government_orders.csv", \
            "../../rt_web_crawler/results/government_regulations.csv", \
            "../../rt_web_crawler/results/local_government_acts.csv", \
            "../../rt_web_crawler/results/state_laws.csv"\
        ]
    },

JSON sees- ja välispidiseks kasutamiseks:
    self.json_io:
            
    {
        "lemmas_2_ignore": 
        {   "lemmas": [string],     # sisse: kasutab tee_ignoreeritavad_vormid(): ingoreeritavad lemmad
        }
        "sources":
        {   DOCID:                  # sisse (string): dokumendi unikaalne ID 
            {   "content": string   # sisse string2json()/csvpealkrjadest(): "plain text"
                "annotations":
                {   "tokens":                                  # tee_sõnestamine(): sõnede massiiv 
                    [   {   "start": number,                   # tee_sõnestamine(): sõne alguspositsioon algses tekstis 
                            "end": number,                     # tee_sõnestamine(): sõne lõpupositsioon algses tekstis 
                            "features":
                            {   "token": string,               # tee_sõnestamine(): sõne
                                "token_stems": [string],       # morfi_sõned(): liitsõnapiiriga sõnevariandid
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
            {   "lemma_kõik_vormid": [string]           # tee_generator()
            }
        }

        "tabelid":  # lõpptulemus
        {   "lemma_kõik_vormid": [(VORM, PARITOLU, LEMMA)],         # tee_generator(),(LEMMA_kõik_vormid, 0:korpusest|1:abisõnastikust, sisendkorpuses_esinenud_sõnavormi_LEMMA)
            "ignoreeritavad_vormid": [(VORM, 0)],                   # tee_ignoreeritavad_vormid(), 0:vorm on genereeritud etteantud lemmast
            "kirjavead": [(VIGANE_VORM, VORM, KAAL)]                # tee_kirjavead_loendikaupa()
            "lemma_korpuse_vormid": [(LEMMA, VORM)],                # tee_generator()
            "indeks": [(VORM, DOCID, START, END, LIITSÕNA_OSA)]     # tee_sõnede_ja_osaõnede_indeks()
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

        self.VERSION="2023.09.20"

        # https://smart-search.tartunlp.ai/api/tokenizer/process
        self.tokenizer = os.environ.get('TOKENIZER') # vm liidesega veebiteenus sõnestamiseks
        if self.tokenizer is None:
            self.TOKENIZER_IP=os.environ.get('TOKENIZER_IP') if os.environ.get('TOKENIZER_IP') != None else 'localhost'
            self.TOKENIZER_PORT=os.environ.get('TOKENIZER_PORT') if os.environ.get('TOKENIZER_PORT') != None else '6000'
            self.tokenizer = f'http://{self.TOKENIZER_IP}:{self.TOKENIZER_PORT}/api/tokenizer/process'

        # https://smart-search.tartunlp.ai/api/analyser/process
        self.analyser = os.environ.get('ANALYSER')  # vm liidesega veebiteenus morf analüüsiks
        if self.analyser is None:
            self.ANALYSER_IP=os.environ.get('ANALYSER_IP') if os.environ.get('ANALYSER_IP') != None else 'localhost'
            self.ANALYSER_PORT=os.environ.get('ANALYSER_PORT') if os.environ.get('ANALYSER_PORT') != None else '7007'
            self.analyser = f'http://{self.ANALYSER_IP}:{self.ANALYSER_PORT}/api/analyser/process'

        # https://smart-search.tartunlp.ai/api/generator/process     # ELG liidesega veebiteenus morf genereerimiseks
        # https://smart-search.tartunlp.ai/api/wm/generator/process  # vm  liidesega veebiteenus morf genereerimiseks
        self.generator = os.environ.get('GENERATOR') # vm liidesega veebiteenus morf genemiseks
        if self.generator is None:
            self.GENERATOR_IP=os.environ.get('GENERATOR_IP') if os.environ.get('GENERATOR_IP') != None else 'localhost'
            self.GENERATOR_PORT=os.environ.get('GENERATOR_PORT') if os.environ.get('GENERATOR_PORT') != None else '7008'
            self.generator = f'http://{self.GENERATOR_IP}:{self.GENERATOR_PORT}/api/vm/generator/process'
        
        self.ignore_pos = "PZJ" # ignoreerime lemmasid, mille sõnaliik on: Z=kirjavahemärk, J=sidesõna, P=asesõna
 
    def string2json(self, str:str)->None:
        """PUBLIC: String sisendJSONiga DICTiks

        Args:
            str (str): String sisendJSONiga

        Raises:
            Exception: Exception({"warning":"JSON parse error"})

        Returns:
            Lisatud:

            * self.json_io["sources"][DOCID]["content"] : str
        """
        try:
            self.json_io = json.loads(str.replace('\n', ' '))
        except:
            raise Exception({"warning":"JSON parse error"})

    def csvpealkrjadest(self, f)->None:
        """PUBLIC: sisendiks pealkirjad CSV failist

        Args:
            f : CSV faili read

        Returns:

            self.json_io (Dict): DICTiks tehtud sisendCSV

            {   "sources":
                {   DOCID: // "pk"+globaalID+liik
                    {   "content": str, // pealkiri
                    }
                }
            }
        """
        data = list(csv.reader(f, delimiter=","))
        self.json_io = {"sources": {}}
        for d in data[1:]:
            assert len(d)==4
            self.json_io["sources"][f'pk_{d[1]}_{d[0]}'] = {"content" : d[2]}

    def tee_päring(self, url:str, json_in:Dict)->Dict:
        """PRIVATE: Päringu tegemine

        Args:
            url (str): veebiteenuse URL
            json_in (Dict): sisendJSON veebiteenusele
        Raises:
            Exception: Veebiteenuse kasutamine äpardus

        Returns:
            Dict: Veebiteenusest saadud JSON
        """
        try:
            response = requests.post(url, json=json_in)
            if not response.ok:
                raise Exception({"warning":f'Probleemid veebiteenusega {url}, status_code={response.status_code}'})
            return response.json()
        except:
            raise Exception({"warning":f'Probleemid veebiteenusega {url}'})
        

    def tee_sõnestamine(self)->None:
        """PUBLIC: Sõnestame sisendtekstid

        Args:
            Kasutab:
            * json_in["sources"][DOCID]["content"]

        Raises:
            Exception: Veebiteenus self.tokenizer äpardus

        Returns: 
            Sõnestame dokumendid, lisame:
            * self.json_io["sources"][DOCID]["annotations"]["tokens"][N]["start"]:NUMBER
            * self.json_io["sources"][DOCID]["annotations"]["tokens"][N]["end"]:NUMBER
            * self.json_io ["sources"][DOCID]["annotations"]["tokens"][N]["features"]["token"]:VORM
        """
        pbar = tqdm(self.json_io["sources"].keys(), desc='# sõnestamine', disable=(not self.verbose))
        for docid in pbar:
            self.json_io["sources"][docid] = self.tee_päring(
                    self.tokenizer, self.json_io["sources"][docid])
            del self.json_io["sources"][docid]["annotations"]["sentences"]

    def morfi_sõned(self)->None:
        """PUBLIC:Paneme sõnedesse liitsõna- ja järelLiitepiirid sisse

        Args:
            Kasutame:
            * self.json_io["sources"][DOCID]["annotations"]["tokens"][N]["features"]["token"]:TOKEN

        Raises:
            Exception: Veebiteenus self.analyser äpardus
            
        Returns:
            Lisame: 
            * self.json_io["sources"][DOCID]["annotations"]["tokens"][N]["features"]["token_stems"]:[STEM]
              raudteetuga -> raud_tee=tuga
        """
        pbar = tqdm(self.json_io["sources"].keys(), 
                            desc='# morfi_sõned', disable=(not self.verbose))
        for docid in pbar:
            self.json_io["sources"][docid]["params"] = \
                                            {"vmetajson":["--stem", "--guess"]}
            doc = self.tee_päring(self.analyser, self.json_io["sources"][docid])
            for token_idx, token in enumerate(doc["annotations"]["tokens"]):    # tsükkel üle sõnede 
                token_stems = []   # siia korjame sõned, '_': liitsõnapiiri kohal, '=': järelliide
                for mrf in token["features"]["mrf"]:            # tsükkel üle sama sõne alüüsivariantide (neid võib olla mitu)
                    if self.ignore_pos.find(mrf["pos"]) != -1:  # selle sõnaliiiga tüvesid...
                        continue                                # ...ignoreerime, neid ei indekseeri
                    tkn = mrf["stem"]+mrf["ending"] if mrf["ending"] != '0' else mrf["stem"]# tüvi+lõpp
                    if tkn not in token_stems:                  # sõne morf analüüside hulgas võib sama kujuga tüvi erineda ainult käände/põõrde poolest
                        token_stems.append(tkn)
                self.json_io["sources"][docid]["annotations"]["tokens"][token_idx]["features"]["token_stems"] = token_stems                                      # lisame uue tüvi+lõpp stringi, kui sellist veel polnud
        pass
    
    def tee_sõnede_ja_osaõnede_indeks(self) -> None:
        """PUBLIC:Tekitab indeksi

        Args:
            self.json_io: sõnestatud dokumendid, kasutame:
            * ["sources"][DOCID]["annotations"]["tokens"][N]["features"]["token_stems"]:[STEM]
        Returns:
            self.json_io (Dict): lisame:
            * ["indeks"]:{TOKEN: {DOCID: [{'start': int, 'end': int, 'liitsõna_osa': bool}]}} -- vahetulemus
            * ["tabelid"]["indeks"]:[(TOKEN, DOCID, START, END, LIITSÕNAOSA)] -- lõpptulemuses
        """

        if "indeks" not in self.json_io:
            self.json_io["indeks"] = {}
        # teeme self.json_io["indeks"]
        pbar = tqdm(self.json_io["sources"].keys(), desc='# tee_sõnede_ja_osaõnede_indeks', disable=(not self.verbose))
        for docid in pbar:                   # tsükkel üle tekstide
            for token in self.json_io["sources"][docid]["annotations"]["tokens"]: # tsükkel üle sõnega seotud info
                if len(token["features"]["token_stems"])==0:            # kui sõnele ei leitud ühtegi (meid huvitava sõnaliigiga) tüve...
                    continue                                            # ...laseme üle
                for tkn in token["features"]["token_stems"]:            # tsükkel üle leitud liitsõnapiiridega tüvede
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
                                    self.json_io["indeks"][puhas_tkn][docid].append({"liitsõna_osa":True, "start": token["start"], "end":token["end"]})
                            else:                                           # ...polnud selles dokumendis
                                self.json_io["indeks"][puhas_tkn][docid]= [{"liitsõna_osa":True, "start": token["start"], "end":token["end"]}]
                        else:                                           # ...polnud seni üheski dokumendis                               
                            self.json_io["indeks"][puhas_tkn] = {docid:[{"liitsõna_osa":True, "start": token["start"], "end":token["end"]}]}
            #pbar.set_description(f"# tee_sõnede_ja_osaõnede_indeks")                
        if self.verbose:
            sys.stdout.write('# järjestame ja teeme tabelid...')
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
        """PUBLIC:Morfime indeksis olevad sõned lemmadeks ning geneme täieliku ja korpuse paradigma 

        Args:
            * self.json_io["indeks"]:{TOKEN:{}}

        Returns: 
            Lisame:
            * self.json_io["generator"][LEMMA]["lemma_kõik_vormid"]:[VORM]

            * self.json_io["tabelid"]["lemma_kõik_vormid"]:[(VORM, 0,LEMMA)] -- lõpptulemuses, lemma kõik vormid, 0:lemma jooksvas sisendkorpuses
            * self.json_io["tabelid"]["lemma_korpuse_vormid"]:[(LEMMA, VORM)] -- lõpptulemuses, ainult jooksvas sisendkorpuses esinenud vormid
        """
        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "lemma_kõik_vormid" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["lemma_kõik_vormid"] = []
        if "lemma_korpuse_vormid" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["lemma_korpuse_vormid"] = []
        pbar = tqdm(self.json_io["indeks"].keys(), desc="# tee_generator", disable=(not self.verbose))
        for sone in pbar: # järjekordne sõne indeksist
            # leiame sõne võimalikud lemmad
            res = self.tee_päring(self.analyser, 
                        {"params":{"vmetajson":["--guess"]}, 
                         "content": f'{sone}'})
            lemmad = []
            for token in res["annotations"]["tokens"]:
                if "mrf" in token["features"]:
                    for mrf in token["features"]["mrf"]:
                        puhas_tkn = mrf["lemma_ma"].replace('=', '').replace('_', '') 
                        if puhas_tkn not in lemmad:
                            lemmad.append(puhas_tkn)
            # genereerime lemmade kõik vormid
            res = self.tee_päring(self.generator,
                        {"params":{"vmetsjson":["--guess"]}, 
                         "content": f'{" ".join(lemmad)}'})
            if "generator" not in self.json_io:
                self.json_io["generator"] = {}
            for token in res["annotations"]["tokens"]:
                pass
                lemma = token["features"]["token"]
                if lemma not in self.json_io["generator"]:
                    self.json_io["generator"][lemma] = {"lemma_kõik_vormid": []}
                if "mrf" in token["features"]:
                    for mrf in token["features"]["mrf"]:
                        vorm = mrf["stem"].replace('=', '').replace('_', '')
                        if mrf["ending"] != '0':
                            vorm += mrf["ending"]
                        if vorm not in self.json_io["generator"][lemma]["lemma_kõik_vormid"]:
                             self.json_io["generator"][lemma]["lemma_kõik_vormid"].append(vorm)
                        kirje = (vorm, 0, lemma)
                        if kirje not in self.json_io["tabelid"]["lemma_kõik_vormid"]:
                            self.json_io["tabelid"]["lemma_kõik_vormid"].append(kirje)
                        if vorm in self.json_io["indeks"]:
                            kirje = (lemma, vorm)
                            if kirje not in self.json_io["tabelid"]["lemma_korpuse_vormid"]:
                                self.json_io["tabelid"]["lemma_korpuse_vormid"].append(kirje)
            

    def tee_ignoreeritavad_vormid(self)->None:
        """Genereerime ignoreeritavad vormid, pole testinud

        Args:
            * self.json_io["lemmas_2_ignore"]["lemmad"]]


        Return
            * self.json_io["tabelid"]["ignoreeritavad_vormid"]:[vorm]
        """
        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "ignoreeritavad_vormid" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["ignoreeritavad_vormid"] = []
        if "lemmas_2_ignore" not in self.json_io:
            return
        ignoreeritavad_vormid = []
        pbar = tqdm(self.json_io["lemmas_2_ignore"]["lemmad"], disable=(not self.verbose), desc="# tee_ignoreeritavad_vormid")
        for lemma in pbar:
            generator_out = self.tee_päring(self.generator, {"params":{"vmetsjson":["--guess"]}, "content": lemma})
            # lisa saadud vormid ignoreeritavate vormide loendisse
            for token in generator_out["annotations"]["tokens"]:
                if "mrf" in token["features"]:
                    for mrf in token["features"]["mrf"]:
                        puhas_vorm = mrf["stem"].replace("_", "").replace("=", "").replace("+", "")
                        if puhas_vorm not in ignoreeritavad_vormid:
                            ignoreeritavad_vormid.append((puhas_vorm, 0))                       
        del self.json_io["lemmas_2_ignore"]["lemmad"]
        self.json_io["tabelid"]["ignoreeritavad_vormid"] = ignoreeritavad_vormid

    def tee_kirjavead_loendikaupa(self)->None:
        """PUBLIC:Lisame kirjavead parandamiseks vajaliku tabeli

        Args:
            self.json_io: kasutame:
            * self.json_io["generator"][LEMMA]["lemma_kõik_vormid"] : [VORM]


        Returns:
            Lisame:
            * self.json_io["tabelid"]["kirjavead"] : [(VIGANE_VORM, VORM, KAAL)]
        """
        kv = kirjavigastaja.KIRJAVIGASTAJA(self.verbose, self.analyser)
        if "kirjavead" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["kirjavead"] = []
        soneloend = []
        pbar = tqdm(self.json_io["generator"].keys(), disable=(not self.verbose), desc="# tee_kirjavead_loendikaupa")
        for lemma in pbar:
            if any(char.isdigit() for char in lemma) is False:
                self.json_io["tabelid"]["kirjavead"] += kv.kirjavigastaja(self.json_io["generator"][lemma]["lemma_kõik_vormid"])

        print("DEBUG OSA")
        db = {}
        max_cnt = 0
        max_key = ""
        pbar = tqdm(self.json_io["tabelid"]["kirjavead"], desc="# kirjavigade analüüs")
        for rec in pbar:
            if rec[0] not in db:
                db[rec[0]] = []
            if rec[1] not in db[rec[0]]:
                db[rec[0]].append(rec[1])
            if len( db[rec[0]]) > max_cnt:
                max_cnt = len( db[rec[0]])
                max_key = rec[0]
        pass        
        print("### ", max_key, max_cnt, db[max_key])
        pass

    def tee_sources_tabeliks(self)->None:
        """

        Args:
            self.json_io: kasutame:
            * ["sources"][DOCID]["content"]:string 
        
        Returns:
            self.json_io: lisame:
            * ["tabelid"]["allikad"]:[(DOCID, CONTENT)]            # tee_sources_tabeliks() -- lõpptulemuses
        """
        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "allikad" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["allikad"] = []
        pbar = tqdm(self.json_io["sources"].keys(), disable=(not self.verbose))
        for docid in pbar:
            pbar.set_description(f"# tee_sources_tabeliks: {docid}")
            self.json_io["tabelid"]["allikad"].append((docid, self.json_io["sources"][docid]["content"]))
            #del self.json_io["sources"][docid]["content"]
            pbar.set_description(f"# tee_sources_tabeliks")

    def kustuta_vahetulemused(self)->None:
        if self.verbose:
            sys.stdout.write('# kustutame:')
        if self.verbose:
            sys.stdout.write(' sources...')
        del self.json_io["sources"]
        if self.verbose:
            sys.stdout.write(' indeks...')        
        del self.json_io["indeks"]
        if self.verbose:
            sys.stdout.write(' generator...') 
        del self.json_io["generator"]
        if self.verbose:
            sys.stdout.write('\n')

    def kuva_tabelid(self, indent)-> None:
        """PUBLIC:Lõpptulemus JSON kujul std väljundisse

        Std väljundisse:    
            * ["tabelid"]["vorm_lemmaks"]:[(VORM, 0,LEMMA)] -- lemma kõik vormid, 0:lemma jooksvas sisendkorpuses
            * ["tabelid"]["lemma_korpuse_vormid"]:[(LEMMA, VORM)] -- ainult jooksvas sisendkorpuses esinenud vormid
            * ["tabelid"]["kirjavead"]:[(VIGANE_VORM, VORM, KAAL)] -- ainult jooksvas sisendkorpuses esinenud vormid
            * ["tabelid"]["allikad"]:[(DOCID,CONTENT)]
        """
        json.dump(self.json_io, sys.stdout, indent=indent, ensure_ascii=False)
        sys.stdout.write('\n')
   
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
            ettearvutaja.morfi_sõned()
            ettearvutaja.tee_sõnede_ja_osaõnede_indeks()
            ettearvutaja.tee_generator()
            ettearvutaja.tee_ignoreeritavad_vormid()
            ettearvutaja.tee_kirjavead_loendikaupa()
            #ettearvutaja.tee_sources_tabeliks()
            #ettearvutaja.kustuta_vahetulemused()
            #ettearvutaja.kuva_tabelid(args.indent)

    except Exception as e:
        print(f"An exception occurred: {str(e)}")
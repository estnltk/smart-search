#!/usr/bin/python3

"""
Pooleli lemmade indeksi genemine

$ docker run -p 6000:6000 tilluteenused/estnltk_sentok:2023.04.18
$ docker run -p 7008:7008 tilluteenused/vmetsjson:2023.09.21
$ docker run -p 7007:7007 tilluteenused/vmetajson:2023.06.01
silumiseks:
    {
        "name": "content_2_tabelid_2",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/ea_jsoncontent_2_jsontabelid/",
        "program": "./api_ea_jsoncontent_2_jsontabelid_2.py",
        "env": {\
            "GENERATOR": "http://localhost:7008/api/vm/generator/process", \
            "TOKENIZER": "http://localhost:6000/api/tokenizer/process", \
            "ANALYSER": "http://localhost:7007/api/analyser/process" \
        },
        "args": ["--verbose", "--csvpealkirjad", \
            "../../rt_web_crawler/results/government_orders.csv", \
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
import inspect
from tqdm import tqdm
from typing import Dict, List, Tuple

import kirjavigastaja

class TEE_JSON:
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
        """PRIVATE: Päringu tegemine (sõnestamine, analüüs, genereerimine, ...)

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
            * json_in: {"sources": {DOCID: {"content": str}}}

        Raises:
            Exception: Veebiteenus self.tokenizer äpardus

        Returns: 
            Sõnestame dokumendid, lisame:
            * self.json_io:      
            {   "sources":
                {   DOCID:
                    {   "content": str,
                        "annotations":
                        {   "tokens":
                            [   {   "start":NUMBER,
                                    "end":NUMBER,
                                    "features"
                                    {   "token":str
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        """
        pbar = tqdm(self.json_io["sources"].keys(), 
                desc=f'# {inspect.currentframe().f_code.co_name}', 
                disable=(not self.verbose))
        for docid in pbar:
            self.json_io["sources"][docid] = self.tee_päring(
                    self.tokenizer, self.json_io["sources"][docid])
            del self.json_io["sources"][docid]["annotations"]["sentences"]

    
    def tee_kõigi_terviksõnede_indeks(self) -> None:
        """PUBLIC
        * Liitsõna osasõnedega siin ei tegele, ainult terviksõned.
        * Punktuatsioon, asesõnad jms jääb esialgu sisse.

        Sisse
        {   "sources":
            {   DOCID:
                {   "content": str,
                    "annotations":
                    {   "tokens":
                        [   {   "start":NUMBER,
                                "end":NUMBER,
                                "features"
                                {   "token":str
                                }
                            }
                        ]
                    }
                }
            }
        }

        Välja:
        {   "sources":{DOCID:{"content": str,}},
            "sõnavormid":{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}
        }
        """
        if "sõnavormid" not in self.json_io:
            self.json_io["sõnavormid"] = {}
        pbar = tqdm(self.json_io["sources"].keys(), 
                    desc=f'# {inspect.currentframe().f_code.co_name}', 
                    disable=(not self.verbose))
        for docid in pbar:                   # tsükkel üle tekstide
            for token in self.json_io["sources"][docid]["annotations"]["tokens"]: # tsükkel üle sõnede
                if token["features"]["token"] not in self.json_io["sõnavormid"]:
                    self.json_io["sõnavormid"][token["features"]["token"]] = {}
                if docid not in self.json_io["sõnavormid"][token["features"]["token"]]:
                    self.json_io["sõnavormid"][token["features"]["token"]][docid] = []
                self.json_io["sõnavormid"][token["features"]["token"]][docid].append({"start": token["start"], "end": token["end"]})
            del self.json_io["sources"][docid]["annotations"]

    def tee_mõistlike_tervik_ja_osasõnede_indeks(self)->None:
        """PUBLIC
        * self.json_io["sõnavormid"] hulgast eemaldame punktuatsiooni, sidesõnad, asesõnad.
        * self.json_io["osasõnavormid"] sisaldab liitsõna 1-4 komponendilisi osasõnesid.

        Sisse/välja:
        self.json_io:

        {   "sõnavormid"   :{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}},
            "osasõnavormid":{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}
        }
        """
        self.json_io["osasõnavormid"] = {}
        morf_in = {"params":{"vmetajson":["--stem", "--guess"]}}

        pbar = tqdm(list(self.json_io["sõnavormid"].items()),
                desc=f'# {inspect.currentframe().f_code.co_name}',
                disable=(not self.verbose))
        for k, v in pbar:
            morf_in["annotations"] = {"tokens":[{"features":{"token": k}}]}
            mrf_out = self.tee_päring(self.analyser, morf_in)
            # kustutame mõtetu sõnaliigiga analüüsivariandid
            analüüsid = mrf_out["annotations"]["tokens"][0]["features"]["mrf"]
            analüüsid[:] = [a for a in analüüsid if self.ignore_pos.find(a["pos"]) < 0]
            if len(analüüsid) < 1:
                del(self.json_io["sõnavormid"][k])
                continue
            # leiame liitsõna osasõnad  
            for analüüs in analüüsid:
                osasõnad = analüüs["stem"].replace('=', '').split('_')
                if len(osasõnad) < 2:
                    continue
                # lisame 1 komponendilised
                for osasõna in osasõnad:
                    self.lisa_osasõna(osasõna, v)
                if len(osasõnad) < 3:
                    continue
                # lisame 2 komponendilised
                for i in range(1, len(osasõnad)):
                    self.lisa_osasõna(
                        f'{osasõnad[i-1]}{osasõnad[i]}', v)
                if len(osasõnad) < 4:
                    continue
                # lisame 3 komponendilised
                for i in range(2, len(osasõnad)):
                    self.lisa_osasõna(
                        f'{osasõnad[i-2]}{osasõnad[i-1]}{osasõnad[i]}', v)
                if len(osasõnad) < 5:
                    continue
                # lisame 4 komponendilised
                for i in range(3, len(osasõnad)):
                    self.lisa_osasõna(
                        f'{osasõnad[i-3]}{osasõnad[i-2]}{osasõnad[i-1]}{osasõnad[i]}', v)
                         
    def lisa_osasõna(self, osasõna:str, v:Dict)->None:
        """PRIVATE
        """
        if osasõna not in self.json_io["osasõnavormid"]:
            self.json_io["osasõnavormid"][osasõna] = {}
        for docid in v:
            if docid not in self.json_io["osasõnavormid"][osasõna]:
                self.json_io["osasõnavormid"][osasõna][docid] = []
            self.json_io["osasõnavormid"][osasõna][docid] += v[docid]        

    def tee_mõistlike_lemmade_ja_osalemmade_indeks(self)->None:
        """PUBLIC

        Sisse:
        self.json_io:

        {   "sõnavormid"   :{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}},
            "osasõnavormid":{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}
        }

        Välja:
        self.json_io:

        { "lemmmad":   {LEMMA:{DOCID:[{"start":NUMBER,"end":NUMBER}]}},
          "osalemmmad":{LEMMA:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}
        }
        """
        self.json_io["lemmad"] = {}
        morf_in = {"params":{"vmetajson":["--guess"]}, "annotations":{"tokens":[]}}

        pbar = tqdm(self.json_io["sõnavormid"].items(),
                desc=f'# {inspect.currentframe().f_code.co_name}:lemmad',
                disable=(not self.verbose))
        for k, v in pbar:
            morf_in["annotations"]["tokens"] = [{"features":{"token": k}}]
            morf_out = self.tee_päring(self.analyser, morf_in)
            puhtad_lemmad = []
            for mrf in morf_out["annotations"]["tokens"][0]["features"]["mrf"]:
                if (puhas_lemma := mrf["lemma_ma"].replace('=', '').replace('_', '')) not in puhtad_lemmad:
                    puhtad_lemmad.append(puhas_lemma)
            if len(puhtad_lemmad) < 1:
                continue
            for puhas_lemma in puhtad_lemmad:
                if puhas_lemma not in self.json_io["lemmad"]: # sellist lemmat veel polnud
                    self.json_io["lemmad"][puhas_lemma] = {}
                for docid, poslist in v.items():
                    if docid not in self.json_io["lemmad"][puhas_lemma]:
                        self.json_io["lemmad"][puhas_lemma][docid] = []
                    self.json_io["lemmad"][puhas_lemma][docid] += poslist

        self.json_io["osalemmad"] = {}
        pbar = tqdm(self.json_io["osasõnavormid"].items(),
                desc=f'# {inspect.currentframe().f_code.co_name}:osalemmmad',
                disable=(not self.verbose))
        for k, v in pbar:
            morf_in["annotations"]["tokens"] = [{"features":{"token": k}}]
            morf_out = self.tee_päring(self.analyser, morf_in)
            puhtad_lemmad = []
            for mrf in morf_out["annotations"]["tokens"][0]["features"]["mrf"]:
                if (puhas_lemma := mrf["lemma_ma"].replace('=', '').replace('_', '')) not in puhtad_lemmad:
                    puhtad_lemmad.append(puhas_lemma)
            if len(puhtad_lemmad) < 1:
                continue
            for puhas_lemma in puhtad_lemmad:
                if puhas_lemma not in self.json_io["osalemmad"]: # sellist lemmat veel polnud
                    self.json_io["osalemmad"][puhas_lemma] = {}
                for docid, poslist in v.items():
                    if docid not in self.json_io["osalemmad"][puhas_lemma]:
                        self.json_io["osalemmad"][puhas_lemma][docid] = []
                    self.json_io["osalemmad"][puhas_lemma][docid] += poslist
        pass

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
        tj = TEE_JSON(args.verbose)

        for f  in args.file:
            if tj.verbose:
                sys.stdout.write(f'\n# sisendfail: {f.name}\n')
            if args.csvpealkirjad:
                tj.csvpealkrjadest(f.readlines())
            else:
                tj.string2json(f.read())
            tj.tee_sõnestamine()
            tj.tee_kõigi_terviksõnede_indeks()
            tj.tee_mõistlike_tervik_ja_osasõnede_indeks()
            tj.tee_mõistlike_lemmade_ja_osalemmade_indeks()
    except Exception as e:
        print(f"An exception occurred: {str(e)}")

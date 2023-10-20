 #!/usr/bin/python3

"""
TODO funktsioonide päises olevad kommentaarid õigeks sättida

Lemmade indeksi genemine

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
            "../../rt_web_crawler/results/test.csv"
        ]
    },

Käsurealt (vaikimisi kohalikud konteinerid):
cd ~/git/smart-search_github/api/ea_jsoncontent_2_jsontabelid
export FAILID="government_orders.csv government_regulations.csv local_government_acts.csv state_laws.csv"
export PREFIKS=1017

for f in $(echo "${FAILID}")
do
    echo ${f} '>' ${PREFIKS}-${f/.csv/.json}
    venv/bin/python3 ./api_ea_jsoncontent_2_jsontabelid_2.py \
    --csvpealkirjad \
        ../../rt_web_crawler/results/${f} > ${PREFIKS}-${f/.csv/.json}
done


JSON sees- ja välispidiseks kasutamiseks:

    Sisse: json_io:
    {   "lemmas_2_ignore": 
        {   "lemmas": [string],     # sisse: kasutab tee_ignoreeritavad_vormid(): ingoreeritavad lemmad
        }
        "sources":
        {   DOCID:                  # sisse (string): dokumendi unikaalne ID 
            {   "content": string   # sisse string2json()/csvpealkrjadest(): "plain text"
            }
        }
    }

    Välja json_io:
    {   "tabelid":
        {   "indeks_vormid":[(VORM, DOCID, START, END, LIITSÕNA_OSA)],
            "indeks_lemmad":[(LEMMA, DOCID, START, END, LIITSÕNA_OSA)],
            "liitsõnad":[(OSALEMMA, LIITLEMMA)],
            "lemma_kõik_vormid":[(VORM, LEMMA)],
            "lemma_korpuse_vormid":[(VORM, 0, LEMMA)],
            "kirjavead":[[VIGANE_VORM, VORM, KAAL]],
            "kirjavead_2": [[typo, lemma, correct_wordform, confidence]]
            "allikad":[(DOCID, CONTENT)],
            "ignoreeritavad_vormid":[VORM]
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
            "algsedsõnavormid":{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}
        }
        """
        if "algsedsõnavormid" not in self.json_io:
            self.json_io["algsedsõnavormid"] = {}
        pbar = tqdm(self.json_io["sources"].keys(), 
                    desc=f'# {inspect.currentframe().f_code.co_name}', 
                    disable=(not self.verbose))
        for docid in pbar:                   # tsükkel üle tekstide
            for token in self.json_io["sources"][docid]["annotations"]["tokens"]: # tsükkel üle sõnede
                if token["features"]["token"] not in self.json_io["algsedsõnavormid"]:
                    self.json_io["algsedsõnavormid"][token["features"]["token"]] = {}
                if docid not in self.json_io["algsedsõnavormid"][token["features"]["token"]]:
                    self.json_io["algsedsõnavormid"][token["features"]["token"]][docid] = []
                self.json_io["algsedsõnavormid"][token["features"]["token"]][docid].append({"start": token["start"], "end": token["end"]})
            del self.json_io["sources"][docid]["annotations"]

    def tee_mõistlike_tervik_ja_osasõnede_indeks(self)->None:
        """PUBLIC
        Sisse:
            "algsedsõnavormid":{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}

        * self.json_io["sõnavormid"]:{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}} algsete hulgast eemaldame punktuatsiooni, sidesõnad, asesõnad. Suurtähega mängitud
        * self.json_io["osasõnavormid"]:{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}} sisaldab liitsõna 1-4 komponendilisi osasõnesid.

        Sisse/välja:
        self.json_io:

        * {"sõnavormid"   :{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}} -- ilma punktuatsiooni, side- ja asesõnadeta. Algustähe suutusega mÄngitud         {"osasõnavormid":{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}}
        """
        self.json_io["sõnavormid"] = {}
        self.json_io["osasõnavormid"] = {}
        morf_in = {"params":{"vmetajson":["--stem", "--guess"]}}

        pbar = tqdm(list(self.json_io["algsedsõnavormid"].items()),
                desc=f'# {inspect.currentframe().f_code.co_name}',
                disable=(not self.verbose))
        for k, v in pbar:
            morf_in["annotations"] = {"tokens":[{"features":{"token": k}}]}
            mrf_out = self.tee_päring(self.analyser, morf_in)
            # kustutame mõtetu sõnaliigiga analüüsivariandid
            mrfs = mrf_out["annotations"]["tokens"][0]["features"]["mrf"]
            mrfs[:] = [m for m in mrfs if self.ignore_pos.find(m["pos"]) < 0]
            if len(mrfs) < 1:
                continue
            for mrf in mrfs:
                vorm = mrf["stem"]
                if mrf["ending"] != '0':
                    vorm += mrf["ending"]
                puhas_vorm = vorm.replace('=', '').replace('_', '')
                if puhas_vorm not in self.json_io["sõnavormid"]:
                    self.json_io["sõnavormid"][puhas_vorm] = {}
                for docid, poslist in v.items():
                    if docid not in self.json_io["sõnavormid"][puhas_vorm]:
                        self.json_io["sõnavormid"][puhas_vorm][docid] = []
                    for pos in poslist:
                        if pos not in self.json_io["sõnavormid"][puhas_vorm][docid]:
                            self.json_io["sõnavormid"][puhas_vorm][docid].append(pos)

                # leiame liitsõna osasõnad  

                osasõnad = vorm.replace('=', '').split('_')
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
        pass

    def tabelisse_vormide_indeks(self):
        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "indeks_vormid" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["indeks_vormid"] = []
        pbar = tqdm(list(self.json_io["sõnavormid"].items()),
                    desc=f'# {inspect.currentframe().f_code.co_name} sõnavormid ',
                    disable=(not self.verbose))
        for vorm, docids in pbar:
            for docid, poslist in docids.items():
                for pos in poslist:
                    self.json_io["tabelid"]["indeks_vormid"].append(
                        (vorm, docid, pos["start"], pos["end"], False)
            )

        pbar = tqdm(list(self.json_io["osasõnavormid"].items()),
                    desc=f'# {inspect.currentframe().f_code.co_name} osasõnavormid ',
                    disable=(not self.verbose))
        for vorm, docids in pbar:
            for docid, poslist in docids.items():
                for pos in poslist:
                    self.json_io["tabelid"]["indeks_vormid"].append(
                        (vorm, docid, pos["start"], pos["end"], True))        
        pass

    def lisa_osasõna(self, osasõna:str, v:Dict)->None:
        """PRIVATE
        """
        if osasõna not in self.json_io["osasõnavormid"]:
            self.json_io["osasõnavormid"][osasõna] = {}
        for docid, poslist in v.items():
            if docid not in self.json_io["osasõnavormid"][osasõna]:
                self.json_io["osasõnavormid"][osasõna][docid] = []
            for pos in poslist:
                if pos not in self.json_io["osasõnavormid"][osasõna][docid]:
                    self.json_io["osasõnavormid"][osasõna][docid].append(pos)        

    def tee_mõistlike_lemmade_ja_osalemmade_indeks(self)->None:
        """PUBLIC

        Sisse:
        self.json_io:

        {"sõnavormid"   :{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}}
        {"osasõnavormid":{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}}

        Välja:
        self.json_io:

        {"lemmad"   :{LEMMA:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}}
        {"osalemmad":{LEMMA:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}}
        {"liitsõnad" :{OSASÕNALEMMA:[LIITSÕNALEMMA]}}

        {"tabelid":{"liitsõnad":[(OSALEMMA,LIITLEMMA)]}}
        """
        self.json_io["lemmad"] = {}
        self.json_io["liitsõnad"] = {}
        morf_in = {"params":{"vmetajson":["--guess"]}, "annotations":{"tokens":[]}}

        pbar = tqdm(self.json_io["sõnavormid"].items(),
                desc=f'# {inspect.currentframe().f_code.co_name}:lemmad',
                disable=(not self.verbose))
        for k, v in pbar:
            morf_in["annotations"]["tokens"] = [{"features":{"token": k}}]
            morf_out = self.tee_päring(self.analyser, morf_in)
            puhtad_lemmad = []
            for mrf in morf_out["annotations"]["tokens"][0]["features"]["mrf"]:
                self.tee_liitsõnandus(mrf["lemma_ma"])
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

        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "liitsõnad" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["liitsõnad"] = []
        pbar = tqdm(self.json_io["liitsõnad"].items(),
                desc=f'# {inspect.currentframe().f_code.co_name}:liitsõnade tabel ',
                disable=(not self.verbose))
        for osasõna, liitsõnad in pbar:
            for liitsõna in liitsõnad:
                self.json_io["tabelid"]["liitsõnad"].append((osasõna, liitsõna))
        del self.json_io["liitsõnad"]

        self.json_io["osalemmad"] = {}
        pbar = tqdm(self.json_io["osasõnavormid"].items(),
                desc=f'# {inspect.currentframe().f_code.co_name}:osalemmad',
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

    def tabelisse_lemmade_indeks(self):
        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "indeks_lemmad" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["indeks_lemmad"] = []
        pbar = tqdm(list(self.json_io["lemmad"].items()),
                    desc=f'# {inspect.currentframe().f_code.co_name} lemmad ',
                    disable=(not self.verbose))
        for lemma, docids in pbar:
            for docid, poslist in docids.items():
                for pos in poslist:
                    self.json_io["tabelid"]["indeks_lemmad"].append(
                        (lemma, docid, pos["start"], pos["end"], False)
            )  
        pbar = tqdm(list(self.json_io["osalemmad"].items()),
                    desc=f'# {inspect.currentframe().f_code.co_name} osalemmad ',
                    disable=(not self.verbose))
        for lemma, docids in pbar:
            for docid, poslist in docids.items():
                for pos in poslist:
                    self.json_io["tabelid"]["indeks_lemmad"].append(
                        (lemma, docid, pos["start"], pos["end"], True)
            )                      
        pass


    def tee_liitsõnandus(self, lemma_ma:str)->None:
        kombinatsioonid = []
        osasõnad = lemma_ma.replace('=', '').split('_')
        if len(osasõnad) < 2:
            return
        # lisame 1 komponendilised
        for osasõna in osasõnad:
            if osasõna not in kombinatsioonid:
                kombinatsioonid.append(osasõna)
        if len(osasõnad) > 2:
            # lisame 2 komponendilised
            for i in range(1, len(osasõnad)):
                osasõna = f'{osasõnad[i-1]}{osasõnad[i]}'
                if osasõna not in kombinatsioonid:
                    kombinatsioonid.append(osasõna)
        if len(osasõnad) > 3:
            # lisame 3 komponendilised
            for i in range(2, len(osasõnad)):
                osasõna = f'{osasõnad[i-2]}{osasõnad[i-1]}{osasõnad[i]}'
                if osasõna not in kombinatsioonid:
                    kombinatsioonid.append(osasõna)
        if len(osasõnad) > 4:
            # lisame 4 komponendilised
            for i in range(3, len(osasõnad)):
                osasõna = f'{osasõnad[i-3]}{osasõnad[i-2]}{osasõnad[i-1]}{osasõnad[i]}'
                if osasõna not in kombinatsioonid:
                    kombinatsioonid.append(osasõna)
        # teeme tabeli, kus iga osasõna lemma jaoks on kirjas millistes liitsõnades ta esineb
        #morf_in = {"params":{"vmetajson":["--guess"]}, "content": " ".join(kombinatsioonid)}
        morf_in = {"params":{"vmetajson":["--guess"]}, "annotations":{"tokens":[]}}
        for k in kombinatsioonid:
            morf_in["annotations"]["tokens"].append({"features":{"token":k}})
        morf_out = self.tee_päring(self.analyser, morf_in)
        puhtad_lemmad = []
        for token in morf_out["annotations"]["tokens"]:
            for mrf in token["features"]["mrf"]:
                if (puhas_lemma := mrf["lemma_ma"].replace('=', '').replace('_', '')) not in puhtad_lemmad:
                    puhtad_lemmad.append(puhas_lemma)
        # "liitsõnad" :{OSASÕNALEMMA:[LIITSÕNALEMMA]}
        if "liitsõnad" not in self.json_io:
            self.json_io["liitsõnad"] = {}
        for puhas_lemma in puhtad_lemmad:
            if puhas_lemma not in self.json_io["liitsõnad"]:
                self.json_io["liitsõnad"][puhas_lemma] = []
            if lemma_ma not in self.json_io["liitsõnad"][puhas_lemma]:
                self.json_io["liitsõnad"][puhas_lemma].append(lemma_ma)
        pass

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
            #generator_out = self.tee_päring(self.generator, {"params":{"vmetsjson":["--guess"]}, "content": lemma})
            generator_out = self.tee_päring(self.generator, 
                {"params":{"vmetsjson":["--guess"]}, "annotations":{"tokens":[{"features":{"token":lemma}}]}} )
            # lisa saadud vormid ignoreeritavate vormide loendisse
            for token in generator_out["annotations"]["tokens"]:
                if "mrf" in token["features"]:
                    for mrf in token["features"]["mrf"]:
                        puhas_vorm = mrf["stem"].replace("_", "").replace("=", "").replace("+", "")
                        if puhas_vorm not in ignoreeritavad_vormid:
                            ignoreeritavad_vormid.append((puhas_vorm, 0))                       
        del self.json_io["lemmas_2_ignore"]["lemmad"]
        self.json_io["tabelid"]["ignoreeritavad_vormid"] = ignoreeritavad_vormid

    def tee_generator(self) -> None:
        """PUBLIC:Morfime indeksis olevad sõned lemmadeks ning geneme täieliku ja korpuse paradigma 

        Kasutame:
        * "lemmad"   :{LEMMA:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}
        * "osalemmad":{LEMMA:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}

        Returns: 
            Lisame:
            * self.json_io["generator"][LEMMA]["lemma_kõik_vormid"]:[VORM]

            Terviksõnad ja liitsõna osasõnad kõik koos, neid ei erista siin
            * self.json_io["tabelid"]["lemma_kõik_vormid"]:[(VORM, 0, LEMMA)] -- lõpptulemuses, lemma kõik vormid, 0:lemma jooksvas sisendkorpuses
            * self.json_io["tabelid"]["lemma_korpuse_vormid"]:[(LEMMA, VORM)] -- lõpptulemuses, ainult jooksvas sisendkorpuses esinenud vormid
        """
        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "lemma_kõik_vormid" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["lemma_kõik_vormid"] = []
        if "lemma_korpuse_vormid" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["lemma_korpuse_vormid"] = []
        pbar = tqdm(self.json_io["lemmad"].keys(), desc="# tee_generator: terviklemma vormid ", disable=(not self.verbose))
        for lemma in pbar: # tsükkel üle lemmade 
            self.lisa_lemma_kõik_vormid(lemma, False)
        pbar = tqdm(self.json_io["osalemmad"].keys(), desc="# tee_generator: osalemma vormid ", disable=(not self.verbose))
        for lemma in pbar: # tsükkel üle osalemmade 
            self.lisa_lemma_kõik_vormid(lemma, True)    
            
    def lisa_lemma_kõik_vormid(self, lemma_in:str, is_osalemma:bool)->None:
        # genereerime ettantud lemmast kõik vormid, "content" ei sobi tühikut sisaldavate sõnede tõttu
        #res = self.tee_päring(self.generator,{"params":{"vmetsjson":["--guess"]},"content": f'{lemma_in}'})
        res = self.tee_päring(self.generator, 
                {"params":{"vmetsjson":["--guess"]}, "annotations":{"tokens":[{"features":{"token":lemma_in}}]}} )
        if "generator" not in self.json_io:
            self.json_io["generator"] = {}
        # tsükkel üle genereeritud vormide
        for token in res["annotations"]["tokens"]:
            # {"annotations":{"tokens":[{"features":{"token":string,"mrf":[{"stem": TÜVI}]}}]}
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
                    kirje = (vorm, 0, lemma) # (vorm, genereeritud_korpusesõnest, lemma)
                    if kirje not in self.json_io["tabelid"]["lemma_kõik_vormid"]:
                        self.json_io["tabelid"]["lemma_kõik_vormid"].append(kirje)

                    if is_osalemma: # liitsõna osa
                        # {"osasõnavormid":{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}}
                        if vorm in self.json_io["osasõnavormid"]: # selline esines korpuses osasõnena
                            kirje = (lemma, vorm)             # lisame korpusevormide loendisse
                            if kirje not in self.json_io["tabelid"]["lemma_korpuse_vormid"]:
                                self.json_io["tabelid"]["lemma_korpuse_vormid"].append(kirje)
                    else:
                        # {"sõnavormid"   :{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}}
                        if vorm in self.json_io["sõnavormid"]:  # selline esines korpuses terviksõnena
                            kirje = (lemma, vorm)           # lisame korpusevormide loendisse
                            if kirje not in self.json_io["tabelid"]["lemma_korpuse_vormid"]:
                                self.json_io["tabelid"]["lemma_korpuse_vormid"].append(kirje)                       
        pass

    def tee_kirjavead(self)->None:
        """PUBLIC:Lisame kirjavead parandamiseks vajaliku tabeli

        Args:
            self.json_io: kasutame:
            * {"sõnavormid"   :{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}}
            * {"osasõnavormid":{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}}

        Returns:
            Lisame:
            * self.json_io {"tabelid":{"kirjavead":[[VIGANE_VORM, VORM, KAAL]]}}
        """
        kv = kirjavigastaja.KIRJAVIGASTAJA(self.verbose, self.analyser)
        # kaal_ja_vead = {SÕNAVORM:{"kaal":int, "vead": [str]}}
        sõnavormi_kaal_ja_vead = {}
        # liht- ja liitsõnadest
        pbar = tqdm(self.json_io["sõnavormid"].items(), disable=(not self.verbose), desc="# kirjavead sõnavormidest ")
        for sõnavorm, doclist in pbar:
            if any(char.isdigit() for char in sõnavorm) is True:
                continue # ei tee kirjavigasid numbrit sisaldavatest sõnedest
            kaal = 0
            for poslist in doclist.values():
                kaal += len(poslist)
            assert sõnavorm not in sõnavormi_kaal_ja_vead
            sõnavormi_kaal_ja_vead[sõnavorm] = {
                "vead": kv.gene_potentsiaalsed_kirjavead(sõnavorm),
                "kaal": kaal}
        # liitsõna osasõnadest
        pbar = tqdm(self.json_io["osasõnavormid"].items(), disable=(not self.verbose), desc="# kirjavead osasõnavormidest ")
        for sõnavorm, doclist in pbar:
            if any(char.isdigit() for char in sõnavorm) is True:
                continue # ei tee kirjavigasid numbrit sisaldavatest sõnedest
            kaal = 0
            for poslist in doclist.values():
                kaal += len(poslist)
            if sõnavorm not in sõnavormi_kaal_ja_vead:
                sõnavormi_kaal_ja_vead[sõnavorm] = {
                    "vead": kv.gene_potentsiaalsed_kirjavead(sõnavorm),
                    "kaal": kaal}
            else:
                sõnavormi_kaal_ja_vead[sõnavorm]["kaal"] += kaal # lisame liitsõna osasõnade kaalu juurde
        # teeme lõppkujul tabeli
        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "kirjavead" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["kirjavead"] = []
        pbar = tqdm(sõnavormi_kaal_ja_vead.items(), disable=(not self.verbose), desc="# kirjavead tabeliks ")
        for sõnavorm, kaal_ja_vead in pbar:
            for vigane_vorm in kaal_ja_vead["vead"]:
                assert [vigane_vorm, kaal_ja_vead["kaal"], sõnavorm] not in self.json_io["tabelid"]["kirjavead"], f'Pole unikaalne [{vigane_vorm}, {sõnavorm}, {kaal_ja_vead["kaal"]}]'
                self.json_io["tabelid"]["kirjavead"].append([vigane_vorm, sõnavorm, kaal_ja_vead["kaal"]])

    def tee_kirjavead_2(self)->None:
        '''
        "kirjavead":[[VIGANE_VORM, VORM, KAAL]],
        "kirjavead_2": [[typo, lemma, correct_wordform, confidence]]
        '''
        if "kirjavead_2" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["kirjavead_2"] = []
        morf_in = {"params":{"vmetajson":["--guess"]}, "annotations":{"tokens":[{"features":{"token": ""}}]}}
        puhtad_lemmad = []
        pbar = tqdm(self.json_io["tabelid"]["kirjavead"], disable=(not self.verbose), desc="# tee_kirjavead_2")
        for vigane_vorm, vorm, kaal in pbar:
            try:
                if vorm != morf_in["annotations"]["tokens"][0]["features"]["token"]:
                    # uus vorm, arvutame puhtad lemmad uuesti
                    morf_in["annotations"]["tokens"] = [{"features":{"token": vorm}}]
                    morf_out = self.tee_päring(self.analyser, morf_in)
                    puhtad_lemmad = []
                    assert len(morf_out["annotations"]["tokens"]) == 1
                    for mrf in morf_out["annotations"]["tokens"][0]["features"]["mrf"]:
                        if (puhas_lemma := mrf["lemma_ma"].replace('=', '').replace('_', '')) not in puhtad_lemmad:
                            puhtad_lemmad.append(puhas_lemma)
                for lemma in puhtad_lemmad:
                    assert [vigane_vorm, lemma, vorm, kaal] not in self.json_io["tabelid"]["kirjavead_2"]
                    self.json_io["tabelid"]["kirjavead_2"].append([vigane_vorm, lemma, vorm, kaal])
            except:
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

        # kustutame kõik peale tabelite
        for k in list(self.json_io.keys()):
            if k != "tabelid":
                if self.verbose:
                    sys.stdout.write(f' {k}...')
                del self.json_io[k]
 
        if self.verbose:
            sys.stdout.write('\n')
        pass

    def kuva_tabelid(self, indent)-> None:
        """PUBLIC:Lõpptulemus JSON kujul std väljundisse

        Std väljundisse:    
            *TODO
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
            tj.tabelisse_vormide_indeks()
            tj.tee_mõistlike_lemmade_ja_osalemmade_indeks()
            tj.tabelisse_lemmade_indeks()
            tj.tee_generator()
            tj.tee_ignoreeritavad_vormid()
            tj.tee_kirjavead()
            tj.tee_kirjavead_2()
            tj.tee_sources_tabeliks()
            tj.kustuta_vahetulemused()
            tj.kuva_tabelid(args.indent)

    except Exception as e:
        print(f"An exception occurred: {str(e)}")

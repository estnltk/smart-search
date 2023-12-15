 #!/usr/bin/python3

"""
TODO funktsioonide päises olevad kommentaarid õigeks sättida

Teeb teksitfailidest JSON-kuju, millest järgmise programmiga pannakse kokku andmebaas
-----------------------------------------------------------------
// code (silumiseks):
    {
        "name": "content_2_tabelid_2_test",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/api_advanced_indexing/",
        "program": "./api_advanced_indexing.py",
        "env": {},
        "args": ["--verbose", "--csvpealkirjad", \
            "../../rt_web_crawler/results/test.csv"
        ]
    },
// code (laseb kõik pealkirjad läbi) 
    {
        "name": "content_2_tabelid_pealkirjad",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/api_advanced_indexing/",
        "program": "./api_advanced_indexing.py",
        "env": {},
        "args": ["--verbose", "--csvpealkirjad", \
            "../../rt_web_crawler/results/state_laws.csv" \
            "../../rt_web_crawler/results/government_orders.csv" \
            "../../rt_web_crawler/results/government_regulations.csv" \
            "../../rt_web_crawler/results/local_government_acts.csv" \
        ]
    },
-----------------------------------------------------------------
Käsurealt (töötleme mitu sisendfaili paralleelselt):
$   cd ~/git/smart-search_github/api/ea_jsoncontent_2_jsontabelid
$   make clean ; make -j all

Käsurealt (töötleme ühte sisendfaili korraga):
$ venv/bin/python3 ./api_advanced_indexing.py --verbose --csvpealkirjad test_headers.csv > test_headers_indexes.json
$ venv/bin/python3 ./api_advanced_indexing.py --verbose test_document.json > test_document_indexes.json

-----------------------------------------------------------------
JSON sees- ja välispidiseks kasutamiseks:

    Sisse: 
    * json (seda pole ammu testinud):
    {   "sources":
        {   DOCID:                  # sisse (string): dokumendi unikaalne ID 
            {   "content": string   # sisse string2json()/csvpealkrjadest(): "plain text"
            }
        }
    }

    * CSV pealkirjade ja seotud infoga:
        global_id,document_type,document_title,xml_source

    Välja json_io:
    {   "tabelid":
        {   "indeks_vormid":[(VORM, DOCID, START, END, LIITSÕNA_OSA)],
            "indeks_lemmad":[(LEMMA, DOCID, START, END, LIITSÕNA_OSA)],
            "liitsõnad":[(OSALEMMA, LIITLEMMA)],
            "lemma_kõik_vormid":[(VORM, KAAL, LEMMA)],
            "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)],
            "kirjavead":[(VIGANE_VORM, VORM)],
            "allikad":[(DOCID, CONTENT)],
        }
    }

"""

import csv
import os
import sys
import json
import requests
import inspect
import subprocess
from tqdm import tqdm
from typing import Dict, List, Tuple
from inspect import currentframe, getframeinfo

from estnltk import Text
from estnltk.taggers import SentenceTokenizer

proc_vmetajson = subprocess.Popen(['./vmetajson', '--path=.'],  
                            universal_newlines=True, 
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)

proc_vmetsjson = subprocess.Popen(['./vmetsjson', '--path=.'],  
                            universal_newlines=True, 
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)


class TEE_JSON:
    def __init__(self, verbose:bool, kirjavead:bool)->None:
        """Initsialiseerime muutujad: versiooninumber, jne

        Args:
            verbose (bool): True: kuva tööjärjega seotud infot
            kirjavead (bool): True: genereeri kirjavigade tabel
        """
        self.verbose = verbose
        self.kirjavead = kirjavead

        self.VERSION="2023.12.14"
        self.ignore_pos = "PZJ" # ignoreerime lemmasid, mille sõnaliik on: Z=kirjavahemärk, J=sidesõna, P=asesõna

    def verbose_prints(self, message:str) -> None:
        if self.verbose:
            sys.stderr.write(f'# {message}\n')

    def string2json(self, fname:str, str:str)->None:
        """PUBLIC: String sisendJSONiga DICTiks

        Args:
            fname : sisendfaili nimi
            str (str): String sisendJSONiga

        Raises:
            Exception: Exception({"warning":"JSON parse error"})

        Returns:
            Lisatud:

            * self.json_io["sources"][DOCID]["content"] : str
        """
        self.verbose_prints(f'JSON sisendfail: {fname}')
        try:
            self.json_io = json.loads(str.replace('\n', ' '))
        except:
            raise Exception({"warning":"JSON parse error, {getframeinfo(currentframe()).filename}:{getframeinfo(currentframe()).lineno}"})

    def csvpealkrjadest(self, fname, f)->None:
        """PUBLIC: sisendiks pealkirjad CSV failist

        Args:
            fname : sisendfaili nimi
            f : CSV faili read: global_id,document_type,document_title,xml_source

        Returns:

            self.json_io (Dict): DICTiks tehtud sisendCSV

            {   "sources":
                {   DOCID: // "pk_"+globaalID+liik
                    {   "content": str, // pealkiri
                    }
                }
            }
        """
        self.verbose_prints(f'CSV sisendfail: {fname}')
        data = list(csv.reader(f, delimiter=","))
        self.json_io = {"sources": {}}
        for d in data[1:]:
            assert len(d)==4, f'assert {getframeinfo(currentframe()).filename}:{getframeinfo(currentframe()).lineno}'  #DB
            self.json_io["sources"][f'pk_{d[1]}_{d[0]}'] = {"content" : d[2]}

    '''
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
                raise Exception({"warning":f'Probleemid veebiteenusega {url}, status_code={response.status_code}, {getframeinfo(currentframe()).filename}:{getframeinfo(currentframe()).lineno}'})
            return response.json()
        except:
            raise Exception({"warning":f'Probleemid veebiteenusega {url}, {getframeinfo(currentframe()).filename}:{getframeinfo(currentframe()).lineno}'})
    '''

    def run_subprocess(self, proc, json_in:Dict) -> Dict:
        proc.stdin.write(f'{json.dumps(json_in)}\n')
        proc.stdin.flush()
        return json.loads(proc.stdout.readline())
        
    def estnltk_sentok(self, content: str) -> List:
        """PRIVATE EstNLTK sõnestaja

        Args:
            content (str): Sõnestatav tekst

        Returns:
            List: [{"start":NUMBER,"end":NUMBER,"features":{"token":str}]        
        """
        estnltk_text = Text(content)
        estnltk_text.tag_layer(['words'])
        SentenceTokenizer().tag(estnltk_text)
        tokens = []
        for sentence in estnltk_text.sentences:
            for word in sentence:
                tokens.append({"start": word.start, "end": word.end, "features": {"token": word.enclosing_text}})
        return tokens

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
            if "annotations" not in self.json_io["sources"][docid]:
                self.json_io["sources"][docid]["annotations"] = {}
            self.json_io["sources"][docid]["annotations"]["tokens"] = \
                    self.estnltk_sentok(self.json_io["sources"][docid]["content"])
    
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

        * {"sõnavormid"   :{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}} algsete hulgast eemaldame punktuatsiooni, sidesõnad, asesõnad. Suurtähega mängitud
        * {"osasõnavormid":{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}} sisaldab liitsõna 1-4 komponendilisi osasõnesid.

        Sisse/välja:
        self.json_io:

        Punktuatsioon, asesõnad, sidesõnad väljavisatud, kõik suurtäheliseks
        * {"sõnavormid"   :{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}}
        * {"osasõnavormid":{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}}
        """
        self.json_io["sõnavormid"] = {}
        self.json_io["osasõnavormid"] = {}
        morf_in = {"params":{"vmetajson":["--stem", "--guess"]}}

        pbar = tqdm(list(self.json_io["algsedsõnavormid"].items()),
                desc=f'# {inspect.currentframe().f_code.co_name}',
                disable=(not self.verbose))
        for k, v in pbar:
            morf_in["annotations"] = {"tokens":[{"features":{"token": k}}]}
            #mrf_out = self.tee_päring(self.analyser, morf_in)
            mrf_out = self.run_subprocess(proc_vmetajson, morf_in)
            # kustutame mõtetu sõnaliigiga analüüsivariandid
            mrfs = mrf_out["annotations"]["tokens"][0]["features"]["mrf"]
            mrfs[:] = [m for m in mrfs if self.ignore_pos.find(m["pos"]) < 0]
            if len(mrfs) < 1:
                continue
            for mrf in mrfs:
                vorm = mrf["stem"]
                if mrf["ending"] != '0':
                    vorm += mrf["ending"]
                puhas_vorm = vorm.replace('+', '').replace('=', '').replace('_', '')
                if puhas_vorm not in self.json_io["sõnavormid"]:
                    self.json_io["sõnavormid"][puhas_vorm] = {}
                for docid, poslist in v.items():
                    if docid not in self.json_io["sõnavormid"][puhas_vorm]:
                        self.json_io["sõnavormid"][puhas_vorm][docid] = []
                    for pos in poslist:
                        if pos not in self.json_io["sõnavormid"][puhas_vorm][docid]:
                            self.json_io["sõnavormid"][puhas_vorm][docid].append(pos)

                # leiame liitsõna osasõnad  
                osasõnad = vorm.replace('+', '').replace('=', '').split('_')
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
        pass # DB

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
                    kirje = (vorm, docid, pos["start"], pos["end"], False)
                    if kirje in self.json_io["tabelid"]["indeks_vormid"]:
                        continue
                    self.json_io["tabelid"]["indeks_vormid"].append(kirje)

        pbar = tqdm(list(self.json_io["osasõnavormid"].items()),
                    desc=f'# {inspect.currentframe().f_code.co_name} osasõnavormid ',
                    disable=(not self.verbose))
        for vorm, docids in pbar:
            for docid, poslist in docids.items():
                for pos in poslist:
                    kirje = (vorm, docid, pos["start"], pos["end"], True)
                    if kirje in self.json_io["tabelid"]["indeks_vormid"]:
                        continue
                    self.json_io["tabelid"]["indeks_vormid"].append(kirje)        
        pass # DB

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
            morf_out = self.run_subprocess(proc_vmetajson, morf_in)
            puhtad_lemmad = []
            for mrf in morf_out["annotations"]["tokens"][0]["features"]["mrf"]:
                self.tee_liitsõnandus(mrf["lemma_ma"])
                if (puhas_lemma := mrf["lemma_ma"].replace('+', '').replace('=', '').replace('_', '')) not in puhtad_lemmad:
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
                kirje = (osasõna, liitsõna)
                if kirje not in self.json_io["tabelid"]["liitsõnad"]:
                    self.json_io["tabelid"]["liitsõnad"].append(kirje)
        del self.json_io["liitsõnad"]

        self.json_io["osalemmad"] = {}
        pbar = tqdm(self.json_io["osasõnavormid"].items(),
                desc=f'# {inspect.currentframe().f_code.co_name}:osalemmad',
                disable=(not self.verbose))
        for k, v in pbar:
            morf_in["annotations"]["tokens"] = [{"features":{"token": k}}]
            morf_out = self.run_subprocess(proc_vmetajson, morf_in)
            puhtad_lemmad = []
            for mrf in morf_out["annotations"]["tokens"][0]["features"]["mrf"]:
                if (puhas_lemma := mrf["lemma_ma"].replace('+', '').replace('=', '').replace('_', '')) not in puhtad_lemmad:
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
        pass # DB

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
                    kirje = (lemma, docid, pos["start"], pos["end"], False)
                    if kirje in self.json_io["tabelid"]["indeks_lemmad"]: #DB
                        continue
                    #assert kirje not in self.json_io["tabelid"]["indeks_lemmad"], f'assert {getframeinfo(currentframe()).filename}:{getframeinfo(currentframe()).lineno}'  #DB
                    self.json_io["tabelid"]["indeks_lemmad"].append(kirje)  
        pbar = tqdm(list(self.json_io["osalemmad"].items()),
                    desc=f'# {inspect.currentframe().f_code.co_name} osalemmad ',
                    disable=(not self.verbose))
        for lemma, docids in pbar:
            for docid, poslist in docids.items():
                for pos in poslist:
                    kirje = (lemma, docid, pos["start"], pos["end"], True)
                    if kirje in self.json_io["tabelid"]["indeks_lemmad"]:
                        continue
                    #assert kirje not in self.json_io["tabelid"]["indeks_lemmad"], f'assert {getframeinfo(currentframe()).filename}:{getframeinfo(currentframe()).lineno}'  #DB
                    self.json_io["tabelid"]["indeks_lemmad"].append(kirje)                      
        pass # DB


    def tee_liitsõnandus(self, lemma_ma:str)->None:
        kombinatsioonid = []
        osasõnad = lemma_ma.replace('+', '').replace('=', '').split('_')
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
        morf_in = {"params":{"vmetajson":["--guess"]}, "annotations":{"tokens":[]}}
        for k in kombinatsioonid:
            morf_in["annotations"]["tokens"].append({"features":{"token":k}})
        morf_out = self.run_subprocess(proc_vmetajson, morf_in)
        puhtad_lemmad = []
        for token in morf_out["annotations"]["tokens"]:
            for mrf in token["features"]["mrf"]:
                if (puhas_lemma := mrf["lemma_ma"].replace('+', '').replace('=', '').replace('_', '')) not in puhtad_lemmad:
                    puhtad_lemmad.append(puhas_lemma)
        # "liitsõnad" :{OSASÕNALEMMA:[LIITSÕNALEMMA]}
        if "liitsõnad" not in self.json_io:
            self.json_io["liitsõnad"] = {}
        puhas_liitlemma = lemma_ma.replace('+', '').replace('=', '').replace('_', '')
        for puhas_lemma in puhtad_lemmad:
            if puhas_lemma not in self.json_io["liitsõnad"]:
                self.json_io["liitsõnad"][puhas_lemma] = []
            if lemma_ma not in self.json_io["liitsõnad"][puhas_lemma]:
                self.json_io["liitsõnad"][puhas_lemma].append(puhas_liitlemma)
        pass # DB

    def tee_generator(self) -> None:
        """PUBLIC:Morfime indeksis olevad sõned lemmadeks ning geneme täieliku ja korpuse paradigma 

        Kasutame:
        * "lemmad"   :{LEMMA:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}
        * "osalemmad":{LEMMA:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}

        Returns: 
            Lisame:
            * generator = {LEMMA: [{"kaal":int, "vorm":str}]}} 

            Terviksõnad ja liitsõna osasõnad kõik koos, neid ei erista siin
            * self.json_io["tabelid"]["lemma_kõik_vormid"]:[(VORM, KAAL, LEMMA)] -- lõpptulemuses, genetud_vorm, mitu_korda_genetud_vorm_esines, genetud_vormi_lemma
            * self.json_io["tabelid"]["lemma_korpuse_vormid"]:[(LEMMA, KAAL, VORM)] -- lõpptulemuses, korpusevorm, mitu_korda_korpusevorm_esines, korpusevormi_lemma
        """
        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "lemma_kõik_vormid" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["lemma_kõik_vormid"] = []
        if "lemma_korpuse_vormid" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["lemma_korpuse_vormid"] = []
        if "generator" not in self.json_io:
            self.json_io["generator"] = {}
        pbar = tqdm(self.json_io["lemmad"].keys(), desc="# tee_generator: terviklemma vormid ", disable=(not self.verbose))
        for lemma in pbar: # tsükkel üle lemmade 
            if lemma not in self.json_io["generator"]:
                self.lisa_lemma_vormid(lemma)
        pbar = tqdm(self.json_io["osalemmad"].keys(), desc="# tee_generator: osalemma vormid ", disable=(not self.verbose))
        for lemma in pbar: # tsükkel üle osalemmade 
            if lemma not in self.json_io["generator"]:
                self.lisa_lemma_vormid(lemma)    
        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "lemma_kõik_vormid" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["lemma_kõik_vormid"] = []
        if "lemma_korpuse_vormid" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["lemma_korpuse_vormid"] = []
        for lemma, vormid in self.json_io["generator"].items():
            for vorm, kaal in self.json_io["generator"][lemma].items():
                self.json_io["tabelid"]["lemma_kõik_vormid"].append((vorm, kaal, lemma))
                if kaal > 0:
                    self.json_io["tabelid"]["lemma_korpuse_vormid"].append((lemma, kaal, vorm))    
        pass # DB

    def lisa_lemma_vormid(self, lemma_in:str)->None:
        # genereerime ettantud lemmast kõik vormid, "content" ei sobi tühikut sisaldavate sõnede tõttu
        # res = self.tee_päring(self.generator,{"params":{"vmetsjson":["--guess"]},"content": f'{lemma_in}'})
        # {"generator": {LEMMA: {VORM:KAAL}} 
        # {"sõnavormid"   :{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}}
        # {"osasõnavormid":{SÕNAVORM:{DOCID:[{"start":NUMBER,"end":NUMBER}]}}}
        res = self.run_subprocess(proc_vmetsjson, 
            {"params":{"vmetsjson":["--guess"]}, "annotations":{"tokens":[{"features":{"token":lemma_in}}]}} )
        if "generator" not in self.json_io:
            self.json_io["generator"] = {}
        # tsükkel üle genereeritud vormide
        for token in res["annotations"]["tokens"]:
            # {"annotations":{"tokens":[{"features":{"token":string,"mrf":[{"stem": TÜVI}]}}]}
            lemma = token["features"]["token"]
            if lemma not in self.json_io["generator"]:
                self.json_io["generator"][lemma] = {}
            if "mrf" in token["features"]:
                for mrf in token["features"]["mrf"]:
                    vorm = mrf["stem"].replace('+', '').replace('=', '').replace('_', '')
                    if mrf["ending"] != '0':
                        vorm += mrf["ending"]
                    if vorm not in self.json_io["generator"][lemma]:
                        kaal = 0
                        if vorm in self.json_io["sõnavormid"]:
                            for _, poslist in self.json_io["sõnavormid"][vorm].items():
                                kaal += len(poslist)
                        if vorm in self.json_io["osasõnavormid"]:
                            for _, poslist in self.json_io["osasõnavormid"][vorm].items():
                                kaal += len(poslist)
                        self.json_io["generator"][lemma][vorm]=kaal
        pass # DB

    def gene_potentsiaalsed_kirjavead(self, token:str)->List[str]:
        """PRIVATE:Genereeri sõnavormist potentsiaalsed kirjavigased vormid

        Args:
            token (str): sõnavorm

        Returns:
            List[str]: need genereeritud kirjavead, mida morf ilma oletamiseta ära ei tunna 
        """
        potentsiaalsed_kirjavead = []
        for i in range(len(token)):
            if len(token) > 3: # peab olema vähemalt 3 tähte
                # 2 tähte vahetuses: tigu -> itgu, tgiu, tiug
                if i > 0 and token[i] != token[i-1]: # kahte ühesugust tähte ei vaheta
                    t = token[0:i-1]+token[i]+token[i-1]+token[i+1:]
                    if t not in potentsiaalsed_kirjavead:
                        potentsiaalsed_kirjavead.append(t) 
                # 1 täht läheb topelt
                t = token[:i]+token[i]+token[i]+token[i+1:]
                if t not in potentsiaalsed_kirjavead:
                    potentsiaalsed_kirjavead.append(t) 
                # 1 täht kaob ära
                t = token[:i]+token[i+1:]
                if t not in potentsiaalsed_kirjavead:
                        potentsiaalsed_kirjavead.append(t) 
                # g b d k p t-> k p t g b d
                if (n := "gbdkpt".find(token[i])) > -1:
                    t = token[:i]+"kptgbd"[n]+token[i+1:]                   
                    if t not in potentsiaalsed_kirjavead:
                        potentsiaalsed_kirjavead.append(t)
        if len(potentsiaalsed_kirjavead) == 0:
            return []
        morf_in = {"params": {"vmetajson":["--stem"]}, "annotations":{"tokens":[]}}
        for pkv in potentsiaalsed_kirjavead:
            morf_in["annotations"]["tokens"].append({"features":{"token": pkv}})
        morf_out = self.run_subprocess(proc_vmetajson, morf_in)
        for token in morf_out["annotations"]["tokens"]:
            if "mrf" not in token["features"]:
                potentsiaalsed_kirjavead.append(token["features"]["token"])
        return potentsiaalsed_kirjavead

    def tee_kirjavead(self)->None:
        """PUBLIC:Lisame kirjavead parandamiseks vajaliku tabeli

        Args:
            self.json_io: kasutame:
            Kõigi sõnavormide loend
            * self.json_io["tabelid"]["lemma_kõik_vormid"]:[[VORM, KAAL, LEMMA]]
        Returns:
            Lisame:
            * self.json_io {"tabelid":{"kirjavead":[(VIGANE_VORM, VORM)]}}
        """
        if self.kirjavead is False:
            return
        
        if "tabelid" not in self.json_io:
            self.json_io["tabelid"] = {}
        if "kirjavead" not in self.json_io["tabelid"]:
            self.json_io["tabelid"]["kirjavead"] = []
        kvead = {} # {VORM:[VIGANE_VORM]}
        pbar = tqdm(self.json_io["tabelid"]["lemma_kõik_vormid"], disable=(not self.verbose), desc="# kirjavead kõigist genetud sõnavormidest ")
        for vorm, _, _ in pbar:
            if any(char.isdigit() for char in vorm) is True:
                continue # ei tee kirjavigasid numbreid sisaldavatest sõnedest
            if vorm not in kvead:
                kvead[vorm] = []
            kvead[vorm] = self.gene_potentsiaalsed_kirjavead(vorm)
        pbar = tqdm(kvead.items(), disable=(not self.verbose), desc="# genetud kirjavead tabeliks ")
        for vorm, kirjavead in pbar:
            for kirjaviga in kirjavead:
                kirje = (kirjaviga, vorm)
                #if kirje not in self.json_io["tabelid"]["kirjavead"]:
                self.json_io["tabelid"]["kirjavead"].append(kirje)
        self.json_io["tabelid"]["kirjavead"] = list(set(self.json_io["tabelid"]["kirjavead"]))
        pass # DB

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
        pbar = tqdm(self.json_io["sources"].keys(), disable=(not self.verbose), desc="# tee_sources_tabeliks")
        for docid in pbar:
            #pbar.set_description(f"# tee_sources_tabeliks: {docid}")
            self.json_io["tabelid"]["allikad"].append((docid, self.json_io["sources"][docid]["content"]))
            #del self.json_io["sources"][docid]["content"]
            #pbar.set_description(f"# tee_sources_tabeliks")
        pass # DB

    def kustuta_vahetulemused(self)->None:

        #if self.verbose:
        #    sys.stdout.write('# kustutame:')

        # kustutame kõik peale tabelite
        pbar = tqdm(self.json_io.keys(), disable=(not self.verbose), desc="# kustutame vahetulemused")
        for k in list(pbar):
            if k != "tabelid":
                #if self.verbose:
                #    sys.stdout.write(f' {k}...')
                #logging.info(f'# Kustatame Vahetulemuse: {k}')
                del self.json_io[k]
        #if self.verbose:
        #    sys.stdout.write('\n')
        pass # DB

    def kordused_tabelitest_välja(self):
        '''
        {   "tabelid":
            {   "indeks_vormid":[(VORM, DOCID, START, END, LIITSÕNA_OSA)],
                "indeks_lemmad":[(LEMMA, DOCID, START, END, LIITSÕNA_OSA)],
                "liitsõnad":[(OSALEMMA, LIITLEMMA)],
                "lemma_kõik_vormid":[(VORM, KAAL, LEMMA)],
                "lemma_korpuse_vormid":[(VORM, KAAL, LEMMA)],
                "kirjavead":[[VIGANE_VORM, KAAL]],
                "allikad":[(DOCID, CONTENT)],
            }
        }
        '''
        if self.kirjavead is True:
            tabelid = ["indeks_vormid", "indeks_lemmad", "liitsõnad", "lemma_kõik_vormid", "lemma_korpuse_vormid", "kirjavead"]
        else:
            tabelid = ["indeks_vormid", "indeks_lemmad", "liitsõnad", "lemma_kõik_vormid", "lemma_korpuse_vormid"]
        pbar = tqdm(tabelid, disable=(not self.verbose), desc="# kustutame tabelitest kordused")
        for tabel in pbar:
            #pbar.set_description(f'# {inspect.currentframe().f_code.co_name} : {tabel}')
            self.json_io["tabelid"][tabel] = list(set(self.json_io["tabelid"][tabel]))
        pass # DB

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
        return  {"ettearvutaja.version": self.VERSION }


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-p', '--csvpealkirjad',  action="store_true", help='sisendfaili formaat')
    argparser.add_argument('-k', '--kirjavead',  action="store_true", help='genereeri kirjavead')
    argparser.add_argument('-v', '--verbose',  action="store_true", help='kuva rohkem infot tööjärje kohta')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    argparser.add_argument('file', type=argparse.FileType('r'), nargs='+')
    args = argparser.parse_args()

    try:
        tj = TEE_JSON(args.verbose, args.kirjavead)

        for f  in args.file:
            if args.csvpealkirjad:
                tj.csvpealkrjadest(f.name, f.readlines())
            else:
                tj.string2json(f.name, f.read())
            tj.tee_sõnestamine()
            tj.tee_kõigi_terviksõnede_indeks()
            tj.tee_mõistlike_tervik_ja_osasõnede_indeks()
            tj.tabelisse_vormide_indeks()
            tj.tee_mõistlike_lemmade_ja_osalemmade_indeks()
            tj.tabelisse_lemmade_indeks()
            tj.tee_generator()
            tj.tee_kirjavead()
            tj.tee_sources_tabeliks()
            tj.kustuta_vahetulemused()
            tj.kordused_tabelitest_välja()
            tj.kuva_tabelid(args.indent)

    except Exception as e:
        print(f"An exception occurred: {str(e)}")

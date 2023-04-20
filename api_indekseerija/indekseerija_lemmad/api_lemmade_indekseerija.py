#!/usr/bin/python3

import os
import sys
import json
import requests
from typing import Dict, List
from collections import OrderedDict

'''
Ilma argumentideta loeb JSONit std-sisendist ja kirjutab tulemuse std-väljundisse
Muidu JSON käsirealt lipu "--json=" tagant.
{   "sources":
    {   DOCID:              // dokumendi ID
        {   "content": str  // dokumendi tekst ("plain text", märgendus vms teraldi tõstetud)
                            // dokumendi kohta käiv lisainfo pane siia...
        }
    }
}

Välja:
{   "sources":
    {   DOCID:              // dokumendi ID
        {   "content": str  // dokumendi tekst ("plain text", märgendus vms teraldi tõstetud)
                            // dokumendi kohta käiv lisainfo, kui see oli algses JSONis
        }
    }
    "index":
    {   SÕNE:                               // string tekstist, esinemiste arv == "positions" massiivi pikkus
        {   DOCID:                              // dokumendi ID
            [   {   "start": int,               // alguspostsioon jooksvas tekst
                    "end": int,                 // lõpupostsioon jooksvas tekst  
                    "liitsõna_osa": bool,       // SÕNE on liitsõna osa, vahel korrektne, vahel mitte, mõistlik oleks võtta ainult liitsõna viimane komponent
                    // "järeliide_eemaldatud:bool  // kui järelliiteid üldse käsitleda, siis väikest hulka eriti regulaarseid ja sagedasi
                }
            ]
        }
    }
}
'''

class LEMMADE_IDX:
    def __init__(self):
        self.VERSION="2023.04.20"

        self.tokenizer = os.environ.get('TOKENIZER')
        if self.tokenizer is None:
            self.TOKENIZER_IP=os.environ.get('TOKENIZER_IP') if os.environ.get('TOKENIZER_IP') != None else 'localhost'
            self.TOKENIZER_PORT=os.environ.get('TOKENIZER_PORT') if os.environ.get('TOKENIZER_PORT') != None else '6000'
            self.tokenizer = f'http://{self.TOKENIZER_IP}:{self.TOKENIZER_PORT}/api/tokenizer/process'

        self.analyser = os.environ.get('ANALYSER')
        if self.analyser is None:
            self.ANALYSER_IP=os.environ.get('ANALYSER_IP') if os.environ.get('ANALYSER_IP') != None else 'localhost'
            self.ANALYSER_PORT=os.environ.get('ANALYSER_PORT') if os.environ.get('ANALYSER_PORT') != None else '7007'
            self.analyser = f'http://{self.ANALYSER_IP}:{self.ANALYSER_PORT}/api/analyser/process'

        self.ignore_pos = "PZJ" # ignoreerime lemmasid, mille sõnaliik on: Z=kirjavahemärk, J=sidesõna, P=asesõna

    def string2json(self, str:str) -> Dict:
        """JSON sisendstring "päris" JSONiks

        Args:
            str (str): _description_

        Raises:
            Exception: Jama sisendJSONi parsimisega
        Returns:
            Dict: _description_
        """
        self.json_io = {}
        try:
            self.json_io = json.loads(str)
            return self.json_io
        except:
            raise Exception({"error": "JSON parse error"})

    def morfi_1(self, tokens:List) -> List:
        """Leia sõne unikaalsed lemmad

        Ignoreerime asesõnu, sidesõnu, kirjavahemärke
        Args:
            tokens (List): sõnede massiiv

        Raises:
            Exception: Hoiatus, kui morfi veebiteenus täiega sakib

        Returns:
            List: unikaalsete lemmade loend ilma liitsõna ja järelliite piirimärkideta
        """
        json_in = {"params":{"vmetajson":["--guess"]}, "annotations":{"tokens":[]}}
        for token in tokens: 
            json_in["annotations"]["tokens"].append({"features":{"token": token}})
        lemmas = [] # siia korjame erinevad lemma-stringid
        try:
            json_out = json.loads(requests.post(self.analyser, json=json_in).text)
        except:
            raise Exception({"warning":'Probleemid morf analüüsi veebiteenusega'})
        for token in json_out["annotations"]["tokens"]:                          # tsükkel üle sõnede (ainult üks sõne meil antud juhul on)                           
            for mrf in token["features"]["mrf"]:                                    # tsükkel üle sama sõne alüüsivariantide (neid võib olla mitu)
                if self.ignore_pos.find(mrf["pos"]) != -1:                              # selle sõnaliiiga lemmasid...
                    continue                                                                # ...ignoreerime, neid ei indekseeri
                lemma = mrf["lemma_ma"].replace("_", "").replace("=", "")
                if lemma not in lemmas:                                                   # sõne morf analüüside hulgas võib sama kujuga lemma erineda ainult käände/põõrde poolest
                    lemmas.append( lemma)                                                      # lisame uue lemma-stringi, kui sellist veel polnud
        return lemmas

    def morfi(self)->None:
        """_summary_

        Raises:
            Exception: Jama morf analüüsi veebiteenusega

        Returns:
            None: Lisab self.json_io'sse morf analüüsi 
        """

        for docid in self.json_io["sources"]:
            self.json_io["sources"][docid]["params"] = {"vmetajson":["--guess"]}
            try:
                doc = json.loads(requests.post(self.analyser, json=self.json_io["sources"][docid]).text)
            except:
                raise Exception({"warning":'Probleemid morf analüüsi veebiteenusega'})
            for idx_token, token in enumerate(doc["annotations"]["tokens"]):        # tsükkel üle sõnede (ainult üks sõne meil antud juhul on)
                tokens = []                                                             # siia korjame erinevad lemma-stringid
                for mrf in token["features"]["mrf"]:                                    # tsükkel üle sama sõne alüüsivariantide (neid võib olla mitu)
                    if self.ignore_pos.find(mrf["pos"]) != -1:                              # selle sõnaliiiga lemmasid...
                        continue                                                                # ...ignoreerime, neid ei indekseeri
                    if mrf["lemma_ma"] not in tokens:                                                   # sõne morf analüüside hulgas võib sama kujuga lemma erineda ainult käände/põõrde poolest
                        tokens.append( mrf["lemma_ma"])                                                      # lisame uue lemma-stringi, kui sellist veel polnud
                self.json_io["sources"][docid]["annotations"]["tokens"][idx_token]["features"]["tokens"] = tokens # lisame leitud lemmad tulemusse

    
    def tee_lemmade_indeks(self, json_in:Dict, dct_sorted:bool, sortorder_reverse:bool) -> Dict:
        """Tekitab indeksi

        Args:
            json_io (Dict): SisendJSON_
            sorted_by_token (bool): Väljund järjestatud sõnede järgi
            sortorder_reverse (bool): Sõnede pöördjärjestus

        Raises:
            Exception: Jama sõnestamise veebiteenusega

        Returns:
            Dict: Indeks JSONkujul
        """

        self.json_io = json_in
        for docid in self.json_io["sources"]:
            try:                                                # sõnestame
                self.json_io["sources"][docid] = json.loads(requests.post(self.tokenizer, json=self.json_io["sources"][docid]).text)
            except:                                             # sõnestamine äpardus
                return {"warning":'Probleemid sõnestamise veebiteenusega'}
        self.morfi()                                            # leiame iga tekstisõne võimalikud sobiva sõnaliigiga tüvi+lõpud (liitsõnapiir='_', järelliite eraldaja='=')   
        if "index" not in self.json_io:
            self.json_io["index"] = {}
        for docid in self.json_io["sources"]:                   # tsükkel üle tekstide
            for token in self.json_io["sources"][docid]["annotations"]["tokens"]: # tsükkel üle lemmade
                if len(token["features"]["tokens"])==0:             # kui pole ühtegi meid huvitava sõnaliigiga...
                    continue                                            # ...laseme üle
                for tkn in token["features"]["tokens"]:             # tsükkel üle leitud liitsõnapiiridega lemmade
                    puhas_tkn = tkn.replace('_', '').replace('=', '')   # terviklemma lisamine...
                    if puhas_tkn in self.json_io["index"]:              # kui selline lemma juba oli...
                        if docid in self.json_io["index"][puhas_tkn]:       # ...selles dokumendis
                            self.json_io["index"][puhas_tkn][docid].append({"liitsõna_osa":False, "start": token["start"], "end":token["end"]})
                        else:                                               # ...polnud selles dokumendis
                            self.json_io["index"][puhas_tkn][docid] = [{"liitsõna_osa":False, "start": token["start"], "end":token["end"]}]
                    else:                                               # ...polnud seni üheski dokumendis                               
                        self.json_io["index"][puhas_tkn] = {docid:[{"liitsõna_osa":False, "start": token["start"], "end":token["end"]}]}
                                                                        # liitsõna osalemmade lisamine, tegelt võiks piirduda viimasega
                    osasonad = tkn.replace('=', '').split('_')          # tükeldame liitsõna piirilt
                    if len(osasonad) <= 1:                              # kui pole liitsõna...
                        continue                                            # ...laseme üle
                    fragmendid = []                                     # siia hakkame korjame liitsõna tükikesi
                    # Suure tõenäosusega oleks mõistlik võtta ainult
                    # liitsõna viimane komponent.
                    for idx, osasona in enumerate(osasonad):            # tsükkel ole liitsõna osasõnade
                        if idx == 0:                                    # algab esimese osasõnaga
                            sona = osasona
                            #fragmendid.append(sona) 
                            fragmendid += self.morfi_1([sona])          # esimene osasõna, lemmatiseerime                                                  
                            for idx2 in range(idx+1, len(osasonad)-1):
                                sona += osasonad[idx2]
                                #fragmendid.append(sona)
                                fragmendid += self.morfi_1([sona])      # ei lõppe viimase osasõnaga, lemmatiseerime
                        elif idx == len(osasonad)-1:                    # lõppeb viimase osasõnaga
                            fragmendid.append(osasona)
                        else:                                           # vahepealsed jupid (kui liitsõnas 3 või enam komponenti)
                            #fragmendid.append(osasona)
                            fragmendid += self.morfi_1([osasona])
                            sona = osasonad[idx]
                            for idx2 in range(idx+1, len(osasonad)):
                                sona += osasonad[idx2]
                                if idx2 < len(osasonad)-1:
                                    #fragmendid.append(sona)
                                    fragmendid += self.morfi_1([sona])  # ei lõppe viimase osasõnaga, lemmatiseerime
                                else:
                                    fragmendid.append(sona)
                    for puhas_tkn in fragmendid:                        # lisame leitud osasõnade lemmad indeksisse 
                        if puhas_tkn in self.json_io["index"]:          # kui selline sõne juba oli...
                            if docid in self.json_io["index"][puhas_tkn]:   # ...selles dokumendis
                                    self.json_io["index"][puhas_tkn][docid].append({"liitsõna_osa":True, "start": token["start"], "end":token["end"]})
                            else:                                           # ...polnud selles dokumendis
                                self.json_io["index"][puhas_tkn][docid] = [{"liitsõna_osa":True, "start": token["start"], "end":token["end"]}]
                        else:                                           # ...polnud seni üheski dokumendis                               
                            self.json_io["index"][puhas_tkn] = {docid:[{"liitsõna_osa":True, "start": token["start"], "end":token["end"]}]}
            del self.json_io["sources"][docid]["annotations"]["sentences"] # kustutame morf analüüsist järgi jäänud mudru
            del self.json_io["sources"][docid]["annotations"]["tokens"]
            if len(self.json_io["sources"][docid]["annotations"]) == 0:
                del self.json_io["sources"][docid]["annotations"]
            del self.json_io["sources"][docid]["params"]
        # järjestame vastavalt etteantud parameetritele
        if dct_sorted is True:
            self.json_io["index"] = OrderedDict(sorted(self.json_io["index"].items(), reverse=sortorder_reverse, key=lambda t: t[0]))
        return self.json_io

if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-s', '--sorted', action="store_true", help='sorted JSON')
    argparser.add_argument('-r', '--reverse', action="store_true", help='reverse sort order')
    argparser.add_argument('-j', '--json', type=str, help='json input')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    argparser.add_argument('-c', '--csv', action="store_true", help='CSV-like output')
    args = argparser.parse_args()

    idx = LEMMADE_IDX()
    if args.json is not None:
        json_in = idx.string2json(args.json)
        if "error" in json_in:
            json.dump(json_in, sys.stdout, indent=args.indent)
            sys.exit(1)
        idx = idx.tee_lemmade_indeks(json_in, args.sorted, args.reverse)
        if args.csv is True:
            for sone in idx["index"]:
                for docid in idx["index"][sone]:
                    for k in idx["index"][sone][docid]:
                        sys.stdout.write(f'{sone}\t{k["liitsõna_osa"]}\t{idx["sources"][docid]["content"][k["start"]:k["end"]]}\t{docid}\t{k["start"]}\t{k["end"]}\n')
        else:
            json.dump(idx, sys.stdout, indent=args.indent, ensure_ascii=False)
            sys.stdout.write('\n')
    else:
        for line in sys.stdin:
            line = line.strip()
            if len(line) <= 0:
                continue
            json_in = idx.string2json(line)
            if "error" in json_in:
                json.dump(json_in, sys.stdout, indent=args.indent)
                sys.exit(1)
            idx = idx.leia_soned_osasoned(json_in, args.sorted, args.reverse)
            if args.csv is True:
                for sone in idx["index"]:
                    for docid in idx["index"][sone]:
                        for k in idx["index"][sone][docid]:
                            sys.stdout.write(f'{sone}\t{k["liitsõna_osa"]}\t{idx["sources"][docid]["content"][k["start"]:k["end"]]}\t{docid}\t{k["start"]}\t{k["end"]}\n')
            else:
                json.dump(idx, sys.stdout, indent=args.indent, ensure_ascii=False)
                sys.stdout.write('\n')


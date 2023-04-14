#!/usr/bin/python3

import os
import sys
import json
import requests
from typing import Dict, List
from collections import OrderedDict

'''
See programm kasutab Tartu Ülikooli pilves olevaid
sõnestamise ja morf analüüsi konteinereid.
Programmi saab kiiremaks kui vastavad konteinerid töötavad "lähemal".
'''

class SONEDE_IDX:
    VERSION="2023.04.06"
    TOKENIZER='https://smart-search.tartunlp.ai/api/tokenizer/process'
    LEMMATIZER='https://smart-search.tartunlp.ai/api/lemmatizer/process'
    ANALYSER='https://smart-search.tartunlp.ai/api/analyser/process'

    ignore_pos = "PZJ" # ignoreerime lemmasid, mille sõnaliik on: Z=kirjavahemärk, J=sidesõna, P=asesõna

    json_io = {}

    def string2json(self, str:str) -> Dict:
        """_summary_

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
        

    def morfi(self)->None:
        """_summary_

        Raises:
            Exception: Jama morf analüüsi veebiteenusega

        Returns:
            None: Lisab self.json_io'sse morf analüüsi 
        """

        for docid in self.json_io["sources"]:
            self.json_io["sources"][docid]["params"] = {"vmetajson":["--stem", "--guess"]}
            try:
                doc = json.loads(requests.post(self.ANALYSER, json=self.json_io["sources"][docid]).text)
            except:
                raise Exception({"warning":'Probleemid morf analüüsi veebiteenusega'})
            for idx_token, token in enumerate(doc["annotations"]["tokens"]):        # tsükkel üle sõnede (ainult üks sõne meil antud juhul on)
                tokens = []                                                             # siia korjame erinevad tüvi+lõpp stringid
                for mrf in token["features"]["mrf"]:                                    # tsükkel üle sama sõne alüüsivariantide (neid võib olla mitu)
                    if self.ignore_pos.find(mrf["pos"]) != -1:                              # selle sõnaliiiga tüvesid...
                        continue                                                                # ...ignoreerime, neid ei indekseeri
                    tkn = mrf["stem"]+mrf["ending"] if mrf["ending"] != '0' else mrf["stem"]# tüvi+lõpp
                    if tkn not in tokens:                                                   # sõne morf analüüside hulgas võib sama kujuga tüvi erineda ainult käände/põõrde poolest
                        tokens.append(tkn)                                                      # lisame uue tüvi+lõpp stringi, kui sellist veel polnud
                self.json_io["sources"][docid]["annotations"]["tokens"][idx_token]["features"]["tokens"] = tokens # lisame tulemusse

    
    def leia_soned_osasoned(self, json_in:Dict, dct_sorted:bool, sortorder_reverse:bool) -> Dict:
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
                self.json_io["sources"][docid] = json.loads(requests.post(self.TOKENIZER, json=self.json_io["sources"][docid]).text)
            except:                                             # sõnestamine äpardus
                return {"warning":'Probleemid sõnestamise veebiteenusega'}

        try:
            self.morfi()                                            # leiame iga tekstisõne võimalikud sobiva sõnaliigiga tüvi+lõpud (liitsõnapiir='_', järelliite eraldaja='=')   
        except Exception:
            return  {"warning":'Probleemid morf analüüsi veebiteenusega'}
        if "index" not in self.json_io:
            self.json_io["index"] = {}
        for docid in self.json_io["sources"]:                   # tsükkel üle tekstide
            for token in self.json_io["sources"][docid]["annotations"]["tokens"]: # tsükkel üle sõnede
                if len(token["features"]["tokens"])==0:             # kui pole ühtegi meid huvitava sõnaliigiga...
                    continue                                            # ...laseme üle
                for tkn in token["features"]["tokens"]:             # tsükkel üle leitud liitsõnapiiridega sõnede
                    puhas_tkn = tkn.replace('_', '').replace('=', '')
                    if puhas_tkn in self.json_io["index"]:              # kui selline sõne juba oli...
                        if docid in self.json_io["index"][puhas_tkn]:       # ...selles dokumendis
                            self.json_io["index"][puhas_tkn][docid].append({"liitsõna_osa":False, "start": token["start"], "end":token["end"]})
                        else:                                               # ...polnud selles dokumendis
                            self.json_io["index"][puhas_tkn][docid] = [{"liitsõna_osa":False, "start": token["start"], "end":token["end"]}]
                    else:                                               # ...polnud seni üheski dokumendis                               
                        self.json_io["index"][puhas_tkn] = {docid:[{"liitsõna_osa":False, "start": token["start"], "end":token["end"]}]}

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
                        if puhas_tkn in self.json_io["index"]:          # kui selline sõne juba oli...
                            if docid in self.json_io["index"][puhas_tkn]:   # ...selles dokumendis
                                    self.json_io["index"][puhas_tkn][docid].append({"liitsõna_osa":False, "start": token["start"], "end":token["end"]})
                            else:                                           # ...polnud selles dokumendis
                                self.json_io["index"][puhas_tkn][docid] = [{"liitsõna_osa":False, "start": token["start"], "end":token["end"]}]
                        else:                                           # ...polnud seni üheski dokumendis                               
                            self.json_io["index"][puhas_tkn] = {docid:[{"liitsõna_osa":False, "start": token["start"], "end":token["end"]}]}
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
    '''
    Ilma argumentideta loeb JSONit std-sisendist ja kirjutab tulemuse std-väljundisse
    Muidu JSON käsirealt lipu "--json=" tagant.
    {   "sources":
        {   DOCID:   // dokumendi ID
            {   "content": str  // dokumendi tekst ("plain text", märgendus vms teraldi tõstetud)
                // dokumendi kohta käiv lisainfo pane siia...
            }
        }
    }

    Välja:
    {   "sources":
        {   DOCID:   // dokumendi ID
            {   "content": str  // dokumendi tekst ("plain text", märgendus vms teraldi tõstetud)
                // dokumendi kohta käiv lisainfo, kui see oli algsess JSONis
            }
        }
        "index":
        {   SÕNE: // string tekstist, esinemiste arv == "positions" massiivi pikkus
            {   DOCID:  // dokumendi ID
                [   {   "start": int,               // alguspostsioon jooksvas tekst
                        "end": int,                 // lõpupostsioon jooksvas tekst  
                        "liitsõna_osa": bool,       // SÕNE on liitsõna osa, vahel korrektne, vahel mitte
                        "järeliide_eemaldatud:bool  // SÕNE on järelliitega sõna osa, vahel korrektne, vahel mitte
                    }
                ]
            }
        }
    }

    '''
    import argparse

    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-s', '--sorted', action="store_true", help='sorted JSON')
    argparser.add_argument('-r', '--reverse', action="store_true", help='reverse sort order')
    argparser.add_argument('-j', '--json', type=str, help='json input')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    argparser.add_argument('-c', '--csv', action="store_true", help='CSV-like output')
    args = argparser.parse_args()

    if args.json is not None:
        json_in = SONEDE_IDX().string2json(args.json)
        if "error" in json_in:
            json.dump(json_in, sys.stdout, indent=args.indent)
            sys.exit(1)
        idx = SONEDE_IDX().leia_soned_osasoned(json_in, args.sorted, args.reverse)
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
            json_in = SONEDE_IDX().string2json(line)
            if "error" in json_in:
                json.dump(json_in, sys.stdout, indent=args.indent)
                sys.exit(1)
            idx = SONEDE_IDX().leia_soned_osasoned(json_in, args.sorted, args.reverse)
            if args.csv is True:
                for sone in idx["index"]:
                    for docid in idx["index"][sone]:
                        for k in idx["index"][sone][docid]:
                            sys.stdout.write(f'{sone}\t{k["liitsõna_osa"]}\t{idx["sources"][docid]["content"][k["start"]:k["end"]]}\t{docid}\t{k["start"]}\t{k["end"]}\n')
            else:
                json.dump(idx, sys.stdout, indent=args.indent, ensure_ascii=False)
                sys.stdout.write('\n')


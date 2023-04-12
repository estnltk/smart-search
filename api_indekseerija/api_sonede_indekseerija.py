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
        """JSONit sisaldav string püütoni DICTiks

        Teeme mõningast veakontrolli 
        Args:
            str (str): sisend JSON stringina

        Returns:
            Dict: sisendstringist saadud püütoni DICT
        """
        self.json_io = {}
        try:
            self.json_io = json.loads(str)
            return self.json_io
        except:
            return {"error": "JSON parse error"}
        

    def morfi(self)->None:
        """_summary_

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
        # genereerime morfi päringu (üks sõne, tundmatute sõnade oletamisega
        self.json_io["params"] = {"vmetajson":["--stem", "--guess"]} 
        try:
            self.json_io=json.loads(requests.post(self.ANALYSER, json=self.json_io).text)
        except:
            raise Exception({"warning":'Probleemid morf analüüsi veebiteenusega'})
        soned = []                                      # selle massiivi abil hoiame meeles, millesed lemma kujud olema juba leidnud
        for token in self.json_io["annotations"]["tokens"]:  # tsükkel üle sõnede (ainult üks sõne meil antud juhul on)
            token["features"]["tokens"] = []     # siia massiivi korjame unikaalsed tüvi+lõpp stringid
            for mrf in token["features"]["mrf"]:            # tsükkel üle sama sõne alüüsivariantide (neid võib olla mitu)
                if self.ignore_pos.find(mrf["pos"]) != -1:      # selle sõnaliiiga tüvesid...
                    continue                                    # ...ignoreerime, neid ei indekseeri
                tkn = mrf["stem"]+mrf["ending"] if mrf["ending"] != '0' else mrf["stem"]
                if tkn not in token["features"]["tokens"]: # sõne morf analüüside hulgas võib sama kujuga tüvi erineda ainult käände/põõrde poolest
                    token["features"]["tokens"].append(tkn)    # lisame uue tüvi+lõpp stringi, sellist veel polnud
        return self.json_io
    
    def leia_soned_osasoned_1(self, json_in:Dict, sorted_by_token:bool, sortorder_reverse:bool) -> None:
        """_summary_

        Args:
            json_io (Dict): _description_
            sorted_by_token (bool): _description_
            sortorder_reverse (bool): _description_

        Raises:
            Exception: _description_

        Returns:
            Dict: _description_
        """
        try:                                                # sõnestame
            self.json_io=json.loads(requests.post(self.TOKENIZER, json=json_in).text)
        except:                                             # sõnestamine äpardus
            raise Exception({"warning":'Probleemid sõnestamise veebiteenusega'})

        idx_dct = {}
        self.morfi()                                        # leiame liitsõnapiirid ja sobiva sõnaliigiga tüvi+lõpud
        for token in self.json_io["annotations"]["tokens"]: # tsükkel üle sõnede
            if len(token["features"]["tokens"])==0:             # kui pole ühtegi meid huvitava sõnaliigiga...
                continue                                            # ...laseme üle
            for tkn in token["features"]["tokens"]:             # tsükkel üle leitud liitsõnapiiridega sõnede
                puhas_tkn = tkn.replace('_', '').replace('=', '')
                if puhas_tkn in idx_dct:                       # kui selline sõne juba oli...
                    idx_dct[puhas_tkn].append({"liitsõna_osa":False, "start": token["start"], "end":token["end"]})
                else:                                           # esimene selline...     
                    idx_dct[puhas_tkn] = [{"liitsõna_osa":False, "start": token["start"], "end":token["end"]}]
                osasonad = tkn.replace('=', '').split('_')  # tükeldame liitsõna piirilt
                if len(osasonad) <= 1:                      # kui pole liitsõna...
                    continue                                    # ...laseme üle
                fragmendid = []                             # siia hakkame korjame liitsõna tükikesi
                for idx, osasona in enumerate(osasonad):    # tsükkel ole liitsõna osasõnade
                    if idx == 0:                            # algab esimese osasõnaga
                        sona = osasonad[idx]
                        fragmendid.append(sona)                                                           
                        for idx2 in range(idx+1, len(osasonad)-1):
                            sona += osasonad[idx2]
                            fragmendid.append(sona)
                    elif idx == len(osasonad)-1:            # lõppeb viimase osasõnaga
                        fragmendid.append(osasona)
                    else:                                   # vahepealsed jupid (kui liitsõnas 3 või enam komponenti)
                        fragmendid.append(osasona)
                        sona = osasonad[idx]
                        for idx2 in range(idx+1, len(osasonad)):
                            sona += osasonad[idx2]
                            if idx2 < len(osasonad)-1:
                                fragmendid.append(sona)
                            else:
                                fragmendid.append(sona)
                for fragment in fragmendid:
                    if fragment in idx_dct:                # kui selline sõne juba oli...
                        idx_dct[fragment].append({"liitsõna_osa":True, "start": token["start"], "end":token["end"]})
                    else:                                   # esimene selline...     
                        idx_dct[fragment] = [{"liitsõna_osa":True, "start": token["start"], "end":token["end"]}] # ...lisame uue kirje 

        # järjestame vastavalt etteantud parameetritele
        if sorted_by_token is True:
            return OrderedDict(sorted(idx_dct.items(), reverse=sortorder_reverse, key=lambda t: t[0])) 
 
        return idx_dct

    def leia_soned_osasoned(self, json_io:List, sorted_by_token:bool, sortorder_reverse:bool) -> List:
        for doc in json_in:
            if "annotations" not in doc:
                doc["annotations"] = {}
            doc["annotations"]["index"] = self.leia_soned_osasoned_1(doc, sorted_by_token, sortorder_reverse)
        return json_io

    

if __name__ == '__main__':
    '''
    Ilma argumentideta loeb JSONit std-sisendist ja kirjutab tulemuse std-väljundisse
    Muidu JSON käsirealt lipu "--json=" tagant.
    [   {   "docid": str,   // dokumendi ID
            "content": str, // dokumendi tekst ("plain text", märgendus eraldi tõstetud)
            "annotations":
            {   "tags":     // tekstist väljatõstetud HTML/XML vms märgendid
                [   {   "start": int,   // alguspositsioon
                        "end", int,     // lõpupositsioon
                        "tag": str      // HTML/XML vms märgend
                    }
                ]
            }
        }
    ]

    Välja:
    {   "docid": str,   // dokumendi ID
        "content": str, // dokumendi tekst ("plain text", märgendus tõstetud "tags" alla)
        "annotations":
        {   "index":
            {   SÕNE: // string tekstist, esinemiste arv == "positions" massiivi pikkus
                {   "positions": 
                    [   {   "start": int,           // alguspostsioon jooksvas tekst
                            "end": int,             // lõpupostsioon jooksvas tekst  
                            "liitsõna_osa": bool    // SÕNE on liitsõna osa, vahel korrektne, vahel mitte
                        }
                    ]
                }
            }
            "tags":     // tekstist väljatõstetud HTML/XML vms märgendid
            [   {   "start": int,   // alguspositsioon
                    "end", int,     // lõpupositsioon
                    "tag": str      // HTML/XML vms märgend
                }
            ]   
        }
    }
    
    '''
    import argparse

    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-s', '--sorted_by_token', action="store_true", help='sorted by lemma')
    argparser.add_argument('-r', '--reverse', action="store_true", help='reverse sort order')
    argparser.add_argument('-j', '--json', type=str, help='json input')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    argparser.add_argument('-c', '--csv', action="store_true", help='CSV-like output')
    args = argparser.parse_args()

    json_io = {}
    if args.json is not None:
        json_in = SONEDE_IDX().string2json(args.json)
        if "error" in json_in:
            json.dump(json_in, sys.stdout, indent=args.indent)
            sys.exit(1)
        idx = SONEDE_IDX().leia_soned_osasoned(json_in, args.sorted_by_token, args.reverse)
        if args.csv is True:
            for doc in idx:
                for i in doc["annotations"]["index"]:
                    for t in doc["annotations"]["index"][i]:
                        sys.stdout.write(f'{i}\t{t["liitsõna_osa"]}\t{t["start"]}\t{t["end"]}\t{doc["docid"]}\n')
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
            idx = SONEDE_IDX().leia_soned_osasoned(json_in, args.sorted_by_token, args.reverse)
            if args.csv is True:
                for doc in idx:
                    for i in doc["annotations"]["index"]:
                        for t in doc["annotations"]["index"][i]:
                            sys.stdout.write(f'{i}\t{t["liitsõna_osa"]}\t{t["start"]}\t{t["end"]}\t{doc["docid"]}\n')
            else:
                json.dump(idx, sys.stdout, indent=args.indent, ensure_ascii=False)
                sys.stdout.write('\n')


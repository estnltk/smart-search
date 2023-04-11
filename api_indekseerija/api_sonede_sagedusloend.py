#!/usr/bin/python3

import os
import sys
import json
import requests
from typing import Dict, List
from collections import OrderedDict

'''
See programm kasutab lemmade leidmiseks ja sõnestamiseks Tartu Ülikooli pilves olevaid
sõnestamise ja morf analüüsi konteinereid.
Programmi saab kiiremaks kui vastavad konteinerid töötavad "lähemal".
'''

class IDX_STAT_LEMMAS:
    VERSION="2023.04.06"
    TOKENIZER='https://smart-search.tartunlp.ai/api/tokenizer/process'
    LEMMATIZER='https://smart-search.tartunlp.ai/api/lemmatizer/process'
    ANALYSER='https://smart-search.tartunlp.ai/api/analyser/process'

    ignore_pos = "PZJ" # ignoreerime lemmasid, mille sõnaliik on: Z=kirjavahemärk, J=sidesõna, P=asesõna

    def string2json(self, str:str) -> Dict:
        """JSONit sisaldav string püütoni DICTiks

        Teeme mõningast veakontrolli 
        Args:
            str (str): sisend JSON stringina

        Returns:
            Dict: sisendstringist saadud püütoni DICT
        """
        json_io = {}
        try:
            json_io = json.loads(str)
            if "content" not in json_io:
                return {'error': 'Missing "content" in JSON'} 
            return json_io
        except:
            return {"error": "JSON parse error"}
        

    def morfi(self, token:str)->List:
        """Morfime sisendstringi ja korjame välja unikaalsete tüvi+lõpp stringide massiivi

        Args:
            token (str): morfitav sõne

        Raises:
            Exception: Exception('Probleemid morf analüüsi veebiteenusega')

        Returns:
            List: unikaalsete lemmade massiivi
        """
        # genereerime morfi päringu (üks sõne, tundmatute sõnade oletamisega
        json_io = {"params":{"vmetajson":["--stem", "--guess"]}, "annotations":{"tokens":[{"features":{"token": token}}]}} 
        try:
            json_io=json.loads(requests.post(self.ANALYSER, json=json_io).text)
        except:
            raise Exception({"warning":'Probleemid morf analüüsi veebiteenusega'})
        soned = []                                     # selle massiivi abil hoiame meeles, millesed lemma kujud olema juba leidnud
        for token in json_io["annotations"]["tokens"]:  # tsükkel üle sõnede (ainult üks sõne meil antud juhul on)
            for mrf in token["features"]["mrf"]:            # tsükkel üle sama sõne alüüsivariantide (neid võib olla mitu)
                if self.ignore_pos.find(mrf["pos"]) != -1:      # selle sõnaliiiga lemmasid...
                    continue                                    # ...ignoreerime, neid ei indekseeri
                if mrf["ending"] != '0':
                    mrf["stem"] += mrf["ending"]
                if mrf["stem"] not in soned: # sõne morf analüüside hulgas võib sama kujuga tüvi erineda ainult käände/põõrde poolest
                    soned.append(mrf["stem"])    # lisame uue tüvi+lõpp stringi, sellist veel polnud
        return soned                                   # erinevate tüvi+lõpp stringide loend

    def leia_soned_osasoned(self, json_io:List, sorted_by_token:bool, sortorder_reverse:bool) -> List:
        try:
            json_io=json.loads(requests.post(self.TOKENIZER, json=json_io).text)
        except:
            return {"error": "tokenization failed"}

        stat_dct = {}
        stat_list = []
        for token in json_io["annotations"]["tokens"]:      # tsükkel üle sõnede
            soned = self.morfi(token["features"]["token"])  # leiame algses sõnes liitsõnapiirid
            if len(soned) == 0:                             # kui pole meid huvitava sõnaligiga...
                continue                                        # ...laseme üle
            if token["features"]["token"] in stat_dct:      # kui selline sõne juba oli...
                if stat_dct[token["features"]["token"]]["liitsõna_osa"] is False: # ...ja oli terviksõne, suurendame loendajat
                    stat_dct[token["features"]["token"]]["count"] += 1
            else:                                           # esimene selline...     
                stat_dct[token["features"]["token"]] = {"count": 1, "liitsõna_osa":False} # ...lisame uue kirje
            for sone in soned:                              # lisame liitsõna osasõnad, kui neid oli
                osasonad = sone.replace('=', '').split('_')
                if len(osasonad) <= 1:                      # kui pole liitsõna...
                    continue                                    # ...laseme üle
                fragmendid = []                             # siia hakkame korjame liitsõna tükikesi
                for idx, osasona in enumerate(osasonad):    # tsükkel ole liitsõna osasõnade
                    if idx == 0:                            # algab esimese osasõnaga
                        sona = osasonad[idx]
                        fragmendid.append(sona+'_')                                                           
                        for idx2 in range(idx+1, len(osasonad)-1):
                            sona += osasonad[idx2]
                            fragmendid.append(sona+'_')
                    elif idx == len(osasonad)-1:            # lõppeb viimase osasõnaga
                        fragmendid.append('_'+osasona)
                    else:                                   # vahepealsed jupid (kui liitsõnas 3 või enam komponenti)
                        fragmendid.append('_'+osasona+'_')
                        sona = osasonad[idx]
                        for idx2 in range(idx+1, len(osasonad)):
                            sona += osasonad[idx2]
                            if idx2 < len(osasonad)-1:
                                fragmendid.append('_'+sona+'_')
                            else:
                                fragmendid.append('_'+sona)
                for fragment in fragmendid:
                    if fragment in stat_dct:                # kui selline sõne juba oli...
                        if stat_dct[fragment]["liitsõna_osa"] is True: # ...ja oli liitsõna osa, suurendame loendajat
                            stat_dct[fragment]["count"] += 1
                    else:                                   # esimene selline...     
                        stat_dct[fragment] = {"count": 1, "liitsõna_osa":True} # ...lisame uue kirje 

        # järjestame vastavalt etteantud parameetritele
        if sorted_by_token is True:
            ordered_stat_dct = OrderedDict(sorted(stat_dct.items(), reverse=sortorder_reverse, key=lambda t: t[0])) 
        else:       
            ordered_stat_dct = OrderedDict(sorted(stat_dct.items(), reverse=sortorder_reverse, key=lambda t: t[1]['count']))

        return ordered_stat_dct

    def sort_by_lemma(self, i):
        return i[0]
    
    def sort_by_count(self, i):
        return i[1]

if __name__ == '__main__':
    '''
    Ilma argumentideta loeb JSONit std-sisendist ja kirjutab tulemuse std-väljundisse
    Muidu JSON käsirealt lipu "--json=" tagant.
    [{"docid": str, "content": str}]
    
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
        json_io = IDX_STAT_LEMMAS().string2json(args.json)
        if "error" in json_io:
            json.dump(json_io, sys.stdout, indent=args.indent)
            sys.exit(1)
        ordered_stat_dct = IDX_STAT_LEMMAS().leia_soned_osasoned(json_io, args.sorted_by_token, args.reverse)
        if args.csv is True:
            for token in ordered_stat_dct:
                sys.stdout.write(f'{token}\t{ordered_stat_dct[token]["count"]}\t{ordered_stat_dct[token]["liitsõna_osa"]}\n')
        else:
            json.dump(ordered_stat_dct, sys.stdout, indent=args.indent, ensure_ascii=False)
            sys.stdout.write('\n')
    else:
        for line in sys.stdin:
            line = line.strip()
            if len(line) <= 0:
                continue
            json_io = IDX_STAT_LEMMAS().string2json(line)
            if "error" in json_io:
                json.dump(json_io, sys.stdout, indent=args.indent)
                sys.exit(1)
            ordered_stat_dct = IDX_STAT_LEMMAS().leia_soned_osasoned(json_io, args.sorted_by_token, args.reverse)
            if args.csv is True:
                for token in ordered_stat_dct:
                    sys.stdout.write(f'{token}\t{ordered_stat_dct[token]["count"]}\t{ordered_stat_dct[token]["liitsõna_osa"]}\n')
            else:
                json.dump(ordered_stat_dct, sys.stdout, indent=args.indent, ensure_ascii=False)           
                sys.stdout.write('\n')


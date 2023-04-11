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
Programmi saab kiiremaks kui vastavad konteinerid töötavad "lähemal"
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
        """Morfime sisendstringi ja korjame välja unikaalsete lemmade massiivi

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
        lemmad = []                                     # selle massiivi abil hoiame meeles, millesed lemma kujud olema juba leidnud
        for token in json_io["annotations"]["tokens"]:  # tsükkel üle sõnede (ainult üks sõne meil antud juhul on)
            for mrf in token["features"]["mrf"]:            # tsükkel üle sama sõne alüüsivariantide (neid võib olla mitu)
                if self.ignore_pos.find(mrf["pos"]) != -1:      # selle sõnaliiiga lemmasid...
                    continue                                    # ...ignoreerime, neid ei indekseeri
                if mrf["lemma_ma"] not in lemmad:                   # sõne morf analüüside hulgas võib sama kujuga lemma erineda ainult käände/põõrde poolest
                    lemmad.append(mrf["lemma_ma"])                      # lisame uue lemma, sellist veel polnud
        return lemmad                                   # erinevate lemmade loend

    def leia_soned_osasoned(self, json_io:List, sorted_by_lemma:bool, sortorder_reverse:bool) -> List:
        try:
            json_io=json.loads(requests.post(self.TOKENIZER, json=json_io).text)
        except:
            return {"error": "tokenization failed"}
        json_io["params"]={"vmetajson":["--guess"]} # morfime tundmatute oletamisega
        #json_io["params"]={"vmetajson":["--guess", "--stem"]} # morfime tundmatute
        try:
            json_io=json.loads(requests.post(self.ANALYSER, json=json_io).text)
        except:
            return {"error": "lemmatizer failed"}

        stat_dct = {}
        stat_list = []
        for token in json_io["annotations"]["tokens"]:  # tsükkel üle sõnede
            if token["features"]["token"] in stat_dct:      # selline terviksõne juba oli, suurendame loendajat
                stat_dct[token["features"]["token"]]["count"] += 1
            else:                                           # esimene selline terviksõne
                stat_dct[token["features"]["token"]] = {"count": 1, "liitsõna_osa":False, "liide_eemaldatud": False}

            # nüüd vaatame liitsõna osasõnasid ja järelliiteid
            


        # teeme sõnastikust listi...
        for d in stat_dct:
            stat_list.append([d, stat_dct[d]["count"], stat_dct[d]["liitsõna_osa"],stat_dct[d]["liide_eemaldatud"]])
        # ... ja järjestame listi etteantud parameetritete järgi
        if sorted_by_lemma is True:
            stat_list.sort(key=self.sort_by_lemma,reverse=sortorder_reverse)
        else:
            stat_list.sort(key=self.sort_by_count,reverse=sortorder_reverse)
        return stat_list

        #if sorted_by_lemma is True:                       # järjestame lemma järgi kasvavalt/kahanevalt
        #    ordered_stat_dct = OrderedDict(sorted(stat_dct.items(), reverse=sortorder_reverse, key=lambda t: t[0]))
        #else:                                           # järjestame sageduse järgi kasvavalt, kahanevalt
        #    ordered_stat_dct = OrderedDict(sorted(stat_dct.items(), reverse=sortorder_reverse, key=lambda t: t[1]))
        #return ordered_stat_dct

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
    argparser.add_argument('-s', '--sorted_by_lemma', action="store_true", help='sorted by lemma')
    argparser.add_argument('-r', '--reverse', action="store_true", help='reverse sort order')
    argparser.add_argument('-j', '--json', type=str, help='json input')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    argparser.add_argument('-c', '--cvs', action="store_true", help='CVS-like output')
    args = argparser.parse_args()

    json_io = {}
    if args.json is not None:
        json_io = IDX_STAT_LEMMAS().string2json(args.json)
        if "error" in json_io:
            json.dump(json_io, sys.stdout, indent=args.indent)
            sys.exit(1)
        stat_list = IDX_STAT_LEMMAS().leia_soned_osasoned(json_io, args.sorted_by_lemma, args.reverse)
        if args.cvs is True:
            for i in stat_list:
                sys.stdout.write(f'{i[0]}\t{i[1]}\n')
        else:
            json.dump(stat_list, sys.stdout, indent=args.indent, ensure_ascii=False)
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
            stat_list = IDX_STAT_LEMMAS().leia_soned_osasoned(json_io, args.sorted_by_lemma, args.reverse)
            if args.cvs is True:
                for i in stat_list:
                    sys.stdout.write(f'{i[0]}\t{i[1]}\n')
            else:
                json.dump(stat_list, sys.stdout, indent=args.indent, ensure_ascii=False)           
                sys.stdout.write('\n')


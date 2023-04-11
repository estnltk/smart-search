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

class IDX_STAT:
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
        json_io = {"params":{"vmetajson":["--guess"]}, "annotations":{"tokens":[{"features":{"token": token}}]}} 
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

    def fragmendi_lemmatiseerimine_ja_lisamine(self, fragment:str,  fragments: List)->None:
        """Lemmade leidmine ja lisamine

        Args:
            fragment (str): sõne, võimalikud liitsõnapiiride eraldaja ('_') ja järelliite eraldaja ('=') on sõnes sees 
            fragments (List): Sellesse massiivi lisame saadud info.

        Returns:
            _type_: _description_
        """
        puhas_fragment = fragment.replace('_', '').replace('=', '') # eemadame liitsõna ja järelliite piirid          
        lemmad = self.morfi(puhas_fragment)                         # leiame liitsõna osasõna lemmad, võinalikku järelliidet ei eemalda
        for lemma in lemmad:                                        # lisame leitud lemmad 
            fragments.append({"lemma":lemma, "liitsõna_osa":True, "liide_eemaldatud":False})
        liite_alguspos = fragment.find('=')                         # otsime järelliite eraldajat
        if liite_alguspos <= 1:
            return                                                      # polnud järelliidet, kõik tehtud
        puhas_fragment = fragment[:liite_alguspos].replace('_', '') # eemaldame järelliite ja liitsõnapiirid
        lemmad = self.morfi(puhas_fragment)                         # saadud sõne morfime
        for lemma in lemmad:                                        # lisame leitud lemmad 
                fragments.append({"lemma":lemma, "liitsõna_osa":True, "liide_eemaldatud":True})


    def leia_muud_tykiksesd(self, lemma:str, inf:Dict) -> None:
        """Lisame liitsõnade ja järelliitega sõnadega seotud info

        Args:
            lemma (str): _description_
            inf (Dict): _description_
        """
        '''
        "sublemmas": 
        [
            {   "lemma": str,               # lemma
                "liitsõna_osa": bool,       # liitsõna osa (raudteejaamalik -> raud, tee, jaamalik, raudtee, teejaam)
                "liide_eemaldatud": bool    # järelliide eemaldatud (raudteejaamalik ->raudteejaam, jaamalik -> jaam)
            }
        ]
        '''      
        if lemma[0] == '_' or lemma[len(lemma)-1] == '_':
            return; # mingi sodi, sellega ei tegele
        osasonad = lemma.split('_')                                                         # tükeldame liitsõna piiri järgi
        if len(osasonad) > 1:                                                               # oli liitsõna, tegeleme sellega
            for idx, osasona in enumerate(osasonad):                                        # tsükkel ole liitsõna osasõnade
                if idx == 0:                                                                    # algab esimese osasõnaga
                    self.fragmendi_lemmatiseerimine_ja_lisamine(osasona, inf["fragments"])      # esimest sisaldavad variandid
                    sona = osasonad[idx]                                                            
                    for idx2 in range(idx+1, len(osasonad)-1):
                        sona += '_' + osasonad[idx2]
                        self.fragmendi_lemmatiseerimine_ja_lisamine(sona, inf["fragments"])
                elif idx == len(osasonad)-1: # lõppeb viimase osasõnaga                         # vahepealseid sisealdavad variandid
                    self.fragmendi_lemmatiseerimine_ja_lisamine(osasona, inf["fragments"])
                else:   # vahepealsed jupid (kui liitsõnas 3 või enam komponenti)               # viimast sisaldavad variandid
                    self.fragmendi_lemmatiseerimine_ja_lisamine(osasona, inf["fragments"])
                    sona = osasonad[idx]
                    for idx2 in range(idx+1, len(osasonad)):
                        sona += osasonad[idx2]
                        if idx2 < len(osasonad)-1:
                           sona += '_'
                        self.fragmendi_lemmatiseerimine_ja_lisamine(sona, inf["fragments"])

    def leia_koik_lemmad(self, json_io:List) -> List:
        """




        Args:
            json_io (Dict): 

        SisendJSON:

        [{"docid": str, "content": str}]

        Returns:
            List:

        

        """
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

        '''

        '''
        stat_dct = {}
        for token in json_io["annotations"]["tokens"]:  # tsükkel üle sõnede
            lisatud_lemmavariandid = []                     # selle massivi abil hoimae meeles, millesed lemma kujud olema juba lisanud
            for mrf in token["features"]["mrf"]:            # tsükkel üle sama sõne alüüsivariantide
                if self.ignore_pos.find(mrf["pos"]) != -1:      # selle sõnaliiiga lemmasid...
                    continue                                    # ...ignoreerime, neid ei indekseeri
                if mrf["lemma_ma"] in lisatud_lemmavariandid:   # sõne morf analüüside hulgas võib sama kujuga lemma erineda ainult käände/põõrde poolest
                    continue                                    # ei lisa sama kujuga lemmat mitu korda
                lisatud_lemmavariandid.append(mrf["lemma_ma"])  # jätame meelde, et sellise lemma lisame
                if mrf["lemma_ma"] not in stat_dct:             # pole tekstist sellist lemmat varem saanud
                    stat_dct[mrf["lemma_ma"]] = {               # lisame lemmaga seotud info
                        "cnt":1, 
                        "tokens": [{"token": token["features"]["token"], "start": token["start"], "end":token["end"]}],
                        "fragments": []}
                    self.leia_muud_tykiksesd(mrf["lemma_ma"], stat_dct[mrf["lemma_ma"]])
                else:                                           # sellist lemmat oleme juba näinud...
                    stat_dct[mrf["lemma_ma"]]["cnt"] += 1       # suurendame loendajat ja jätame meelde, kus kohas ta tekstis esines
                    stat_dct[mrf["lemma_ma"]]["tokens"].append({"token": token["features"]["token"], "start": token["start"], "end":token["end"]})



                liite_alguspos = mrf["lemma_ma"].find('=')      # otsime järelliite eraldajat
                if liite_alguspos > 1:                          # oli järelliitega
                    liitsona_osa = True if mrf["lemma_ma"].find('_') > 1 else False
                    puhas_fragment = mrf["lemma_ma"][:liite_alguspos].replace('_', '') # eemaldame järelliite ja liitsõnapiirid
                    lemmad = self.morfi(puhas_fragment)                         # saadud sõne morfime
                    for lemma in lemmad:                                        # lisame leitud lemmad 
                        stat_dct[mrf["lemma_ma"]]["fragments"].append({"lemma":lemma, "liitsõna_osa":False, "liide_eemaldatud":True})
        #if sorted_by_key is True:
        #    ordered_stat = OrderedDict(sorted(stat.items(), reverse=sortorder_reverse, key=lambda t: t[0]))
        #else:
        #    ordered_stat = OrderedDict(sorted(stat.items(), reverse=sortorder_reverse, key=lambda t: t[1]))
        return stat_dct

if __name__ == '__main__':
    '''
    Ilma argumentideta loeb JSONit std-sisendist ja kirjutab tulemuse std-väljundisse
    Muidu JSON käsirealt lipu "--json=" tagant.
    [{"docid": str, "content": str}]
    
    '''
    import argparse

    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--lemmastat', action="store_true", help='use debug mode')
    #argparser.add_argument('-s', '--sorted_by_key', action="store_true", help='sorted by key')
    #argparser.add_argument('-r', '--reverse', action="store_true", help='reverse sort order')
    argparser.add_argument('-j', '--json', type=str, help='json input')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    args = argparser.parse_args()
    json_io = {}
    idx_stat = IDX_STAT()
    if args.json is not None:
        json_io = idx_stat.string2json(args.json)
        if "error" in json_io:
            json.dump(json_io, sys.stdout, indent=args.indent)
            sys.exit(1)
        if args.lemmastat is True:
            json.dump(IDX_STAT().leia_koik_lemmad(json_io), sys.stdout, indent=args.indent, ensure_ascii=False)
    else:
        for line in sys.stdin:
            line = line.strip()
            if len(line) <= 0:
                continue
            json_io = idx_stat.string2json(line)
            if "error" in json_io:
                json.dump(json_io, sys.stdout, indent=args.indent)
                sys.exit(1)
            if args.lemmastat is True:
                json.dump(IDX_STAT().leia_koik_lemmad(json_io), sys.stdout, indent=args.indent, ensure_ascii=False)           
                sys.stdout.write('\n')


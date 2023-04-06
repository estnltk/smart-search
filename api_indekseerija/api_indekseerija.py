#!/usr/bin/python3

import os
import sys
import json
import requests

from collections import OrderedDict

VERSION="2023.04.06"
TOKENIZER='https://smart-search.tartunlp.ai/api/tokenizer/process'
LEMMATIZER='https://smart-search.tartunlp.ai/api/lemmatizer/process'
ANALYSER='https://smart-search.tartunlp.ai/api/analyser/process'

ignore_pos = "PZJ" # ignoreerime lemmasid, mille sõnaliik on: Z=kirjavahemärk, J=sidesõna, P=asesõna

class IDX_STAT:
    def string2json(self, str:str):
        json_io = {}
        try:
            json_io = json.loads(str)
            if "content" not in json_io:
                return {'error': 'Missing "content" in JSON'} 
            return json_io
        except:
            return {"error": "JSON parse error"}
        
    def lemmade_sagedusloend(self, json_io, sortorder_reverse, sorted_by_key):
        try:
            json_io=json.loads(requests.post(TOKENIZER, json=json_io).text)
        except:
            return {"error": "tokenization failed"}
        
        try:
            json_io=json.loads(requests.post(LEMMATIZER, json=json_io).text)
        except:
            return {"error": "lemmatizer failed"}

        stat = {}
        for token in json_io["annotations"]["tokens"]:
            for mrf in token["features"]["mrf"]:
                if ignore_pos.find(mrf["pos"]) != -1:
                    continue # neid sõnaliike ei indekseeri
                if mrf["lemma_ma"] not in stat:
                    stat[mrf["lemma_ma"]] = 1
                else:
                    stat[mrf["lemma_ma"]] += 1

        if sorted_by_key is True:
            ordered_stat = OrderedDict(sorted(stat.items(), reverse=sortorder_reverse, key=lambda t: t[0]))
        else:
            ordered_stat = OrderedDict(sorted(stat.items(), reverse=sortorder_reverse, key=lambda t: t[1]))
        return ordered_stat

if __name__ == '__main__':
    '''
    Ilma argumentideta loeb JSONit std-sisendist ja kirjutab tulemuse std-väljundisse
    Muidu JSON käsirealt lipu "--json=" tagant.
    '''
    import argparse

    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--lemmastat', action="store_true", help='use debug mode')
    argparser.add_argument('-s', '--sorted_by_key', action="store_true", help='sorted by key')
    argparser.add_argument('-r', '--reverse', action="store_true", help='reverse sort order')
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
            json.dump(IDX_STAT().lemmade_sagedusloend(json_io, args.reverse, args.sorted_by_key), sys.stdout, indent=args.indent)
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
                json.dump(IDX_STAT().lemmade_sagedusloend(json_io), sys.stdout, indent=args.indent)           

            sys.stdout.write('\n')


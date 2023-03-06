#!/usr/bin/python3

import os
import sys
import json
import requests
import re
from typing import Dict #, List

# docker run -p 6666:7000 tilluteenused/vabamorf_synth:2022.08.15
def synteesi(lemma:str):
    json_query=json.loads(f'{{"type": "text","content":"{lemma}"}}')
    json_response=json.loads(requests.post(f'http://localhost:6666/process', json=json_query).text)
    return json_response

def tee_mis_vaja(index:Dict) -> Dict:

    '''
    Indeksfaili formaat
    {   "sources": { DOCID: { "filename": str, "heading": str, "content": str } }
        "annotations": { "lemmas": { "LEMMA": { "DOCID": { "STARTPOS":{"endpos":int, "fragment":bool}} } } } }
    }
    '''

    geneout = {}
    for lemma_str in index["annotations"]["lemmas"]:
        #print(lemma_str)
        clean_lemma = re.sub('[ _=+"]', '', lemma_str)
        syn_res = synteesi(clean_lemma)
        for text in syn_res["response"]["texts"]:
            for generated_form in text["features"]["generated_forms"]:
                clean_token = re.sub('[ _=+]', '', generated_form["token"])
                rec = geneout.get(clean_token)
                if rec is None:
                    geneout[clean_token] = [lemma_str]
                else:
                    if lemma_str not in rec:
                        rec.append(lemma_str) 
                    else:
                        pass
                pass
    return geneout



if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-i', '--indexin', type=str, help='olemasolev indeks')
    args = argparser.parse_args()

    if args.indexin is not None:
        with open(args.indexin, 'r') as file_index_in:
            index = json.loads(file_index_in.read())
            json.dump(tee_mis_vaja(index), sys.stdout, ensure_ascii=False)
    
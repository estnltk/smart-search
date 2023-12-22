#!/usr/bin/python3

import os
import sys
import json
import requests
import re
from typing import Dict #, List

# docker run -p 6666:7000 tilluteenused/vabamorf_synth:2022.08.15

ignore_pos = "PZJ" # ignoreerime lemmasid, mille sõnaliik on: Z=kirjavahemärk, J=sidesõna, P=asesõna

class WORDFORM2LEMMA:
    wordform2lemma = {}

    def synteesi(self, lemma:str):
        json_query=json.loads(f'{{"type": "text","content":"{lemma}"}}')
        json_response=json.loads(requests.post(f'http://localhost:6666/process', json=json_query).text)
        return json_response

    def gene_ja_lisa(self, algne_lemma, genetav_lemma:str, whole_fragment:str) -> None:
        syn_res = self.synteesi(genetav_lemma)
        for text in syn_res["response"]["texts"]:
            for genetud_vorm in text["features"]["generated_forms"]:
                if ignore_pos.find(genetud_vorm["pos"]) != -1:
                    continue # neid sõnaliike ei indekseeri
                puhas_genetud_sonavorm = re.sub('[ _=+]', '', genetud_vorm["token"])
                rec = self.wordform2lemma.get(puhas_genetud_sonavorm)
                if rec is None:
                    self.wordform2lemma[puhas_genetud_sonavorm] = {whole_fragment: [algne_lemma]}
                else:
                    if whole_fragment not in rec:
                        rec[whole_fragment] = []
                    if genetav_lemma not in rec[whole_fragment]:
                        rec[whole_fragment].append(algne_lemma) 
                    else:
                        pass # juba oli olemas
                pass

    def __init__(self, index:Dict):
        '''
        Indeksfaili formaat
        {   "sources": { DOCID: { "filename": str, "heading": str, "content": str } }
            "annotations": { "lemmas": { "LEMMA": { "DOCID": { "STARTPOS":{"endpos":int, "fragment":bool}} } } } }
        }

        genetud asi

        {   "GENETUD_SÕNAVORM": 
            {   "whole": ["ALGNE_LEMMA"],   /* GENETUD_SÕNAVORM on genetud ALGNE_LEMMAst (raudteest - raudtee) */
                "fragment": ["ALGNE_LEMMA"] /* GENETUD_SÕNAVORM on genetud ALGNE_LEMMA osasõnast (rauast - raudtee, teest - raudtee) */
            }
        }

        '''

        for lemma_str in index["annotations"]["lemmas"]:
            #print("DB:", lemma_str)

            # vaatame sõne (sh liitsõnu) tervikuna
            clean_lemma = re.sub('[ _=+"]', '', lemma_str)
            self.gene_ja_lisa(clean_lemma, clean_lemma, "whole")
            
            # nüüd vaatame, kas liitsaõna ja geneme liitsõna osasõnadest kõik vormid
            fragments = re.sub('[ =+"]', '', lemma_str).split('_') # tükeldame sõna osasõnade piirilt
            if len(fragments) > 1: # oli liitsõna
                for fragment in fragments: # geneme osasõna kõik vormid
                    #print("DB:", lemma_str, fragment)
                    self.gene_ja_lisa(clean_lemma, fragment, "fragment")


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-i', '--indexin', type=str, help='olemasolev indeks')
    argparser.add_argument('-o', '--geneout', type=str, required=True, help='genereeritud vorm->lemmaks')

    args = argparser.parse_args()


    if args.indexin is not None:
        with open(args.indexin, 'r') as file_index_in:
            index = json.loads(file_index_in.read())
            wordform2lemma = WORDFORM2LEMMA(index)
            with open(args.geneout, 'w') as gene_out:
                json.dump(wordform2lemma.wordform2lemma, gene_out, ensure_ascii=False)
    
    lemmade_arv_indeksis = len(index["annotations"]["lemmas"])
    print('lemmade_arv_indeksis=', lemmade_arv_indeksis)

    liitsonalemmade_arv_indeksis = 0
    for lemma_str in index["annotations"]["lemmas"]:
        if lemma_str.find('_') > 0:
            liitsonalemmade_arv_indeksis += 1
    print('liitsõnalemmade_arv_indeksis=', liitsonalemmade_arv_indeksis)

    genetud_sonavormide_arv_koos_liitsonadega = len(wordform2lemma.wordform2lemma)
    print('genetud_sonavormide_arv_koos_liitsonadega=', genetud_sonavormide_arv_koos_liitsonadega)

    genetud_sonavormide_arv_ilma_liitsonadega = 0
    for genetud_sonavorm in wordform2lemma.wordform2lemma:
        if "whole" in wordform2lemma.wordform2lemma[genetud_sonavorm]:
            genetud_sonavormide_arv_ilma_liitsonadega += 1    
    print('genetud_sonavormide_arv_ilma_liitsonadega=', genetud_sonavormide_arv_ilma_liitsonadega)

    
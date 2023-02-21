#!/usr/bin/python3

import os
import sys
import json
import requests
from typing import Dict #, List

ignore_pos = "ZJ" # Z=kirjavahemärk, J=sidesõna

'''
Kasutusnäide
* installi
  * python
* Lase pythoni programmil oma tekst morfida (väljundfaili nimi saadakse sisendfaili nimes laiendi asendamisega (.lemmas))
  > ./sonesta-lausesta.py --indexin=ALGNEINDEKSFAIL --indexout=TÄIENDATUDINDEKSFAIL INDEKSEERITAVFAIL.tokens [INDEKSEERITAVFAIL.tokens...]
'''


def lisa_indeksisse(index:Dict, sisend:Dict)->None:
    """_summary_

    Args:
        index (Dict): täiendatav indeksfail
        sisend (Dict): morfi väljund, need lemmad lisame indeksisse
    """

    sisendjson = json.loads(sisend)
    if sisendjson["docid"] in index["sources"]:
        sys.stderr(f'DocID {sisendjson["docid"]} on juba indeksis olemas\n')
        sys.exit(1)
    index["sources"][sisendjson["docid"]] = {"filename":sisendjson["filename"],"heading": sisendjson["heading"], "content": sisendjson["content"]}
    for token in sisendjson["annotations"]["tokens"]:
        if "mrf" not in token["features"]:
            continue # misiganes põhjusel, seda ei suutnud isegi oletamisega morfida 
        for mrf in token["features"]["mrf"]:
            if ignore_pos.find(mrf["pos"]) != -1:
                continue # neid sõnaliike ei indekseeri

            if mrf["lemma_ma"] not in index["annotations"]["lemmas"]: # sellist lemmat kohtame üldse esimest korda
                index["annotations"]["lemmas"][mrf["lemma_ma"]] = {sisendjson["docid"]:{token["start"]:token["end"]}}
            elif sisendjson["docid"] not in index["annotations"]["lemmas"][mrf["lemma_ma"]]: # sellist lemmat oleme yteistes dokumentides kohanud
                index["annotations"]["lemmas"][mrf["lemma_ma"]][sisendjson["docid"]] = {token["start"]:token["end"]}
            elif token["start"] not in index["annotations"]["lemmas"][mrf["lemma_ma"]][sisendjson["docid"]]: # sellist lemmat oleme selles dokumendis kohanud, aga teise koha peal
                index["annotations"]["lemmas"][mrf["lemma_ma"]][sisendjson["docid"]][token["start"]] = token["end"]


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-i', '--indexin', type=str, help='olemasolev indeks')
    argparser.add_argument('-o', '--indexout', type=str, required=True, help='täiendatud indeks')
    argparser.add_argument('FILES', nargs='*', help='need lisame indeksisse')                       
    args = argparser.parse_args()

    # index["sources"][docid] = {"filename":str, "heading":str} # igal dokumendil peab olema unikaalne docid
    # index["lemmas"][lemma_ma] = {"lemma_ma":str, [{"source": idx, ["start":int, "end":int]}]
    index = {"annotations":{"lemmas":{}}, "sources":{}} # sources = [{"filename": str, "heading":str}]
    if args.indexin is not None:
        with open(args.indexin, 'r') as file_index_in:
            index = json.loads(file_index_in.read())
            sys.stdout.write(f'indeksfail: {args.indexin}\n')

    for filename_in in args.FILES:
      with open(filename_in, 'r') as file_in:
        sys.stdout.write(f'+ {filename_in}\n')
        sisend = file_in.read()
        lisa_indeksisse(index, sisend)

    sys.stdout.write(f'Uuendatud indeksfaili {args.indexout} salvestamine...')
    with open(args.indexout, 'w') as file_index_out:
        file_index_out.write(json.dumps(index))
    sys.stdout.write('ok\n')

    
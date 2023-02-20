#!/usr/bin/python3

import os
import sys
import json
import requests
from typing import Dict #, List

'''
Kasutusnäide
* installi
  * python
* Lase pythoni programmil oma tekst morfida (väljundfaili nimi saadakse sisendfaili nimes laiendi asendamisega (.lemmas))
  > ./sonesta-lausesta.py --indexin=ALGNEINDEKSFAIL --indexout=TÄIENDATUDINDEKSFAIL INDEKSEERITAVFAIL.tokens [INDEKSEERITAVFAIL.tokens...]
'''


def lisa_indeksisse(index:Dict, sisend:str)->None:
    """Lemmade indeksi kontrueerimine

    Args:
        text (str): Morfitud tekst json kujul

    Returns:
        lemmade indeks json-kujul
    """

    # index["sources"][docid] = {"filename":str, "heading":str}
    sisendjson = json.loads(sisend)
    if sisendjson["docid"] in index["sources"]:
        sys.stderr(f'DocID {sisendjson["docid"]} on juba indeksis olemas\n')
        sys.exit(1)
    index["sources"][sisendjson["docid"]] = {"filename":sisendjson["filename"],"heading": sisendjson["heading"]}
    for token in sisendjson["annotations"]["tokens"]:
        for mrf in token["features"]["mrf"]:
            print(mrf["lemma"])
    #        if mrf["lemma"] not in index["lemmas"]:
    #            index["lemmas"].append({"lemma": mrf["lemma"], "source_idx": source_idx, {"positions":[{"start": , "end"}]}}})

    return None


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-i', '--indexin', type=str, help='olemasolev indeks')
    argparser.add_argument('-o', '--indexout', type=str, required=True, help='täiendatud indeks')
    argparser.add_argument('FILES', nargs='*', help='need lisame indeksisse')                       
    args = argparser.parse_args()

    # index["sources"][docid] = {"filename":str, "heading":str} # igal dokumendil peab olema unikaalne docid
    # index["lemmas"][lemma] = {"lemma":str, [{"source": idx, ["start":int, "end":int]}]
    index = {"annotations":{}, "sources":{}} # sources = [{"filename": str, "heading":str}]
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

    
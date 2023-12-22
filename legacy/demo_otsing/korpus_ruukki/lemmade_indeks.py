#!/usr/bin/python3

import os
import sys
import json
import requests
from typing import Dict #, List

ignore_pos = "PZJ" # ignoreerime lemmasid, mille sõnaliik on: Z=kirjavahemärk, J=sidesõna, P=asesõna

'''
Kasutusnäide
* installi
  * python
* Lase pythoni programmil oma tekst morfida (väljundfaili nimi saadakse sisendfaili nimes laiendi asendamisega (.lemmas))
  > ./lemmade_indeks.py --indexin=ALGNEINDEKSFAIL --indexout=TÄIENDATUDINDEKSFAIL INDEKSEERITAVFAIL.lemmas [INDEKSEERITAVFAIL.lemmas...]
 
Indeksfaili formaat
{   "sources": { DOCID: { "filename": str, "heading": str, "content": str } }
    "annotations": { "lemmas": { "LEMMA": { "DOCID": { "STARTPOS":{"endpos":int, "fragment":bool}} } } } }
}

Sisendjsoni/morfi-väljundi/.lemmas-faili see osa, mida kasutame
morfi-väljund
{   "content": string,  /* algne tekst, võib puududa */
    "annotations":
    "tokens":           /* sõnede massiiv */
    [
        {
            "start": number,  /* sõne alguspositsioon algses tekstis, võib puududa */
            "end": number,    /* sõne lõpupositsioon  algses tekstis, võib puududa */
            "features":
            {
                "token": SÕNE,  /* algne morf analüüsitav sõne */
                "mrf" :           /* sisendsõne analüüsivariantide massiiv */
                [
                    {
                        "lemma_ma": LEMMA_MA, /* --stem lipu puudumise korral, verbilemmale on lisatud ```ma```, muudel juhtudel sama mis LEMMA */
                        "pos":      SÕNALIIK,
                    }
                ],
                "fragments" : [str] /* liitsõna korral osasõnade lemmad, muidu puudub */
            }
        }
    ],
}  
  
'''


def lisa_indeksisse(index:Dict, sisendjson:Dict)->None:
    """_summary_

    Args:
        index (Dict): täiendatav indeksfail
        sisend (Dict): morfi väljund, need lemmad lisame indeksisse
    """

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
            lemmas_lemma_ma = index["annotations"]["lemmas"].get(mrf["lemma_ma"])
            if lemmas_lemma_ma is None: # sellist lemmat pole varem üheski dokumendis kohanud
                #index["annotations"]["lemmas"][mrf["lemma_ma"]] = {sisendjson["docid"]:{token["start"]:token["end"]}}
                index["annotations"]["lemmas"][mrf["lemma_ma"]] = {sisendjson["docid"]:{token["start"]:{"endpos":token["end"], "fragment":False,
                    "token":index["sources"][sisendjson["docid"]]["content"][ token["start"] : token["end"] ]  }}}
                continue
            # sellist lemmat olema juba varem kohanud...
            lemmas_lemma_ma_docid = lemmas_lemma_ma.get(sisendjson["docid"])
            if lemmas_lemma_ma_docid is None: # ...aga mitte selles dokumendis
                #lemmas_lemma_ma[sisendjson["docid"]] = {token["start"]:token["end"]}
                lemmas_lemma_ma[sisendjson["docid"]] = {token["start"]:{"endpos":token["end"], "fragment":False,
                    "token":index["sources"][sisendjson["docid"]]["content"][ token["start"] : token["end"] ] }}
                continue
            # Sellist lemmat oleme selles dokumendis varem kohanud...
            lemmas_lemma_ma_docid_start = lemmas_lemma_ma_docid.get(token["start"])
            if lemmas_lemma_ma_docid_start is None: # ...aga teise koha peal
                #lemmas_lemma_ma_docid[token["start"]] = token["end"]
                lemmas_lemma_ma_docid[token["start"]] = {"endpos":token["end"], "fragment":False, 
                    "token":index["sources"][sisendjson["docid"]]["content"][ token["start"] : token["end"] ] }
            #else:
            #    pass
            # Samas dokumendis, sama lemma, sama koha peal - ainult teises vormis, vormierinevusi ignoreerime 
        # lisame liitsõna komponendud indeksisse
        # "annotations": { "lemmas": { "LEMMA": { "DOCID": { "STARTPOS":{"endpos":int, "fragment":bool}} } } } }
        if "fragments" not in  token["features"]:
            continue # polnud liitsõna
        for fragment in  token["features"]["fragments"]:
            lemmas_lemma_ma = index["annotations"]["lemmas"].get(fragment)
            if lemmas_lemma_ma is None: # sellist fragmenti/lemmat pole varem üheski dokumendis kohanud
                index["annotations"]["lemmas"][fragment] = {sisendjson["docid"]:{token["start"]:{"endpos":token["end"], "fragment":True,
                    "token":index["sources"][sisendjson["docid"]]["content"][ token["start"] : token["end"] ]  }}}
                continue
            # sellist fragmenti/lemmat oleme juba varem kohanud...
            lemmas_lemma_ma_docid = lemmas_lemma_ma.get(sisendjson["docid"])
            if lemmas_lemma_ma_docid is None: # ...aga mitte selles dokumendis
                lemmas_lemma_ma[sisendjson["docid"]] = {token["start"]:{"endpos":token["end"], "fragment":True,
                    "token":index["sources"][sisendjson["docid"]]["content"][ token["start"] : token["end"] ] }}
                continue
            # Sellist lemmat/fragmenti oleme selles dokumendis varem kohanud...
            lemmas_lemma_ma_docid_start = lemmas_lemma_ma_docid.get(token["start"])
            if lemmas_lemma_ma_docid_start is None: # ...aga teise koha peal
                lemmas_lemma_ma_docid[token["start"]] = {"endpos":token["end"], "fragment":True,
                    "token":index["sources"][sisendjson["docid"]]["content"][ token["start"] : token["end"] ] }

if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-i', '--indexin', type=str, help='olemasolev indeks')
    argparser.add_argument('-o', '--indexout', type=str, required=True, help='täiendatud indeks')
    argparser.add_argument('FILES', nargs='*', help='need lisame indeksisse')                       
    args = argparser.parse_args()

    # igal dokumendil peab olema unikaalne DOCID
    index = {"annotations":{"lemmas":{}}, "sources":{}} # index["sources"] = { DOCID: { "filename": str, "heading": str, "content": str } }
    if args.indexin is not None:
        with open(args.indexin, 'r') as file_index_in:
            index = json.loads(file_index_in.read())
            sys.stdout.write(f'indeksfail: {args.indexin}\n')

    for filename_in in args.FILES:
      with open(filename_in, 'r') as file_in:
        sys.stdout.write(f'+ {filename_in}\n')
        lisa_indeksisse(index, json.loads(file_in.read()))

    sys.stdout.write(f'Uuendatud indeksfaili {args.indexout} salvestamine...')
    with open(args.indexout, 'w') as file_index_out:
        file_index_out.write(json.dumps(index))
    sys.stdout.write('ok\n')

    
#!/usr/bin/env python3

'''
cd ~/git/smart-search_github/scripts/query_extender_setup/example_script_based_workflow/
venv/bin/python3 ./semi_automatic_word_form_generator.py \
    --jsonfile ../../../demod/toovood/riigi_teataja_pealkirjaotsing/01_dokumentide_indekseerimine/inputs/wordforms2addmanually.json \
    --db_name koond.sqlite --indent 4
'''

import sys
import json
import sqlite3
from typing import Dict, List, Tuple

def tee_tabelid(verbose:bool, json_in:Dict, db_name:str)->Dict:
    if verbose:
        sys.stdout.write(f"# teeme/avame andmebaasi {db_name}\n")

    con_baas = sqlite3.connect(f'file:{db_name}?mode=ro', uri=True)
    cur_baas = con_baas.cursor()

    json_out = {"tabelid":{"lemma_kõik_vormid":[], "lemma_korpuse_vormid":[]}}
    for sl in json_in["lemma+stem"]:
        lemma = sl["lemma"]
        tüvi = sl["stem"]
        lõpud = sl["endings"]
        for lõpp in json_in["endings"][lõpud]:
            vorm = tüvi + (lõpp if lõpp != '0' else '')
            res = cur_baas.execute(f'SELECT COUNT(*) FROM indeks_vormid WHERE vorm="{vorm}"')
            kaal = res.fetchall()[0][0]
            json_out["tabelid"]["lemma_kõik_vormid"].append((lemma, kaal, vorm))
            if kaal > 0:
                json_out["tabelid"]["lemma_korpuse_vormid"].append((lemma, kaal, vorm))
                
    con_baas.close()
    if verbose is True:
        print(f"# Suletud andmebaas {db_name}") 
    return json_out

if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-v', '--verbose',  action="store_true", help='kuva rohkem infot')
    argparser.add_argument('-j', '--jsonfile', type=str, help='tüved, lemmad ja vastavad lõpud')
    argparser.add_argument('-d', '--db_name', type=str, help='andmebaas')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    args = argparser.parse_args()

    try:
        with open(args.jsonfile) as json_file:
            json_in = {}
            #json_str = json_file.read().replace('\n', ' ')
            json_str = json_file.read()
            try:
                json_in = json.loads(json_str)
            except Exception as e:
                raise
        json_out = tee_tabelid(args.verbose, json_in, args.db_name)
        json.dump(json_out, sys.stdout, indent=args.indent, ensure_ascii=False)
    except Exception as e:
        print("\n\n", e, file=sys.stderr)
        sys.exit(1)
    sys.exit(0)
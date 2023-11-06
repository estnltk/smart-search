 #!/usr/bin/env python3

"""Silumiseks
    {
        "name": "api_sl_lemmatiser_json",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/sl_lemmatizer/",
        "program": "./api_lemmatizer4sl.py",
        "env": {},
        "args": ["--json={\"tss\":\"kinnipeetud\\tpidama\\tallmaaraudteejaam\"}", "--indent=4"]
    },
    {
        "name": "api_sl_lemmatiser_tsv",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/sl_lemmatizer/",
        "program": "./api_lemmatizer4sl.py",
        "env": {},
        "args": ["--json={\"tss\":\"kinnipeetud\\tpidama\\tallmaaraudteejaam\"}", "--tsv"]
    },
"""

import sys
import subprocess
import json
from typing import Dict, List

proc = subprocess.Popen(['./vmetajson', '--path=.'],  
                    universal_newlines=True, 
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL)

class LEMMATIZER4SL:
    def __init__(self):
        self.VERSION = "2023.10.26"

    def lemmatizer2json(self, tokens:List[str])->Dict:
        """Lemmatiseerme etteantud sõneloendi

        Sisse:
        {"tsv":str} 

        Returns:
            ~flask.Response: Lemmatiseerimise tulemused JSON-kujul
            {   TOKEN:      // sisendsõne
                {   LEMMA:  // sisendsõne lemma
                    [SUBLEMMA], // liitsõna korral osalemmad
                }
            }
        """
        json_mrf = {"params":{"vmetajson":["--guess"]}, "annotations":{"tokens":[]}}
        for token in tokens:
            json_mrf["annotations"]["tokens"].append({"features":{"token":token}})

        proc.stdin.write(f'{json.dumps(json_mrf)}\n')
        proc.stdin.flush()
        json_mrf = json.loads(proc.stdout.readline())

        res_json = {}
        for anno_tkn in json_mrf["annotations"]["tokens"]:
            TOKEN = anno_tkn["features"]["token"]
            if TOKEN not in res_json:
                res_json[TOKEN] = {}
                lemmas = []
                if "mrf" in anno_tkn["features"]:           
                    for mrf in anno_tkn["features"]["mrf"]:
                        lemmas.append(mrf["lemma_ma"].replace('=', ''))
                    lemmas = list(set(lemmas))
                    for lemma in lemmas:
                        LEMMA = lemma.replace('_', '')
                        if LEMMA not in res_json[TOKEN]:
                            res_json[TOKEN][LEMMA] = []
                        sublemmas = lemma.split('_')
                        len_sublemmas = len(sublemmas)
                        all_sublemmas   = [sublemmas[i] for i in range(0, len_sublemmas) if len_sublemmas > 1]
                        all_sublemmas  += [sublemmas[i-1]+sublemmas[i] for i in range(1, len_sublemmas) if len_sublemmas > 2]
                        all_sublemmas  += [sublemmas[i-2]+sublemmas[i-1]+sublemmas[i] for i in range(2, len_sublemmas) if len_sublemmas > 3]
                        all_sublemmas  += [sublemmas[i-3]+sublemmas[i-2]+sublemmas[i-1]+sublemmas[i] for i in range(3, len_sublemmas) if len_sublemmas > 4]
                        # sublemmad morfida
                        res_json[TOKEN][LEMMA] = all_sublemmas
        return res_json

    def lemmatizer2list(self, tokens:List[str])->List:
        res_json = self.lemmatizer2json(tokens)
        """_summary_
        {   TOKEN:      // sisendsõne
            {   LEMMA:  // sisendsõne lemma
                [SUBLEMMA], // liitsõna korral osalemmad
            }
        }
        ('location', 'input', 'stem', 'wordform')
        """
        res_list = []
        for location, (token, tokeninf) in enumerate(res_json.items()):
            for lemma, sublemmas in tokeninf.items():
                res_list.append((location, token, lemma, False))
                for sublemma in sublemmas:
                    res_list.append((location, token, sublemma, True))
        res_list = sorted(res_list, key = lambda x: (x[0], x[1], x[2], x[3]))
        return [("location", "input", "lemma", "is_sublemma")]+res_list


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-j', '--json', type=str, help='json input')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    argparser.add_argument('-t', '--tsv', action="store_true", help='TSV-like output')
    args = argparser.parse_args()

    lemmatizer = LEMMATIZER4SL()
    if args.tsv is False:
        res_json = lemmatizer.lemmatizer2json(json.loads(args.json)["tss"].split("\t"))
        json.dump(res_json, sys.stdout, indent=args.indent, ensure_ascii=False)
        sys.stdout.write('\n')
    else:
        res_list = lemmatizer.lemmatizer2list(json.loads(args.json)["tss"].split("\t"))
        for location, token, lemma, is_sublemma in res_list:
            sys.stdout.write(f"{location}\t{token}\t{lemma}\t{str(is_sublemma)}\n")




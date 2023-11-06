 #!/usr/bin/env python3

"""Silumiseks
    {
        "name": "sl_generator.py",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/sl_generator/",
        "program": "./sl_generator.py",
        "env": {},
        "args": ["--json={\"tss\":\"kinnipeetud\\tpidama\\tallmaaraudteejaam\"}"]
    },

"""

import sys
import subprocess
import json
from typing import Dict, List

proc = subprocess.Popen(['./vmetsjson', '--path=.'],  
                            universal_newlines=True, 
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)

class GENERATOR4SL:
    def __init__(self):
        self.VERSION = "2023.11.32"

    def generator2list(self, lemmas:List[str], with_apostrophe=False)->List:
        """
        Sisse:
            lemmas -- genereeritavate lemmade loend
            with_apostrophe -- True: lisa vormid kus käänedelõpp on tüvest ' või - märgiga eraldatud

        Märkus: päriselus on suur hulk erineva koodiga "ülakomasid" ja "sidekriipse".

        Returns:
            [(location, input, stem, wordform)] #input==lemma, wordform==lemma_vorm
        """
        json_mrf = {"params":{"vmetsjson":["--guess"]}, "annotations":{"tokens":[]}}
        for lemma in lemmas:
            json_mrf["annotations"]["tokens"].append({"features":{"token":lemma}})

        proc.stdin.write(f'{json.dumps(json_mrf)}\n')
        proc.stdin.flush()
        json_gen = json.loads(proc.stdout.readline())
        '''
        {   "annotations":
            {   "tokens":           /* sõnede massiiv */
                [   {   "features":
                        {   "token": SÕNE,  /* algne morf genereeritav sõne */
                            "mrf" :           /* sisendsõne sünteesivariantide massiiv */
                            [   {   "stem":     TÜVI,
                                    "ending":   LÕPP,    
                                }
                            ]               
                        }
                    }
                ]
            }
        }
        '''
        res_json = []
        
        for location, token in enumerate(json_gen["annotations"]["tokens"]):
            input = token["features"]["token"]
            stem = ""      # genereeritud sõnavormi tüvi
            wordform = ""   # genereeritud sõnavorm
            if "mrf" in token["features"]:
                for mrf in token["features"]["mrf"]:
                    stem = mrf["stem"].replace("_", "").replace("=", "")
                    wordform = stem
                    if mrf["ending"] != '0':
                        if with_apostrophe:
                            res_json.append((location, input, stem, wordform+"'"+mrf["ending"]))
                            res_json.append((location, input, stem, wordform+"-"+mrf["ending"]))
                        wordform = stem+mrf["ending"]
                    res_json.append((location, input, stem, wordform))                                                                
        res_json = list(set(res_json))
        res_json = [('location', 'input', 'stem', 'wordform')] \
            + sorted(res_json, key = lambda x: (x[0], x[1], x[2], x[3]))

        return res_json

if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-j', '--json', type=str, help='{"tss": "TAB-separeted-strings"')
    args = argparser.parse_args()

    generator = GENERATOR4SL()
    lemmas = json.loads(args.json)["tss"].split("\t")
    res_list = generator.generator2list(lemmas)
    for line in res_list:
        sys.stdout.write(f'{str(line[0])}\t{line[1]}\t{line[2]}\t{line[3]}\n')



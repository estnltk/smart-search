 #!/usr/bin/env python3

"""Silumiseks (code)
    {
        "name": "api_sl_lemmatiser_json",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/lemmatizer/",
        "program": "./api_lemmatizer4sl.py",
        "env": {},
        "args": ["--json={\"tss\":\"hõõguvpunast\\tpeeti\"}", "--indent=4"]
    },
    {
        "name": "api_sl_lemmatiser_tsv",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/lemmatizer/",
        "program": "./api_lemmatizer4sl.py",
        "env": {},
        "args": ["--json={\"tss\":\"hõõguvpunast\\tpeeti\"}", "--tsv"]
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
        self.VERSION = "2023.12.02"

    def lemmatizer2json(self, tokens:List[str])->Dict:
        """Lemmatiseerme etteantud sõneloendi

        Sisse:
        {"tsv":str} 

        Returns:
            {   TOKEN:
                {   STEM:
                    {   "lemmas":[str], 
                        "component":bool, 
                        "weight":real
                    }
                }
            }
        """
        assert proc.stdin is not None and proc.stdout is not None
        json_mrf = {"params":{"vmetajson":["--guess", "--stem"]}, "annotations":{"tokens":[]}}
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
            stems = []
            for mrf in anno_tkn["features"]["mrf"]:
                stems.append(mrf["stem"])
            stems = list(set(stems))
            for stem in stems:
                res_json[TOKEN][stem.replace("+", '').replace("=", '').replace("_", '')] = {"lemmas":[], "component":False, "weight": 1.0}
                components = stem.replace("+", '').replace("=", '').split("_")
                if len(components) <= 1:
                    continue
                for component in components:
                    res_json[TOKEN][component] = {"lemmas":[], "component":True, "weight": 1.0/float(len(components))}

        json_mrf = {"params":{"vmetajson":["--guess"]}, "annotations":{"tokens":[]}}
        for TOKEN, TOKENINF in res_json.items():
            for STEM, STEMINF in TOKENINF.items():
                json_mrf["annotations"]["tokens"].append({"features":{"orig_token":TOKEN , "token":STEM, "weight":STEMINF["weight"], "component":STEMINF["component"] }})
        proc.stdin.write(f'{json.dumps(json_mrf)}\n')
        proc.stdin.flush()
        json_mrf = json.loads(proc.stdout.readline())

        for token in json_mrf["annotations"]["tokens"]:
            TOKEN = token["features"]["orig_token"]
            STEM = token["features"]["token"]
            if "mrf" not in token["features"]:
                continue
            lemmas = []
            for mrf in token["features"]["mrf"]:
                lemmas.append(mrf["lemma_ma"].replace("+", '').replace("=", '').replace("_", ''))
            lemmas = list(set(lemmas))
            res_json[TOKEN][STEM]["lemmas"] += lemmas                 
        return res_json

    def lemmatizer2list(self, tokens:List[str])->List:
        res_json = self.lemmatizer2json(tokens)
        """_summary_
            {   TOKEN:
                {   STEM:
                    {   "lemmas":[str], 
                        "component":bool, 
                        "weight":real
                    }
                }
            }
        (location, TOKEN, STEM, component, weight, [LEMMAS])
        """
        res_list = []
        for location, (token, tokeninf) in enumerate(res_json.items()):
            for stem, steminf in tokeninf.items():
                res_list.append((location, token, stem, steminf["component"], steminf["weight"], steminf["lemmas"]))
        res_list = sorted(res_list, key = lambda x: (x[0], x[1], x[3], x[2], x[4]))
        return res_list


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-j', '--json',   type=str, help='json input')
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
        for (location, TOKEN, STEM, component, weight, LEMMAS) in res_list:
            sys.stdout.write(f"{location}\t{TOKEN}\t{STEM}\t{component}\t{weight}\t{LEMMAS}\n")




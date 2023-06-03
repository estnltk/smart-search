#!/usr/bin/python3

import os
import sys
import json
import requests
from typing import Dict, List

class PARING_SONED:
    def __init__(self):
        self.VERSION="2023.06.02"

        self.tokenizer = os.environ.get('TOKENIZER')
        if self.tokenizer is None:
            self.TOKENIZER_IP=os.environ.get('TOKENIZER_IP') if os.environ.get('TOKENIZER_IP') != None else 'localhost'
            self.TOKENIZER_PORT=os.environ.get('TOKENIZER_PORT') if os.environ.get('TOKENIZER_PORT') != None else '6000'
            self.tokenizer = f'http://{self.TOKENIZER_IP}:{self.TOKENIZER_PORT}/api/tokenizer/process'

        self.analyser = os.environ.get('ANALYSER')
        if self.analyser is None:
            self.ANALYSER_IP=os.environ.get('ANALYSER_IP') if os.environ.get('ANALYSER_IP') != None else 'localhost'
            self.ANALYSER_PORT=os.environ.get('ANALYSER_PORT') if os.environ.get('ANALYSER_PORT') != None else '7007'
            self.analyser = f'http://{self.ANALYSER_IP}:{self.ANALYSER_PORT}/api/analyser/process'

        self.generator = os.environ.get('GENERATOR')
        if self.generator is None:
            self.GENERATOR_IP=os.environ.get('GENERATOR_IP') if os.environ.get('GENERATOR_IP') != None else 'localhost'
            self.GENERATOR_PORT=os.environ.get('GENERATOR_PORT') if os.environ.get('GENERATOR_PORT') != None else '7000'
            self.generator = f'http://{self.GENERATOR_IP}:{self.GENERATOR_PORT}/process' # NB! generaator ei ole selle koha peal analoogiline teiste teenustega

        self.ignore_pos = "PZJ" # ignoreerime lemmasid, mille sõnaliik on: Z=kirjavahemärk, J=sidesõna, P=asesõna

    def string2json(self, str:str) -> Dict:
        """JSONis sisendstring "päris" JSONiks

        Args:
            str (str): _description_

        Raises:
            Exception: Jama sisendJSONi parsimisega
        Returns:
            Dict: _description_
        """
        json_out = {}
        try:
            json_out = json.loads(str)
            return json_out
        except:
            raise Exception({"error": "JSON parse error"})
        
    def paring_json(self, json_in:Dict) -> Dict:
        """Sõnestame, lemmatiseerime ja genereerime JSON-kujul päringu


        Args:
            json_io (Dict): 
                {   "content": str // päringustring
                }

        Returns:
            Dict:
            {   "content": str // päringustring,
                "annotatsions":
                {   "query": 
                    [   [str11, str12, ...], // (str11 V str12 V ...) & (str21 V str22 V ...) & ....
                        [str21, str22, ...]
                        ...
                    ]
                }    
            }
        """
        json_out = {}
        # Sõnestame, et näiteks kokkukirjutatud "Sarved&Sõrad" tükeldataks samamoodi nagu on indeksis 
        try:                                                # sõnestame
            json_out = json.loads(requests.post(self.tokenizer, json=json_in).text)
        except:                                             # sõnestamine äpardus
            raise Exception({"warning":'Probleemid sõnestamise veebiteenusega'})
        # Leiame lemmad
        try:
            json_out["params"] = {"vmetajson":["--guess"]}
            json_out = json.loads(requests.post(self.analyser, json=json_out).text)
        except:
            raise Exception({"warning":'Probleemid morf analüüsi veebiteenusega'})
        json_paring = []

        # genereerime lemmadest kõik vormid
        for token in json_out["annotations"]["tokens"]:
            vormid_genemiseks = []
            for mrf in token["features"]["mrf"]:
                if self.ignore_pos.find(mrf["pos"]) != -1:                              # selle sõnaliiiga lemmasid...
                    continue
                if mrf["lemma_ma"] not in vormid_genemiseks:                                                   # sõne morf analüüside hulgas võib sama kujuga lemma erineda ainult käände/põõrde poolest
                    vormid_genemiseks.append( mrf["lemma_ma"].replace("_", "").replace("=", ""))
            generator_in = {"type":"text", "content": " ".join(vormid_genemiseks)}
            # gene selle sõne kõigi lemmade kõik vormid
            try:
                generator_out = json.loads(requests.post(self.generator, json=generator_in).text)
            except:
                raise Exception({"warning":'Probleemid morf sünteesi veebiteenusega'})
            # lisa saadud vormid päringusse
            tokens = []
            for text in generator_out["response"]["texts"]:
                for generated_form in text["features"]["generated_forms"]:
                    tokens.append(generated_form["token"].replace("_", "").replace("=", "").replace("+", ""))
            if len(tokens) > 0:
                json_paring.append(tokens)    
        json_out["annotations"]["query"] = json_paring
        del json_out["annotations"]["sentences"]
        del json_out["annotations"]["tokens"]
        del json_out["params"]

        return json_out
    
    def paring_text(self, json_io:Dict) -> str:
        """Sõnestame, lemmatiseerime ja genereerime loogilist avaldist sisaldava päringustringi

        Args:
            json_io (Dict):
                {   "content": str // päringustring
                }

        Returns:
            str: Loogilist avaldist sisaldava päringustring
        """
        json_out = self.paring_json(json_io)
        paring = []
        for lemmad in json_out["annotations"]["query"]:
           paring.append('(' + f' ∨ '.join(lemmad) + ')')
        paring = ' & '.join(paring)
        return paring
    
    def version_json(self) -> Dict:
        return {"version": self.VERSION, "tokenizer": self.tokenizer, "analyser": self.analyser, "generator": self.generator}
        
if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-t', '--text', action="store_true", help='text output')
    argparser.add_argument('-j', '--json', type=str, help='json input')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    args = argparser.parse_args()

    prng = PARING_SONED()
    if args.json is not None:
        json_in = prng.string2json(args.json)
        if args.text is True:
            print(prng.paring_text(json_in))
        else:
            json.dump(prng.paring_json(json_in), sys.stdout, indent=args.indent, ensure_ascii=False)
            sys.stdout.write('\n')


        

        
        
    
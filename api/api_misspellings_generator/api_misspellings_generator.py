 #!/usr/bin/python3

"""
Teeb teksitfailidest JSON-kuju, millest järgmise programmiga pannakse kokku andmebaas
-----------------------------------------------------------------
// code (silumiseks):
    {
        "name": "api_misspellings_generator",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/api_misspellings_generator/",
        "program": "./api_misspellings_generator.py",
        "env": {},
        "args": ["--verbose", "test.txt"]
    },

-----------------------------------------------------------------
käsurealt:

$ venv/bin/python3 ./api_misspellings_generator.py --verbose test.txt > test.json

"""

import csv
import os
import sys
import json
import inspect
import subprocess
from tqdm import tqdm
from typing import Dict, List, Tuple
from inspect import currentframe, getframeinfo

proc_vmetajson = subprocess.Popen(['./vmetajson', '--path=.'],  
                            universal_newlines=True, 
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)

class KIRJAVIGUR:
    def __init__(self, verbose:bool)->None:
        """Initsialiseerime muutujad: versiooninumber, jne

        Args:
            verbose (bool): True: kuva tööjärjega seotud infot
        """
        self.wordforms = []
        self.json_out = {"tabelid":{"kirjavead":[]}}
        self.verbose = verbose
        self.VERSION="2023.12.14"

    def verbose_prints(self, message:str) -> None:
        """PRIVATE: Kirjutad teade stderr'i

        Args:
            message (str): teade
        """
        if self.verbose:
            sys.stderr.write(f'# {message}\n')

    def run_subprocess(self, proc, json_in:Dict) -> Dict:
        proc.stdin.write(f'{json.dumps(json_in)}\n')
        proc.stdin.flush()
        return json.loads(proc.stdout.readline())

    def gene_potentsiaalsed_kirjavead(self, token:str)->List[str]:
        """PRIVATE:Genereeri sõnavormist potentsiaalsed kirjavigased vormid

        Args:
            token (str): sõnavorm

        Returns:
            List[str]: need genereeritud kirjavead, mida morf ilma oletamiseta ära ei tunne
        """
        potentsiaalsed_kirjavead = []
        for i in range(len(token)):
            if len(token) > 3: # peab olema vähemalt 3 tähte
                # 2 tähte vahetuses: tigu -> itgu, tgiu, tiug
                if i > 0 and token[i] != token[i-1]: # kahte ühesugust tähte ei vaheta
                    t = token[0:i-1]+token[i]+token[i-1]+token[i+1:]
                    if t not in potentsiaalsed_kirjavead:
                        potentsiaalsed_kirjavead.append(t) 
                # 1 täht läheb topelt
                t = token[:i]+token[i]+token[i]+token[i+1:]
                if t not in potentsiaalsed_kirjavead:
                    potentsiaalsed_kirjavead.append(t) 
                # 1 täht kaob ära
                t = token[:i]+token[i+1:]
                if t not in potentsiaalsed_kirjavead:
                        potentsiaalsed_kirjavead.append(t) 
                # g b d k p t-> k p t g b d
                if (n := "gbdkpt".find(token[i])) > -1:
                    t = token[:i]+"kptgbd"[n]+token[i+1:]                   
                    if t not in potentsiaalsed_kirjavead:
                        potentsiaalsed_kirjavead.append(t)
        if len(potentsiaalsed_kirjavead) == 0:
            return []
        morf_in = {"params": {"vmetajson":["--stem"]}, "annotations":{"tokens":[]}}
        for pkv in potentsiaalsed_kirjavead:
            morf_in["annotations"]["tokens"].append({"features":{"token": pkv}})
        morf_out = self.run_subprocess(proc_vmetajson, morf_in)
        for token in morf_out["annotations"]["tokens"]:
            if "mrf" not in token["features"]:
                potentsiaalsed_kirjavead.append(token["features"]["token"])
        return list(set(potentsiaalsed_kirjavead))

    def tee_kirjavead(self)->None:
        """PUBLIC:Lisame kirjavead parandamiseks vajaliku tabeli

        Kasutame:
            self.wordforms
        Returns:

            * self.json_out={"tabelid":{"kirjavead":[(VIGANE_VORM, VORM, 1.0)]}}
        """
        self.verbose_prints(f"Kustutame kordused")
        self.wordforms = list(set(self.wordforms))        
        pbar = tqdm(self.wordforms, disable=(not self.verbose), desc="# teeme potentsiaalsed kirjavead")
        for vorm in pbar:
            if any(char.isdigit() for char in vorm) is True:
                continue # ei tee kirjavigasid numbreid sisaldavatest sõnedest
            vigased_vormid = self.gene_potentsiaalsed_kirjavead(vorm)
            for vigane_vorm in vigased_vormid:
                # {"tabelid":{ "kirjavead":[[VIGANE_VORM, VORM, KAAL]] }
                self.json_out["tabelid"]["kirjavead"].append((vigane_vorm, vorm, 1.0))
        pass # DB
 
    def kuva_tabelid(self, indent)-> None:
        """PUBLIC:Lõpptulemus JSON kujul std väljundisse

        Std väljundisse:    
            *TODO
        """
        json.dump(self.json_out, sys.stdout, indent=indent, ensure_ascii=False)
        sys.stdout.write('\n')

    def version_json(self) -> Dict:
        """PUBLIC:Kuva JSONkujul versiooniinfot ja kasutatavate veebiteenuste URLe

        Returns:
            Dict: versiooninfo ja URLid
        """
        return  {"kirjavigade generaatori version": self.VERSION }

    def file2list(self, fname:str, file) -> None:
        self.verbose_prints(f"Loeme failist {fname}")
        self.wordforms += file.read().splitlines()
        pass

if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-v', '--verbose',  action="store_true", help='kuva rohkem infot tööjärje kohta')
    argparser.add_argument('-i', '--indent', type=int, default=None, help='indent for json output, None=all in one line')
    argparser.add_argument('file', type=argparse.FileType('r'), nargs='+')
    args = argparser.parse_args()

    try:
        kv = KIRJAVIGUR(args.verbose)
        for file  in args.file:
            kv.file2list(file.name, file)
        kv.tee_kirjavead()
        kv.kuva_tabelid(args.indent)
    except Exception as e:
        print(f"An exception occurred: {str(e)}")

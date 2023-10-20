#!/usr/bin/python3

'''


'''


import os
import sys
import json
import requests
from typing import Dict, List, Tuple

class KIRJAVIGASTAJA:
    """Korrektsetest sõnadest kirjavigaste variantide genereerimine
    """
    def __init__(self, verbose:bool, analyser:str)->None:
        """Initsialiseeri klass

        Args:
            analyser (str): morf analüsaatori URL
        """
        self.verbose = verbose
        self.analyser = analyser

    def kirjavigastaja(self, soneloend:List[str])->List:
        potentsiaalsed_kirjavead = []
        for sone in soneloend:
            potentsiaalsed_kirjavead += self.gene_potentsiaalsed_kirjavead(sone)
        return list(set(potentsiaalsed_kirjavead))


    def gene_potentsiaalsed_kirjavead(self, token:str)->List[str]:
        """PUBLIC:Genereeri sõnavormist potentsiaalsed kirjavigased vormid

        Args:
            token (str): sõnavorm

        Returns:
            List[str]: need genereeritud kirjavead, mida morf ilma oletamiseta ära ei tunna 
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
        # morfi_sisend = {"params": {"vmetajson":["--stem"]}, "content": " ".join(potentsiaalsed_kirjavead)}
        # kontent ei sobi, sest sest sõnestaja teeb (vahel) tühikuga sõnesid 
        morfi_sisend = {"params": {"vmetajson":["--stem"]}, "annotations":{"tokens":[]}}
        for pkv in potentsiaalsed_kirjavead:
            morfi_sisend["annotations"]["tokens"].append({"features":{"token": pkv}})
        # laseme võimalikud kirjavead ilma oletamiseta morfist läbi 
        try:
            response = requests.post(self.analyser, json=morfi_sisend)
            if not response.ok:
                raise Exception({"warning":f'Probleemid veebiteenusega {self.analyser}, status_code={response.status_code}'})
            resp_json = response.json()
        except:
            raise Exception({"warning":f'Probleemid veebiteenusega {self.analyser}'})
        
        potentsiaalsed_kirjavead = []
        for token in resp_json["annotations"]["tokens"]:
            if "mrf" not in token["features"]:
                potentsiaalsed_kirjavead.append(token["features"]["token"])
        return potentsiaalsed_kirjavead

if __name__ == '__main__':
    kv = KIRJAVIGASTAJA(True, 'https://smart-search.tartunlp.ai/api/analyser/process')
    for sõne in sys.argv[1:]:
        print(sõne, " : ", kv.gene_potentsiaalsed_kirjavead(sõne))




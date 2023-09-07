#!/usr/bin/python3

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

    def kirjavigur(self, token:str)->List[Tuple[str, str, int]]:
        """PUBLIC:Genereeri sisendstrigist kirjavigased vormid

        Args:
            token (str): sisendstring

        Returns:
            List: kirjavigade (kirjavigane_vorm, algne_sõne, 0) list
        """
        võimalikud_kirjavead = []
        for i in range(len(token)):
            # 2 tähte vahetuses: tigu -> itgu, tgiu, tiug
            if i > 0 and token[i] != token[i-1]: # kahte ühesugust tähte ei vaheta
                t = token[0:i-1]+token[i]+token[i-1]+token[i+1:]    
                pigem_kirjavead = võimalikud_kirjavead.append(t) 
            # 1 täht läheb topelt
            t = token[:i]+token[i]+token[i]+token[i+1:]
            pigem_kirjavead = võimalikud_kirjavead.append(t) 
            # 1 täht kaob ära
            t = token[:i]+token[i+1:]
            pigem_kirjavead = võimalikud_kirjavead.append(t) 

            # g b d k p t-> k p t g b d
            if (n := "gbdkpt".find(token[i])) > -1:
                t = token[:i]+"kptgbd"[n]+token[i+1:]                   
                pigem_kirjavead = võimalikud_kirjavead.append(t)
        pigem_kirjavead = self.leia_kirjavead(võimalikud_kirjavead)
        if self.verbose:
            sys.stdout.write(f'#    {len(võimalikud_kirjavead)}/{len(pigem_kirjavead)}\n')
        kirjavead = []
        for vk in pigem_kirjavead:
            kirjavead.append((vk, token, 0))
        return kirjavead

    def leia_kirjavead(self, võimalikud_kirjavead:List[str])->List[str]:
        """PRIVATE:Kontrolli kas võib olla kirjaviga

        Args:
            võimalikud_kirjavead (List[str]): kontrollitav sõnavorm
        

        Raises:
            Exception: Exception({"warning":f'Probleemid veebiteenusega {self.analyser}'})

        Returns:
            List[str]: ilma oletamiseta morf jaoks tundmatuks jäänud sisendsõned
        """
        paring = {   "params": {"vmetajson":["--stem"]},"annotations":{"tokens":[]}}
        for kv in võimalikud_kirjavead:
            paring["annotations"]["tokens"].append({"features":{"token":kv}})
        try:
            resp = json.loads(requests.post(self.analyser, json=paring).text)
        except:
            raise Exception({"warning":f'Probleemid veebiteenusega {self.analyser}'})
        kirjavead = []
        for kv in resp["annotations"]["tokens"]:
            if "mrf" not in kv["features"]:
                kirjavead.append(kv["features"]["token"])
        return kirjavead


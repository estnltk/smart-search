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

    def kirjavigastaja(self, soneloend:List[str])->List[Tuple[str, str, int]]:
        morfi_sisend = {
            "params": {"vmetajson":["--stem"]}, 
            "annotations":{"tokens": []}}
        for i, s in enumerate(soneloend):
            # genereerime iga sõne kohta võimalikud kirjavead
            võimalikud_kirjavead = self.gene_kõikvõimalikud_kirjavigastised(s)
            for võimalik_kirjaviga in võimalikud_kirjavead:
                morfi_sisend["annotations"]["tokens"].append({"features":{"idx": i, "token": võimalik_kirjaviga}})
        # laseme võimalikud kirjavead ilma oletamiseta morfist läbi 
        try:
            response = requests.post(self.analyser, json=morfi_sisend)
            if not response.ok:
                raise Exception({"warning":f'Probleemid veebiteenusega {self.analyser}, status_code={response.status_code}'})
            resp_json = response.json()
        except:
            raise Exception({"warning":f'Probleemid veebiteenusega {self.analyser}'})
        # jätame alles ainult need, millel ilma oletamiseta ei olnud võimalikke analüüse
        võimalikud_kirjavead = []
        for t in resp_json["annotations"]["tokens"]:
            if "mrf" not in t["features"]:
                võimalikud_kirjavead.append((t["features"]["token"] , soneloend[t["features"]["idx"]],0))
                pass
        return võimalikud_kirjavead


    def gene_kõikvõimalikud_kirjavigastised(self, token:str)->List[str]:
        """PUBLIC:Genereeri sisendstrigist kirjavigased vormid

        Args:
            token (str): sisendstring

        Returns:
            List: kirjavigade (kirjavigane_vorm, algne_sõne, 0) list
        """
        võimalikud_kirjavead = []
        for i in range(len(token)):
            if len(token) > 3: # peab olema vähemalt 3 tähte
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
        return võimalikud_kirjavead

    def kirjavigur(self, token:str)->List[Tuple[str, str, int]]:
        """PUBLIC:Genereeri sisendstrigist kirjavigased vormid

        Args:
            token (str): sisendstring

        Returns:
            List: kirjavigade (kirjavigane_vorm, algne_sõne, 0) list
        """
        võimalikud_kirjavead = []
        for i in range(len(token)):
            if len(token) > 3: # peab olema vähemalt 3 tähte
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

if __name__ == '__main__':
    kv = KIRJAVIGASTAJA(True, 'https://smart-search.tartunlp.ai/api/analyser/process')
    print(kv.kirjavigastaja(sys.argv[1:]))
    #for token in sys.argv[1:]:
    #    kirjavead = kv.kirjavigur(token)
    #    print(token, ':', kirjavead)



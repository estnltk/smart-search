#!/usr/bin/python3

import os
import sys
import json
import requests

'''
Kasutusnäide
* installi docker
* Laadi alla ja käivita sõnstajat sisaldav dockeri konteiner
  > docker pull tilluteenused/vmetajson:2022.09.09
  > docker run -p 6666:7000 tilluteenused/vmetajson:2022.09.09
* installi
  * python
  * pythoni pakett request 
* Lase pythoni programmil oma tekst morfida (väljundfaili nimi saadakse sisendfaili nimes laiendi asendamisega (.lemmas))
  > ./sonesta-lausesta.py SISENDFILE.tokens [SISENDFAIL.tokens...]

  
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
                "classic": str, /* sõne morf analüüsistring vmeta-kujul, ainult --classic lipu korral */
                "complexity": KEERUKUS,
                "mrf" :           /* sisendsõne analüüsivariantide massiiv */
                [
                    {
                        "stem":     TÜVI,     /* --stem lipu korral */
                        "lemma":    LEMMA,    /* --stem lipu puudumise korral */
                        "lemma_ma": LEMMA_MA, /* --stem lipu puudumise korral, verbilemmale on lisatud ```ma```, muudel juhtudel sama mis LEMMA */
                        "ending":   LÕPP,    
                        "kigi":     KIGI,
                        "pos":      SÕNALIIK,
                        "fs":       KATEGOORIAD,
                        "gt":       KATEGOORIAD,  /* --gt lipu korral */
                        "source":   ALLIKAS,      /* P:põhisõnastikust, L:lisasõnastikust, O:sõnepõhisest oletajast, S:lausepõhisest oletajast, X:ei tea kust */
                    }
                ],
                "fragments" : [str] /* liitsõna korral osasõnade lemmad */
            }
        }
    ],
}  
  
  
'''


def morfi(sisend:str) -> str:
    """Sonesta ja lausesta

    Args:
        text (str): Sõnestatav ja lausestav tekst json-stringina

    Returns:
        str: Sõnestatud ja lausestatud värk
    """
    sisend_json = json.loads(sisend)
    sisend_json["params"]={"vmetajson":["--guess"]} # morfime koos oletamisega
    #return requests.post('http://localhost:6666/process', json=sisend_json).text
    valjund_json = json.loads(requests.post('http://localhost:6666/process', json=sisend_json).text)

    for token in valjund_json["annotations"]["tokens"]:
      for mrf in token["features"]["mrf"]:
        token["features"]["fragments"] = []
        lemma = mrf["lemma_ma"]
        if (lemma == '_') or (lemma[0] == '_') or (lemma == '=') or (lemma[len(lemma)-1] == '='):
          continue  
        if lemma.find('=') > 0:       # sisaldab järelliidet...
          lemma = lemma.split('=')[0] # ...kustutame järelliite
        fragments = lemma.split('_')
        if len(fragments) > 1: # liitsõna, leiame osasõnede lemmad
          fragments_json_in = {"content": ' '.join(fragments)}
          fragments_json_out = json.loads(requests.post('http://localhost:6666/process', json={"content": ' '.join(fragments)}).text)
          for fragments_token in fragments_json_out["annotations"]["tokens"]:
             for fragments_mrf in fragments_token["features"]["mrf"]:
                if fragments_mrf["lemma_ma"] not in token["features"]["fragments"]:
                   token["features"]["fragments"].append(fragments_mrf["lemma_ma"])      
    return json.dumps(valjund_json)


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('FILES', nargs='*', help='sisendfailid')                       
    args = argparser.parse_args()

    for filename_in in args.FILES:
      with open(filename_in, 'r') as file_in:
          sys.stdout.write(f'{filename_in}->')
          sisend = file_in.read()
          valjund = morfi(sisend)
          filename, file_extension = os.path.splitext(filename_in)
          with open(filename+'.lemmas', 'w') as file_out:
            file_out.write(valjund)
            sys.stdout.write(f'{filename}.lemmas\n')

    
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
  > docker run -p 7000:7000 tilluteenused/vmetajson:2022.09.09
* installi
  * python
  * pythoni pakett request 
* Lase pythoni programmil oma tekst morfida (väljundfaili nimi saadakse sisendfaili nimes laiendi asendamisega (.lemmas))
  > ./sonesta-lausesta.py SISENDFILE.tokens [SISENDFAIL.tokens...]
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
    return requests.post('http://localhost:7000/process', json=sisend_json).text


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('FILES', nargs='*', help='sisendfailid')                       
    args = argparser.parse_args()

    for filename_in in args.FILES:
      with open(filename_in, 'r') as file_in:
          sys.stdout.write(f'{filename_in}->')
          sisend = file_in.read()
          valjund = json.loads(morfi(sisend))
          filename, file_extension = os.path.splitext(filename_in)
          with open(filename+'.lemmas', 'w') as file_out:
            file_out.write(json.dumps(valjund))
            sys.stdout.write(f'{filename}.lemmas\n')

    
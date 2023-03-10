#!/usr/bin/python3

import os
import sys
import json
import requests

'''
Kasutusnäide
* installi docker
* Laadi alla ja käivita sõnstajat sisaldav dockeri konteiner
  > docker pull tilluteenused/estnltk_sentok:2022.09.09
  > docker run -p 6000:6000 tilluteenused/estnltk_sentok:2022.09.09
* installi
  * python
  * pythoni pakett request 
* Lase pythoni programmil oma tekst sõnestada (väljundfaili nimi saadakse sisendfaili nimes laiendi asendamisega (.tokens))
  > ./sonesta-lausesta.py --heading="PEALKIRI" --docid="DOCID" SISENDFILE.txt
'''


def sonesta_lausesta(sisend:str) -> str:
    """Sonesta ja lausesta

    Args:
        text (str): Sõnestatav ja lausestav tekst json-stringina

    Returns:
        str: Sõnestatud ja lausestatud värk
    """
    return requests.post('http://localhost:6000/process', json=json.loads(sisend)).text


if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('--heading', type=str, required=True, help='documendi pealkiri')
    argparser.add_argument('--docid',   type=str, required=True, help='documendi unikaalne id')
    argparser.add_argument('FILE', help='sisendfail')                       
    args = argparser.parse_args()


    filename_in = args.FILE
    with open(args.FILE, 'r') as file_in:
        sys.stdout.write(f'{args.FILE} -> ')
        raw_data = file_in.read()
        sisend = f"{{\"filename\":\"{filename_in}\",\"heading\":{json.dumps(args.heading)},\"docid\":\"{args.docid}\",\"content\":{json.dumps(raw_data)}}}" 
        valjund = json.loads(sonesta_lausesta(sisend))
        filename, file_extension = os.path.splitext(args.FILE)
        with open(filename+'.tokens', 'w') as file_out:
          file_out.write(json.dumps(valjund))
          sys.stdout.write(f'{filename}.tokens\n')

    
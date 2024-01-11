#!/usr/bin/python3

'''Flask api, (eel)arvutab JSON-failid mis on vajlikud andmebaasi kokkupanemiseks
----------------------------------------------
Mida uut:
2023-12-27  sõnede eraldajaks on '\n' (tühik ei eralda enam sõnesid)
            SMART_SEARCH_MAX_CONTENT_LENGTH vaikimisi 600000
----------------------------------------------
// code (serveri käivitamine silumiseks):
        {
            "name": "flask_api_misspellings_generator",
            "type": "python",
            "request": "launch",
            "cwd": "${workspaceFolder}/api/api_misspellings_generator/",
            "program": "./flask_api_misspellings_generator.py",
            "env": {}
            "args": []
        },
----------------------------------------------
Lähtekoodist pythoni skripti kasutamine:
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2) ja käivitamine(1.3)
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git sqmart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/api/api_misspellings_generator
    $ ./create_venv.sh
1.3 Sätime paika kasutatvad teenused: kasutame veebis olevaid konteinereid (1.3.1) või kasutame kohalikus masinas töötavaid konteinereid (1.3.2)
1.3 Pythoni skripti käivitamine:
    $ venv/bin/python3 ./api_misspellings_generator.py --verbose test.txt > test.json
----------------------------------------------
Lähtekoodist veebiserveri käivitamine & kasutamine
2 Lähtekoodi allalaadimine (2.1), virtuaalkeskkonna loomine (2.2), veebiteenuse käivitamine pythoni koodist (2.3) ja CURLiga veebiteenuse kasutamise näited (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Virtuaalkeskkonna loomine: järgi punkti 1.2
2.3 Veebiteenuse käivitamine pythoni koodist
2.3.1 Vaikeseadetaga
    $ cd ~/git/smart_search_github/api/api_misspellings_generator
    $ ./venv/bin/python3 ./flask_api_misspellings_generator.py
2.3.2 Etteantud parameetriga
    $ SMART_SEARCH_MAX_CONTENT_LENGTH='500000' \
        venv/bin/python3 ./flask_api_misspellings_generator.py
2.4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/text" \
        localhost:6603/api/misspellings_generator/version | jq
    $ curl --silent --request POST --header "Content-Type: application/text" \
      --data-binary @test.txt \
      localhost:6603/api/misspellings_generator/process  | jq
----------------------------------------------
Lähtekoodist tehtud konteineri kasutamine
3 Lähtekoodi allalaadimine (3.1), konteineri kokkupanemine (3.2), konteineri käivitamine (3.3) ja CURLiga veebiteenuse kasutamise näited  (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/api/api_misspellings_generator
    $ docker build -t tilluteenused/smart_search_api_misspellings_generator:2023.12.27 . 
    # docker login -u tilluteenused
    # docker push tilluteenused/smart_search_api_misspellings_generator:2023.12.27 
2.3 Konteineri käivitamine
    $ docker run -p 6603:6603  \
        --env SMART_SEARCH_MAX_CONTENT_LENGTH='500000' \
       tilluteenused/smart_search_api_misspellings_generator:2023.12.27 
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4
----------------------------------------------
DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_api_misspellings_generator:2023.12.27 
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4
----------------------------------------------
TÜ pilves töötava konteineri kasutamine
4 CURLiga veebiteenuse kasutamise näited
    $ cd ~/git/smart_search_github/api/api_misspellings_generator # selles kataloogis on test.txt
    $ curl --silent --request POST --header "Content-Type: application/text" \
        --data-binary @test.txt \
        https://smart-search.tartunlp.ai/api/misspellings_generator/process | jq | less
    $ curl --silent --request POST --header "Content-Type: application/text" \
        https://smart-search.tartunlp.ai/api/misspellings_generator/version | jq

----------------------------------------------
'''
import os
import sys
import json
import requests
import subprocess
import json
import argparse
from flask import Flask, request, jsonify, make_response, abort
from functools import wraps
from typing import Dict, List, Tuple
from collections import OrderedDict

import api_misspellings_generator

VERSION="2023.12.27"

kv = api_misspellings_generator.KIRJAVIGUR(verbose=False)

app = Flask("flask_api_misspellings_generator")

# JSONsisendi max suuruse piiramine {{
try:
    SMART_SEARCH_MAX_CONTENT_LENGTH=int(os.environ.get('SMART_SEARCH_MAX_CONTENT_LENGTH'))
except:
    SMART_SEARCH_MAX_CONTENT_LENGTH = 6 * 100000 # 6 GB 

def limit_content_length(max_length):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            cl = request.content_length
            if cl is not None and cl > max_length:
                abort(413)
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.errorhandler(413) # Liiga mahukas päring
def request_entity_too_large(error):
    #return 'File Too Large', 413
    return jsonify({"error":"Request Entity Too Large"})

# }} JSONsisendi max suuruse piiramine 

@app.route('/api/misspellings_generator/process', methods=['POST'])
@app.route('/process', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_amisspellings_generator_process():
    try:
        kv.json_out = {"tabelid":{"kirjavead":[]}}
        data = request.data.decode("utf-8").strip()
        kv.wordforms = [wordform.strip() for wordform in data.split('\n')]
        kv.tee_kirjavead()
        return jsonify(kv.json_out)
    except Exception as e:
        return jsonify({"warning": list(e.args)})    

@app.route('/api/misspellings_generator/version', methods=['GET', 'POST'])
@app.route('/version', methods=['POST'])
def api_advanced_indexing_version():
    """Kuvame versiooni ja muud infot

    Returns:
        ~flask.Response: Lemmatiseerija versioon
    """
    json_response = kv.version_json()
    json_response["FLASk-liidese versioon"] = VERSION
    json_response["SMART_SEARCH_MAX_CONTENT_LENGTH"] = SMART_SEARCH_MAX_CONTENT_LENGTH

    return jsonify(json_response)

if __name__ == '__main__':
    default_port=6603
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)



        

        
        
    

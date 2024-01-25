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
1 Lähtekoodist pythoni skripti kasutamine:
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git sqmart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/api/api_misspellings_generator \
        && ./create_venv.sh
1.3 Sätime paika kasutatvad teenused: kasutame veebis olevaid konteinereid (1.3.1) või kasutame kohalikus masinas töötavaid konteinereid (1.3.2)
1.3 Pythoni skripti käivitamine:
    $ cd ~/git/smart_search_github/api/api_misspellings_generator \
        && venv/bin/python3 ./api_misspellings_generator.py --verbose test.txt > test.json
----------------------------------------------
2 Lähtekoodist veebiserveri käivitamine & kasutamine
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Virtuaalkeskkonna loomine: järgi punkti 1.2
2.3 Veebiteenuse käivitamine pythoni koodist
2.3.1 Vaikeseadetaga
    $ cd ~/git/smart_search_github/api/api_misspellings_generator \
        && ./venv/bin/python3 ./flask_api_misspellings_generator.py
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
3 Lähtekoodist tehtud konteineri kasutamine
3.1 Lähtekoodi allalaadimine: järgi punkti 1.1
3.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/api/api_misspellings_generator \
        && docker-compose build
3.3 Konteineri käivitamine
    $ cd ~/git/smart_search_github/api/api_misspellings_generator \
        && docker-compose up -d
3.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 2.4
3.5 Konteineri peatamine
    $ cd ~/git/smart_search_github/api/api_misspellings_generator \
        && docker-compose down
----------------------------------------------
4 DockerHUBist tõmmatud konteineri kasutamine
4.1 DockerHUBist konteineri tõmbamine
    $  cd ~/git/smart_search_github/api/api_misspellings_generator \
        && docker-compose pull
4.2 Konteineri käivitamine: järgi punkti 3.3
4.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 2.4
4.4 Konteineri peatamine: järgi punkti 3.5
----------------------------------------------
5 TÜ pilves töötava konteineri kasutamine
    $ curl --silent --request POST --header "Content-Type: application/text" \
        https://smart-search.tartunlp.ai/api/misspellings_generator/version | jq
    $ curl --silent --request POST --header "Content-Type: application/text" \
        --data-binary @test.txt \
        https://smart-search.tartunlp.ai/api/misspellings_generator/process  | jq
----------------------------------------------
6 DockerHUBis oleva konteineri lisamine KUBERNETESesse
6.1 Tekitame vaikeväärtustega deployment-i

$ kubectl create deployment smart-search-api-misspellings-generator \
  --image=tilluteenused/smart_search_api_misspellings_generator:2024.01.21

6.2 Tekitame vaikeväärtustega service'i

$ kubectl expose deployment smart-search-api-misspellings-generator \
    --type=ClusterIP --port=80 --target-port=6603

6.3 Lisame ingress-i konfiguratsioonifaili

- backend:
    service:
    name: smart-search-api-misspellings-generator
    port:
        number: 80
path: /api/misspellings_generator/?(.*)
pathType: Prefix     
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
kv = api_misspellings_generator.KIRJAVIGUR(verbose=False)

app = Flask(__name__)

VERSION="2024.01.21"

#---------------------------------------------------------------------------

# JSONsisendi max suuruse piiramine {{
try:
    SMART_SEARCH_MAX_CONTENT_LENGTH=int(os.environ.get('SMART_SEARCH_MAX_CONTENT_LENGTH'))
except:
    SMART_SEARCH_MAX_CONTENT_LENGTH = 10 * 1000000000 # 10 GB 

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
# }} JSONsisendi max suuruse piiramine 

@app.errorhandler(413) # Request Entity Too Large: The data value transmitted exceeds the capacity limit.
def request_entity_too_large(e):
    return jsonify(error=str(e)), 413

@app.errorhandler(404) # The requested URL was not found on the server.
def page_not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(400) # Rotten JSON
def rotten_json(e):
    return jsonify(error=str(e)), 400

@app.errorhandler(500) # Internal Error
def internal_error(e):
    return jsonify(error=str(e)), 500

#---------------------------------------------------------------------------

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
        abort(500, description=str(e))

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



        

        
        
    

#!/usr/bin/env python3

""" 
----------------------------------------------

Flask veebiserver, pakendab lemmapõhise päringute normaliseerija veebiteenuseks

----------------------------------------------

Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2), veebiteenuse käivitamine pythoni koodist (1.3) ja CURLiga veebiteenuse kasutamise näited (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/api/paring_soned
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd ~/git/smart_search_github/api/paring_soned
    $ TOKENIZER='https://smart-search.tartunlp.ai/api/tokenizer/process' \
      ANALYSER='https://smart-search.tartunlp.ai/api/analyser/process' \
      GENERATOR='https://smart-search.tartunlp.ai/api/generator/process' \
        venv/bin/python3 ./flask_api_paring_soned.py
1.4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"content": "katus profiil"}' \
        localhost:6609/api/paring-soned/json | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"content": "katus profiil"}' \
        localhost:6609/api/paring-soned/text
    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:6609/api/paring-soned/version | jq  

----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja CURLiga veebiteenuse kasutamise näited  (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/api/paring_soned
    $ docker build -t tilluteenused/smart_search_api_paring_soned:2023.06.02 .
2.3 Konteineri käivitamine
    $ docker run -p 6609:6609  \
        --env TOKENIZER='https://smart-search.tartunlp.ai/api/tokenizer/process' \
        --env ANALYSER='https://smart-search.tartunlp.ai/api/analyser/process' \
        --env GENERATOR='https://smart-search.tartunlp.ai/api/generator/process' \
        tilluteenused/smart_search_api_paring_soned:2023.06.02
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_api_paring_soned:2023.06.02 
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"content": "katus profiil"}' \
        https://smart-search.tartunlp.ai/api/paring-soned/json | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"content": "katus profiil"}' \
        https://smart-search.tartunlp.ai/api/paring-soned/text
    $ curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai//api/paring-soned/version | jq  

----------------------------------------------
"""
import subprocess
import json
import argparse
from flask import Flask, request, jsonify, make_response

import api_paring_soned

paring = api_paring_soned.PARING_SONED()
app = Flask("sonedega")

@app.route('/api/paring-soned/json', methods=['POST'])
@app.route('/json', methods=['POST'])
def paring_json():
    try:   
        json_response = paring.paring_json(request.json)
        return jsonify(json_response)
    except Exception as e:
        json_response = e
    
@app.route('/api/paring-soned/text', methods=['POST'])
@app.route('/text', methods=['POST'])
def paring_text():
    try:   
        txt_response = make_response(paring.paring_text(request.json))
        txt_response.headers["Content-type"] = "text/html; charset=utf-8"
    except Exception as e:
        txt_response = e
    return txt_response

@app.route('/api/paring-soned/version', methods=['POST'])
@app.route('/version', methods=['POST'])
def version():
    """Kuvame versiooni ja muud infot

    Returns:
        ~flask.Response: Lemmatiseerija versioon
    """
    json_response = paring.version_json()
    return jsonify(json_response)

if __name__ == '__main__':
    default_port=6609
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

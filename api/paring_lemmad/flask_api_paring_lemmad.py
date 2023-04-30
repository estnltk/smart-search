#!/usr/bin/env python3

""" 
# Eeldused
$ docker run -p 6000:6000 tilluteenused/estnltk_sentok:2023.04.18 # käivitame sõnestaja konteineri
$ docker run -p 7007:7007 tilluteenused/vmetajson:2023.04.19      # käivitame morfoloogilise analüsaatori konteineri

# Serveri käivitamine käsurealt
$ ./create_venv.sh                                       # virtuaalkeskkonna tegemine, ühekordne tegevus
$ ./venv/bin/python3 ./flask_api_paring_lemmad.py       # käivitame veebiserveri loodud virtuaalkeskkonnas

# Serveri käivitamine konteinerist
$ cd ~/git/smart_search_github/api_indekseerija/paring_lemmad
$ docker build -t tilluteenused/smart_search_api_paring_lemmad:2023.04.21 .        # konteineri tegemine, ühekordne tegevus
$ docker run -p 6608:6608  \
    --env TOKENIZER_IP=$(hostname -I | sed 's/^\([^ ]*\) .*$/\1/') \
    --env ANALYSER_IP=$(hostname -I | sed 's/^\([^ ]*\) .*$/\1/') \
    tilluteenused/smart_search_api_paring_lemmad:2023.04.21

# Päringute näited:

$ curl --silent --request POST --header "Content-Type: application/json" localhost:6608/version

$ curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"content": "katus profiil"}' \
  localhost:6608/json | jq

$ curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"content": "katus profiil"}' \
  localhost:6608/api/paring_lemmad/json | jq

$ curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"content": "katus profiil"}' \
  localhost:6608/api/paring_lemmad/text
"""
import subprocess
import json
import argparse
from flask import Flask, request, jsonify, make_response

import api_paring_lemmad

paring = api_paring_lemmad.PARRING_LEMMAD()
app = Flask("lemmadega_paring")

@app.route('/api/paring-lemmad/json', methods=['POST'])
@app.route('/json', methods=['POST'])
def paring_json():
    try:   
        json_response = paring.paring_json(request.json)
        return jsonify(json_response)
    except Exception as e:
        json_response = e
    
@app.route('/api/paring-lemmad/text', methods=['POST'])
@app.route('/text', methods=['POST'])
def paring_text():
    try:   
        csv_response = make_response(paring.paring_text(request.json))
        csv_response.headers["Content-type"] = "text/html; charset=utf-8"
    except Exception as e:
        csv_response = e
    return csv_response

@app.route('/api/paring-lemmad/version', methods=['POST'])
@app.route('/version', methods=['POST'])
def version():
    """Kuvame versiooni ja muud infot

    Returns:
        ~flask.Response: Lemmatiseerija versioon
    """
    json_response = {"version":paring.version_json()}
    return jsonify(json_response)

if __name__ == '__main__':
    default_port=6608
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

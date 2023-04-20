 #!/usr/bin/env python3

# VERSION võta api_lemmade_indekseerija'jast

""" 
# Eeldused
$ docker run -p 6000:6000 tilluteenused/estnltk_sentok:2023.04.18 # käivitame sõnestaja konteineri
$ docker run -p 7007:7007 tilluteenused/vmetajson:2023.04.19      # käivitame morfoloogilise analüsaatori konteineri

# Serveri käivitamine käsurealt
$ ./create_venv.sh                                       # virtuaalkeskkonna tegemine, ühekordne tegevus
$ ./venv/bin/python3 ./flask_api_lemmade_indekseerija.py # käivitame veebiserveri loodud virtuaalkeskkonnas

# Serveri käivitamine konteinerist
$ cd ~/git/smart_search_github/api_indekseerija/indekseerija_lemmad
$ docker build -t tilluteenused/smart_search_api_lemmade_indekseerija:2023.04.20 .        # konteineri tegemine, ühekordne tegevus
$ docker run -p 6607:6607  \
    --env TOKENIZER_IP=$(hostname -I | sed 's/^\([^ ]*\) .*$/\1/') \
    --env ANALYSER_IP=$(hostname -I | sed 's/^\([^ ]*\) .*$/\1/') \
    tilluteenused/smart_search_api_lemmade_indekseerija:2023.04.20

# Päringute näited:

$ curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"sources": {"DOC_1":{"content":"Jahimehed jahikoertega."},"DOC_2":{"content":"Daam sülekoeraga ja mees jahikoeraga."}}}' \
  localhost:6607/api/lemmade-indekseerija/json

$ curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"sources": {"DOC_1":{"content":"Jahimehed jahikoertega."},"DOC_2":{"content":"Daam sülekoeraga ja mees jahikoeraga."}}}' \
  localhost:6607/api/lemmade-indekseerija/csv

$ curl --silent --request POST --header "Content-Type: application/json" \
  localhost:6607/api/lemmade-indekseerija/version

$ curl --silent --request POST --header "Content-Type: application/json" \
  https://smart-search.tartunlp.ai/api/lemmade-indekseerija/version | jq  
"""

import subprocess
import json
import argparse
from flask import Flask, request, jsonify, make_response

import api_lemmade_indekseerija

indekseerija = api_lemmade_indekseerija.LEMMADE_IDX()
app = Flask("lemmade_indeks")

@app.route('/api/lemmade-indekseerija/json', methods=['POST'])
@app.route('/json', methods=['POST'])
def sonede_indeks_json():
    try:   
        json_response = indekseerija.tee_lemmade_indeks(request.json, True, False)
    except Exception as e:
        json_response = e
    return jsonify(json_response)

@app.route('/api/lemmade-indekseerija/csv', methods=['POST'])
@app.route('/csv', methods=['POST'])
def sonede_indeks_csv():
    try:   
        json_response = indekseerija.tee_lemmade_indeks(request.json, True, False)
        # Teeme JSONist CSVlaadse moodustise
        csv_str = ''
        for sone in json_response["index"]:
            for docid in json_response["index"][sone]:
                for k in json_response["index"][sone][docid]:
                    csv_str += f'{sone}\t{k["liitsõna_osa"]}\t{json_response["sources"][docid]["content"][k["start"]:k["end"]]}\t{docid}\t{k["start"]}\t{k["end"]}\n'
        csv_response = make_response(csv_str)
        csv_response.headers["Content-type"] = "text/csv; charset=utf-8"
    except Exception as e:
        csv_response = e
    return csv_response

@app.route('/api/lemmade-indekseerija/version', methods=['POST'])
@app.route('/version', methods=['POST'])
def version():
    """Kuvame versiooni ja muud infot

    Returns:
        ~flask.Response: Lemmatiseerija versioon
    """
    json_response = {"version":indekseerija.VERSION, "tokenizer":indekseerija.tokenizer, "analyser":indekseerija.analyser}
    return jsonify(json_response)

if __name__ == '__main__':
    default_port=6607
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

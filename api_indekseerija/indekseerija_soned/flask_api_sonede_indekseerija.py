 #!/usr/bin/env python3

VERSION="2023.04.18"

""" 
# Eeldused
$ docker run -p 6000:6000 tilluteenused/estnltk_sentok:2023.04.18 # käivitame sõnestaja konteineri
$ docker run -p 7007:7007 tilluteenused/vmetajson:2023.04.19      # käivitame morfoloogilise analüsaatori konteineri

# Serveri käivitamine käsurealt
$ ./create_venv.sh                                      # virtuaalkeskkonna tegemine, ühekordne tegevus
$ ./venv/bin/python3 ./flask_api_sonede_indekseerija.py # käivitame veebiserveri loodud virtuaalkeskkonnas

# Serveri käivitamine konteinerist
$ cd ~/git/smart_search_github/api_indekseerija/indekseerija_soned
$ docker build -t tilluteenused/smart_search_api_sonede_indekseerija:2023.04.20 .        # konteineri tegemine, ühekordne tegevus
$ docker run -p 6606:6606  \
    --env TOKENIZER_IP=$(hostname -I | sed 's/^\([^ ]*\) .*$/\1/') \
    --env ANALYSER_IP=$(hostname -I | sed 's/^\([^ ]*\) .*$/\1/') \
    tilluteenused/smart_search_api_sonede_indekseerija:2023.04.20

# Päringute näited:
$ curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"sources": {"DOC_1":{"content":"Daam koerakesega."},"DOC_2":{"content":"Härra ja daam. Daam sülekoeraga ja härra hundikoeraga."}}}' \
  http://127.0.0.1:6606/json | jq
$ curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"sources": {"DOC_1":{"content":"Daam koerakesega."},"DOC_2":{"content":"Härra ja daam. Daam sülekoeraga ja härra hundikoeraga."}}}' \
  http://127.0.0.1:6606/csv
$ curl --silent --request POST --header "Content-Type: application/json" \
  http://127.0.0.1:6606/version | jq

$ curl --silent --request POST --header "Content-Type: application/json" \
  https://smart-search.tartunlp.ai/api/sonede-indekseerija/version | jq  
"""

import subprocess
import json
import argparse
from flask import Flask, request, jsonify, make_response
import re

import api_sonede_indekseerija

indekseerija = api_sonede_indekseerija.SONEDE_IDX()
app = Flask("sonede_indeks")

@app.route('/api/sonede-indekseerija/json', methods=['POST'])
@app.route('/json', methods=['POST'])
def sonede_indeks_json():
    try:   
        json_response = indekseerija.leia_soned_osasoned(request.json, True, False)
    except Exception as e:
        json_response = e
    return jsonify(json_response)

@app.route('/api/sonede-indekseerija/csv', methods=['POST'])
@app.route('/csv', methods=['POST'])
def sonede_indeks_csv():
    try:   
        json_response = indekseerija.leia_soned_osasoned(request.json, True, False)
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

@app.route('/api/sonede-indekseerija/version', methods=['POST'])
@app.route('/version', methods=['POST'])
def version():
    """Kuvame versiooni ja muud infot

    Returns:
        ~flask.Response: Lemmatiseerija versioon
    """
    json_response = {"version":indekseerija.VERSION, "tokenizer":indekseerija.tokenizer, "analyser":indekseerija.analyser}
    return jsonify(json_response)

if __name__ == '__main__':
    default_port=6606
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

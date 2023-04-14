 #!/usr/bin/env python3

VERSION="2023.03.30"

""" 
# Virtuaalkeskkonna loomine:
$ ./create_venv

# Serveri käivitamine käsurealt
$ ./create_venv.sh # tekitame virtuaalkeskkonna, ühekordne tegevus
$ ./venv/bin/python3 ./flask_api_sonede_indekseerija.py # käivitame veebiserveri loodid virtuaalkeskkonnas

# Päringute näited:
$ curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Vanamehe kodujuustu peeti keaks."}' localhost:6606/process|jq
$ curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Vanamehe kodujuustu peeti keaks .","params":{"vmetltjson":["--guess"]}}' localhost:5000/process|jq

# Konteineri tegemine:
$ docker build -t tilluteenused/flask_api_indekseerija:2023.04.10 . 

# Konteineri käivitamine:
$ docker run -p 6606:6606  tilluteenused/flask_api_sonede_indekseerija:2023.04.10

# Päringute näited:
$ curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Vanamehe kodujuustu peeti keaks ."}' localhost:7000/process|jq
$ curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Vanamehe kodujuustu peeti keaks .","params":{"vmetltjson":["--guess"]}}' localhost:7000/process|jq
"""

import subprocess
import json
import argparse
from flask import Flask, request, jsonify, make_response
import re

import api_sonede_indekseerija

app = Flask("sonede_indeks")

'''
 
curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"sources": {"DOC_1":{"content":"Daam koerakesega."},"DOC_2":{"content":"Härra ja daam. Daam sülekoeraga ja härra hundikoeraga."}}}' \
  http://127.0.0.1:6606/sonede_indeks_json | jq
'''

@app.route('/sonede_indeks_json', methods=['GET', 'POST'])
def sonede_indeks_json():
    indekseerija = api_sonede_indekseerija.SONEDE_IDX()
    try:   
        json_response = indekseerija.leia_soned_osasoned(request.json, True, False)
    except Exception as e:
        json_response = e
    return jsonify(json_response)

'''
 
curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"sources": {"DOC_1":{"content":"Daam koerakesega."},"DOC_2":{"content":"Härra ja daam. Daam sülekoeraga ja härra hundikoeraga."}}}' \
  http://127.0.0.1:6606/sonede_indeks_csv
'''

@app.route('/sonede_indeks_csv', methods=['GET', 'POST'])
def sonede_indeks_csv():
    indekseerija = api_sonede_indekseerija.SONEDE_IDX()
    try:   
        json_response = indekseerija.leia_soned_osasoned(request.json, True, False)
        # Teeme JSONist CSVlaadse moodustise
        csv_str = ''
        for doc in json_response:
            for sone in json_response["index"]:
                for docid in json_response["index"][sone]:
                    for k in json_response["index"][sone][docid]:
                        #csv_list.append([ sone, k["liitsõna_osa"], json_response["sources"][docid]["content"][k["start"]:k["end"]], docid, k["start"], k["end"] ])
                        csv_str += f'{sone}\t{k["liitsõna_osa"]}\t{json_response["sources"][docid]["content"][k["start"]:k["end"]]}\t{docid}\t{k["start"]}\t{k["end"]}\n'
        csv_response = make_response(csv_str)
        csv_response.headers["Content-type"] = "text/csv" 
    except Exception as e:
        csv_response = e
    return csv_response


@app.route('/version', methods=['POST']) #@app.route('/process', methods=['GET', 'POST'])
def version():
    """Kuvame versiooni

    Returns:
        ~flask.Response: Lemmatiseerija versioon
    """
    return jsonify(json.loads(f'{{"version":"{VERSION}"}}'))

if __name__ == '__main__':
    default_port=6606
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

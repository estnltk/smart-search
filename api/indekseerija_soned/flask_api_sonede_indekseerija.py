 #!/usr/bin/env python3

VERSION="2023.04.20"

""" 
----------------------------------------------

Flask veebiserver, pakendab sõnepõhise indekseerija veebiteenuseks

----------------------------------------------

Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2), veebiteenuse käivitamine pythoni koodist (1.3) ja CURLiga veebiteenuse kasutamise näited (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/api/indekseerija_soned
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ TOKENIZER='https://smart-search.tartunlp.ai/api/tokenizer/process' \
      ANALYSER='https://smart-search.tartunlp.ai/api/analyser/process' \
        venv/bin/python3 flask_api_sonede_indekseerija.py
1.4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Jahimehed jahikoertega."},"DOC_2":{"content":"Daam sülekoeraga ja mees jahikoeraga."}}}' \
        localhost:6606/api/sonede-indekseerija/json | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Jahimehed jahikoertega."},"DOC_2":{"content":"Daam sülekoeraga ja mees jahikoeraga."}}}' \
        localhost:6606/api/sonede-indekseerija/csv
    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:6606/api/sonede-indekseerija/version | jq  

----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja CURLiga veebiteenuse kasutamise näited  (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/api/indekseerija_soned
    $ docker build -t tilluteenused/smart_search_api_sonede_indekseerija:2023.04.20 . 
2.3 Konteineri käivitamine
    $ docker run -p 6606:6606  \
        --env TOKENIZER='https://smart-search.tartunlp.ai/api/tokenizer/process' \
        --env ANALYSER='https://smart-search.tartunlp.ai/api/analyser/process' \
        tilluteenused/smart_search_api_sonede_indekseerija:2023.04.20 
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_api_sonede_indekseerija:2023.04.20 
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Jahimehed jahikoertega."},"DOC_2":{"content":"Daam sülekoeraga ja mees jahikoeraga."}}}' \
        https://smart-search.tartunlp.ai/api/sonede-indekseerija/json | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Jahimehed jahikoertega."},"DOC_2":{"content":"Daam sülekoeraga ja mees jahikoeraga."}}}' \
        https://smart-search.tartunlp.ai/api/sonede-indekseerija/csv
    $ curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/sonede-indekseerija/version | jq  
----------------------------------------------
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

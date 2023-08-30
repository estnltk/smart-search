#!/usr/bin/python3

'''Flask api, eelarvuta kõigi sisendkorpuses esinevate lemmade kõikvõimalikud vormid
ja millised neist esinevad tegelikult korpuses esinevad

----------------------------------------------

Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2), veebiteenuse käivitamine pythoni koodist (1.3) ja CURLiga veebiteenuse kasutamise näited (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/api/paringu_ettearvutaja
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd  ~/git/smart_search_github/api/paringu_ettearvutaja
    $ OTSING_SONED='https://smart-search.tartunlp.ai/api/sonede-indeks/check' \
      TOKENIZER='https://smart-search.tartunlp.ai/api/tokenizer/process'   \
      ANALYSER='https://smart-search.tartunlp.ai/api/analyser/process'     \
      GENERATOR='https://smart-search.tartunlp.ai/api/generator/process'   \
      INDEKSEERIJA_LEMMAD='https://smart-search.tartunlp.ai/api/lemmade-indekseerija' \
        venv/bin/python3 ./flask_api_paringu_ettearvutaja.py
1.4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Presidendi kantselei."},"DOC_2":{"content":"Kuidas valitakse presidenti. Valimissüsteemi alused."}}}' \
        localhost:6602/api/paringu-ettearvutaja/json | jq | less

    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Presidendi kantselei."},"DOC_2":{"content":"Kuidas valitakse presidenti. Valimissüsteemi alused."}}}' \
        localhost:6602/api/paringu-ettearvutaja/csv | less

    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:6602/api/paringu-ettearvutaja/version | jq

----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja CURLiga veebiteenuse kasutamise näited  (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd  ~/git/smart_search_github/api/paringu_ettearvutaja
    $ docker build -t tilluteenused/smart_search_api_paringu_ettearvutaja:2023.08.22 . 
2.3 Konteineri käivitamine
    $ docker run -p 6602:6602  \
        --env OTSING_SONED='https://smart-search.tartunlp.ai/api/sonede-indeks/check' \
        --env TOKENIZER='https://smart-search.tartunlp.ai/api/tokenizer/process' \
        --env ANALYSER='https://smart-search.tartunlp.ai/api/analyser/process' \
        --env GENERATOR='https://smart-search.tartunlp.ai/api/generator/process' \
        --env INDEKSEERIJA_LEMMAD='https://smart-search.tartunlp.ai/api/lemmade-indekseerija' \
        tilluteenused/smart_search_api_paringu_ettearvutaja:2023.08.22 
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_api_paringu_ettearvutaja:2023.08.22 
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Presidendi kantselei."},"DOC_2":{"content":"Kuidas valitakse presidenti. Valimissüsteemi alused."}}}' \
        https://smart-search.tartunlp.ai/api/paringu-ettearvutaja/json | jq

    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Presidendi kantselei."},"DOC_2":{"content":"Kuidas valitakse presidenti. Valimissüsteemi alused."}}}' \
        https://smart-search.tartunlp.ai/api/paringu-ettearvutaja/csv

    $ curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/paringu-ettearvutaja/version | jq

----------------------------------------------

'''


import os
import sys
import json
import requests
import subprocess
import json
import argparse
from flask import Flask, request, jsonify, make_response
from typing import Dict, List, Tuple
from collections import OrderedDict

import api_paringu_ettearvutaja

ettearvutaja = api_paringu_ettearvutaja.ETTEARVUTAJA(None, False)

app = Flask("api_lemmade_ettervutaja")

@app.route('/api/paringu-ettearvutaja/json', methods=['POST'])
@app.route('/json', methods=['POST'])
def api_lemmade_ettearvutaja_json():
    """Leia sisendkorpuse sõnede kõikvõimalikud vormid ja nonde hulgast need, mis esinesid korpuses

    Args:

        request.json: // SisendJSON, sisaldab korpusetekste

        {   "sources":
            {   DOCID:              // dokumendi ID
                {   "content": str  // dokumendi tekst ("plain text", märgendus vms teraldi tõstetud)
                                    // dokumendi kohta käiv lisainfo pane siia...
                }
            }
        }

    Returns:
        Response: VäljundJSON:

        {   "index":
            {   "lemma_paradigma_korpuses": # järjestatud LEMMA järgi
                {   LEMMA: [VORM] # LEMMA esines korpuses VORMides
                }
                "vorm_lemmaks":
                {   VORM: [LEMMA]   # sõnavormile vastavad lemmad, järjestatud VORMi järgi
                }
            }
        } 
    """
    try:
        ettearvutaja.tee_lemmade_indeks(request.json)
        ettearvutaja.tee_json()
        return jsonify(ettearvutaja.json_io)
    except Exception as e:
        return jsonify(e.args[0])    

@app.route('/api/paringu-ettearvutaja/version', methods=['GET', 'POST'])
@app.route('/version', methods=['POST'])
def api_lemmade_ettearvutaja_version():
    """Kuvame versiooni ja muud infot

    Returns:
        ~flask.Response: Lemmatiseerija versioon
    """
    json_response = ettearvutaja.version_json()
    return jsonify(json_response)

if __name__ == '__main__':
    default_port=6602
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)



        

        
        
    
 #!/usr/bin/env python3

""" 
----------------------------------------------

Flask veebiserver sindsõnede tüvede ja lemmade leidmiseks.
Kasutab Filosofti morfoloogilist analüsaatorit.

----------------------------------------------
Serveri käivtamine code'is, päringud vt 1.4
    {
        "name": "flask_api_lemmatiser",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/api_lemmatizer/",
        "program": "./flask_api_lemmatizer.py",
        "env": {},
        "args": []
    },
----------------------------------------------
Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2), veebiteenuse käivitamine pythoni koodist (1.3) ja CURLiga veebiteenuse kasutamise näited (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone https://github.com/estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/api/api_lemmatizer
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd ~/git/smart_search_github/api/api_lemmatizer
    $ venv/bin/python3 ./flask_api_lemmatizer.py
1.4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"kinnipeetuga\tpeeti\tallmaaraudteejaamas"}' \
        localhost:7009/api/lemmatizer/json | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"kinnipeetuga\tpeeti\tallmaaraudteejaamas"}' \
        localhost:7009/api/lemmatizer/tsv
    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:7009/api/lemmatizer/version | jq
----------------------------------------------
Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja CURLiga veebiteenuse kasutamise näited  (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/api/api_lemmatizer
    $ docker build -t tilluteenused/smart_search_api_lemmatizer:2024.01.10 .
    # docker login -u tilluteenused
    # docker push tilluteenused/smart_search_api_lemmatizer:2024.01.10
2.3 Konteineri käivitamine
    $ docker run -p 7009:7009 tilluteenused/smart_search_api_lemmatizer:2024.01.10
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4
----------------------------------------------
DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_api_lemmatizer:2024.01.10
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4
----------------------------------------------
TÜ pilves töötava konteineri kasutamine
4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"kinnipeetuga\tpeeti\tallmaaraudteejaamas"}' \
         https://smart-search.tartunlp.ai/api/lemmatizer/json | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"kinnipeetuga\tpeeti\tallmaaraudteejaamas"}' \
         https://smart-search.tartunlp.ai/api/lemmatizer/tsv
    $ curl --silent --request POST --header "Content-Type: application/json" \
         https://smart-search.tartunlp.ai/api/lemmatizer/version | jq
"""

import sys
import subprocess
import json
import argparse
from flask import Flask, request, jsonify, make_response

import api_lemmatizer4ss

VERSION="2024.01.10"

app = Flask("api_lemmatizer")
sll = api_lemmatizer4ss.LEMMATIZER4SL()

@app.route('/api/lemmatizer/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def api_lemmatizer_version():
    """Tagastame veebiliidese versiooni

    Returns:
        ~flask.Response: JSONkujul versioonistring
    """
    return jsonify({"api_version":sll.VERSION, "flask_liidese_versiooon":  VERSION})

@app.route('/api/lemmatizer/tsv', methods=['POST'])
@app.route('/tsv', methods=['POST'])
def api_sl_lemmatizer_tsv():
    """Morf analüüsime JSONiga antud sõnesid ja kuvame tulemust JSONkujul
    Sisse
        {"tss":str}   // TAB separeated strings/tokens
        
    Returns:
        ~flask.Response: Morf analüüsi tulemused

        {   "tokens": 
            {   TOKEN:      // sisendsõne
                {   LEMMA:  // sisendsõne lemma
                    [SUBLEMMA], // liitsõna korral osalemmad
                }
            }
        }      
    """
    if request.json is None or "tss" not in request.json:
        return jsonify({"warning": "the request does not contain valid JSON"})
    else:
        res_list = sll.lemmatizer2list(request.json["tss"].split("\t"))
        res_tsv = "location\ttoken\tstem\tis_component\tweight\tlemmas\n"
        for location, token, stem,  is_component, weight, lemmas in res_list:
            res_tsv += f"{location}\t{token}\t{stem}\t{is_component}\t{weight}\t{lemmas}\n"
        response = make_response(res_tsv)
    response.headers["Content-type"] = "text/tsv"
    return response

@app.route('/api/lemmatizer/json', methods=['POST'])
@app.route('/json', methods=['POST'])
def api_lemmatizer_json():
    """Morf analüüsime JSONiga antud sõnesid ja kuvame tulemust JSONkujul
    Sisse
        {"tss":str}   // TAB separeated strings/tokens

    Returns:
        ~flask.Response: Morf analüüsi tulemused

        {   "tokens": 
            {   TOKEN:      // sisendsõne
                {   LEMMA:  // sisendsõne lemma
                    [SUBLEMMA], // liitsõna korral osalemmad
                }
            }
        }      
    """
    if request.json is None or "tss" not in request.json:
        return jsonify({"warning": "the request does not contain valid JSON"})
    res = sll.lemmatizer2json(request.json["tss"].split("\t"))
    return jsonify(res)

if __name__ == '__main__':
    import argparse
    default_port=7009
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug',  action="store_true", help='debug flag for flask')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

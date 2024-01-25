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
    $ cd ~/git/smart_search_github/api/api_lemmatizer \
        && ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd ~/git/smart_search_github/api/api_lemmatizer \
        && venv/bin/python3 ./flask_api_lemmatizer.py
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
    $ cd ~/git/smart_search_github/api/api_lemmatizer \
        && docker-compose build
2.3 Konteineri käivitamine
    $ cd ~/git/smart_search_github/api/api_lemmatizer \
        && docker-compose up -d
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4
2.5 Konteineri peatamine
    $ cd ~/git/smart_search_github/api/api_lemmatizer \
        && docker-compose down
----------------------------------------------
DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ cd ~/git/smart_search_github/api/api_lemmatizer \
        && docker-compose pull
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4
3.4 Konteineri peatamine: järgi punkti 2.5
----------------------------------------------
4 TÜ pilves töötava konteineri kasutamine
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"kinnipeetuga\tpeeti\tallmaaraudteejaamas"}' \
         https://smart-search.tartunlp.ai/api/lemmatizer/json | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"kinnipeetuga\tpeeti\tallmaaraudteejaamas"}' \
         https://smart-search.tartunlp.ai/api/lemmatizer/tsv
    $ curl --silent --request POST --header "Content-Type: application/json" \
         https://smart-search.tartunlp.ai/api/lemmatizer/version | jq
----------------------------------------------
5 DockerHUBis oleva konteineri lisamine KUBERNETESesse
4.1 Tekitame vaikeväärtustega deployment-i

$ kubectl create deployment smart-search-api-lemmatizerr \
  --image=tilluteenused/smart_search_api_advanced_indexing:2024.01.10

5.2 Tekitame vaikeväärtustega service'i

$ kubectl expose deployment smart-search-api-lemmatizer \
    --type=ClusterIP --port=80 --target-port=7009

5.3 Lisame ingress-i konfiguratsioonifaili

- backend:
    service:
    name: smart-search-api-lemmatizer
    port:
        number: 80
path: /api/lemmatizer/?(.*)
pathType: Prefix        
----------------------------------------------
"""

import sys
import subprocess
import json
import argparse
import os
from flask import Flask, request, jsonify, make_response, abort
from functools import wraps

import api_lemmatizer4ss
sll = api_lemmatizer4ss.LEMMATIZER4SL()

VERSION="2024.01.21"

app = Flask(__name__)

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

@app.route('/api/lemmatizer/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_lemmatizer_version():
    """Tagastame veebiliidese versiooni

    Returns:
        ~flask.Response: JSONkujul versioonistring
    """
    return jsonify({"api_version":sll.VERSION, 
        "flask_liidese_versiooon":  VERSION,
        "SMART_SEARCH_MAX_CONTENT_LENGTH": SMART_SEARCH_MAX_CONTENT_LENGTH})

@app.route('/api/lemmatizer/tsv', methods=['POST'])
@app.route('/tsv', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
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
    try:
        request_json = json.loads(request.data)
    except ValueError as e:
        abort(400, description=str(e))  

    try:
        res_list = sll.lemmatizer2list(request_json["tss"].split("\t"))
        res_tsv = "location\ttoken\tstem\tis_component\tweight\tlemmas\n"
        for location, token, stem,  is_component, weight, lemmas in res_list:
            res_tsv += f"{location}\t{token}\t{stem}\t{is_component}\t{weight}\t{lemmas}\n"
        response = make_response(res_tsv)
        response.headers["Content-type"] = "text/tsv"
    except Exception as e:
        abort(500, description=str(e))

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
    try:
        request_json = json.loads(request.data)
    except ValueError as e:
        abort(400, description=str(e)) 
    try:
        res = sll.lemmatizer2json(request_json["tss"].split("\t"))
    except Exception as e:
        abort(500, description=str(e))  
          
    return jsonify(res)

if __name__ == '__main__':
    import argparse
    default_port=7009
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug',  action="store_true", help='debug flag for flask')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

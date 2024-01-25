 #!/usr/bin/env python3

""" 
----------------------------------------------
Flask veebiserver, pakendab Filosofti morfoloogilise süntesaatori veebiteenuseks,
smartsearch projektile kohendatud versioon.

Mida uut:
* 2024-01-21 Veakäsitlust parandatud

----------------------------------------------
Silumiseks (serveri käivtamine code'is, päringud vt 1.4):
    {
        "name": "flask_api_generator.py",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/api_generator/",
        "program": "./flask_api_generator.py",
        "env": {},
        "args": []
    },
----------------------------------------------
Lähtekoodist pythoni skripti kasutamine
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone https://github.com/estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/api/api_generator \
        && ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd ~/git/smart_search_github/api/api_generator \
        && venv/bin/python3 flask_api_generator.py
1.4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"tere\tpidama"}' \
        localhost:7008/api/sl_generator/tss
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":["with_apostrophe"], "tss":"Strassbourg"}' \
        localhost:7008/api/sl_generator/tss
    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:7008/api/sl_generator/version
----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/api/api_generator \
        && docker-compose build
2.3 Konteineri käivitamine
    $ cd ~/git/smart_search_github/api/api_generator \
        && docker-compose up -d
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4
2.5 Konteineri peatamine
    $ cd ~/git/smart_search_github/api/api_generator \
        && docker-compose down
----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_api_generator.2024.01.21 
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"tere\ttalv"}' \
        https://smart-search.tartunlp.ai/api/generator/tss
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":["with_apostrophe"], "tss":"Strassbourg"}' \
        https://smart-search.tartunlp.ai/api/generator/tss
    $ curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/generator/version

----------------------------------------------
DockerHubis oleva konteineri lisamine oma KUBERNETESesse

kubectl create deployment smart-search-api-generator \
  --image=tilluteenused/smart_search_api_generator:2024.01.21

kubectl expose deployment smart-search-api-generator \
    --type=ClusterIP --port=80 --target-port=7008

kubectl edit ingress smart-search-api-ingress

- backend:
    service:
    name: smart-search-api-generator
    port:
        number: 80
path: /api/generator/?(.*)
pathType: Prefix
"""

import subprocess
import json
import argparse
import os
from flask import Flask, request, jsonify, make_response, abort
from functools import wraps

import api_generator
slg = api_generator.GENERATOR4SL()

VERSION = "2024.01.21"

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

@app.route('/api/sl_generator/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_sl_generator_version():
    """Tagastame veebiliidese versiooni

    Returns:
        ~flask.Response: JSONkujul versioonistring
    """
    return jsonify({"api-versioon":slg.VERSION, 
        "FLASK-liidese versioon": VERSION, 
        "SMART_SEARCH_MAX_CONTENT_LENGTH": SMART_SEARCH_MAX_CONTENT_LENGTH})

@app.route('/api/sl_generator/tss', methods=['POST'])
@app.route('/tss', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_sl_generator_process_tsv():
    """Morf sünteesime JSONiga nõutud lemmade+vormid ja kuvame tulemust TSV-kujul

    Returns:
        ~flask.Response: Morf sünteesi tulemused
    """
    try:
        request_json = json.loads(request.data)
    except ValueError as e:
        abort(400, description=str(e))   

    try:
        with_apostrophe = False
        if "params" in request_json:
            if "with_apostrophe" in request_json["params"]:
                with_apostrophe = True
        res_list = slg.generator2list(request_json["tss"].split('\t'), with_apostrophe)
        res_str = ''
        for line in res_list:
            res_str += f'{str(line[0])}\t{line[1]}\t{line[2]}\t{line[3]}\n'
        response = make_response(res_str)
        response.headers["Content-type"] = "text/tsv"
    except Exception as e:
        abort(500, description=str(e))

    return response

if __name__ == '__main__':
    default_port=7008
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

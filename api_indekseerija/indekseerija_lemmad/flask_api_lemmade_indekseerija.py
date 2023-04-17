 #!/usr/bin/env python3

VERSION="2023.03.30"

""" 
# Virtuaalkeskkonna loomine:
$ ./create_venv

# Serveri käivitamine käsurealt
$ ./create_venv.sh # tekitame virtuaalkeskkonna, ühekordne tegevus
$ ./venv/bin/python3 ./flask_api_indekseerija.py # käivitame veebiserveri loodid virtuaalkeskkonnas

# Päringute näited:
$ curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Vanamehe kodujuustu peeti keaks."}' localhost:6606/process|jq
$ curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Vanamehe kodujuustu peeti keaks .","params":{"vmetltjson":["--guess"]}}' localhost:5000/process|jq

# Konteineri tegemine:
$ docker build -t tilluteenused/flask_api_indekseerija:2023.04.10 . 

# Konteineri käivitamine:
$ docker run -p 6606:6606  tilluteenused/flask_api_indekseerija:2023.04.10

# Päringute näited:
$ curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Vanamehe kodujuustu peeti keaks ."}' localhost:7000/process|jq
$ curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Vanamehe kodujuustu peeti keaks .","params":{"vmetltjson":["--guess"]}}' localhost:7000/process|jq
"""

import subprocess
import json
import argparse
from flask import Flask, request, jsonify

import api_lemmade_indekseerija

app = Flask("leia_koik_lemmad")

@app.route('/process', methods=['GET', 'POST'])
@app.route('/leia_lemmad', methods=['GET', 'POST'])
def leia_lemmad():
    if "content" not in request.json:
        request.json["warnings"] = ["Missing content"]
        return jsonify(request.json)
    try:   
        json_response = api_lemmade_indekseerija.LEMMADE_IDX().leia_koik_lemmad(request.json)
    except Exception as e:
        json_response = e
    return jsonify(json_response)
    
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

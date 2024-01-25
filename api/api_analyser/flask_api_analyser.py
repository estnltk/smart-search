 #!/usr/bin/env python3

""" 
----------------------------------------------

Flask veebiserver, pakendab Filosofti morfoloogilise analüsaatori veebiteenuseks
JSON väljundisse lisatud eksplitsiitne liitsõna osasõnadeks tükeldamine.

Mida uut:
* 2024-01-21 VEakäsitlust parandatud
----------------------------------------------

1 Veebiserveri käivitamine pythoni koodist
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone git@github.com:estnltk/smart_search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/api/api_analyser
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd ~/git/smart_search_github/api/api_analyser
    $ venv/bin/python3 ./flask_api_analyser.py
1.4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--stem", "--guess"]} ,"tss":"punameremaoga\tlambiõliga\tpeeti\t_a"}' \
        localhost:7007/api/analyser/process | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--guess"]} ,"tss":"punameremaoga\tlambiõliga\tpeeti\t_a"}' \
        localhost:7007/api/analyser/process | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--version"]}}' \
        localhost:7007/api/analyser/process | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:7007/api/analyser/version | jq

----------------------------------------------

2 Lähtekoodist tehtud konteineri kasutamine
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/api/api_analyser \
        && docker-compose build
2.3 Konteineri käivitamine
    $  cd ~/git/smart_search_github/api/api_analyser \
        && docker-compose up -d
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4
2.5 Konteineri peatamine
    $ cd ~/git/smart_search_github/api/api_analyser \
        && docker-compose down

----------------------------------------------

3 DockerHUBist tõmmatud konteineri kasutamine
3.1 DockerHUBist konteineri tõmbamine
    $ cd ~/git/smart_search_github/api/api_analyser \
        && docker-compose pull
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4
3.5 Konteineri peatamine: järgi punnkti 2.5

----------------------------------------------

4 TÜ KUBERNETESes töötava konteineri kasutamine
4.1 CURLiga veebiteenuse kasutamise näited

    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--stem", "--guess"]} ,"tss":"punameremaoga\tlambiõliga\tpeeti\t_a"}' \
        https://smart-search.tartunlp.ai/api/analyser/process | jq

    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--guess"]} ,"tss":"punameremaoga\tlambiõliga\tpeeti\t_a"}' \
        https://smart-search.tartunlp.ai/api/analyser/process | jq

    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--version"]}}' \
       https://smart-search.tartunlp.ai/api/analyser/process | jq

    $ curl --silent --request POST --header "Content-Type: application/json" \
         https://smart-search.tartunlp.ai/api/analyser/version | jq

----------------------------------------------
4 DockerHUBis oleva konteineri lisamine KUBERNETESesse

4.1 Tekitame vaikeväärtustega deployment-i

$ kubectl create deployment smart-search-api-analyser \
  --image=tilluteenused/smart_search_api_advanced_indexing:2024.01.10

4.2 Tekitame vaikeväärtustega service'i

$ kubectl expose deployment smart-search-api-analyser \
    --type=ClusterIP --port=80 --target-port=7007

4.3 Lisame ingress-i konfiguratsioonifaili

- backend:
    service:
    name: smart-search-api-analyser
    port:
        number: 80
path: /api/analyser/?(.*)
pathType: Prefix

----------------------------------------------
"""

import subprocess
import json
import argparse
from flask import Flask, request, jsonify
import os
from flask import Flask, request, jsonify, make_response, abort
from functools import wraps

VERSION = "2024.01.21"

proc = subprocess.Popen(['./vmetajson', '--path=.'],  
                            universal_newlines=True, 
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)

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

@app.route('/api/analyser/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_analyser_version():
    """Tagastame veebiliidese versiooni

    Returns:
        ~flask.Response: JSONkujul versioonistring
    """
    return jsonify({"version":VERSION})

@app.route('/api/analyser/process', methods=['POST'])
@app.route('/process', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_analyser_process():
    """Morf analüüsime JSONiga antud sõnesid ja kuvame tulemust JSONkujul

    Returns:
        ~flask.Response: Morf analüüsi tulemused
    """

    try:
        request_json = json.loads(request.data)
    except ValueError as e:
        abort(400, description=str(e))    

    if "tss" in request_json:
        tokens = request_json["tss"].split('\t')
        if "annotations" not in request_json:
            request_json["annotations"] = {}
        if "tokens" not in request_json["annotations"]:
            request_json["annotations"]["tokens"] = []
        for token in tokens:
            request_json["annotations"]["tokens"].append({"features": {"token": token}})
    
    # assert proc.stdin is not None and proc.stdout is not None

    try:
        proc.stdin.write(f'{json.dumps(request_json)}\n')
        proc.stdin.flush()
        mrf_out = json.loads(proc.stdout.readline())
        if "annotations" in mrf_out and "tokens" in  mrf_out["annotations"]:
            for token in mrf_out["annotations"]["tokens"]:
                if "features" in token and "mrf" in token["features"]:
                    for mrf in token["features"]["mrf"]:
                        if "lemma_ma" in mrf:
                            morfa_result = mrf["lemma_ma"]
                        elif "stem" in mrf:
                            morfa_result = mrf["stem"]
                        else:
                            continue
                        mrf["lisamärkideta"] = morfa_result
                        mrf["komponendid"  ] = []
                        if len(morfa_result) >= 3:
                            mrf["lisamärkideta"] = morfa_result.replace("+", "").replace("=", "").replace("_", "")
                            mrf["komponendid"  ] = morfa_result.replace("+", "").replace("=", "").split("_")
                            if len(mrf["lisamärkideta"]) < 1:
                                mrf["lisamärkideta"] = morfa_result
                                mrf["komponendid"  ] = []
                            if len(mrf["komponendid"]) == 1:
                                mrf["komponendid"] = []
    except Exception as e:
        abort(500, description=str(e))   
    return jsonify(mrf_out)

if __name__ == '__main__':
    default_port=7007
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

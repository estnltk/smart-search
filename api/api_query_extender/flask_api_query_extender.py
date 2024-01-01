#!/usr/bin/python3

'''Flask api, päringustring päringut esitavaks JSONiks
Mida uut:
2023-12-28
* kohendatud "suggestion" ja "not_indexed" käsitlust
---------------------------------

Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2), veebiteenuse käivitamine pythoni koodist (1.3) ja CURLiga veebiteenuse kasutamise näited (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart-search_github/api/api_query_extender
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd  ~/git/smart-search_github/api/api_query_extender
    $ cp ../../demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts/koond.sqlite .
    $ SMART_SEARCH_QE_DBASE="./smart_search.sqlite" \
        venv/bin/python3 ./flask_api_query_extender.py
1.4 CURLiga veebiteenuse kasutamise näited

    $ curl --silent --request POST \
        --header "Content-Type: application/json" \
        --data "{\"tss\":\"presitendi\\tpresidendiga\", \"params\":{\"otsi_liitsõnadest\":\"false\"}}" \
        localhost:6604/api/query_extender/tsv
        
    $ curl --silent --request POST \
        --header "Content-Type: application/json" \
        --data "{\"tss\":\"presitendi\\tpresidendiga\"}" \
        localhost:6604/api/query_extender/tsv
        
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data "{\"content\":\"presitendi\\tpresidendiga\", \"params\":{\"otsi_liitsõnadest\":\"false\"}}" \
        localhost:6604/api/query_extender/process | jq
        
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data "{\"tss\":\"presitendi\\tpresidendiga\", \"params\":{\"otsi_liitsõnadest\":\"false\"}}" \
        localhost:6604/api/query_extender/json | jq
        
    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:6604/api/query_extender/version | jq
----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja CURLiga veebiteenuse kasutamise näited  (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart-search_github/api/api_query_extender
    $ docker build -t tilluteenused/smart_search_api_query_extender:2023.12.28 . 
2.3 Konteineri käivitamine
    $ docker run -p 6604:6604 \
        --env  SMART_SEARCH_QE_DBASE='./smart_search.sqlite' \
        tilluteenused/smart_search_api_query_extender:2023.12.28 
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_api_query_extender:2023.12.28
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data "{\"content\":\"presitendi ja polekorpuses kantseleis\"}" \
        https://smart-search.tartunlp.ai/api/ea_paring/json
    $ curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/ea_paring/version | jq
----------------------------------------------

'''

import argparse
from flask import Flask, request, jsonify, make_response, abort
from typing import Dict, List, Tuple
from functools import wraps
import api_query_extender

VERSION='2023.12.28'

paring_soned = api_query_extender.Q_EXTENDER(None, csthread=False)

app = Flask("api_query_extender")

# JSONsisendi max suuruse piiramine {{
try:
    SMART_SEARCH_MAX_CONTENT_LENGTH=int(os.environ.get('SMART_SEARCH_MAX_CONTENT_LENGTH'))
except:
    SMART_SEARCH_MAX_CONTENT_LENGTH = 1 * 100000 # 1 GB 

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

@app.errorhandler(413) # Liiga mahukas päring
def request_entity_too_large(error):
    #return 'File Too Large', 413
    return jsonify({"error":"Request Entity Too Large"})

# }} JSONsisendi max suuruse piiramine 


@app.route('/api/query_extender/process', methods=['POST'])
@app.route('/process', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_ea_paring_process():
    '''
    response_json
    {   "content": CONTENT",
        "params": {"otsi_liitsõnadest": "false" } # optional, default: true 
        "annotations": {"query": [[LEMMA]],  
            "ignore": [IGNORE_WORDWORM],
            "not indexed": [NOT_INDEXED_LEMMA],
            "typos": {TYPO: {"suggestions":[SUGGESTION]}}},
    }
    '''
    try:
        paring_soned.response_json = request.json
        paring_soned.paring_json()
        return jsonify(paring_soned.response_json)
    except Exception as e:
        return jsonify(list(e.args))    

@app.route('/api/query_extender/json', methods=['POST'])
@app.route('/json', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_ea_paring_json_json():
    try:
        paring_soned.response_json = request.json
        paring_soned.paring_tsv()
        return jsonify(paring_soned.response_json)
    except Exception as e:
        return jsonify(list(e.args))    

@app.route('/api/query_extender/tsv', methods=['POST'])
@app.route('/tsv', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_ea_paring_tsv():
    try:
        paring_soned.response_json = request.json
        paring_soned.paring_tsv()
        res_str = ''
        for rec in paring_soned.response_table:
            res_str += f'{rec[0]}\t{rec[1]}\t{rec[2]}\t{rec[3]}\t{rec[4]}\t{rec[5]}\n'
        response = make_response(res_str)
        response.headers["Content-type"] = "text/tsv"
        return response
    except Exception as e:
        return jsonify(list(e.args))   

@app.route('/api/query_extender/version', methods=['GET', 'POST'])
@app.route('/version', methods=['POST'])
def api_ea_paring_version():
    """Kuvame versiooni ja muud infot

    Returns:
        ~flask.Response: Versiooni-info
    """
    version_json = paring_soned.version_json()
    version_json["container_version"] = VERSION
    version_json["SMART_SEARCH_MAX_CONTENT_LENGTH"] = SMART_SEARCH_MAX_CONTENT_LENGTH
    return jsonify(version_json)

if __name__ == '__main__':
    default_port=6604
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)



        

        
        
    
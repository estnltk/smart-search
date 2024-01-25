#!/usr/bin/python3

'''Flask api, päringustring päringut esitavaks JSONiks
Mida uut:
2023-12-28 flask_api_query_extender.py
* kohendatud "suggestion" ja "not_indexed" käsitlust
2023-12-29 konteiner
* andmebaasi lisatud DBASE_VERSION ja (test)tabel "ignoreeritavad_vormid"
2024-01-03 konteiner
* konteinerisse lisatud stlspellerjson ja et.dct
2024-01-04 konteiner
* konteinerisse lisatud uues versioon stlspellerjson programmist
2024-01-05 
* lisatud /api/query_extender/wordform_check

---------------------------------
code:


---------------------------------
'''
import json
import os
import argparse
from flask import Flask, request, jsonify, make_response, abort
from typing import Dict, List, Tuple
from functools import wraps
import api_query_extender

VERSION_FLASK_SHELL='2024.01.21'

paring_soned = api_query_extender.Q_EXTENDER("", csthread=False)

app = Flask("api_query_extender")

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


@app.route('/api/query_extender/wordform_check', methods=['POST'])
@app.route('/wordform_check', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_ea_paring_wordform_check():
    try:
        request_json = json.loads(request.data)
    except ValueError as e:
        abort(400, description=str(e)) 

    try:
        paring_soned.response_json = request_json
        paring_soned.in_indeks_vormid()
    except Exception as e:
        abort(500, description=str(e)) 

    return jsonify(paring_soned.response_json)

@app.route('/api/query_extender/process', methods=['POST'])
@app.route('/process', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_ea_paring_process():
    '''
    response_json
    {   "content": CONTENT",
        "params": {"otsi_liitsõnadest": "false" } # optional, default: true 
        "annotations": 
           {"query": [[LEMMA]],  
            "ignore": [IGNORE_WORDWORM],
            "not indexed": [NOT_INDEXED_LEMMA],
            "typos": {TYPO: {"suggestions":[SUGGESTION]}}},
    }
    '''
    try:
        request_json = json.loads(request.data)
    except ValueError as e:
        abort(400, description=str(e))

    try:
        paring_soned.response_json = request_json
        paring_soned.paring_process()
    except Exception as e:
        abort(500, description=str(e))
    
    return jsonify(paring_soned.response_json)

@app.route('/api/query_extender/json', methods=['POST'])
@app.route('/json', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_ea_paring_json_json():
    try:
        request_json = json.loads(request.data)
    except ValueError as e:
        abort(400, description=str(e))

    try:
        paring_soned.response_json = request_json
        paring_soned.paring_jsontsv()
    except Exception as e:
        abort(500, description=str(e))    

    return jsonify(paring_soned.response_json)

@app.route('/api/query_extender/tsv', methods=['POST'])
@app.route('/tsv', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_ea_paring_tsv():
    try:
        request_json = json.loads(request.data)
    except ValueError as e:
        abort(400, description=str(e))

    try:
        paring_soned.response_json = request_json
        paring_soned.paring_jsontsv()
        res_str = ''
        for rec in paring_soned.response_table:
            res_str += f'{rec[0]}\t{rec[1]}\t{rec[2]}\t{rec[3]}\t{rec[4]}\t{rec[5]}\n'
        response = make_response(res_str)
        response.headers["Content-type"] = "text/tsv"
        return response
    except Exception as e:
        abort(500, description=str(e))  

@app.route('/api/query_extender/version', methods=['GET', 'POST'])
@app.route('/version', methods=['POST'])
def api_ea_paring_version():
    """Kuvame versiooni ja muud infot

    Returns:
        ~flask.Response: Versiooni-info
    """
    version_json = paring_soned.version_json()
    version_json["VERSION_FLASK_SHELL"] = VERSION_FLASK_SHELL
    version_json["SMART_SEARCH_MAX_CONTENT_LENGTH"] = SMART_SEARCH_MAX_CONTENT_LENGTH
    return jsonify(version_json)

if __name__ == '__main__':
    default_port=6604
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)
    
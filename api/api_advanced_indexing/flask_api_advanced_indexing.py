#!/usr/bin/python3

'''Flask api, (eel)arvutab JSON-failid mis on vajlikud andmebaasi kokkupanemiseks
Mida uut:
2024-01-09
    * /api/advanced_indexing/json
    * /api/advanced_indexing/csv_input

----------------------------------------------
// code (serveri käivitamine silumiseks):
        {
            "name": "flask_advanced_indexing",
            "type": "python",
            "request": "launch",
            "cwd": "${workspaceFolder}/api/api_advanced_indexing/",
            "program": "./flask_api_advanced_indexing.py",
            "env": {}
            "args": []
        },
----------------------------------------------
'''
import os
import sys
import json
import requests
import subprocess
import json
import argparse
from flask import Flask, request, jsonify, make_response, abort
from functools import wraps
from typing import Dict, List, Tuple
from collections import OrderedDict

import api_advanced_indexing

VERSION="2024.01.10"

try:
    SMART_SEARCH_GENE_TYPOS=(os.environ.get('SMART_SEARCH_GENE_TYPOS').upper()=="TRUE")
except:
    SMART_SEARCH_GENE_TYPOS = False # vaikimisi ei genereeri kirjavigasid
    
tj = api_advanced_indexing.TEE_JSON(verbose=False, kirjavead=SMART_SEARCH_GENE_TYPOS, tabelid=[])

app = Flask("api_ea_jsoncontent_2_jsontabelid")

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

@app.errorhandler(413) # Liiga mahukas päring
def request_entity_too_large(error):
    #return 'File Too Large', 413
    return jsonify({"error":"Request Entity Too Large"})

# }} JSONsisendi max suuruse piiramine 

@app.route('/api/advanced_indexing/csv_input', methods=['POST'])
@app.route('/csv_input', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_advanced_indexing_headers():
    """Leia sisendkorpuse sõnede kõikvõimalikud vormid ja nonde hulgast need, mis esinesid korpuses

    Args:

    * CSV pealkirjade ja seotud infoga:
        global_id,document_type,document_title,xml_source

        
    Kui dokumendiga tuleb kaasa lisainfot, siis tuleb alljärgnevatesse tabelitesse tekitada
    vastavatesse kohtadesse lisaveerud vastava infoga    

    Returns:
        Response: VäljundJSON:

        {   "indeks_vormid":[(VORM, DOCID, START, END, LIITSÕNA_OSA)],
            "indeks_lemmad":[(LEMMA, DOCID, START, END, LIITSÕNA_OSA)],
            "liitsõnad":[(OSALEMMA, LIITLEMMA)],
            "lemma_kõik_vormid":[(LEMMA, KAAL, VORM)],
            "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)],
            "kirjavead":[(VIGANE_VORM, VORM)],              # kirjavigade tabel tehakse ainult siis kui keskkonnamuutuja SMART_SEARCH_GENE_TYPOS=true
            "allikad":[(DOCID, CONTENT)],
        }

    https://stackoverflow.com/questions/62685107/open-csv-file-in-flask-sent-as-binary-data-with-curl
    """
    try:
        csv_data = request.data.decode("utf-8")
        tj.csvpealkrjadest('veebipäringust', csv_data.splitlines())
        tj.tee_sõnestamine()
        tj.tee_kõigi_terviksõnede_indeks()
        tj.tee_mõistlike_tervik_ja_osasõnede_indeks()
        tj.tabelisse_vormide_indeks()
        tj.tee_mõistlike_lemmade_ja_osalemmade_indeks()
        tj.tabelisse_lemmade_indeks()
        tj.tee_generator()
        tj.tee_kirjavead()
        tj.tee_sources_tabeliks()
        tj.kustuta_vahetulemused()
        tj.kordused_tabelitest_välja()

        return jsonify(tj.json_io)
    except Exception as e:
        return jsonify({"warning": str(e)})    

@app.route('/api/advanced_indexing/json', methods=['POST'])
@app.route('/json', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def api_advanced_indexing_document():
    """Leia sisendkorpuse sõnede kõikvõimalikud vormid ja nonde hulgast need, mis esinesid korpuses

    Args: 

    * JSON:
        {"sources":{DOCID:{"content:str}}}

    Returns:
        Response: VäljundJSON:
        {   "indeks_vormid":[(VORM, DOCID, START, END, LIITSÕNA_OSA)],
            "indeks_lemmad":[(LEMMA, DOCID, START, END, LIITSÕNA_OSA)],
            "liitsõnad":[(OSALEMMA, LIITLEMMA)],
            "lemma_kõik_vormid":[(LEMMA, KAAL, VORM)],
            "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)],
            "kirjavead":[(VIGANE_VORM, VORM)],              # kirjavigade tabel tehakse ainult siis kui keskkonnamuutuja SMART_SEARCH_GENE_TYPOS=true
            "allikad":[(DOCID, CONTENT)],
        }

    https://stackoverflow.com/questions/62685107/open-csv-file-in-flask-sent-as-binary-data-with-curl
    """
    try:
        if request.json is None:
            return jsonify({"warning": "the request does not contain valid JSON"})
        tj.json_io = request.json
        tj.tee_sõnestamine()
        tj.tee_kõigi_terviksõnede_indeks()
        tj.tee_mõistlike_tervik_ja_osasõnede_indeks()
        tj.tabelisse_vormide_indeks()
        tj.tee_mõistlike_lemmade_ja_osalemmade_indeks()
        tj.tabelisse_lemmade_indeks()
        tj.tee_generator()
        tj.tee_kirjavead()
        tj.tee_sources_tabeliks()
        tj.kustuta_vahetulemused()
        tj.kordused_tabelitest_välja()

        return jsonify(tj.json_io)
    except Exception as e:
        return jsonify({"warning": str(e)})    


@app.route('/api/advanced_indexing/version', methods=['GET', 'POST'])
@app.route('/version', methods=['POST'])
def api_advanced_indexing_version():
    """Kuvame versiooni ja muud infot

    Returns:
        ~flask.Response: Lemmatiseerija versioon
    """
    json_response = tj.version_json()
    json_response["FLASk-liidese versioon"] = VERSION
    json_response["SMART_SEARCH_MAX_CONTENT_LENGTH"] = SMART_SEARCH_MAX_CONTENT_LENGTH
    json_response["genereeri_kirjavead"] = tj.kirjavead

    return jsonify(json_response)

if __name__ == '__main__':
    default_port=6602
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)



        

        
        
    

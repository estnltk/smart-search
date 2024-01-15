#!/usr/bin/env python3

'''
----------------------------------------------
Flask veebiserver otsingumootori pakendamiseks ja veebilehel domonstreerimiseks
Mida uut
2023-12-29
* uus port 6605
* pisikohendused seoses päringulaiendajaga
2024-01-14 Kasutusjuhendi link parandatud
----------------------------------------------
Silumiseks:
launch.json:
    {
        "name": "flask_api_ea_paring_otsing",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/demod/veebilehed/ea_paring_otsing",
        "program": "./flask_wp_ea_paring_otsing.py",
        "env": { \
            "DB_INDEX": "./koond.sqlite", \
            "SMART_SEARCH_API_QE": "http://localhost:6604/api/query_extender/process", \
        }
    }
----------------------------------------------
'''

import os
from flask import Flask, jsonify, render_template, render_template_string, request, make_response
import requests
import json

import api_ea_paring_otsing

class ENVIRONMENT:
    def __init__(self):
        self.VERSION="2024.01.14"


eapo = api_ea_paring_otsing.SEARCH_DB()                     # otsingumootor
environment = ENVIRONMENT()                                 # keskkonnamuutujatest võetud inf 
app = Flask(__name__)                                       # Fläski äpp

@app.route('/rt_pealkirjaotsing/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def api_verioon():
    """Versiooniinfo kuvamines
    """
    version_json = eapo.version_json()
    version_json["veebilehe_versioon"] = environment.VERSION
    version_json["eapo.ea_paring"] = eapo.ea_paring
    return jsonify(version_json)  


@app.route(f'/rt_pealkirjaotsing/process', methods=['GET', 'POST'])
@app.route('/process', methods=['GET', 'POST'])
def process():
    """Veebileht päringu sisestamiseks ja päringutulemuste kuvamiseks
    """
    content = ""
    if request.method == 'POST':
        my_query_words = ''
        norm_paring = True if len(request.form.getlist('norm_paring')) > 0 else False   # kuva päringut algsel või normaliseeritud kujul
        fragments = True if len(request.form.getlist('fragments')) > 0 else False       # otsi liitsõna osasõnadest ka
        formaat = request.form.getlist('formaat')[0] # päringu tulemuse esitusviis {"html"|"html+details"|"json"}
        my_query_words = request.form.get('message').strip()    
        try:
            my_query_json = json.loads(requests.post(eapo.ea_paring, json={"content":my_query_words}).text)
        except:
            raise Exception({"warning":f'Probleemid veebiteenusega {eapo.ea_paring}'})                           # päringusõned

        eapo.otsing(fragments, my_query_words, my_query_json)                                      # otsime normaliseeritud päringu järgi tekstidest

        if norm_paring is True:                                                 # teisendame päringu kuvamiseks vajalikule kujule
            my_query_str = json.dumps(my_query_json, ensure_ascii=False, indent=2).replace(' ', '&nbsp;').replace('\n', '<br>')
        else:
            my_query_str = my_query_words
        eapo.koosta_vastus(formaat, norm_paring)
        content = eapo.content
    return render_template('process.html', query_result=content)
  
if __name__ == '__main__':
    import argparse
    default_port=6605
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

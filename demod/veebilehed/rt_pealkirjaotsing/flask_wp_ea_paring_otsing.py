#!/usr/bin/env python3

'''
----------------------------------------------
Flask veebiserver otsingumootori pakendamiseks ja veebilehel domonstreerimiseks
Mida uut
2023-12-29
* uus port 6605
* pisikohendused seoses päringulaiendajaga
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

Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2) veebiserveri käivitamine pythoni koodist (1.3) ja brauseriga veebilehe poole pöördumine (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir ~/git ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart-search_github/demod/veebilehed/ea_paring_otsing
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist (päringulaiendaja kohalikus konteineris)
    $ cd ~/git/smart-search_github/demod/veebilehed/ea_paring_otsing
    $ DB_INDEX=./index.sqlite \
      EA_PARING=http://localhost:6604/api/query_extender/process \
      ./venv/bin/python3 ./flask_wp_ea_paring_otsing.py
1.4 Brauseriga veebilehe poole pöördumine
    $ google-chrome http://localhost:6605/wp/ea_paring_otsing/process &
    $ google-chrome http://localhost:6605/wp/ea_paring_otsing/version &

----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteinerite käivitamine (2.3), konteinerite peatamine (2.4) ja brauseriga veebilehe poole pöördumine (2.5)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart-search_github/demod/veebilehed/ea_paring_otsing
    $ docker build -t tilluteenused/smart_search_wp_ea_paring_otsing:2023.12.29 .
2.3 Konteinerite käivitamine kohaikus arvutis
    $ cd ~/git/smart-search_github/demod/veebilehed/ea_paring_otsing
    $ MY_IP=$(hostname -I | sed 's/ .*$//g') docker-compose up -d && docker-compose ps
2.4 Konteinerite peatamine:
    $ cd ~/git/smart-search_github/demod/veebilehed/ea_paring_otsing
    $ docker-compose down && docker-compose ps
2.4 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteinerite käivitamine (3.2), konteinerite peatamine (3.4) ja brauseriga veebilehe poole pöördumine (3.5)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_wp_ea_paring_otsing:2023.12.29
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 Konteinerite peatamine: järgi punkti 2.4
3.4 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 Brauseriga veebilehe poole pöördumine
    $ google-chrome https://smart-search.tartunlp.ai/wp/ea_paring_otsing/process &
    $ google-chrome https://smart-search.tartunlp.ai/wp/ea_paring_otsing/version &

----------------------------------------------
'''

import os
from flask import Flask, jsonify, render_template, render_template_string, request, make_response
import requests
import json

import api_ea_paring_otsing

class ENVIRONMENT:
    def __init__(self):
        self.VERSION="2023.12.31"


eapo = api_ea_paring_otsing.SEARCH_DB()                     # otsingumootor
environment = ENVIRONMENT()                                 # keskkonnamuutujatest võetud inf 
app = Flask(__name__)                                       # Fläski äpp

@app.route('/wp/ea_paring_otsing/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def api_verioon():
    """Versiooniinfo kuvamines
    """
    version_json = eapo.version_json()
    version_json["veebilehe_versioon"] = environment.VERSION
    version_json["eapo.ea_paring"] = eapo.ea_paring
    return jsonify(version_json)  


@app.route(f'/wp/ea_paring_otsing/process', methods=['GET', 'POST'])
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

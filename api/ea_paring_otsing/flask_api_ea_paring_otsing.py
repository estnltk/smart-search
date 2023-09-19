#!/usr/bin/env python3

'''
----------------------------------------------

Flask veebiserver otsingumootori pakendamiseks ja veebilehel domonstreerimiseks
Täitsa vale, see kommentaar on veel korda tegemata
----------------------------------------------

Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2) veebiserveri käivitamine pythoni koodist (1.3) ja brauseriga veebilehe poole pöördumine (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir ~/git ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/wp/wp_otsing
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist: sõnepõhine otsingumootor (1.3.1) või lemmapõhine otsingumootor (1.3.2)
1.3.1 Sõnepõhise otsingumootori käivitamine
    $ cd ~/git/smart_search_github/wp/wp_otsing
    $ OTSINGU_VIIS=soned \
        IDXFILE=riigiteataja-soned-json.idx \
        PARING_SONED=https://smart-search.tartunlp.ai/api/paring-soned/ \
        venv/bin/python3 ./flask-wp-otsing.py
1.3.2 Lemmapõhise otsingumootori käivitamine
    $ cd ~/git/smart_search_github/wp/wp_otsing
    $ OTSINGU_VIIS=lemmad \
        IDXFILE=riigiteataja-lemmad-json.idx \
        PARING_LEMMAD=https://smart-search.tartunlp.ai/api/paring-lemmad/ \
        venv/bin/python3 ./flask-wp-otsing.py
1.4 Brauseriga veebilehe poole pöördumine: sõnepõhine otsingumootor (1.4.1) või lemmapõhine otsingumootor (1.4.2)
1.4.1 Sõnepõhise otsingumootori poole pöördumine
    $ google-chrome http://localhost:6013/wp/otsing-soned/version &
    $ google-chrome http://localhost:6013/wp/otsing-soned/texts &
    $ google-chrome http://localhost:6013/wp/otsing-soned/process &
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data  '["presidendiga", "presidendiks", "president", "presidendi"]' \
        http://localhost:6013/api/sonede-indeks/check
    $ curl --silent --request POST --header "Content-Type: application/json" \
        http://localhost:6013/api/sonede-indeks/api-version        
1.4.2 Lemmapõhise otsingumootori poole pöördumine
    $ google-chrome http://localhost:6013/wp/otsing-lemmad/version &
    $ google-chrome http://localhost:6013/wp/otsing-lemmad/texts &
    $ google-chrome http://localhost:6013/wp/otsing-lemmad/process &
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data  '["presidendiga", "presidendiks", "president", "presidendi"]' \
        http://localhost:6013/api/lemmade-indeks/check
    $ curl --silent --request POST --header "Content-Type: application/json" \
        http://localhost:6013/api/lemmade-indeks/api-version

----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja brauseriga veebilehe poole pöördumine (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/wp/wp_otsing
    $ docker build -t tilluteenused/smart_search_wp_otsing:2023.06.26 .
2.3 Konteineri käivitamine: sõnepõhine otsingumootor (2.3.1) või lemmapõhine otsingumootor (2.3.2)
2.3.1 Sõnepõhise otsingumootori käivitamine
    $ cd ~/git/smart_search_github/wp/wp_otsing
    $ docker run -p 6013:6013 \
        --env OTSINGU_VIIS=soned \
        --env IDXFILE=riigiteataja-soned-json.idx \
        --env PARING_SONED=https://smart-search.tartunlp.ai/api/paring-soned/ \
        tilluteenused/smart_search_wp_otsing:2023.08.10
2.3.2 Lemmapõhise otsingumootori käivitamine
    $ docker run -p 6013:6013 \
        --env OTSINGU_VIIS=lemmad \
        --env IDXFILE=riigiteataja-lemmad-json.idx  \
        --env PARING_LEMMAD=https://smart-search.tartunlp.ai/api/paring-lemmad/ \
        tilluteenused/smart_search_wp_otsing:2023.08.10
2.4 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja brauseriga veebilehe poole pöördumine (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_wp_otsing:2023.06.26
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 Brauseriga veebilehe poole pöördumine: sõnepõhine otsingumootor (4.1) või lemmapõhine otsingumootor (4.2)
4.1 Sõnepõhise otsingumootori poole pöördumine
    $ google-chrome https://smart-search.tartunlp.ai/wp/otsing-soned/version &
    $ google-chrome https://smart-search.tartunlp.ai/wp/otsing-soned/texts &
    $ google-chrome https://smart-search.tartunlp.ai/wp/otsing-soned/process &
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data  '["presidendiga", "presidendiks", "president", "presidendi"]' \
        https://smart-search.tartunlp.ai/api/sonede-indeks/check
    $ curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/sonede-indeks/api-version
4.2 Lemmapõhise otsingumootori poole pöördumine
    $ google-chrome https://smart-search.tartunlp.ai/wp/otsing-lemmad/version &
    $ google-chrome https://smart-search.tartunlp.ai/wp/otsing-lemmad/texts &
    $ google-chrome https://smart-search.tartunlp.ai/wp/otsing-lemmad/process &
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data  '["presidendiga", "presidendiks", "president", "presidendi"]' \
        https://smart-search.tartunlp.ai/api/lemmade-indeks/check
    $ curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/lemmade-indeks/api-version

----------------------------------------------
'''

import os
from flask import Flask, jsonify, render_template, render_template_string, request, make_response
import requests
import json

import api_ea_paring_otsing

class ENVIRONMENT:
    def __init__(self):
        self.VERSION="2023.09.16"


eapo = api_ea_paring_otsing.SEARCH_DB()                     # otsingumootor
environment = ENVIRONMENT()                                 # keskkonnamuutujatest võetud inf 
app = Flask(__name__)                                       # Fläski äpp

@app.route('/wp/ea_paring_otsing/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def api_verioon():
    return jsonify({    "veebilehe_versioon": environment.VERSION, 
                        "otsingu_versioon": eapo.VERSION, 
                        "DB_INDEX": eapo.idxfile, 
                        "EA_PARING":eapo.ea_paring})  

@app.route(f'/wp/ea_paring_otsing/texts', methods=['GET', 'POST'])
@app.route('/texts', methods=['GET', 'POST'])
def texts():
    """Kuvame veebilehel kasutaja valitud dokumenti 
    
    Korjame andmebaasist DOCIDid ja CONTENTid kokku ja meisterdame neist menüü
    ja siis meisterdame veebilehe kus näitab valitud dokumenti
    """
    content = 'TODO'

    #if request.method == 'POST':
    #    docid = request.form.getlist('document')[0]
    #    content = f'<h2>DocID: {docid}</h2>'
    #    content += smart_search.idx_json["sources"][docid]["content"].replace('\n', '<br>')+'<hr>'
    #return render_template('texts.html', query_result=content)
    return render_template_string(content)


@app.route(f'/wp/ea_paring_otsing/process', methods=['GET', 'POST'])
@app.route('/process', methods=['GET', 'POST'])
def process():
    """Veebileht päringu sisestamiseks ja päringutulemuste kuvamiseks
    """
    content = ''
    paringu_str = ''
    if request.method == 'POST':
        my_query_words = ''
        my_result_json = ''
        norm_paring = True if len(request.form.getlist('norm_paring')) > 0 else False   # kuva päringut algsel või normaliseeritud kujul
        fragments = True if len(request.form.getlist('fragments')) > 0 else False       # otsi liitsõna osasõnadest ka
        formaat = request.form.getlist('formaat')[0] # päringu tulemuse esitusviis {"html"|"html+details"|"json"}
        query_words = request.form.get('message').strip()    
        try:
            my_query_json = json.loads(requests.post(eapo.ea_paring, json={"content":query_words}).text)
        except:
            raise Exception({"warning":f'Probleemid veebiteenusega {eapo.ea_paring}'})                           # päringusõned

        eapo.otsing(fragments, my_query_json)                                      # otsime normaliseeritud päringu järgi tekstidest

        if norm_paring is True:                                                 # teisendame päringu kuvamiseks vajalikule kujule
            my_query_str = json.dumps(my_result_json, ensure_ascii=False, indent=2).replace(' ', '&nbsp;').replace('\n', '<br>')
        else:
            my_query_str = my_query_words
        eapo.koosta_vastus(formaat, my_query_str)
    return render_template('process.html', query_result=content)
  
if __name__ == '__main__':
    import argparse
    default_port=6013
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)
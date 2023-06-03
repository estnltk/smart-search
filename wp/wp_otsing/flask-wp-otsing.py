#!/usr/bin/env python3

'''
----------------------------------------------

Flask veebiserver otsingumootori pakendamiseks ja veebilehel domonstreerimiseks

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
    $ google-chrome http://localhost:6013/wp/otsing-soned/version
    $ google-chrome http://localhost:6013/wp/otsing-soned/texts
    $ google-chrome http://localhost:6013/wp/otsing-soned/process 
1.4.2 Lemmapõhise otsingumootori poole pöördumine
    $ google-chrome http://localhost:6013/wp/otsing-lemmad/version
    $ google-chrome http://localhost:6013/wp/otsing-lemmad/texts
    $ google-chrome http://localhost:6013/wp/otsing-lemmad/process

----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja brauseriga veebilehe poole pöördumine (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/wp/wp_otsing
    $ docker build -t tilluteenused/smart_search_wp_otsing:2023.05.15 .
2.3 Konteineri käivitamine: sõnepõhine otsingumootor (2.3.1) või lemmapõhine otsingumootor (2.3.2)
2.3.1 Sõnepõhise otsingumootori käivitamine
    $ cd ~/git/smart_search_github/wp/wp_otsing
    $ docker run -p 6013:6013 \
        --env OTSINGU_VIIS=soned \
        --env IDXFILE=riigiteataja-soned-json.idx \
        --env PARING_SONED=https://smart-search.tartunlp.ai/api/paring-soned/ \
        tilluteenused/smart_search_wp_otsing:2023.05.15
2.3.2 Lemmapõhise otsingumootori käivitamine
    $ docker run -p 6013:6013 \
        --env OTSINGU_VIIS=lemmad \
        --env IDXFILE=riigiteataja-lemmad-json.idx  \
        --env PARING_LEMMAD=https://smart-search.tartunlp.ai/api/paring-lemmad/ \
        tilluteenused/smart_search_wp_otsing:2023.05.15
2.4 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja brauseriga veebilehe poole pöördumine (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_wp_otsing:2023.05.15
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 Brauseriga veebilehe poole pöördumine: sõnepõhine otsingumootor (4.1) või lemmapõhine otsingumootor (4.2)
4.1 Sõnepõhise otsingumootori poole pöördumine
    $ google-chrome https://smart-search.tartunlp.ai/wp/otsing-soned/version
    $ google-chrome https://smart-search.tartunlp.ai/wp/otsing-soned/texts
    $ google-chrome https://smart-search.tartunlp.ai/wp/otsing-soned/process
4.2 Lemmapõhise otsingumootori poole pöördumine
    $ google-chrome https://smart-search.tartunlp.ai/wp/otsing-lemmad/version
    $ google-chrome https://smart-search.tartunlp.ai/wp/otsing-lemmad/texts
    $ google-chrome https://smart-search.tartunlp.ai/wp/otsing-lemmad/process

----------------------------------------------
'''

import os
from flask import Flask, render_template, render_template_string, request, make_response
import requests
import json
from collections import OrderedDict

import wp_otsing

class ENVIRONMENT:
    def __init__(self):
        self.VERSION="2023.05.15"

        self.otsingu_viis = os.environ.get('OTSINGU_VIIS')                  # otsingu viis ("lemmad" või "soned") keskkonnamuutujast
        if self.otsingu_viis is None:                                       # keskkonnamuutujat polnud...
            self.otsingu_viis = 'lemmad'                                        # ...kasutame vaikeväärtust

        self.paring = os.environ.get(f'PARING_{self.otsingu_viis.upper()}') # otsisõnede normaliseerimise veebiteenuse URL  keskkonnamuutujast
        if self.paring is None: 
            self.PARING_IP=os.environ.get(f'PARING_{self.otsingu_viis.upper()}_IP') if os.environ.get(f'PARING_{self.otsingu_viis.upper()}_IP') != None else 'localhost'
            self.PARING_PORT=os.environ.get(f'PARING_{self.otsingu_viis.upper()}_PORT') if os.environ.get(f'PARING_{self.otsingu_viis.upper()}_PORT') != None else '7007'
            self.paring = f'http://{self.PARING_IP}:{self.PARING_PORT}/api/paring-{self.otsingu_viis}/'

smart_search = wp_otsing.SMART_SEARCH()                     # otsingumootor
environment = ENVIRONMENT()                                 # keskkonnamuutujatest võetud inf 
app = Flask(__name__)                                       # Fläski äpp

@app.route(f'/wp/otsing-{environment.otsingu_viis}/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def versioon():
    """Kuvame veebilehel versiooniinfot ja veel üht-teist

    """
    return render_template('version.html', veebilehe_versioon=environment.VERSION, otsingu_versioon=smart_search.VERSION, 
                          otsingu_viis=environment.otsingu_viis,  paringu_url=environment.paring, idxfile=smart_search.idxfile)

@app.route(f'/wp/otsing-{environment.otsingu_viis}/texts', methods=['GET', 'POST'])
@app.route('/texts', methods=['GET', 'POST'])
def texts():
    """Kuvame veebilehel kasutaja valitud dokumenti 
    
    """
    content = ''
    if request.method == 'POST':
        docid = request.form.getlist('document')[0]
        content = f'<h2>DocID: {docid}</h2>'
        content += smart_search.idx_json["sources"][docid]["content"].replace('\n', '<br>')+'<hr>'
    return render_template('texts.html', query_result=content)

'''
Indeksi formaat:
    environment.idxfile =
    {   "sources":{DOCID:{"content":str}}
        "index":{LEMMA:{DOCID:[{"start":int, "end":int, "liitsõna_osa": bool}]
    }

Päringuvastuse formaat:
{   "annotations":
    {   "query":
        [ [LEMMA, ...],
          ...
        ]
    }
}

Otsinguvastuse fromaat:
{   DOCID:
    {   STARTPOS:
        {   "endpos": int,
            "token": str,
            "tokens": [str]
        }
    }
}
'''

@app.route(f'/wp/otsing-{environment.otsingu_viis}/process', methods=['GET', 'POST'])
@app.route('/process', methods=['GET', 'POST'])
def process():
    """Veebileht päringu sisestamiseks ja päringutulemuste kuvamiseks

    """
    content = ''
    paringu_str = ''
    if request.method == 'POST':
        smart_search.query_json = ''
        smart_search.result_json = ''
        norm_paring = True if len(request.form.getlist('norm_paring')) > 0 else False   # kuva päringut algsel või normaliseeritud kujul
        fragments = True if len(request.form.getlist('fragments')) > 0 else False       # vaata liitsõna osasõnu
        formaat = request.form.getlist('formaat')[0]                                    # päringu tulemus html või json
        query_words = request.form.get('message').strip()                               # päringusõned
        paringu_url=environment.paring+'json'                                            # päringut normaliseeriva serveri URL
        query_json = json.loads(requests.post(paringu_url, json={"content":query_words}).text)  # normaliseerime päringu
        smart_search.otsing(fragments, query_json)                                      # otsime normaliseeritud päringu järgi tekstidest

        if norm_paring is True:                                                         # teisendame päringu kuvamiseks vajalikule kujule
            paringu_str = json.dumps(query_json, ensure_ascii=False, indent=2).replace(' ', '&nbsp;').replace('\n', '<br>')
        else:
            paringu_str = query_words
        smart_search.koosta_vastus(formaat, paringu_str)
    return render_template('process.html', query_result=smart_search.content)


if __name__ == '__main__':
    import argparse
    default_port=6013
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

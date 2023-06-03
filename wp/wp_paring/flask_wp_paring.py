#!/usr/bin/env python3

'''
----------------------------------------------

Flask veebiserver päringu normaliseerija pakendamiseks ja veebilehel domonstreerimiseks

----------------------------------------------

Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2) veebiserveri käivitamine pythoni koodist (1.3) ja brauseriga veebilehe poole pöördumine (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir ~/git ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/wp/wp_paring
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd ~/git/smart_search_github/wp/wp_paring
    $ PARING_SONED=https://smart-search.tartunlp.ai/api/paring-soned/ \
        PARING_LEMMAD=https://smart-search.tartunlp.ai/api/paring-lemmad/ \
        venv/bin/python3 ./flask_wp_paring.py
1.4 Brauseriga veebilehe poole pöördumine
    $ google-chrome http://localhost:6003/wp/paring/process
    $ google-chrome http://localhost:6003/wp/paring/version
   
----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja brauseriga veebilehe poole pöördumine (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/wp/wp_paring
    $ docker build -t tilluteenused/smart_search_wp_paring:2023.05.23 . 
2.3 Konteineri käivitamine
    $ cd ~/git/smart_search_github/wp/wp_paring 
    $ docker run -p 6003:6003 \
        --env PARING_SONED=https://smart-search.tartunlp.ai/api/paring-soned/ \
        --env PARING_LEMMAD=https://smart-search.tartunlp.ai/api/paring-lemmad/ \
        tilluteenused/smart_search_wp_paring:2023.05.23
2.4 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja brauseriga veebilehe poole pöördumine (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_wp_paring:2023.05.23 
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 Brauseriga veebilehe poole pöördumine
    $ google-chrome https://smart-search.tartunlp.ai/wp/paring/process
    $ google-chrome https://smart-search.tartunlp.ai/wp/paring/version

----------------------------------------------
'''

import os
from flask import Flask, render_template, request, make_response
import requests
import json

class ENVIRONMENT:
    def __init__(self):
        self.VERSION="2023.05.23"

        self.paring_soned = os.environ.get('PARING_SONED')
        if self.paring_soned is None:
            self.PARING_SONED_IP=os.environ.get('PARING_SONED_IP') if os.environ.get('PARING_SONED_IP') != None else 'localhost'
            self.PARING_SONED_PORT=os.environ.get('PARING_SONED_PORT') if os.environ.get('PARING_SONED_PORT') != None else '6000' #???
            self.paring_soned = f'http://{self.PARING_SONED_IP}:{self.PARING_SONED_PORT}/api/paring-soned/'

        self.paring_lemmad = os.environ.get('PARING_LEMMAD')
        if self.paring_lemmad is None:
            self.PARING_LEMMAD_IP=os.environ.get('PARING_LEMMAD_IP') if os.environ.get('PARING_LEMMAD_IP') != None else 'localhost'
            self.PARING_LEMMAD_PORT=os.environ.get('PARING_LEMMAD_PORT') if os.environ.get('PARING_LEMMAD_PORT') != None else '7007' #???
            self.paring_lemmad = f'http://{self.PARING_LEMMAD_IP}:{self.PARING_LEMMAD_PORT}/api/paring-lemmad/'


app = Flask(__name__)
environment = ENVIRONMENT()

@app.route('/wp/paring/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def lemmatiseerija_versioon():
    return render_template('version.html',
                           lemmapohine_paringu_normaliseerija_url=environment.paring_lemmad,
                           sonavormipohine_paringu_normaliseerija_url=environment.paring_soned)

@app.route('/wp/paring/process', methods=['GET', 'POST'])
@app.route('/process', methods=['GET', 'POST'])
def lemmatiseerija_paring():
    content = ''
    if request.method == 'POST':
        paring = request.form.getlist('paring')[0]
        formaat = request.form.getlist('formaat')[0]
        query_words = request.form.get('message').strip()
        if len(query_words) > 0: # ei koosne ainult 'white space'idest
            if formaat == 'json':
                if paring == "paring-lemmad":
                    paringu_url=environment.paring_lemmad+formaat
                else:
                    paringu_url=environment.paring_soned+formaat
                try:                                                
                    json_out = json.loads(requests.post(paringu_url, json={"content":query_words}).text)
                    content = f'{query_words} ⇒ '
                    content += json.dumps(json_out, indent=2, ensure_ascii=False).replace(' ', '&nbsp;').replace('\n', '<br>')+'<br><br><hr><br>'  
                except:                                            
                    content = 'Probleemid veebiteenusega<br><br><hr><br>'
            else: # format == 'text'
                if paring == "paring-lemmad":
                    paringu_url=environment.paring_lemmad+formaat
                else:
                    paringu_url=environment.paring_soned+formaat
                try:       
                    text_out = requests.post(paringu_url, json={"content":query_words}).text
                    content = f'{query_words} ⇒<br>{text_out}<br><hr><br>'.replace('&', '<br>&<br>')
                except:                                            
                    content = 'Probleemid veebiteenusega<br><hr><br>'
    return render_template('process.html', content=content)

if __name__ == '__main__':
    import argparse
    default_port=6003
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

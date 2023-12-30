#!/usr/bin/env python3

'''
----------------------------------------------

Flask veebiserver spelleri pakendamiseks ja veebilehel domonstreerimiseks
Testitud:2023.06.28

----------------------------------------------

Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2) veebiserveri käivitamine pythoni koodist (1.3) ja brauseriga veebilehe poole pöördumine (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir ~/git ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/wp/wp_speller
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd ~/git/smart_search_github/wp/wp_speller
    $ PARING_SPELLER=https://smart-search.tartunlp.ai/api/speller/process \
        venv/bin/python3 ./flask_wp_speller.py
1.4 Brauseriga veebilehe poole pöördumine
    $ google-chrome http://localhost:6003/wp/speller/process &
    $ google-chrome http://localhost:6003/wp/speller/version &
   
----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja brauseriga veebilehe poole pöördumine (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/wp/wp_speller
    $ docker build -t tilluteenused/smart_search_wp_speller:2023.06.24 .
2.3 Konteineri käivitamine
    $ docker run -p 6003:6003 \
        --env PARING_SPELLER=https://smart-search.tartunlp.ai/api/speller/process \
        tilluteenused/smart_search_wp_speller:2023.06.24
2.4 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja brauseriga veebilehe poole pöördumine (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_wp_speller:2023.06.24
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 Brauseriga veebilehe poole pöördumine
    $ google-chrome https://smart-search.tartunlp.ai/wp/speller/process &
    $ google-chrome https://smart-search.tartunlp.ai/wp/speller/version &

----------------------------------------------
'''

import os
from flask import Flask, render_template, request, make_response
import requests
import json

class ENVIRONMENT:
    def __init__(self):
        self.VERSION="2023.06.24"

        self.PARING_SPELLER_IP=None
        self.PARING_SPELLER_PORT=None
        self.paring_speller = os.environ.get('PARING_SPELLER')
        if self.paring_speller is None:
            self.PARING_SPELLER_IP=os.environ.get('PARING_SPELLER_IP') if os.environ.get('PARING_SPELLER_IP') != None else 'localhost'
            self.PARING_SPELLER_PORT=os.environ.get('PARING_SPELLER_PORT') if os.environ.get('PARING_SPELLER_PORT') != None else '6004'
            self.paring_speller = f'http://{self.PARING_SPELLER_IP}:{self.PARING_SPELLER_PORT}/api/speller/process'

app = Flask(__name__)
environment = ENVIRONMENT()

@app.route('/wp/speller/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def versioon():
    return render_template('version.html', veebilehe_versioon=environment.VERSION, api_speller_url=environment.paring_speller)

@app.route('/wp/speller/process', methods=['GET', 'POST'])
@app.route('/process', methods=['GET', 'POST'])
def process():
    content = ''
    if request.method == 'POST':
        formaat = request.form.getlist('formaat')[0]
        query_words = request.form.get('message').strip()
        if len(query_words) > 0: # ei koosne ainult 'white space'idest
            try:                                                
                json_out = json.loads(requests.post(environment.paring_speller, json={"content":query_words}).text)
                if formaat == 'json':
                    content += json.dumps(json_out, indent=2, ensure_ascii=False).replace(' ', '&nbsp;').replace('\n', '<br>')+'<br><br><hr>' 
                else:       
                    for token in  json_out["annotations"]["tokens"]:
                        content += f'{token["features"]["token"]}'
                        if "suggestions" in token[ "features"]:
                            content += f' ⇒ {" ".join(token["features"]["suggestions"])}'
                        content += '<br>'
                    content += '<br><hr>'
            except:                                            
                content = 'Probleemid veebiteenusega<br><br><hr>'
    return render_template('process.html', content=content)


if __name__ == '__main__':
    import argparse
    default_port=6003
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

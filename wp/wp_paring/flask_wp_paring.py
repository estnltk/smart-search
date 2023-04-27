#!/usr/bin/python3

'''
1. käivita lemmatiseerija konteiner (konteiner peab olema tehtud/allalaaditud)
    $ docker run -p 7000:7000 tilluteenused/lemmatizer konteiner
2. käivita lemmatiseerija konteineriga suhtlev veebiserver käsurealt või konteinerist
  2.1. käsurealt pythoni skriptiga (pythoni pakett requests peab olema installitud, ubuntu korral: sudo apt install -y python3-requests)
    $ cd demo_lemmatiseerija ; ./flask_demo_lemmatiseerija.py
  2.2. dockeri konteinerist
    $ docker run --env LEMMATIZER_IP=localhost --env LEMMATIZER_PORT=7777 tilluteenused/demo_lemmatiseerija:2023.04.03
3. Ava brauseris localhost:7777/lemmad ja järgi brauseris avanenud veebilehe juhiseid
    $ google-chrome http://localhost:7777/lemmatiseerija/lemmad
    $ google-chrome http://localhost:7777/lemmatiseerija/paring
    $ google-chrome http://localhost:7777/lemmatiseerija/json
    $ google-chrome http://localhost:7777/lemmatiseerija/versioon
'''

import os
from flask import Flask, render_template_string, request, make_response
import requests
import json

class HTML_FORMS:
    def __init__(self):
        self.VERSION="2023.04.26"

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

        self.html_pref = '<!DOCTYPE html><html lang="et"><head><meta charset="UTF-8"></head><body>'

        self.form_paring = \
            '''
            <form method='POST' enctype='multipart/form-data' action='/wp/paring'>
                Väljundformaat:
                    <input checked type="radio" name="formaat", value="json"> JSON    </input>
                    <input         type="radio" name="formaat", value="text"> avaldis </input><br>
                Päringus:
                    <input checked type="radio" name="paring", value="paring-lemmad"> lemmad     </input>
                    <input         type="radio" name="paring", value="paring-soned">  sõnavormid </input><br><br>                          
                <input name="message" type="text"><input type="submit" value="Päring" >
            </form>
            '''

        self.html_suf = \
                '''
                </body></html>
                '''
        '''
                <br><br
                <h3>Kasutusjuhendid</h3><br>
                <ul>
                <li><a href="https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/README-CLOUD.md">Lemmatiseerija demo</a><br>
                <li><a href="https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/README-CLOUD.md">Otsimootori demo</a>
                </ul>
        '''


app = Flask(__name__)
html_forms = HTML_FORMS()

@app.route('/wp/versioon', methods=['GET', 'POST'])
def lemmatiseerija_versioon():
    content = f'<html><body>Versioon: {html_forms.VERSION}</body></html>' 
    return render_template_string(html_forms.html_pref+content+html_forms.html_suf)

@app.route('/wp/paring', methods=['GET', 'POST'])
def lemmatiseerija_paring():
    content = ''
    if request.method == 'POST':
        paring = request.form.getlist('paring')[0]
        formaat = request.form.getlist('formaat')[0]
        query_words = request.form.get('message').strip()
        if len(query_words) > 0: # ei koosne ainult 'white space'idest
            if formaat == 'json':
                if paring == "paring-lemmad":
                    paringu_url=html_forms.paring_lemmad+formaat
                else:
                    paringu_url=html_forms.paring_soned+formaat
                try:                                                
                    json_out = json.loads(requests.post(paringu_url, json={"content":query_words}).text)
                    content = f'{query_words} ⇒ '
                    content += json.dumps(json_out, indent=2).replace(' ', '&nbsp;').replace('\n', '<br>')+'<br><br><hr><br>'  
                except:                                            
                    content = 'Probleemid veebiteenusega<br><br><hr><br>'
            else: # format == 'text'
                if paring == "paring-lemmad":
                    paringu_url=html_forms.paring_lemmad+formaat
                else:
                    paringu_url=html_forms.paring_soned+formaat
                try:       
                    text_out = requests.post(paringu_url, json={"content":query_words}).text
                    content = f'{query_words} ⇒<br>{text_out}<br><hr><br>'.replace('&', '<br>&<br>')
                except:                                            
                    content = 'Probleemid veebiteenusega<br><hr><br>'
    return render_template_string(html_forms.html_pref+content+html_forms.form_paring+html_forms.html_suf)


if __name__ == '__main__':
    import argparse
    default_port=6003
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

#!/usr/bin/env python3

'''
1. kasuta veebiteenust või käivita spelleriga suhtlev veebiserver pythoni skriptist või konteinerist 
  1.1 pilveteenuse smart-search.tartunlp.ai kasutamisel pole kohalikus masinas vaja midagi teha
  1.2 käsurealt pythoni skriptiga
    $ cd ~/git/smart_search_github/wp/wp_speller
    $ ./create_venv.sh
    $ PARING_SPELLER=https://smart-search.tartunlp.ai/api/speller/process \
      venv/bin/python3 ./flask_wp_speller.py
  1.3 kohalikust dockeri konteinerist (teeme ise või tõmbame dockerhubist)
    1.3.1 paneme konteineri ise kokku
    $ cd ~/git/smart_search_github/wp/wp_speller
    $ docker build -t tilluteenused/smart_search_wp_speller:2023.05.22 . 
    1.3.2 tõmbame dockerhubist juba valmistehtud konteineri
    $ docker pull tilluteenused/smart_search_wp_speller:2023.05.22
    1.3.3 käivitame kohalikus masinas 1.3.1 või 1.3.2 viisil saadud konteineri 
    $ docker run -p 6003:6003 \
        --env PARING_SPELLER=https://smart-search.tartunlp.ai/api/speller/process
        tilluteenused/smart_search_wp_speller:2023.05.22
  
2. Ava brauseris veebileht ja järgi juhiseid
  2.1 Veebiserver kohalikus masinas (1.1 või 1.2)
    $ google-chrome http://localhost:6003/wp/speller/process
    $ google-chrome http://localhost:6003/wp/speller/version
  2.2 Veebiserver pilves (1.3)
    $ google-chrome https://smart-search.tartunlp.ai/wp/speller/process
    $ google-chrome https://smart-search.tartunlp.ai/wp/speller/version
'''

import os
from flask import Flask, render_template_string, request, make_response
import requests
import json

class HTML_FORMS:
    def __init__(self):
        self.VERSION="2023.05.22"

        self.PARING_SPELLER_IP=None
        self.PARING_SPELLER_PORT=None
        self.paring_speller = os.environ.get('PARING_SPELLER')
        if self.paring_speller is None:
            self.PARING_SPELLER_IP=os.environ.get('PARING_SPELLER_IP') if os.environ.get('PARING_SPELLER_IP') != None else 'localhost'
            self.PARING_SPELLER_PORT=os.environ.get('PARING_SPELLER_PORT') if os.environ.get('PARING_SPELLER_PORT') != None else '6004'
            self.paring_speller = f'http://{self.PARING_SPELLER_IP}:{self.PARING_SPELLER_PORT}/api/speller/process'

        self.html_pref = '<!DOCTYPE html><html lang="et"><head><meta charset="UTF-8"></head><body>'

        self.form_paring = \
            '''
            <form method='POST' enctype='multipart/form-data'>
                Väljundformaat:
                    <input         type="radio" name="formaat", value="json"> JSON    </input>
                    <input checked type="radio" name="formaat", value="text"> tekst </input><br>
                <input name="message" type="text"><input type="submit" value="Kontrolli ja soovita" >
            </form>
            '''

        self.html_suf = \
        '''
            <br>
            <a href="https://github.com/estnltk/smart-search/blob/main/wp/wp_speller/README.md">Kasutusjuhend</a>
            </body></html>
        '''

app = Flask(__name__)
html_forms = HTML_FORMS()

@app.route('/wp/speller/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def versioon():
    content = f'<html><body>Veebilehe versioon: {html_forms.VERSION}<br>paring_speller={html_forms.paring_speller}<br>'
    if html_forms.PARING_SPELLER_IP is not None:
        content += f'PARING_SPELLER_IP={html_forms.PARING_SPELLER_IP}<br>'
    if html_forms.PARING_SPELLER_PORT is not None:
        content += f'PARING_SPELLER_PORT={html_forms.PARING_SPELLER_PORT}<br>'
    content += '</body></html>'
    return render_template_string(html_forms.html_pref+content+html_forms.html_suf)

@app.route('/wp/speller/process', methods=['GET', 'POST'])
@app.route('/process', methods=['GET', 'POST'])
def process():
    content = ''
    if request.method == 'POST':
        formaat = request.form.getlist('formaat')[0]
        query_words = request.form.get('message').strip()
        if len(query_words) > 0: # ei koosne ainult 'white space'idest
            try:                                                
                json_out = json.loads(requests.post(html_forms.paring_speller, json={"content":query_words}).text)
                if formaat == 'json':
                    content += json.dumps(json_out, indent=2, ensure_ascii=False).replace(' ', '&nbsp;').replace('\n', '<br>')+'<br><br><hr><br>' 
                else:       
                    for token in  json_out["annotations"]["tokens"]:
                        content += f'{token["features"]["token"]}'
                        if "suggestions" in token[ "features"]:
                            content += f' ⇒ {" ".join(token["features"]["suggestions"])}'
                        content += '<br>'
                    content += '<br><br><hr><br>'

            except:                                            
                content = 'Probleemid veebiteenusega<br><br><hr><br>'

    return render_template_string(html_forms.html_pref+content+html_forms.form_paring+html_forms.html_suf)


if __name__ == '__main__':
    import argparse
    default_port=6003
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

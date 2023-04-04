#!/usr/bin/python3
"""'
Flask-kest ümber lemmatiseerija veebiteenuse demomiseks mõeldud klassi.
"""

VERSION="2023.04.04"

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

from flask import Flask, render_template_string, request
import demo_lemmatiseerija

class HTML_FORMS:
    html_pref = '<!DOCTYPE html><html lang="et"><head><meta charset="UTF-8"></head><body>'
    form_lemmad = \
        '''
        <form method='POST' enctype='multipart/form-data' action='/lemmatiseerija/lemmad'>
        <input name="message" type="text"><input type="submit" value="Lemmatiseeri (1 sõna korraga)" >
        </form>
        '''
    form_paring = \
        '''
        <form method='POST' enctype='multipart/form-data' action='/lemmatiseerija/paring'>
        <input name="message" type="text"><input type="submit" value="Leia päringule vastav lemmade kombinatsioon" >
        </form>
        '''
    form_json = \
        '''
        <form method='POST' enctype='multipart/form-data' action='/lemmatiseerija/json'>
        <input name="message" type="text"><input type="submit" value="Kuva lemmatiseerija JSON-väljund" >
        </form>
        '''
    html_suf = \
            '''
            <br><br
            <h3>Kasutusjuhendid</h3><br>
            <ul>
            <li><a href="https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/README-CLOUD.md">Lemmatiseerija demo</a><br>
            <li><a href="https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/README-CLOUD.md">Otsimootori demo</a>
            </ul>
            </body></html><br>
            '''

app = Flask(__name__)

@app.route('/lemmatiseerija/versioon', methods=['GET', 'POST'])
def lemmatiseerija_versioon():
    content = f'<html><body>{VERSION}</body></html>' 
    return render_template_string(HTML_FORMS.html_pref+content+HTML_FORMS.html_suf)

@app.route('/lemmatiseerija/lemmad', methods=['GET', 'POST'])
def lemmatiseerija_lemmad():
    content = ''
    if request.method == 'POST':
        current_query = request.form.get('message').strip()
        if len(current_query) > 0: # ei koosnenud ainult 'white space'idest
            content = f'<h2>{current_query} ⇒ {demolemmatiseerija.lemmad(current_query)}</h2>' 
    return render_template_string(HTML_FORMS.html_pref+content+HTML_FORMS.form_lemmad+HTML_FORMS.html_suf)

@app.route('/lemmatiseerija/paring', methods=['GET', 'POST'])
def lemmatiseerija_paring():
    content = ''
    if request.method == 'POST':
        current_query = request.form.get('message').strip()
        if len(current_query) > 0: # ei koosnenud ainult 'white space'idest
            content = f'<h2>{current_query} ⇒ {demolemmatiseerija.paring(current_query)}</h2>' 
    return render_template_string(HTML_FORMS.html_pref+content+HTML_FORMS.form_paring+HTML_FORMS.html_suf)

@app.route('/lemmatiseerija/json', methods=['GET', 'POST'])
def lemmatiseerija_json():
    content = ''
    if request.method == 'POST':
        current_query = request.form.get('message').strip()
        if len(current_query) > 0: # ei koosnenud ainult 'white space'idest
            content = f'<h2>{current_query} ⇒ </h2>{demolemmatiseerija.json_paring(current_query)}' 
    return render_template_string(HTML_FORMS.html_pref+content+HTML_FORMS.form_json+HTML_FORMS.html_suf)

demolemmatiseerija = demo_lemmatiseerija.DEMO_LEMMATISEERIJA()

if __name__ == '__main__':
    import argparse
    default_port=7777
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

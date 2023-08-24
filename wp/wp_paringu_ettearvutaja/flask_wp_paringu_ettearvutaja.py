#!/usr/bin/env python3

'''Flask veebiserver päringu ettearvutaja ja veebilehel domonstreerimiseks
----------------------------------------------

Testitud TODO

----------------------------------------------

Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2), veebiserveri käivitamine pythoni koodist (1.3) ja brauseriga veebilehe poole pöördumine (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir ~/git ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/wp/wp_paringu_ettearvutaja
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd ~/git/smart_search_github/wp/wp_paringu_ettearvutaja
    $ PARINGU_ETTEARVUTAJA=https://smart-search.tartunlp.ai/api/paringu-ettearvutaja/   \
        venv/bin/python3 ./flask_wp_paringu_ettearvutaja.py
1.4 Brauseriga veebilehe poole pöördumine
    $ google-chrome http://localhost:5000/wp/paringu-ettearvutaja/process
    $ google-chrome http://localhost:5000/wp/paringu-ettearvutaja/version
   
----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja brauseriga veebilehe poole pöördumine (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/wp/wp_paringu_ettearvutaja
    $ docker build -t tilluteenused/smart_search_wp_paringu_ettearvutaja:2023.08.20 .
2.3 Konteineri käivitamine
    $ docker run -p 5000:5000 \
      --env PARINGU_ETTEARVUTAJA=https://smart-search.tartunlp.ai/api/paringu-ettearvutaja/    \
      tilluteenused/smart_search_wp_paringu-ettearvutaja:2023.08.20
2.4 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja brauseriga veebilehe poole pöördumine (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_wp_paringu-ettearvutaja:2023.08.20
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 Brauseriga veebilehe poole pöördumine
    $ google-chrome https://smart-search.tartunlp.ai/wp/paringu-ettearvutaja/process &
    $ google-chrome https://smart-search.tartunlp.ai/wp/paringu-ettearvutaja/version &

----------------------------------------------
'''

import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, abort, render_template_string, make_response
from werkzeug.utils import secure_filename
from pathlib import Path
import requests
import json
#from io import StringIO

class ENVIRONMENT:
    def __init__(self):
      self.VERSION="2023.08.20"

      self.paringu_ettearvutaja = os.environ.get('PARINGU_ETTEARVUTAJA')
      if self.paringu_ettearvutaja is None:
          self.PARINGU_ETTEARVUTAJA_IP=os.environ.get('PARINGU_ETTEARVUTAJA_IP') if os.environ.get('PARINGU_ETTEARVUTAJA_IP') != None else 'localhost'
          self.INDEKSEERIJA_SONED_PORT=os.environ.get('PARINGU_ETTEARVUTAJA_PORT') if os.environ.get('PARINGU_ETTEARVUTAJA_PORT') != None else '6606'
          self.paringu_ettearvutaja = f'http://{self.PARINGU_ETTEARVUTAJA_IP}:{self.PARINGU_ETTEARVUTAJA}/api/paringu-ettearvutaja/'


environment = ENVIRONMENT()
app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.txt','.json']
#app.config['UPLOAD_PATH'] = 'uploads'      

@app.route('/wp/paringu-ettearvutaja/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def paringu_ettearvutaja_versioon(): 
    return render_template('version.html', veebilehe_versioon=environment.VERSION,
                           paringu_ettarvutaja_url=environment.paringu_ettearvutaja)

@app.route('/wp/paringu-ettearvutaja/process', methods=['GET', 'POST'])
@app.route('/json', methods=['GET', 'POST'])
def paringu_ettearvutaja_process():
    content = ''
    if request.method == 'POST':
      formaat = request.form.getlist('formaat')[0]
      uploaded_file = request.files['file']
      filename = secure_filename(uploaded_file.filename)
      if filename != '':
          file_ext = os.path.splitext(filename)[1]
          if file_ext not in app.config['UPLOAD_EXTENSIONS']:
              content = 'Sisendfail peab olema tekstifail (.txt) või JSONformaadis (.json laiendiga).'
              return render_template('form.html', query_result=content)
          uploaded_content = uploaded_file.read().decode()
          if file_ext == '.json': # failis oli JSON
            try:
              query_json =json.loads(uploaded_content)
            except:
              content = f'Vigane json: {uploaded_file.filename}'
              return render_template('process.html', query_result=content)
          else: # file_ext == '.txt' # failis oli tekst, teeme JSONiks
            query_json = {"sources": {filename:{"content":uploaded_content}}}
          content = f'<h2>{filename} ⇒</h2>'
          try:
            response = requests.post(f'{environment.paringu_ettearvutaja}{formaat}', json=query_json)
            if response.status_code != 200:
              raise Exception(f'Probleemid veebiteenusega: {environment.paringu_ettearvutaja}{formaat}')
            if formaat == 'json':
              content += json.dumps(json.loads(response.text), indent=2, ensure_ascii=False).replace(' ', '&nbsp;').replace('\n', '<br>')+'<br><br>'
            else: # formaat=='csv'
                content = response.text.replace('\n', '<br>')+'<br><br>'
          except:
            content = f'Probleemid veebiteenusega: {environment.paringu_ettearvutaja}{formaat}'
    return render_template('process.html', query_result=content)

if __name__ == '__main__':
    import argparse
    default_port=5000
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

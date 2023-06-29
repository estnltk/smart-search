#!/usr/bin/env python3

'''
----------------------------------------------

Flask veebiserver indekseerija pakendamiseks ja veebilehel domonstreerimiseks
Testitud 2023.06.26
----------------------------------------------

Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2), veebiserveri käivitamine pythoni koodist (1.3) ja brauseriga veebilehe poole pöördumine (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir ~/git ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/wp/wp_indekseerija
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd ~/git/smart_search_github/wp/wp_indekseerija
    $ INDEKSEERIJA_SONED=https://smart-search.tartunlp.ai/api/sonede-indekseerija/   \
      INDEKSEERIJA_LEMMAD=https://smart-search.tartunlp.ai/api/lemmade-indekseerija/ \
      venv/bin/python3 ./flask_wp_indekseerija.py
1.4 Brauseriga veebilehe poole pöördumine
    $ google-chrome http://localhost:5000/wp/indekseerija/process
    $ google-chrome http://localhost:5000/wp/indekseerija/version
   
----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja brauseriga veebilehe poole pöördumine (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/wp/wp_indekseerija
    $ docker build -t tilluteenused/smart_search_wp_indekseerija:2023.06.26 .
2.3 Konteineri käivitamine
    $ docker run -p 5000:5000 \
      --env INDEKSEERIJA_SONED=https://smart-search.tartunlp.ai/api/sonede-indekseerija/   \
      --env INDEKSEERIJA_LEMMAD=https://smart-search.tartunlp.ai/api/lemmade-indekseerija/ \
      tilluteenused/smart_search_wp_indekseerija:2023.06.26
2.4 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja brauseriga veebilehe poole pöördumine (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_wp_indekseerija:2023.06.26
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 Brauseriga veebilehe poole pöördumine: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 Brauseriga veebilehe poole pöördumine
    $ google-chrome https://smart-search.tartunlp.ai/wp/indekseerija/process &
    $ google-chrome https://smart-search.tartunlp.ai/wp/indekseerija/version &

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
      self.VERSION="2023.06.26"

      self.indekseerija_soned = os.environ.get('INDEKSEERIJA_SONED')
      if self.indekseerija_soned is None:
          self.INDEKSEERIJA_SONED_IP=os.environ.get('INDEKSEERIJA_SONED_IP') if os.environ.get('INDEKSEERIJA_SONED_IP') != None else 'localhost'
          self.INDEKSEERIJA_SONED_PORT=os.environ.get('INDEKSEERIJA_SONED_PORT') if os.environ.get('INDEKSEERIJA_SONED_PORT') != None else '6606'
          self.indekseerija_soned = f'http://{self.INDEKSEERIJA_SONED_IP}:{self.INDEKSEERIJA_SONED_PORT}/api/sonede-indekseerija/'

      self.indekseerija_lemmad = os.environ.get('INDEKSEERIJA_LEMMAD')
      if self.indekseerija_lemmad is None:
          self.INDEKSEERIJA_LEMMAD_IP=os.environ.get('INDEKSEERIJA_LEMMAD_IP') if os.environ.get('INDEKSEERIJA_LEMMAD_IP') != None else 'localhost'
          self.INDEKSEERIJA_LEMMAD_PORT=os.environ.get('INDEKSEERIJA_LEMMAD_PORT') if os.environ.get('INDEKSEERIJA_LEMMAD_PORT') != None else '6607' 
          self.indekseerija_lemmad = f'http://{self.INDEKSEERIJA_LEMMAD_IP}:{self.INDEKSEERIJA_LEMMAD_PORT}/api/lemmade-indekseerija/'

environment = ENVIRONMENT()
app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.txt','.json']
#app.config['UPLOAD_PATH'] = 'uploads'      

@app.route('/wp/indekseerija/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def lemmatiseerija_versioon(): 
    return render_template('version.html', veebilehe_versioon=environment.VERSION,
                           lemmade_indekseerija_url=environment.indekseerija_lemmad,
                           sonavormide_indekseerija_url=environment.indekseerija_soned)

@app.route('/wp/indekseerija/process', methods=['GET', 'POST'])
@app.route('/process', methods=['GET', 'POST'])
def upload_files():
    content = ''
    if request.method == 'POST':
      indekseerija = request.form.getlist('indekseerija')[0]
      formaat = request.form.getlist('formaat')[0]
      uploaded_file = request.files['file']
      filename = secure_filename(uploaded_file.filename)
      if filename != '':
          file_ext = os.path.splitext(filename)[1]
          if file_ext not in app.config['UPLOAD_EXTENSIONS']:
              content = 'Sisendfail peab olema tekstifail (.txt) või JSONformaadis (.json laiendiga).'
              #return render_template_string(environment.html_pref+content+environment.form+environment.html_suf)
              return render_template('form.html', query_result=content)
          
          uploaded_content = uploaded_file.read().decode()
          # content = uploaded_content
          # uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
          # content = Path(app.config['UPLOAD_PATH']+'/'+filename).read_text()+indekseerija+formaat
          # os.remove(app.config['UPLOAD_PATH']+'/'+filename)
          
          if file_ext == '.json': # failis oli JSON
            try:
              query_json =json.loads(uploaded_content)
            except:
              content = f'Vigane json:<br>{uploaded_file}'
              return render_template_string(environment.html_pref+content+environment.form+environment.html_suf)
          else: # file_ext == '.txt' # failis oli tekst, teeme JSONiks
            query_json = {"sources": {filename:{"content":uploaded_content}}}
          content = f'<h2>{filename} ⇒</h2>'
          if indekseerija == "indekseerija-lemmad":
            url_indekseerija = environment.indekseerija_lemmad
          else:
            url_indekseerija = environment.indekseerija_soned
          try:
            response = requests.post(url_indekseerija+formaat, json=query_json)
            if response.status_code != 200:
              content = f'Probleemid veebiteenusega: {url_indekseerija}{formaat} status_code={response.status_code}'
            else:
              if formaat == 'json':
                content += json.dumps(json.loads(response.text), indent=2, ensure_ascii=False).replace(' ', '&nbsp;').replace('\n', '<br>')+'<br><br>'
              else: # formaat=='csv'
                  content = response.text.replace('\n', '<br>')+'<br><br>'
          except:
            content = f'Probleemid veebiteenusega: {url_indekseerija}{formaat}'
    return render_template('process.html', query_result=content)

if __name__ == '__main__':
    import argparse
    default_port=5000
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

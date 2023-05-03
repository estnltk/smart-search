#!/usr/bin/env python3

'''
Eeldused:
$ cd ~/git/smart_search_github/wp/wp_indekseerija
$ ./create_venv.sh
$ mkdir uploads
'''

import os
from flask import Flask, render_template, request, redirect, url_for, abort, render_template_string, make_response
from werkzeug.utils import secure_filename
from pathlib import Path
import requests
import json
#from io import StringIO

class HTML_FORMS:
    def __init__(self):
      self.VERSION="2023.05.01"

      self.indekseerija_soned = os.environ.get('INDEKSEERIJA_SONED')
      if self.indekseerija_soned is None:
          self.INDEKSEERIJA_SONED_IP=os.environ.get('INDEKSEERIJA_SONED_IP') if os.environ.get('INDEKSEERIJA_SONED_IP') != None else 'localhost'
          self.INDEKSEERIJA_SONED_PORT=os.environ.get('INDEKSEERIJA_SONED_PORT') if os.environ.get('INDEKSEERIJA_SONED_PORT') != None else '6606'
          self.indekseerija_soned = f'http://{self.INDEKSEERIJA_SONED_IP}:{self.INDEKSEERIJA_SONED_PORT}/api/indekseerija-soned/'

      self.indekseerija_lemmad = os.environ.get('INDEKSEERIJA_LEMMAD')
      if self.indekseerija_lemmad is None:
          self.INDEKSEERIJA_LEMMAD_IP=os.environ.get('INDEKSEERIJA_LEMMAD_IP') if os.environ.get('INDEKSEERIJA_LEMMAD_IP') != None else 'localhost'
          self.INDEKSEERIJA_LEMMAD_PORT=os.environ.get('INDEKSEERIJA_LEMMAD_PORT') if os.environ.get('INDEKSEERIJA_LEMMAD_PORT') != None else '6607' 
          self.indekseerija_lemmad = f'http://{self.INDEKSEERIJA_LEMMAD_IP}:{self.INDEKSEERIJA_LEMMAD_PORT}/api/indekseerija-lemmad/'


      self.html_pref = \
      '''
        <!DOCTYPE html><html lang="et"><head><meta charset="UTF-8"></head><body>
      '''

      self.form = \
      '''
      <br><hr><br>
        <h1>Indeksi koostamine</h1>
        <form method="POST" action="" enctype="multipart/form-data">
          <input type="file" name="file"><br><br>
        
        Indeksis:
          <input checked type="radio" name="indekseerija", value="indekseerija-lemmad"> lemmad     </input>
          <input         type="radio" name="indekseerija", value="indekseerija-soned">  sõnavormid </input><br>   

        Väljundformaat:
          <input checked type="radio" name="formaat", value="json"> JSON    </input>
          <input         type="radio" name="formaat", value="csv"> CSV </input><br><br>
                     
          <input type="submit" value="Indekseeri">
        </form>
      '''

      self.html_suf = \
      '''
        </body></html>
      '''


html_forms = HTML_FORMS()
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.txt','.json']
app.config['UPLOAD_PATH'] = 'uploads'      

@app.route('/wp/indekseerija/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def lemmatiseerija_versioon():
    content = f'<html><body>Versioon: {html_forms.VERSION}</body></html>' 
    return render_template_string(html_forms.html_pref+content+html_forms.html_suf)

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
              return render_template_string(html_forms.html_pref+content+html_forms.form+html_forms.html_suf)
          
          uploaded_content = uploaded_file.read().decode()
          # content = uploaded_content
          # uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
          # content = Path(app.config['UPLOAD_PATH']+'/'+filename).read_text()+indekseerija+formaat
          # os.remove(app.config['UPLOAD_PATH']+'/'+filename)
          
          if file_ext == '.json': # failis oli JSON
            try:
              query_json =json.loads(uploaded_content)
            except:
              content = 'Vigane json:\n'+uploaded_file
              return render_template_string(html_forms.html_pref+content+html_forms.form+html_forms.html_suf)
          else: # file_ext == '.txt' # failis oli tekst, teeme JSONiks

            query_json = {"sources": {filename:{"content":uploaded_content}}}
          if indekseerija == "indekseerija-lemmad":
            url_indekseerija = html_forms.indekseerija_lemmad
          else:
            url_indekseerija = html_forms.indekseerija_soned
          try:
            response = requests.post(url_indekseerija+formaat, json=query_json)
            if response.status_code != 200:
              content = f'Probleemid veebiteenusega: {url_indekseerija}{formaat} status_code={response.status_code}'
            else:
              if formaat == 'json':
                content = json.dumps(json.loads(response.text), indent=2, ensure_ascii=False).replace(' ', '&nbsp;').replace('\n', '<br>')+'<br><br>'
              else: # formaat=='csv'
                  tmp = response.text
                  content = response.text.replace('\n', '<br>')+'<br><br>'
          except:
            content = f'Probleemid veebiteenusega: {url_indekseerija}{formaat}'
    return  render_template_string(html_forms.html_pref+content+html_forms.form+html_forms.html_suf)

if __name__ == '__main__':
    import argparse
    default_port=5000
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

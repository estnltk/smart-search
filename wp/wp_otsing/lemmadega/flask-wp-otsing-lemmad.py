#!/usr/bin/env python3

import os
from flask import Flask, render_template_string, request, make_response
import requests
import json

class HTML_FORMS:
    def __init__(self):
        self.VERSION="2023.05.06"

        self.idxfile = os.environ.get('IDXFILE')
        if self.idxfile is None:
            self.idxfile = 'riigiteataja-lemmad-json.idx'

        with open(self.idxfile, 'r') as file:
            self.idx_json = json.load(file)

        self.paring_lemmad = os.environ.get('PARING_LEMMAD')
        if self.paring_lemmad is None:
            self.PARING_LEMMAD_IP=os.environ.get('PARING_LEMMAD_IP') if os.environ.get('PARING_LEMMAD_IP') != None else 'localhost'
            self.PARING_LEMMAD_PORT=os.environ.get('PARING_LEMMAD_PORT') if os.environ.get('PARING_LEMMAD_PORT') != None else '7007' #???
            self.paring_lemmad = f'http://{self.PARING_LEMMAD_IP}:{self.PARING_LEMMAD_PORT}/api/paring-lemmad/'

        self.html_pref = '<!DOCTYPE html><html lang="et"><head><meta charset="UTF-8"></head><body>'

        #<form method='POST' enctype='multipart/form-data' action='/wp/otsing/tekstid'>
        self.form_show_docs = \
            '''
            <form method='POST' enctype='multipart/form-data'>
                <b>Vali dokument:</b><br>
                    <input type="radio" name="document", 
                        value="kuberturvalisuse-seadus_1_peatukk"> Küberturvalisuse seadus. 1. peatükk </input><br>
                    <input type="radio" name="document", 
                        value="kuberturvalisuse-seadus_2_peatukk"> Küberturvalisuse seadus. 2. peatükk </input><br>
                    <input type="radio" name="document", 
                        value="kuberturvalisuse-seadus_3_peatukk"> Küberturvalisuse seadus. 3. peatükk </input><br>
                    <input type="radio" name="document", 
                        value="kuberturvalisuse-seadus_4_peatukk"> Küberturvalisuse seadus. 4. peatükk </input><br>
                    <input type="radio" name="document", 
                        value="kuberturvalisuse-seadus_5_peatukk"> Küberturvalisuse seadus. 5. peatükk </input><br>
                    <input type="radio" name="document", 
                        value="kuberturvalisuse-seadus_6_peatukk"> Küberturvalisuse seadus. 6. peatükk </input><br>

                    <input type="radio" name="document", 
                        value="vabariigi-presidendi-valimise-seadus_1_peatukk"> Vabariigi presidendi valimise seadus. 1. peatükk </input><br>
                    <input type="radio" name="document", 
                        value="vabariigi-presidendi-valimise-seadus_2_peatukk"> Vabariigi presidendi valimise seadus. 2. peatükk </input><br>
                    <input type="radio" name="document", 
                        value="vabariigi-presidendi-valimise-seadus_3_peatukk"> Vabariigi presidendi valimise seadus. 3. peatükk </input><br>
                    <input type="radio" name="document", 
                        value="vabariigi-presidendi-valimise-seadus_4_peatukk"> Vabariigi presidendi valimise seadus. 4. peatükk </input><br>
                    <input type="radio" name="document", 
                        value="vabariigi-presidendi-valimise-seadus_5_peatukk"> Vabariigi presidendi valimise seadus. 5. peatükk </input><br>
                    <input type="radio" name="document", 
                        value="vabariigi-presidendi-valimise-seadus_6_peatukk"> Vabariigi presidendi valimise seadus. 6. peatükk </input><br>

                    <input type="radio" name="document", 
                        value="osmussaare-maastikukaitseala-kaitse-eeskiri_1_peatukk"> Osmussaare maastikukaitseala kaitse-eeskiri. 1. peatukk </input><br>
                    <input type="radio" name="document", 
                        value="osmussaare-maastikukaitseala-kaitse-eeskiri_2_peatukk"> Osmussaare maastikukaitseala kaitse-eeskiri. 2. peatukk </input><br>
                    <input type="radio" name="document", 
                        value="osmussaare-maastikukaitseala-kaitse-eeskiri_3_peatukk"> Osmussaare maastikukaitseala kaitse-eeskiri. 3. peatukk </input><br>
                    <input type="radio" name="document", 
                        value="osmussaare-maastikukaitseala-kaitse-eeskiri_4_peatukk"> Osmussaare maastikukaitseala kaitse-eeskiri. 4. peatukk </input><br>
                    <input type="radio" name="document", 
                        value="osmussaare-maastikukaitseala-kaitse-eeskiri_5_peatukk"> Osmussaare maastikukaitseala kaitse-eeskiri. 5. peatukk </input><br>
                    <br>

                <input type="submit" name='kuva' value="Kuva" >
                <hr>
            </form>
            '''

        self.html_suf = \
        '''
            <br>
            <a href="https://github.com/estnltk/smart-search/blob/main/wp/wp_otsing/lemmadega/README.md">Kasutusjuhend</a>
            </body></html>
        '''

app = Flask(__name__)
html_forms = HTML_FORMS()

@app.route('/wp/otsing/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def versioon():
    content = f'''
    <html><body>
      Versioon: {html_forms.VERSION}<br>
      Keskkonnamuutujatest:<br>
      &nbsp;&nbsp;paring_lemmad: {html_forms.paring_lemmad}<br>
      &nbsp;&nbsp;idxfile: {html_forms.idxfile}
    </body></html>''' 
    return render_template_string(html_forms.html_pref+content+html_forms.html_suf)

@app.route('/wp/otsing/tekstid', methods=['GET', 'POST'])
@app.route('/tekstid', methods=['GET', 'POST'])
def tekstid():
    content = ''
    if request.method == 'POST':
        docid = request.form.getlist('document')[0]
        content = f'<h2>DocID: {docid}</h2>'
        content += html_forms.idx_json["sources"][docid]["content"].replace('\n', '<br>')+'<hr>'
        pass

    return render_template_string(html_forms.html_pref+html_forms.form_show_docs+content+html_forms.html_suf)




if __name__ == '__main__':
    import argparse
    default_port=6013
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

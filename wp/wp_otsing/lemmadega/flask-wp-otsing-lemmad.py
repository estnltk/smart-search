#!/usr/bin/env python3

'''
Flask veebiserver otsingumootori pakendamiseks
'''

import os
from flask import Flask, render_template_string, request, make_response
import requests
import json
from collections import OrderedDict

import wp_otsing_lemmad

class HTML_FORMS:
    def __init__(self):
        self.VERSION="2023.05.06"

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
        
        self.form_otsing = \
            '''
            <form method='POST' enctype='multipart/form-data'>
                <input type="checkbox" name="fragments" value="fragments" checked>Otsi liitsõna osasõnadest</input><br><br>
                Väljundformaat:
                    <input checked type="radio" name="formaat", value="text"> tekst    </input>
                    <input         type="radio" name="formaat", value="json"> JSON </input>
                    <input         type="radio" name="formaat", value="csv"> CSV </input><br><br>               
                <input name="message" type="text"><input type="submit" value="Otsing" ><br><br><hr>
            </form>
            '''
        self.html_suf = \
        '''
            <a href="https://github.com/estnltk/smart-search/blob/main/wp/wp_otsing/lemmadega/README.md">Kasutusjuhend</a>
            </body></html>
        '''


    
smart_search = wp_otsing_lemmad.SMART_SEARCH()   # otsingumootor
html_forms = HTML_FORMS()       # veebilehe kokkupanemiseks vajalikud HTML-tükikesed 
app = Flask(__name__)           # Fläski äpp

@app.route('/wp/otsing/lemmad/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def versioon():
    """Kuvame veebilehel versiooniinfot ja veel üht-teist

    """
    content = f'''
            Veebilehe versioon: {html_forms.VERSION}<br>
            Otsingu versioon: {html_forms.VERSION}<br>
            Keskkonnamuutujatest:<br>
            &nbsp;&nbsp;paring_lemmad: {html_forms.paring_lemmad}<br>
            &nbsp;&nbsp;idxfile: {smart_search.idxfile}<br>
            <hr>
    ''' 
    return render_template_string(html_forms.html_pref+content+html_forms.html_suf)

@app.route('/wp/otsing/lemmad/texts', methods=['GET', 'POST'])
@app.route('/texts', methods=['GET', 'POST'])
def tekstid():
    """Kuvame veebilehel kasutaja valitud dokumenti 
    
    """
    content = ''
    if request.method == 'POST':
        docid = request.form.getlist('document')[0]
        content = f'<h2>DocID: {docid}</h2>'
        content += smart_search.idx_json["sources"][docid]["content"].replace('\n', '<br>')+'<hr>'
    return render_template_string(html_forms.html_pref+html_forms.form_show_docs+content+html_forms.html_suf)

'''
Indeksi formaat:
    html_forms.idxfile =
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
            "lemmas": [str]
        }
    }
}
'''

@app.route('/wp/otsing/lemmad/process', methods=['GET', 'POST'])
@app.route('/process', methods=['GET', 'POST'])
def lemmas_process():
    """Veebileht päringu sisestamiseks ja päringutulemuste kuvamiseks

    """
    content = ''
    if request.method == 'POST':
        fragments = True if len(request.form.getlist('fragments')) > 0 else False
        formaat = request.form.getlist('formaat')[0]
        query_words = request.form.get('message').strip()
        paringu_url=html_forms.paring_lemmad+'json'
        query_json = json.loads(requests.post(paringu_url, json={"content":query_words}).text)
        smart_search.otsing(fragments, query_json)
        content = smart_search.koosta_vastus(formaat)
        pass
    return render_template_string(html_forms.html_pref+html_forms.form_otsing+content+html_forms.html_suf)


if __name__ == '__main__':
    import argparse
    default_port=6013
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

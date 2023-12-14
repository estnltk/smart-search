#!/usr/bin/python3

'''Flask api, (eel)arvutab JSON-failid mis on vajlikud andmebaasi kokkupanemiseks
----------------------------------------------
// code (serveri käivitamine silumiseks):
        {
            "name": "create_jsontables",
            "type": "python",
            "request": "launch",
            "cwd": "${workspaceFolder}/api/ea_jsoncontent_2_jsontabelid/",
            "program": "./flask_api_ea_jsoncontent_2_jsontabelid.py",
            "env": {}
            "args": []
        },
----------------------------------------------
Lähtekoodist pythoni skripti kasutamine:
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2) ja käivitamine(1.3)
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart-search_github/api/ea_jsoncontent_2_jsontabelid
    $ ./create_venv.sh
1.3 Sätime paika kasutatvad teenused: kasutame veebis olevaid konteinereid (1.3.1) või kasutame kohalikus masinas töötavaid konteinereid (1.3.2)
1.3 Pythoni skripti käivitamine
    $ cd ~/git/smart-search_github/api/ea_jsoncontent_2_jsontabelid
    $ make -j all
----------------------------------------------
Lähtekoodist veebiserveri käivitamine & kasutamine
2 Lähtekoodi allalaadimine (2.1), virtuaalkeskkonna loomine (2.2), veebiteenuse käivitamine pythoni koodist (2.3) ja CURLiga veebiteenuse kasutamise näited (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Virtuaalkeskkonna loomine: järgi punkti 1.2
2.3 Veebiteenuse käivitamine pythoni koodist
    $ cd ~/git/smart-search_github/api/ea_jsoncontent_2_jsontabelid
    $ ./venv/bin/python3 ./flask_api_ea_jsoncontent_2_jsontabelid.py
2.4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/text" \
        localhost:6602/api/create_jsontables/version | jq
    $ curl --silent --request POST --header "Content-Type: application/csv" \
      --data-binary @test_headers.csv \
      localhost:6602/api/create_jsontables/headers  | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
      --data-binary @test_document.json \
      localhost:6602/api/create_jsontables/document  | jq
----------------------------------------------
Lähtekoodist tehtud konteineri kasutamine
3 Lähtekoodi allalaadimine (3.1), konteineri kokkupanemine (3.2), konteineri käivitamine (3.3) ja CURLiga veebiteenuse kasutamise näited  (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart-search_github/api/ea_jsoncontent_2_jsontabelid
    $ docker build -t tilluteenused/smart_search_api_ea_content_2_jsontabelid:2023.12.14 . 
    # docker push tilluteenused/smart_search_api_ea_content_2_jsontabelid:2023.12.14
2.3 Konteineri käivitamine
    $ docker run -p 6602:6602  \
        --env SMART_SEARCH_MAX_CONTENT_LENGTH='10000000000' \
        --env SMART_SEARCH_GENE_TYPOS='true' \
        tilluteenused/smart_search_api_ea_content_2_jsontabelid:2023.12.14 
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4
----------------------------------------------
DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_api_ea_content_2_jsontabelid:2023.12.14
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4
----------------------------------------------
TÜ pilves töötava konteineri kasutamine
4 CURLiga veebiteenuse kasutamise näited
    $ cd ~/git/smart-search_github/api/ea_jsoncontent_2_jsontabelid # selles kataloogis on test_headers.csv ja test_document.json

    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data-binary @test_headers.csv \
        https://smart-search.tartunlp.ai/api/create_jsontables/headers | jq | less

    $ curl --silent --request POST --header "Content-Type: application/json" \
      --data-binary @test_document.json \
      https://smart-search.tartunlp.ai/api/create_jsontables/document  | jq | less

    $ curl --silent --request POST --header "Content-Type: application/json" \
      --data '{"sources":{"testdoc_1":{"content":"Presidendi kantselei."}, "testdoc_2":{"content":"Raudteetranspordiga raudteejaamas."}}}' \
      https://smart-search.tartunlp.ai/api/create_jsontables/document  | jq
      
    $ curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/create_jsontables/version | jq

----------------------------------------------
'''
import os
import sys
import json
import requests
import subprocess
import json
import argparse
from flask import Flask, request, jsonify, make_response, abort
from functools import wraps
from typing import Dict, List, Tuple
from collections import OrderedDict

import api_ea_jsoncontent_2_jsontabelid_2

VERSION="2023.12.14"

try:
    SMART_SEARCH_GENE_TYPOS=(os.environ.get('SMART_SEARCH_GENE_TYPOS').upper()=="TRUE")
except:
    SMART_SEARCH_GENE_TYPOS = False # vaikimisi ei genereeri kirjavigasid
tj = api_ea_jsoncontent_2_jsontabelid_2.TEE_JSON(verbose=False, kirjavead=SMART_SEARCH_GENE_TYPOS)

app = Flask("api_ea_jsoncontent_2_jsontabelid")

# JSONsisendi max suuruse piiramine {{
try:
    SMART_SEARCH_MAX_CONTENT_LENGTH=int(os.environ.get('SMART_SEARCH_MAX_CONTENT_LENGTH'))
except:
    SMART_SEARCH_MAX_CONTENT_LENGTH = 10 * 1000000000 # 10 GB 

def limit_content_length(max_length):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            cl = request.content_length
            if cl is not None and cl > max_length:
                abort(413)
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.errorhandler(413) # Liiga mahukas päring
def request_entity_too_large(error):
    #return 'File Too Large', 413
    return jsonify({"error":"Request Entity Too Large"})

# }} JSONsisendi max suuruse piiramine 

@app.route('/api/create_jsontables/headers', methods=['POST'])
@app.route('/headers', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def create_jsontables_headers():
    """Leia sisendkorpuse sõnede kõikvõimalikud vormid ja nonde hulgast need, mis esinesid korpuses

    Args:

    * CSV pealkirjade ja seotud infoga:
        global_id,document_type,document_title,xml_source

        
    Kui dokumendiga tuleb kaasa lisainfot, siis tuleb alljärgnevatesse tabelitesse tekitada
    vastavatesse kohtadesse lisaveerud vastava infoga    

    Returns:
        Response: VäljundJSON:

        {   "tabelid":  // lõpptulemus
            {   "lemma_kõik_vormid": [(VORM, PARITOLU, LEMMA)],     # (LEMMA_kõik_vormid, 0:korpusest|1:abisõnastikust, sisendkorpuses_esinenud_sõnavormi_LEMMA)
                "ignoreeritavad_vormid": [(VORM, 0)],               # tee_ignoreeritavad_vormid(), 0:vorm on genereeritud etteantud lemmast
                "kirjavead": [(VIGANE_VORM, VORM, KAAL)]            # (kõikvõimalikud_VORMi_kirjavigased_variandid, sisendkorpuses_esinenud_sõnaVORM, kaal_hetkel_alati_0)
                "lemma_korpuse_vormid": [(LEMMA, VORM)],            # (sisendkorpuses_esinenud_sõnavormi_LEMMA, kõik_LEMMA_vormid_mis_sisendkorpuses_esinesid)
                "indeks": [(VORM, DOCID, START, END, LIITSÕNA_OSA)] # (sisendkorpuses_esinenud_sõnaVORM, dokumendi_id, alguspos, lõpupos, True:liitsõna_osa|False:terviksõna)
                "allikad": [(DOCID, CONTENT)]                       # (docid, dokumendi_"plain_text"_mille_suhtes_on_arvutatud_START_ja_END)
            }
        }  

    https://stackoverflow.com/questions/62685107/open-csv-file-in-flask-sent-as-binary-data-with-curl
    """
    try:
        csv_data = request.data.decode("utf-8")
        tj.csvpealkrjadest(csv_data.splitlines())
        tj.tee_sõnestamine()
        tj.tee_kõigi_terviksõnede_indeks()
        tj.tee_mõistlike_tervik_ja_osasõnede_indeks()
        tj.tabelisse_vormide_indeks()
        tj.tee_mõistlike_lemmade_ja_osalemmade_indeks()
        tj.tabelisse_lemmade_indeks()
        tj.tee_generator()
        tj.tee_kirjavead()
        tj.tee_sources_tabeliks()
        tj.kustuta_vahetulemused()
        tj.kordused_tabelitest_välja()

        return jsonify(tj.json_io)
    except Exception as e:
        return jsonify(e.args[0])    

@app.route('/api/create_jsontables/document', methods=['POST'])
@app.route('/document', methods=['POST'])
@limit_content_length(SMART_SEARCH_MAX_CONTENT_LENGTH)
def create_jsontables_document():
    """Leia sisendkorpuse sõnede kõikvõimalikud vormid ja nonde hulgast need, mis esinesid korpuses

    Args: 

    * JSON:
        {"sources":{DOCID:{"content:str}}}
        
    Kui dokumendiga tuleb kaasa lisainfot, siis tuleb alljärgnevatesse tabelitesse tekitada
    vastavatesse kohtadesse lisaveerud vastava infoga    

    Returns:
        Response: VäljundJSON:
    {   "tabelid":
        {   "indeks_vormid":[(VORM, DOCID, START, END, LIITSÕNA_OSA)],
            "indeks_lemmad":[(LEMMA, DOCID, START, END, LIITSÕNA_OSA)],
            "liitsõnad":[(OSALEMMA, LIITLEMMA)],
            "lemma_kõik_vormid":[(VORM, KAAL, LEMMA)],
            "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)],
            "kirjavead":[(VIGANE_VORM, VORM)],
            "allikad":[(DOCID, CONTENT)],
        }
    } 

    https://stackoverflow.com/questions/62685107/open-csv-file-in-flask-sent-as-binary-data-with-curl
    """
    try:
        tj.json_io = request.json
        tj.tee_sõnestamine()
        tj.tee_kõigi_terviksõnede_indeks()
        tj.tee_mõistlike_tervik_ja_osasõnede_indeks()
        tj.tabelisse_vormide_indeks()
        tj.tee_mõistlike_lemmade_ja_osalemmade_indeks()
        tj.tabelisse_lemmade_indeks()
        tj.tee_generator()
        tj.tee_kirjavead()
        tj.tee_sources_tabeliks()
        tj.kustuta_vahetulemused()
        tj.kordused_tabelitest_välja()

        return jsonify(tj.json_io)
    except Exception as e:
        return jsonify(e.args[0])    


@app.route('/api/create_jsontables/version', methods=['GET', 'POST'])
@app.route('/version', methods=['POST'])
def api_create_jsontables_version():
    """Kuvame versiooni ja muud infot

    Returns:
        ~flask.Response: Lemmatiseerija versioon
    """
    json_response = tj.version_json()
    json_response["SMART_SEARCH_MAX_CONTENT_LENGTH"] = SMART_SEARCH_MAX_CONTENT_LENGTH
    json_response["genereeri_kirjavead"] = tj.kirjavead
    return jsonify(json_response)

if __name__ == '__main__':
    default_port=6602
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)



        

        
        
    
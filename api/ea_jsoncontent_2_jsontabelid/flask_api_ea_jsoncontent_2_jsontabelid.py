#!/usr/bin/python3

'''Flask api, eelarvutab JSON-failid

----------------------------------------------

Lähtekoodist pythoni skripti kasutamine:
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2), kasutavate teenuste paikasättimine (1.3) ja pythoni skripti käivitamine(1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart-search_github/api/ea_jsoncontent_2_jsontabelid
    $ ./create_venv.sh
1.3 Sätime paika kasutatvad teenused: kasutame veebis olevaid konteinereid (1.3.1) või kasutame kohalikus masinas töötavaid konteinereid (1.3.2)
1.3.1 Kasutame veebis olevaid konteinereid
    $ export TOKENIZER=https://smart-search.tartunlp.ai/api/tokenizer/process \
    $ export GENERATOR=https://smart-search.tartunlp.ai/api/vm/generator/process \
    $ export ANALYSER=https://smart-search.tartunlp.ai/api/analyser/process  \
1.3.2 Kasutame kohalikus masinas töötavaid konteinereid        
    $ docker run -p 6000:6000 tilluteenused/estnltk_sentok:2023.04.18
    $ docker run -p 7008:7008 tilluteenused/vmetsjson:2023.09.21
    $ docker run -p 7007:7007 tilluteenused/vmetajson:2023.06.01
1.4 Pythoni skripti käivitamine
    $ cd ~/git/smart-search_github/api/ea_jsoncontent_2_jsontabelid
    $ ./venv/bin/python3 ./api_ea_jsoncontent_2_jsontabelid.py --verbose --indent=4\
        ../../testkorpused/microcorpus/microcorpus1.json \
        ../../testkorpused/microcorpus/microcorpus2.json

----------------------------------------------

Lähtekoodist veebiserveri käivitamine & kasutamine
2 Lähtekoodi allalaadimine (2.1), virtuaalkeskkonna loomine (2.2), kasutavate teenuste paikasättimine (2.3) veebiteenuse käivitamine pythoni koodist (2.4) ja CURLiga veebiteenuse kasutamise näited (2.5)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Virtuaalkeskkonna loomine: järgi punkti 1.2
2.3 Sätime paika kasutatvad teenused: järgi punkti 1.3
2.4 Veebiteenuse käivitamine pythoni koodist
    $ cd ~/git/smart-search_github/api/ea_jsoncontent_2_jsontabelid
    $ ./venv/bin/python3 ./flask_api_ea_jsoncontent_2_jsontabelid.py
2.5 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Peaministri kantselei."}}}' \
        localhost:6602/api/ea_jsoncontent_2_jsontabelid/json | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:6602/api/ea_jsoncontent_2_jsontabelid/version | jq
----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
3 Lähtekoodi allalaadimine (3.1), konteineri kokkupanemine (3.2), konteineri käivitamine (3.3) ja CURLiga veebiteenuse kasutamise näited  (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart-search_github/api/ea_jsoncontent_2_jsontabelid
    $ docker build -t tilluteenused/smart_search_api_ea_jsoncontent_2_jsontabelid:2023.09.20 . 
2.3 Konteineri käivitamine
    $ docker run -p 6602:6602  \
        --env TOKENIZER='https://smart-search.tartunlp.ai/api/tokenizer/process' \
        --env ANALYSER='https://smart-search.tartunlp.ai/api/analyser/process' \
        --env GENERATOR='https://smart-search.tartunlp.ai/api/generator/process' \
        tilluteenused/smart_search_api_ea_jsoncontent_2_jsontabelid:2023.09.20 
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_api_ettearvutaja:2023.09.20 
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Presidendi kantselei."}}}' \
        https://smart-search.tartunlp.ai/api/ea_jsoncontent_2_jsontabelid/json | jq | less
    $ curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/ea_jsoncontent_2_jsontabelid/version | jq
----------------------------------------------
'''


import os
import sys
import json
import requests
import subprocess
import json
import argparse
from flask import Flask, request, jsonify, make_response
from typing import Dict, List, Tuple
from collections import OrderedDict

import api_ea_jsoncontent_2_jsontabelid

ettearvutaja = api_ea_jsoncontent_2_jsontabelid.ETTEARVUTAJA(False)

app = Flask("api_ea_jsoncontent_2_jsontabelid")

@app.route('/api/ea_jsoncontent_2_jsontabelid/json', methods=['POST'])
@app.route('/json', methods=['POST'])
def api_lemmade_ettearvutaja_json():
    """Leia sisendkorpuse sõnede kõikvõimalikud vormid ja nonde hulgast need, mis esinesid korpuses

    Args:

        request.json: // SisendJSON, sisaldab korpusetekste

        {   "sources":
            {   DOCID:              // dokumendi ID
                {   "content": str  // dokumendi "plain text" 
                                    // dokumendi kohta käiv lisainfo pane siia eraldi eraldi võtmete alla
                }
            }
        }

    Kui dokumendiga tuleb kaasa lisainfot, siis tuleb alljärgnevatesse tabelitesse tekitada
    vastavatesse kohtadesse lisaveerud vastava infoga    

    Returns:
        Response: VäljundJSON:

        {   "tabelid":  // lõpptulemus
            {   "lemma_kõik_vormid": [(VORM, PARITOLU, LEMMA)],     # (LEMMA_kõik_vormid, 0:korpusest|1:abisõnastikust, sisendkorpuses_esinenud_sõnavormi_LEMMA)
                "ignoreeritavad_vormid": [(VORM, 0)],               # tee_ignoreeritavad_vormid(), 0:vorm on genereeritud etteantud lemmast
                "kirjavead": [(VIGANE_VORM, VORM, KAAL)]            # (kõikvõimalikud_VORMi_kirjavigased_variandid, sisendkorpuses_esinenud_sõnaVORM, kaal_hetkel_alati_0)
                "lemma_korpuse_vormid": [(LEMMA, VORM)],             # (sisendkorpuses_esinenud_sõnavormi_LEMMA, kõik_LEMMA_vormid_mis_sisendkorpuses_esinesid)
                "indeks": [(VORM, DOCID, START, END, LIITSÕNA_OSA)] # (sisendkorpuses_esinenud_sõnaVORM, dokumendi_id, alguspos, lõpupos, True:liitsõna_osa|False:terviksõna)
                "allikad": [(DOCID, CONTENT)]                       # (docid, dokumendi_"plain_text"_mille_suhtes_on_arvutatud_START_ja_END)
            }
        }  
    """
    try:
        ettearvutaja.json_io = request.json
        ettearvutaja.tee_sõnestamine()
        ettearvutaja.tee_sõnede_ja_osaõnede_indeks()
        ettearvutaja.tee_generator()
        ettearvutaja.tee_kirjavead()
        ettearvutaja.tee_sources_tabeliks()
        ettearvutaja.kustuta_vahetulemused()
        return jsonify(ettearvutaja.json_io)
    except Exception as e:
        return jsonify(e.args[0])    

@app.route('/api/ea_jsoncontent_2_jsontabelid/version', methods=['GET', 'POST'])
@app.route('/version', methods=['POST'])
def api_lemmade_ettearvutaja_version():
    """Kuvame versiooni ja muud infot

    Returns:
        ~flask.Response: Lemmatiseerija versioon
    """
    json_response = ettearvutaja.version_json()
    return jsonify(json_response)

if __name__ == '__main__':
    default_port=6602
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)



        

        
        
    
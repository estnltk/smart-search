#!/usr/bin/python3

'''Flask api, päringustring päringut esitavaks JSONiks. Teine variant

----------------------------------------------

Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2), veebiteenuse käivitamine pythoni koodist (1.3) ja CURLiga veebiteenuse kasutamise näited (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart-search_github/api/ea_paring_sl
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd  ~/git/smart-search_github/api/ea_paring_sl
    $ DB_PARING="./1024-koond.sqlite" \
        venv/bin/python3 ./flask_api_ea_paring_sl.py
1.4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"presidendiga\tpalk"}' \
        localhost:6602/api/ea_paring_sl/tsv | less
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"otsi_liitsõnadest":false}, "tss":"presidendiga\tpalk"}' \
        localhost:6602/api/ea_paring_sl/tsv | less
     $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:6602/api/ea_paring_sl/version
----------------------------------------------
Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja CURLiga veebiteenuse kasutamise näited  (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart-search_github/api/ea_paring_sl
    $ docker build -t tilluteenused/smart_search_api_ea_paring_sl:2023.10.14 . 
    # docker push tilluteenused/smart_search_api_ea_paring_sl:2023.10.14
2.3 Konteineri käivitamine
    $ docker run -p 6602:6602  \
        --env DB_PARING="./1024-koond.sqlite" \
        tilluteenused/smart_search_api_ea_paring_sl:2023.10.14
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4
----------------------------------------------
DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_api_ea_paring_sl:2023.10.14
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4
----------------------------------------------
TÜ pilves töötava konteineri kasutamine
4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"presidendiga\tpalk"}' \
        https://smart-search.tartunlp.ai/api/ea_paring_sl/tsv
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"otsi_liitsõnadest":false}, "tss":"presidendiga\tpalk"}' \
        https://smart-search.tartunlp.ai/api/ea_paring_sl/tsv
    $ curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/ea_paring_sl/version | jq
----------------------------------------------
'''

import argparse
from flask import Flask, request, jsonify, make_response
#from typing import Dict, List, Tuple

import api_ea_paring_sl

paring_soned = api_ea_paring_sl.PARING_SONED(None, csthread=False)

app = Flask("api_ea_paring_sl")

@app.route('/api/ea_paring_sl/tsv', methods=['POST'])
@app.route('/tsv', methods=['POST'])
def api_ea_paring_json_json():
    try:
        paring_soned.json_io = request.json
        paring_soned.paring_tsv()
        res_str = ''
        for location, input, lemma, type, confidence, wordform in paring_soned.response_table:
            res_str += f'{location}\t{input}\t{lemma}\t{type}\t{confidence}\t{wordform}\n'
        
        response = make_response(res_str)
        response.headers["Content-type"] = "text/tsv"
        return response
    except Exception as e:
        return jsonify(e.args[0])    

@app.route('/api/ea_paring_sl/version', methods=['GET', 'POST'])
@app.route('/version', methods=['POST'])
def api_ea_paring_version():
    """Kuvame versiooni ja muud infot

    Returns:
        ~flask.Response: Versiooni-info
    """
    return jsonify(paring_soned.version_json())

if __name__ == '__main__':
    default_port=6602
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)



        

        
        
    
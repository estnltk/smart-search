 #!/usr/bin/env python3

""" 
----------------------------------------------
Flask veebiserver, pakendab Filosofti morfoloogilise süntesaatori veebiteenuseks,
smartsearch projektile kohendatud versioon.
----------------------------------------------
Silumiseks (serveri käivtamine code'is, päringud vt 1.4):
    {
        "name": "flask_sl_generator.py",
        "type": "python",
        "request": "launch",
        "cwd": "${workspaceFolder}/api/sl_generator/",
        "program": "./flask_sl_generator.py",
        "env": {},
        "args": []
    },
----------------------------------------------
Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2), veebiteenuse käivitamine pythoni koodist (1.3) ja CURLiga veebiteenuse kasutamise näited (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone https://github.com/estnltk/smart-search.git smart-search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart-search_github/api/sl_generator
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd ~/git/smart-search_github/api/sl_generator
    $ venv/bin/python3 flask_sl_generator.py
1.4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"tere\tpidama"}' \
        localhost:7008/api/sl_generator/tss
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":["with_apostrophe"], "tss":"Strassbourg"}' \
        localhost:7008/api/sl_generator/tss
    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:7008/api/sl_generator/version
----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja CURLiga veebiteenuse kasutamise näited  (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart-search_github/api/sl_generator
    $ docker build -t tilluteenused/smart_search_api_sl_generator.2023.11.32 .
    # docker login -u tilluteenused
    # docker push tilluteenused/smart_search_api_sl_generator.2023.11.32
2.3 Konteineri käivitamine
    $ docker run -p 7008:7008 tilluteenused/smart_search_api_sl_generator.2023.11.32
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_api_sl_generator.2023.11.32
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"tere\ttalv"}' \
        https://smart-search.tartunlp.ai/api/sl_generator/tss
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":["with_apostrophe"], "tss":"Strassbourg"}' \
        https://smart-search.tartunlp.ai/api/sl_generator/tss
    $ curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/sl_generator/version

----------------------------------------------
"""

import subprocess
import json
import argparse
from flask import Flask, request, jsonify, make_response

import sl_generator

app = Flask("sl_generator")
slg = sl_generator.GENERATOR4SL()

@app.route('/api/sl_generator/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def api_sl_generator_version():
    """Tagastame veebiliidese versiooni

    Returns:
        ~flask.Response: JSONkujul versioonistring
    """
    return jsonify({"version":slg.VERSION})

@app.route('/api/sl_generator/tss', methods=['POST'])
@app.route('/tss', methods=['POST'])
def api_sl_generator_process_tsv():
    """Morf sünteesime JSONiga nõutud lemmade+vormid ja kuvame tulemust TSV-kujul

    Returns:
        ~flask.Response: Morf sünteesi tulemused
    """
    with_apostrophe = False
    if "params" in request.json:
        if "with_apostrophe" in request.json["params"]:
            with_apostrophe = True
    res_list = slg.generator2list(request.json["tss"].split('\t'), with_apostrophe)
    res_str = 'with_apostrophe'
    for line in res_list:
        res_str += f'{str(line[0])}\t{line[1]}\t{line[2]}\t{line[3]}\n'
    response = make_response(res_str)
    response.headers["Content-type"] = "text/csv"
    return response

if __name__ == '__main__':
    default_port=7008
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

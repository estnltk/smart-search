 #!/usr/bin/env python3

VERSION = "2023.11.20"

""" 
----------------------------------------------

Flask veebiserver, pakendab Filosofti morfoloogilise analüsaatori veebiteenuseks

----------------------------------------------

Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2), veebiteenuse käivitamine pythoni koodist (1.3) ja CURLiga veebiteenuse kasutamise näited (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone git@github.com:Filosoft/vabamorf.git vabamorf_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart-search_github/api/sl_analyser
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd ~/git/smart-search_github/api/sl_analyser
    $ venv/bin/python3 ./flask_vmetajson.py
1.4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--stem", "--guess"]} ,"tss":"punameremaoga\tlambiõliga\tpeeti\t_a"}' \
        localhost:7007/api/sl_analyser/process | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--guess"]} ,"tss":"punameremaoga\tlambiõliga\tpeeti\t_a"}' \
        localhost:7007/api/sl_analyser/process | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--version"]}}' \
        localhost:7007/api/sl_analyser/process | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--version"]}}' \
        localhost:7007/process | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:7007/api/sl_analyser/version | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:7007/version | jq

----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja CURLiga veebiteenuse kasutamise näited  (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart-search_github/api/sl_analyser
    $ docker build -t tilluteenused/vmetajson:2023.11.20 .
    # docker login -u tilluteenused
    # docker push tilluteenused/vmetajson:2023.11.20
2.3 Konteineri käivitamine
    $ docker run -p 7007:7007 tilluteenused/vmetajson:2023.11.20
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/vmetajson:2023.11.20 
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"content":"Mees peeti kinni. Sarved&Sõrad: telef. +372 345 534."}' \
        https://smart-search.tartunlp.ai/api/analyser/process | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/analyser/version | jq  
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--version"]}}' \
        https://smart-search.tartunlp.ai/api/analyser/process | jq

----------------------------------------------
"""

import subprocess
import json
import argparse
from flask import Flask, request, jsonify

proc = subprocess.Popen(['./vmetajson', '--path=.'],  
                            universal_newlines=True, 
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)

app = Flask("vmetajson")

@app.route('/api/sl_analyser/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def api_analyser_version():
    """Tagastame veebiliidese versiooni

    Returns:
        ~flask.Response: JSONkujul versioonistring
    """
    return jsonify({"version":VERSION})

@app.route('/api/sl_analyser/process', methods=['POST'])
@app.route('/process', methods=['POST'])
def morf():
    """Morf analüüsime JSONiga antud sõnesid ja kuvame tulemust JSONkujul

    Returns:
        ~flask.Response: Morf analüüsi tulemused
    """
    if "tss" in request.json:
        tokens = request.json["tss"].split('\t')
        if "annotations" not in request.json:
            request.json["annotations"] = {}
        if "tokens" not in request.json["annotations"]:
            request.json["annotations"]["tokens"] = []
        for token in tokens:
            request.json["annotations"]["tokens"].append({"features": {"token": token}})    
    proc.stdin.write(f'{json.dumps(request.json)}\n')
    proc.stdin.flush()
    mrf_out = json.loads(proc.stdout.readline())
    if "annotations" in mrf_out and "tokens" in  mrf_out["annotations"]:
        for token in mrf_out["annotations"]["tokens"]:
            if "features" in token and "mrf" in token["features"]:
                for mrf in token["features"]["mrf"]:
                    if "lemma_ma" in mrf:
                        morfa_result = mrf["lemma_ma"]
                    elif "stem" in mrf:
                        morfa_result = mrf["stem"]
                    else:
                        continue
                    mrf["lisamärkideta"] = morfa_result
                    mrf["komponendid"  ] = []
                    if len(morfa_result) >= 3:
                        mrf["lisamärkideta"] = morfa_result.replace("+", "").replace("=", "").replace("_", "")
                        mrf["komponendid"  ] = morfa_result.replace("+", "").replace("=", "").split("_")
                        if len(mrf["lisamärkideta"]) < 1:
                            mrf["lisamärkideta"] = morfa_result
                            mrf["komponendid"  ] = []
                        if len(mrf["komponendid"]) == 1:
                            mrf["komponendid"] = []
    return jsonify(mrf_out)

if __name__ == '__main__':
    default_port=7007
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)

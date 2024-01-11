 #!/usr/bin/env python3

VERSION = "2024.01.11"

""" 
----------------------------------------------

Flask veebiserver, pakendab Filosofti morfoloogilise analüsaatori veebiteenuseks
JSON väljundisse lisatud eksplitsiitne liitsõna osasõnadeks tükeldamine.

Mida uut:


1 Veebiserveri käivitamine pythoni koodist
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone git@github.com:estnltk/smart_search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/api/api_analyser
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd ~/git/smart_search_github/api/api_analyser
    $ venv/bin/python3 ./flask_api_analyser.py
1.4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--stem", "--guess"]} ,"tss":"punameremaoga\tlambiõliga\tpeeti\t_a"}' \
        localhost:7007/api/analyser/process | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--guess"]} ,"tss":"punameremaoga\tlambiõliga\tpeeti\t_a"}' \
        localhost:7007/api/analyser/process | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--version"]}}' \
        localhost:7007/api/analyser/process | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--version"]}}' \
        localhost:7007/process | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:7007/api/analyser/version | jq
    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:7007/version | jq

----------------------------------------------

2 Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja CURLiga veebiteenuse kasutamise näited  (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd ~/git/smart_search_github/api/api_analyser
    $ docker build -t tilluteenused/smart_search_api_analyser:2024.01.11 .
    # docker login -u tilluteenused
    # docker push tilluteenused/smart_search_api_analyser:2024.01.11
2.3 Konteineri käivitamine
    $ docker run -p 7007:7007 tilluteenused/smart_search_api_analyser:2024.01.11
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

3 DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_api_analyser:2024.01.11
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

4 TÜ KUBERNETESes töötava konteineri kasutamine
4.1 CURLiga veebiteenuse kasutamise näited

    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--stem", "--guess"]} ,"tss":"punameremaoga\tlambiõliga\tpeeti\t_a"}' \
        https://smart-search.tartunlp.ai/api/analyser/process | jq

    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--guess"]} ,"tss":"punameremaoga\tlambiõliga\tpeeti\t_a"}' \
        https://smart-search.tartunlp.ai/api/analyser/process | jq

    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--version"]}}' \
       https://smart-search.tartunlp.ai/api/analyser/process | jq

    $ curl --silent --request POST --header "Content-Type: application/json" \
         https://smart-search.tartunlp.ai/api/analyser/version | jq

----------------------------------------------
4 DockerHUBis oleva konteineri lisamine KUBERNETESesse

4.1 Tekitame vaikeväärtustega deployment-i

$ kubectl create deployment smart-search-api-analyser \
  --image=tilluteenused/smart_search_api_advanced_indexing:2024.01.10

4.2 Tekitame vaikeväärtustega service'i

$ kubectl expose deployment smart-search-api-analyser \
    --type=ClusterIP --port=80 --target-port=7007

4.3 Lisame ingress-i konfiguratsioonifaili

- backend:
    service:
    name: smart-search-api-analyser
    port:
        number: 80
path: /api/analyser/?(.*)
pathType: Prefix

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

@app.route('/api/analyser/version', methods=['GET', 'POST'])
@app.route('/version', methods=['GET', 'POST'])
def api_analyser_version():
    """Tagastame veebiliidese versiooni

    Returns:
        ~flask.Response: JSONkujul versioonistring
    """
    return jsonify({"version":VERSION})

@app.route('/api/analyser/process', methods=['POST'])
@app.route('/process', methods=['POST'])
def api_analyser_process():
    """Morf analüüsime JSONiga antud sõnesid ja kuvame tulemust JSONkujul

    Returns:
        ~flask.Response: Morf analüüsi tulemused
    """
    if request.json is None:
        return jsonify({"warning": "the request does not contain valid JSON"})
    if "tss" in request.json:
        tokens = request.json["tss"].split('\t')
        if "annotations" not in request.json:
            request.json["annotations"] = {}
        if "tokens" not in request.json["annotations"]:
            request.json["annotations"]["tokens"] = []
        for token in tokens:
            request.json["annotations"]["tokens"].append({"features": {"token": token}})
    assert proc.stdin is not None and proc.stdout is not None
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

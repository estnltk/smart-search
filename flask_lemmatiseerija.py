 #!/usr/bin/env python3

""" 
# Virtuaalkeskkonna loomine:
$ ./create_venv

# Serveri käivitamine käsurealt
$ ./venv/bin/python3 ./flask_lemmatiseerija.py

# Päringute näited:
$ curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Vanamehe kodujuustu peeti keaks ."}' localhost:5000/process|jq
$ curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Vanamehe kodujuustu peeti keaks .","params":{"vmetltjson":["--guess"]}}' localhost:5000/process|jq

# Konteineri tegemine:
$ docker build -t vabamorf/lemmatizer . 

# Konteineri käivitamine:
$ docker run -p 7000:7000  vabamorf/lemmatizer

# Päringute näited:
$ curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Vanamehe kodujuustu peeti keaks ."}' localhost:7000/process|jq
$ curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Vanamehe kodujuustu peeti keaks .","params":{"vmetltjson":["--guess"]}}' localhost:7000/process|jq
"""

import subprocess
import json
import argparse
from flask import Flask, request, jsonify

proc = subprocess.Popen(['./vmetltjson', '--path=.'],  
                            universal_newlines=True, 
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)

app = Flask("vmetltjson")

@app.route('/process', methods=['POST']) #@app.route('/morf', methods=['GET', 'POST'])
def morf():
    """Lemmatiseerime JSONiga antud sõnesid ja kuvame tulemust JSONkujul

    Returns:
        ~flask.Response: Lemmatiseerimise tulemused
    """
    proc.stdin.write(f'{json.dumps(request.json)}\n')
    proc.stdin.flush()
    return jsonify(json.loads(proc.stdout.readline()))

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug)


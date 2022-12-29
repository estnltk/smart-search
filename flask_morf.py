 #!/usr/bin/env python3

""" 
Virtuaalkeskkonna loomine:
$ ./create_venv
Serveri käivitamine
./venv/bin/python3 ./flask_vmetajson.py
Päringute näited:
curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Mees peeti kinni ."}' localhost:6000/morf|jq
curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"Mees peeti kinni .","params":{"vmetajson":["--guess"]}}' localhost:6000/morf|jq
"""

import os
import json
import argparse
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask("vabamorf")

status_data = { 
    "STARTED": "{:%Y.%m.%d_%H:%M:%S}".format(datetime.now()), 
    "WORKERS":os.getenv('WORKERS'),"TIMEOUT":os.getenv('TIMEOUT'),
    "WORKER_CLASS":os.getenv('WORKER_CLASS')
    }

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Tagastame pisut tehnilist infot

    Returns:
        ~flask.Response: Pisut tehnilist infot
    """
    return jsonify(status_data)

if __name__ == '__main__':
    app.run()

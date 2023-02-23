 #!/usr/bin/env python3

""" 
index =
{
    "sources":
    {
        DOCID:
        {
            "filename": str,
            "heading": str,
            "content": str
        }
    }
    annotations:
    {
        "lemmas":
        {
            LEMMA:
            {
                DOCID:
                {
                    {STARTPOS:endpos}
                }
            }
        }
    }
}

result_query=
{
    DOCID:
    {
        {STARTPOS: endpos}
    }
}
"""

import sys
import subprocess
import json
import argparse
from flask import Flask, request, jsonify
from typing import Dict, List


proc = subprocess.Popen(['./normaliseerija/vmetltjson', '--path=./normaliseerija', '--guess'],  
                            universal_newlines=True, 
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)

app = Flask("vmetltjson")

index = {}

@app.route('/process', methods=['POST']) #@app.route('/process', methods=['GET', 'POST'])
def morf():
    """Lemmatiseerime JSONiga antud sõnesid ja kuvame tulemust JSONkujul

    Returns:
        ~flask.Response: Lemmatiseerimise tulemused
    """
    proc.stdin.write(f'{json.dumps(request.json)}\n')
    proc.stdin.flush()
    return jsonify(json.loads(proc.stdout.readline()))

result_query ={}

def my_query(keywords:str)->None:
    result_query ={}
    mq = f'{{"content":"{keywords}"}}\n'
    proc.stdin.write(mq)
    proc.stdin.flush()
    query_lemmas = json.loads(proc.stdout.readline())

    query_tokens = query_lemmas["annotations"]["tokens"]
    idx_query_token = 0
    for idx_mrf, mrf in enumerate(query_tokens[idx_query_token]["features"]["mrf"]): # tsükkel ole päringusõnele vastavate lemmade
        query_lemma_ma = mrf.get("lemma_ma")
        if query_lemma_ma is None: # päringusõna morf analüüsis polnud lemmat
            continue
        index_lemma_ma = index["annotations"]["lemmas"].get(query_lemma_ma)
        if index_lemma_ma is None: # päringusõna lemmat polnud indeksis
            continue

        for index_docid in index_lemma_ma:
            print(f'lemma_ma={query_lemma_ma}, docid={index_docid}')
            if idx_query_token + 1 >= len(query_tokens) or (rec_chk(idx_query_token+1, query_tokens, index_docid) is True):
                result_query_docid = result_query.get(index_docid)
                if result_query_docid is None:
                     result_query[index_docid] = {}
                for startpos in index_lemma_ma[index_docid]:
                    result_query[index_docid][startpos]=(index_lemma_ma[index_docid][startpos], query_lemma_ma,index["sources"][index_docid]["content"][int(startpos):index_lemma_ma[index_docid][startpos]] )
                    pass 
        



        pass
    print(result_query)

def rec_chk(idx_query_token, query_tokens, required_idx_docid) -> bool:
    for idx_mrf, mrf in enumerate(query_tokens[idx_query_token]["features"]["mrf"]): # tsükkel ole päringusõnele vastavate lemmade
        query_lemma_ma = mrf.get("lemma_ma")
        if query_lemma_ma is None: # päringusõna morf analüüsis polnud lemmat
            continue
        index_lemma_ma = index["annotations"]["lemmas"].get(query_lemma_ma)
        if index_lemma_ma is None: # päringusõna lemmat polnud indeksis
            continue

        index_docid = index_lemma_ma.get(required_idx_docid)
        if index_docid is None:
            continue # pole vajalikus dokumendis
        # lemma vajalikus dokumendis olemas
        if (idx_query_token + 1 >= len(query_tokens)) or (rec_chk(idx_query_token+1, query_tokens, required_idx_docid) is True):
            # lisame positsioonid resultaati
            for startpos in index_lemma_ma[index_docid]:
                result_query[index_docid][startpos]=(index_lemma_ma[index_docid][startpos], query_lemma_ma, index["sources"][index_docid]["content"][int(startpos):index_lemma_ma[index_docid][startpos]])  
                pass



"""
for idx_query_token, query_token in enumerate(query_lemmas["annotations"]["tokens"]):
    for mrf in enumerate(query_token["features"]["mrf"]):
        query_lemma_ma = mrf.get("lemma_ma")
        if query_lemma_ma is None:
            continue
        index_lemma_ma = index["annotations"]["lemmas"].get(query_lemma_ma)
        if index_lemma_ma is None: # polnud indeksis
            continue
        for index_docid in index_lemma_ma:
            print(f'lemma_ma={query_lemma_ma}, docid={index_docid}')
        pass
"""


def check_index(lemma_ma:str, docid:str) -> Dict:
    """Kontrollime, kas lemma esines dokumendis

    Args:
        lemma_ma (str): lemma
        docid (str): dokumendi id

    Returns:
        Dict: None: polnud, {STARTPOS:endpos}: nendes positsioonides esineb
    """
    index_lemma_ma = index["annotationa"]["lemmas"].get(lemma_ma)
    if index_lemma_ma is None:
        return None
    positions = index_lemma_ma.get(docid)
    return positions


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    argparser.add_argument('-i', '--index', type=str, help='lemmade indeks')
    args = argparser.parse_args()

    with open(args.index, 'r') as file_index:
        index = json.loads(file_index.read())
        sys.stdout.write(f'indeksfail: {args.index}\n')

    my_query("mesi")
    pass
    #app.run(debug=args.debug)


 #!/usr/bin/python3

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



@app.route('/process', methods=['POST']) #@app.route('/process', methods=['GET', 'POST'])
def morf():
    """Lemmatiseerime JSONiga antud sõnesid ja kuvame tulemust JSONkujul

    Returns:
        ~flask.Response: Lemmatiseerimise tulemused
    """
    proc.stdin.write(f'{json.dumps(request.json)}\n')
    proc.stdin.flush()
    return jsonify(json.loads(proc.stdout.readline()))

class SMART_SEARCH:
    index = {}

    ''' /* tulemus */
    result_query = { "DOCID: { {STARTPOS: endpos} } }
    result_query_sorted = {DOCID : [{"start":int, "end":int}]}
    '''
    result_query = {}
    
    ''' /* lemmatiseeritud päringusõned */
    {   "annotations":
        {   "tokens":
            [   {   "features":
                    {   "token": string,  /* analüüsitud sõne */
                        "complexity": KEERUKUS,
                        "mrf" :           /* sisendsõne lemmade massiiv */
                        [   {   "lemma":    LEMMA,    /* lemma */
                                "lemma_ma": LEMMA_MA, /* verbilemmale on lisatud ```ma```, muudel juhtudel sama mis LEMMA */
                                "source":   ALLIKAS,  /* P:põhisõnastikust, L:lisasõnastikust, O:sõnepõhisest oletajast, S:lausepõhisest oletajast, X:ei tea kust */
                            }
                        ],
                    }
                }
            ]
        }
    }
    '''
    query_tokens = {}
    query_str = ""
    db_version = False
        
    def __init__(self, indexfile:str, db:bool) -> None:

        self.db_version = db
        with open(indexfile, 'r') as file_index:
            self.index = json.loads(file_index.read())
            if self.db_version is True:
                sys.stdout.write(f'indeksfail: {indexfile}\n')

    def my_query(self, keywords:str)->None:
        """Päringusõnede käsitlemine

        Esimest päringusõne käsitleme selles alamprogrammis, 
        järgmiste käsitlemiseks kasutame rekursiivet funktsiooni rec_chk()

        Args:
            keywords (str): Tühikuga eraldatult päringusõned
        """
        self.query_str = keywords
        self.result_query ={}
        mq = f'{{"content":"{keywords}"}}\n'
        proc.stdin.write(mq)
        proc.stdin.flush()
        query_lemmas = json.loads(proc.stdout.readline()) # lemmatiseerime päringusõned

        self.query_tokens = query_lemmas["annotations"]["tokens"] # morfitud päringusõnede massiiv
        idx_query_token = 0 # jooksva päringusõne indeks (algab nullist)
        for idx_mrf, mrf in enumerate(self.query_tokens[idx_query_token]["features"]["mrf"]): # tsükkel ole esimesele päringusõnele vastavate morf analüüside
            query_lemma_ma = mrf.get("lemma_ma") # lemma päringusõna jooksvast morf analüüsist
            if query_lemma_ma is None:  # morf analüüsis polnud lemmat...
                continue                # ...ignoreerime
            index_lemma_ma = self.index["annotations"]["lemmas"].get(query_lemma_ma) # päringusõne jooksvale lemmale vastav DICT indeksis
            if index_lemma_ma is None:  # lemmat polnud indeksis...
                continue                # ...ignoreerime
            for index_docid in index_lemma_ma: # tsükkel üle dokumendi-id'de, kus otsitav lemma esineb
                #print("DB", f'lemma_ma={query_lemma_ma}, docid={index_docid}')
                if idx_query_token + 1 >= len(self.query_tokens) or (self.rec_chk(idx_query_token+1, index_docid) is True):
                    result_query_docid = self.result_query.get(index_docid) # lisame selle dokumendi-id alla tulemustes
                    if result_query_docid is None:      # sellist dokumendi-id'ed veel tulemustes polnud
                        self.result_query[index_docid] = {} # Teeme tühja sõnastiku selle dokumendi-id alla
                    for startpos in index_lemma_ma[index_docid]: # tsükkel üle lemma esinemiste selles dokumendis
                        #if self.db_version is True: # seda kasutame silumiseks
                        index_docid_startpos = self.result_query[index_docid].get(startpos)
                        if index_docid_startpos is None:
                            self.result_query[index_docid][startpos]={
                                    "endpos":index_lemma_ma[index_docid][startpos], 
                                    "token":self.index["sources"][index_docid]["content"][int(startpos):index_lemma_ma[index_docid][startpos]],
                                    "lemmas":[query_lemma_ma] }
                        else:
                            index_docid_startpos["lemmas"].append(query_lemma_ma)
                        #else: # seda kasutame silutud programmis
                        #    self.result_query[index_docid][startpos]=(index_lemma_ma[index_docid][startpos])


    def rec_chk(self, idx_query_token, required_idx_docid) -> bool:
        """Teise ja järgmiste päringusõnede rekursiivne käsitlemine

        Ainult my_query() või rec_chk() funktsioonist väljakutsumiseks
        Args:
            idx_query_token (_type_): jooksva päringusõne idx = 1, ..., len(self.query_tokens)-1
            required_idx_docid (_type_): _description_

        Returns:
            bool: _description_
        """
        resultval = False
        for idx_mrf, mrf in enumerate(self.query_tokens[idx_query_token]["features"]["mrf"]): # tsükkel ole päringusõnele vastavate morf analüüside
            query_lemma_ma = mrf.get("lemma_ma") # päringusõna lemma jooksvas morf analüüsis
            if query_lemma_ma is None:  # morf analüüsis polnud lemmat... 
                continue                # ...ignoreerime
            index_lemma_ma = self.index["annotations"]["lemmas"].get(query_lemma_ma) # päringusõne jooksvale lemmale vastav DICT indeksis
            if index_lemma_ma is None:  # lemmat polnud indeksis...
                continue                # ...ignoreerime
            index_docid = index_lemma_ma.get(required_idx_docid) # päringusõne jooksvale lemmale vastav DICT indeksis
            if index_docid is None:     # lemma ei esinenud nõutavas dokumendis...
                continue                # ...ignoreerime
            # lemma esines nõutavas dokumendis
            if (idx_query_token + 1 >= len(self.query_tokens)) or (self.rec_chk(idx_query_token+1, required_idx_docid) is True):
                # lisame positsioonid resultaati
                result_query_docid = self.result_query.get(required_idx_docid) # lisame selle dokumendi-id alla tulemustes
                if result_query_docid is None:                  # sellist dokumendi-id'ed veel tulemustes polnud
                    self.result_query[required_idx_docid] = {}  # Teeme tühja sõnastiku selle dokumendi-id alla
                for startpos in index_docid: # {STARTPOS:endpos}
                    #if self.db_version is True: # seda kasutame silumiseks
                    index_docid_startpos = self.result_query[required_idx_docid].get(startpos)
                    if index_docid_startpos is None:
                        self.result_query[required_idx_docid][startpos]={
                                "endpos":index_lemma_ma[required_idx_docid][startpos], 
                                "token":self.index["sources"][required_idx_docid]["content"][int(startpos):index_lemma_ma[required_idx_docid][startpos]],
                                "lemmas":[query_lemma_ma] }
                    else:
                        if query_lemma_ma not in index_docid_startpos["lemmas"]:
                            index_docid_startpos["lemmas"].append(query_lemma_ma)
                    #else: # seda kasutame silutud programmis
                    #    self.result_query[required_idx_docid][startpos]=(index_lemma_ma[required_idx_docid][startpos])
                    resultval = True
        return resultval

    def result_query_2_result_query_sorted(self)->None:
        """Teeme otsingusõnede algus- ja lõpupositsioone sisaldavast DICTist pöördjärjestatud LISTi

        Sisse: result_query = { DOCID: { {STARTPOS: endpos} } }
        Välja: result_query_sorted = {DOCID : [{"start":startpos, "end":int}]}
        """     
        self.result_query_sorted = {}
        poslist = []
        for docid_key in self.result_query:
            poslist = []
            docid_dct = self.result_query[docid_key]
            for startpos in docid_dct:
                #poslist.append({"start":int(startpos), "end":docid_dct[startpos]}) # seda kasutame silutud programmis
                poslist.append({"start":int(startpos), "end":docid_dct[startpos]["endpos"], "lemmas":docid_dct[startpos]["lemmas"]}) # seda kasutame silumiseks
            poslist.sort(key=self.sort_by_startpos)
            self.result_query_sorted[docid_key]=poslist

    def sort_by_startpos(self, i):
        return(i["start"])
    
    def result_query_sorted_2_html(self) -> str:
        """Päringuvastet sisaldavast LISTist teeme HTMLi 

        Returns:
            str: Päringuvastet sisaldav HTML
        """
        html_str = f'<!DOCTYPE html><head><title> Otsime: {self.query_str}</title></head>\n<body>\n'
        #html_str += f'<h1>Otsime: {self.query_str}</h1>'
        html_str += f'<h1>Otsime: '
        for token in self.query_tokens: # morfitud päringusõnede massiiv
            html_str += f' {token["features"]["token"]}<i>['
            for mrf in token["features"]["mrf"]:
                  html_str += f' {mrf["lemma_ma"]} '
            html_str += ']</i>' 
        html_str += '</h1>'
        for docid_key in self.result_query_sorted:
            html_str += f'\n<h2>{self.index["sources"][docid_key]["heading"]} [DOCID={docid_key}]</h2>\n\n<p>\n\n'
            # result_query_sorted = {DOCID : [{"start":int, "end":int}]}
            doc_in = self.index["sources"][docid_key]["content"]
            docids = self.result_query_sorted[docid_key]
            html_str += f'{doc_in[:docids[0]["start"]]}<b>{doc_in[docids[0]["start"]:docids[0]["end"]]}</b>'
            html_str += f'<i>[{" ".join(docids[0]["lemmas"])}]</i>' # seda kasutame silumiseks
            for i in range(1,len(docids)):
                html_str += f'{doc_in[docids[i-1]["end"]:docids[i]["start"]]}<b>{doc_in[docids[i]["start"]:docids[i]["end"]]}</b>'
                html_str += f'<i>[{" ".join(docids[i]["lemmas"])}]</i>' # seda kasutame silumiseks
            html_str += f'{doc_in[docids[len(docids)-1]["end"]:]}\n</p>\n'
        html_str += '\n</body>\n'
        return html_str

    def dump_docs_in_html(self) -> str:
        """Dokumentidest veebileht

        Returns:
            str: dokumente sisaldav HTML
        """
        html_str = f'<!DOCTYPE html><head><title> Dokumendid</title></head>\n<body>\n'            
        for docid_key in self.index["sources"]:
            html_str += f'\n<h2>{self.index["sources"][docid_key]["heading"]} [DOCID={docid_key}]</h2>\n\n<p>\n\n'
            html_str += self.index["sources"][docid_key]["content"]
        html_str += '\n</body>\n'
        return(html_str)


if __name__ == '__main__':
    #result_query = { "DOCID: { {STARTPOS: endpos} } }
    #result_query_sorted = {DOCID : [{"start":int, "end":int}]}
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-f', '--flask', action="store_true", help='run webserver') 
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    argparser.add_argument('-l', '--list', action="store_true",  help='näita dokumente')
    argparser.add_argument('-i', '--index', type=str, help='lemmade indeks')
    argparser.add_argument('-q', '--query', type=str, help='päringusõned')
    argparser.add_argument('--result_query', action="store_true", help='show result_query')
    argparser.add_argument('--result_query_sorted', action="store_true", help='show result_query_sorted')
    args = argparser.parse_args()

    search = SMART_SEARCH(args.index, args.debug)
    if args.query is not None:
        search.my_query(args.query)
        search.result_query_2_result_query_sorted()
        if args.result_query is True:
            json.dump(search.result_query, sys.stdout, indent=4)
        elif args.result_query_sorted is True:
            json.dump(search.result_query_sorted, sys.stdout, indent=4)
        else:
            print(search.result_query_sorted_2_html())
    if args.list is True:
       print(search.dump_docs_in_html())
    if args.flask is True:
        app.run(debug=args.debug)


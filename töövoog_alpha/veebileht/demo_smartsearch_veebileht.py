#!/usr/bin/python3

'''
1. käivita lemmatiseerija konteiner (konteiner peab olema tehtud/allalaaditud)
    $ docker run -p 7000:7000 tilluteenused/lemmatizer
2. käivita lemmatiseerija konteineriga suhtlev veebiserver 
   (pythoni pakett requests peab olema installitud, ubuntu korral: sudo apt install -y python3-requests)
    $ cd töövoog_alpha/veebileht ; ./demo_smartsearch_veebileht.py
    või
    $ docker run --env LEMMATIZER_IP=localhost --env LEMMATIZER_PORT=7000 tilluteenused/demo_smartsearch_veebileht
3. Ava brauseris ja järgi brauseris avanenud veebilehe juhiseid
    $ google-chrome http://localhost:7777/otsi
    $ google-chrome http://localhost:7777/tekstid
    
'''

import sys
import os
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi

LEMMATIZER_IP=os.environ.get('LEMMATIZER_IP') if os.environ.get('LEMMATIZER_IP') != None else 'localhost'
LEMMATIZER_PORT=os.environ.get('LEMMATIZER_PORT') if os.environ.get('LEMMATIZER_PORT') != None else '7000'

class SMART_SEARCH:
    """ 
    index =
    {   "sources":
        {   DOCID:
            {   "filename": str,
                "heading": str,
                "content": str
            }
        }
        annotations:
        {   "lemmas":
            {   LEMMA:
                {   DOCID:
                    {   STARTPOS:endpos 
                    }
                }
            }
        }
    }
    """
    index = {}

    ''' /* tulemus */
    result_query = {"DOCID: {STARTPOS: {"endpos: int, "token": str, "lemmas": [str]}}}
    '''
    result_query = {}

    ''' /* tulemus */
    result_query_sorted = {DOCID : [{"start":int, "end":int, "lemmas":[str]}]}
    '''
    result_query_sorted = {} 

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
                print(f'indeksfail: {indexfile}')

    def my_query(self, keywords:str)->None:
        """Päringusõnede käsitlemine

        Esimest päringusõne käsitleme selles alamprogrammis, 
        järgmiste käsitlemiseks kasutame rekursiivet funktsiooni rec_chk()

        Tulemuseks on:
        result_query = {"DOCID: {STARTPOS: {"endpos: int, "token": str, "lemmas": [str]}}}

        Args:
            keywords (str): Tühikuga eraldatult päringusõned
        """

        self.result_query = {}
        self.result_query_sorted = {}
        json_tokens=json.dumps(keywords)
        json_query=json.loads(f"{{\"content\":{json_tokens}}}")
        query_lemmas=json.loads(requests.post(f'http://{LEMMATIZER_IP}:{LEMMATIZER_PORT}/process', json=json_query).text)
        self.query_tokens = query_lemmas["annotations"]["tokens"] # morfitud päringusõnede massiiv
        idx_query_token = 0 # jooksva päringusõne indeks (algab nullist)
        for idx_mrf, mrf in enumerate(self.query_tokens[idx_query_token]["features"]["mrf"]): # tsükkel üle esimesele päringusõnele vastavate morf analüüside
            query_lemma_ma = mrf.get("lemma_ma") # lemma päringusõna jooksvast morf analüüsist
            if query_lemma_ma is None:  # morf analüüsis polnud lemmat...
                continue                # ...ignoreerime
            index_lemma_ma = self.index["annotations"]["lemmas"].get(query_lemma_ma) # päringusõne jooksvale lemmale vastav DICT indeksis
            if index_lemma_ma is None:  # lemmat polnud indeksis...
                continue                # ...ignoreerime
            for index_docid in index_lemma_ma: # tsükkel üle dokumendi-id'de, kus otsitav lemma esineb
                if idx_query_token + 1 >= len(self.query_tokens) or (self.rec_chk(idx_query_token+1, index_docid) is True):
                    result_query_docid = self.result_query.get(index_docid) # lisame selle dokumendi-id alla tulemustes
                    if result_query_docid is None:                          # sellist dokumendi-id'ed veel tulemustes polnud
                        self.result_query[index_docid] = {}                 # Teeme tühja sõnastiku selle dokumendi-id alla
                    for startpos in index_lemma_ma[index_docid]:            # tsükkel üle lemma esinemiste selles dokumendis
                        index_docid_startpos = self.result_query[index_docid].get(startpos)
                        if index_docid_startpos is None:
                            self.result_query[index_docid][startpos]={
                                    "endpos":index_lemma_ma[index_docid][startpos], 
                                    "token":self.index["sources"][index_docid]["content"][int(startpos):index_lemma_ma[index_docid][startpos]],
                                    "lemmas":[query_lemma_ma] }
                        else:
                            index_docid_startpos["lemmas"].append(query_lemma_ma)


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
        for idx_mrf, mrf in enumerate(self.query_tokens[idx_query_token]["features"]["mrf"]): # tsükkel üle päringusõnele vastavate morf analüüside
            query_lemma_ma = mrf.get("lemma_ma")    # päringusõna lemma jooksvas morf analüüsis
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
                    index_docid_startpos = self.result_query[required_idx_docid].get(startpos)
                    if index_docid_startpos is None:
                        self.result_query[required_idx_docid][startpos]={
                                "endpos":index_lemma_ma[required_idx_docid][startpos], 
                                "token":self.index["sources"][required_idx_docid]["content"][int(startpos):index_lemma_ma[required_idx_docid][startpos]],
                                "lemmas":[query_lemma_ma] }
                    else:
                        if query_lemma_ma not in index_docid_startpos["lemmas"]:
                            index_docid_startpos["lemmas"].append(query_lemma_ma)
                    resultval = True
        return resultval

    def result_query_2_result_query_sorted(self)->None:
        """Teeme otsingusõnede algus- ja lõpupositsioone sisaldavast DICTist järjestatud LISTi

        Seda teeme selleks, et oleks mugavam märgendatud otsingusõnedega HTMLi genereerida.
 
        Sisse: result_query = {"DOCID: {STARTPOS: {"endpos: int, "token": str, "lemmas": [str]}}}
        Välja: result_query_sorted = {DOCID : [{"start":int, "end":int, "lemmas":[str]}]}
        """     
        self.result_query_sorted = {}
        for docid_key in self.result_query:
            positionslist = []
            docid_dct = self.result_query[docid_key]
            for startpos in docid_dct:
                positionslist.append({"start":int(startpos), "end":docid_dct[startpos]["endpos"], "lemmas":docid_dct[startpos]["lemmas"]})
            positionslist.sort(key=self.sort_by_startpos)
            self.result_query_sorted[docid_key]=positionslist

    def sort_by_startpos(self, i):
        return(i["start"])
    
    def result_query_sorted_2_html(self) -> str:
        """Päringuvastet sisaldavast LISTist teeme HTMLi 

        Returns:
            str: Päringuvastet sisaldav HTML
        """
        html_str =  ''
        html_str += f'<h1>Otsisime: '
        for token in self.query_tokens: # morfitud päringusõnede massiiv
            html_str += f' {token["features"]["token"]}<i>[ lemmad: '
            for mrf in token["features"]["mrf"]:
                  html_str += f' {mrf["lemma_ma"]} '
            html_str += ']</i>' 
        html_str += '</h1>'
        if len(self.result_query_sorted) == 0:
            html_str += '\n<h2>Päringule vastavaid dokumente ei leidunud!</h2>\n'
        for docid_key in self.result_query_sorted:
            html_str += f'\n<h2>{self.index["sources"][docid_key]["heading"]} [DOCID={docid_key}]</h2>\n\n<p>\n\n'
            doc_in = self.index["sources"][docid_key]["content"]
            docids = self.result_query_sorted[docid_key]
            html_str += f'{doc_in[:docids[0]["start"]]}<b>{doc_in[docids[0]["start"]:docids[0]["end"]]}</b>'
            html_str += f'<i>[lemmad: {" ".join(docids[0]["lemmas"])}]</i>' # seda kasutame silumiseks
            for i in range(1,len(docids)):
                html_str += f'{doc_in[docids[i-1]["end"]:docids[i]["start"]]}<b>{doc_in[docids[i]["start"]:docids[i]["end"]]}</b>'
                html_str += f'<i>[lemmad: {" ".join(docids[i]["lemmas"])}]</i>' # seda kasutame silumiseks
            html_str += f'{doc_in[docids[len(docids)-1]["end"]:]}\n</p>\n'
        return html_str

    def dump_docs_in_html(self) -> str:
        """Dokumentidest veebileht

        Returns:
            str: kõiki dokumente sisaldav HTML
        """
        html_str = ''           
        for docid_key in self.index["sources"]:
            html_str += f'\n<h2>{self.index["sources"][docid_key]["heading"]} [DOCID={docid_key}]</h2>\n\n<p>\n\n'
            html_str += self.index["sources"][docid_key]["content"]
        return(html_str)

class WebServerHandler(BaseHTTPRequestHandler):
    form_html = \
        '''
        <form method='POST' enctype='multipart/form-data' action='/otsi'>
        <h2>Sisesta otsingusõned:</h2>
        <input name="message" type="text"><input type="submit" value="Otsi" >
        </form>
        '''

    def do_GET(self):
        try:
            if self.path.endswith("/otsi"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html;charset=utf-8')
                self.end_headers()
                output = f"<html><body>{self.form_html}</body></html>"
                self.wfile.write(output.encode())
            elif self.path.endswith("/tekstid"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html;charset=utf-8')
                self.end_headers()
                output = f"<html><body>{smart_search.dump_docs_in_html()}</body></html>"
                self.wfile.write(output.encode())
        except IOError:
            self.send_error(404, "File Not Found {}".format(self.path))

    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-type', 'text/html;charset=utf-8')
            self.end_headers()

            # HEADERS are now in dict/json style container
            ctype, pdict = cgi.parse_header(
                self.headers['content-type'])

            # boundary data needs to be encoded in a binary format
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")

            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')

            output = ""
            output += "<html><body>\n"
            
            smart_search.my_query(messagecontent[0])
            smart_search.result_query_2_result_query_sorted()
            output += smart_search.result_query_sorted_2_html()
            
            output += self.form_html
            output += "</body></html>"
            self.wfile.write(output.encode())

        except:
            raise


def demo():
    try:
        port = 7777
        print(f'Web server is running on port {port}')
        print(f'LEMMATIZER_IP={LEMMATIZER_IP}, LEMMATIZER_PORT={LEMMATIZER_PORT}')
        server = HTTPServer(('', port), WebServerHandler)
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered, stopping web server...")

    finally:
        if server:
            server.socket.close()    

smart_search = SMART_SEARCH("./rannila.index", True)

if __name__ == '__main__':
    demo()
    pass

#!/usr/bin/python3

# liitsõnandusega versioon!!!

'''
1. käivita lemmatiseerija konteiner (konteiner peab olema tehtud/allalaaditud)
    $ docker run -p 7000:7000 tilluteenused/lemmatizer
2. käivita lemmatiseerija konteineriga suhtlev veebiserver 
   (pythoni pakett requests peab olema installitud, ubuntu korral: sudo apt install -y python3-requests)
    $ cd töövoog_alpha/veebileht ; ./demo_smartsearch_webpage.py
    või
    $ docker run --env LEMMATIZER_IP=<lemmatiseerija-konteineri-ip> --env LEMMATIZER_PORT=lemmatiseerija-konteineri-port tilluteenused/demo_smartsearch_webpage
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

INDEXFILE="./ruukki.index"


class SMART_SEARCH:
    ''' Sisend: indeksfaili
    index =
    {   "sources":{"<DOCID>":{"filename":str,"heading":str,"content":str}}
        "annotations":{"lemmas":{"<EMMA>":{"<DOCID>":{"<STARTPOS>":{"endpos":int,"fragment":bool}}}}}}
    }
    '''
    index = {}

    ''' Sisend: Lemmatiseeritud päringusõned (ainult see osa jsonist, mida (hetkel) kasutame)
    query_lemmas={"annotations":{"tokens":[{"features":{"token": str, "mrf":[{"lemma_ma":str}]}}}}
    '''

    ''' Päringu algne tulemus
    result_query={"<DOCID>":{"<STARTPOS>":{"endpos:int,"token":str,"lemmas":[str]}}}
    '''
    result_query = {}

    ''' Algne tulemus "start" järgi kasvavalt järjestatud (et oleks lihtsam teksti märgendeid vahele panna)
    result_query_sorted={"<DOCID>":[{"start":int,"end":int,"lemmas":[str]}]}
    '''
    result_query_sorted = {} 

    fragments = True # True: otsime liitsõna osasõnade seest ka, False: liitsõna osasõnasid ei vaata
    query_tokens = {}
    query_str = ""

    db_version = False
    init_ok = False
        
    def __init__(self, indexfile:str, db:bool) -> None:
        print("SMART_SEARCH.init...")
        self.db_version = db
        try:        
            with open(indexfile, 'r') as file_index:
                self.index = json.loads(file_index.read())
                if self.db_version is True:
                    print(f'indeksfail: {indexfile}')
                self.init_ok = True
        except:
            print("SMART_SEARCH.init failure")

    def my_query(self, keywords:str)->None:
        """Päringusõnede käsitlemine

        Esimest päringusõne käsitleme selles alamprogrammis, 
        järgmiste käsitlemiseks kasutame rekursiivet funktsiooni rec_chk()

        Tulemuseks on:
        result_query = {"DOCID: {"STARTPOS": {"endpos: int, "token": str, "lemmas": [str]}}}
        
        Args:
            keywords (str):Tühikuga eraldatult päringusõned
        """
        self.result_query = {}
        self.result_query_sorted = {}
        json_tokens=json.dumps(keywords)
        json_query=json.loads(f"{{\"content\":{json_tokens}}}")
        try:
            query_lemmas=json.loads(requests.post(f'http://{LEMMATIZER_IP}:{LEMMATIZER_PORT}/process', json=json_query).text)
        except:
            self.result_query = {"error": "Lemmatiseerimise veebiteenus ei tööta"}
            return

        self.query_tokens = query_lemmas["annotations"]["tokens"] # morfitud päringusõnede massiiv
        query_token_idx = 0 # päringus query_tokens["annotations"]["features"]["tokens"][ ] jooksev indeks 
        for query_mrf_idx, query_mrf in enumerate(self.query_tokens[query_token_idx]["features"]["mrf"]): # tsükkel üle esimesele päringusõnele vastavate morf analüüside
            # query_mrf = self.query_tokens[0]["features"]["mrf"][query_mrf_idx] -- [{"lemma_ma":LEMMA_MA}], 
            # päringus query_lemma_ma = päringus jooksva sõne 
            query_lemma_ma = query_mrf.get("lemma_ma") # lemma esimese päringusõna jooksvast morf analüüsist
            if query_lemma_ma is None:  # päringu morf analüüsis polnud lemmat...
                continue                # ...ignoreerime
            # query_lemma_ma - seda hakkame indeksist otsima
            index_lemma = self.index["annotations"]["lemmas"].get(query_lemma_ma) # indeksis päringusõne jooksvale lemmale {"DOCID":{"STARTPOS":{"endpos":int,"fragment":bool}}}
            if index_lemma is None:  # indeksis polnud ühtegi päringu lemmat sisaldavat dokumenti
                continue                # ...ignoreerime
            # index_lemma = { "DOCID": { "STARTPOS":{"endpos":int, "fragment":bool}} } }
            for index_docid_key in index_lemma: # indeksis tsükkel üle DOCIDide, kus otsitav (päringu)lemma esineb
                # index_docid =  { "STARTPOS":{"endpos":int, "fragment":bool}} } ja index_docid_key vastav võti
                index_docid = index_lemma[index_docid_key]
                if query_token_idx + 1 >= len(self.query_tokens) or (self.rec_chk(query_token_idx+1, index_docid_key) is True):
                    # indeksis olema õige lemma ja DOCIDi peal, lisame resultaati esinemised tekstis
                    # vajadusel tekitame resultaadis lemma alla DOCID 
                    result_query_docid = self.result_query.get(index_docid_key) # tulemustes lisame selle DOCIDi alla
                    if result_query_docid is None:                              # sellist DOCIDi veel tulemustes polnud
                        self.result_query[index_docid_key] = {}                 # Teeme tühja sõnastiku selle DOCIDi alla
                        result_query_docid = self.result_query[index_docid_key]
                    for index_startpos_key in index_docid:             # indeksis tsükkel üle lemma esinemiste selles DOCIDis
                        # kui oli liitsõna osasõnadega, siis kõik, muidu ainult need mis pole fragmendid 
                        if (self.fragments is False) and (index_docid[index_startpos_key]["fragment"] is True):
                            continue # ei soovi näha liitsõna osades
                        result_docid_startpos =  result_query_docid.get(index_startpos_key) # tulemustes STARTPOSile vastav {"endpos: int, "token": str, "lemmas": [str]}
                        if result_docid_startpos is None: # tulemustes polnud 
                            result_query_docid[index_startpos_key]={
                                    "endpos":index_docid[index_startpos_key]["endpos"], 
                                    "token":self.index["sources"][index_docid_key]["content"][int(index_startpos_key):index_docid[index_startpos_key]["endpos"]],
                                    "lemmas":[query_lemma_ma] }
                        else:
                            if query_lemma_ma not in result_docid_startpos["lemmas"]:
                                result_docid_startpos["lemmas"].append(query_lemma_ma)

    def rec_chk(self, idx_query_token, required_idx_docid_key) -> bool:
        """Teise ja järgmiste päringusõnede rekursiivne käsitlemine

        Ainult my_query() või rec_chk() funktsioonist väljakutsumiseks
        Args:
            idx_query_token (_type_): jooksva päringusõne idx = 1, ..., len(self.query_tokens)-1
            required_idx_docid (_type_): _description_

        Returns:
            bool: True: leidsin, False: ei leidnud
        """
        resultval = False
        for idx_mrf, mrf in enumerate(self.query_tokens[idx_query_token]["features"]["mrf"]): # tsükkel üle päringusõnele vastavate morf analüüside
            query_lemma_ma = mrf.get("lemma_ma")    # päringusõna lemma jooksvas morf analüüsis
            if query_lemma_ma is None:  # morf analüüsis polnud lemmat... 
                continue                # ...ignoreerime
            index_lemma_ma = self.index["annotations"]["lemmas"].get(query_lemma_ma) # päringusõne jooksvale lemmale vastav DICT indeksis
            if index_lemma_ma is None:  # lemmat polnud indeksis...
                continue                # ...ignoreerime
            index_docid = index_lemma_ma.get(required_idx_docid_key) # päringusõne jooksvale lemmale vastav DICT indeksis
            if index_docid is None:     # lemma ei esinenud nõutavas dokumendis...
                continue                # ...ignoreerime
            # lemma esines nõutavas dokumendis
            if (idx_query_token + 1 >= len(self.query_tokens)) or (self.rec_chk(idx_query_token+1, required_idx_docid_key) is True):
                # lisame positsioonid resultaati
                result_query_docid = self.result_query.get(required_idx_docid_key) # lisame selle dokumendi-id alla tulemustes
                if result_query_docid is None:                  # sellist dokumendi-id'ed veel tulemustes polnud
                    self.result_query[required_idx_docid_key] = {}  # Teeme tühja sõnastiku selle dokumendi-id alla
                    result_query_docid = self.result_query[required_idx_docid_key]
                for index_startpos_key in index_docid: # {STARTPOS:endpos}
                    if (self.fragments is False) and (index_docid[index_startpos_key]["fragment"] is True):
                            continue # ei soovi näha liitsõna osades
                    result_docid_startpos = self.result_query[required_idx_docid_key].get(index_startpos_key)
                    if result_docid_startpos is None: # tulemustes polnud 
                        result_query_docid[index_startpos_key]={
                                "endpos":index_docid[index_startpos_key]["endpos"], 
                                "token":self.index["sources"][required_idx_docid_key]["content"][int(index_startpos_key):index_docid[index_startpos_key]["endpos"]],
                                "lemmas":[query_lemma_ma] }
                    else:
                        if query_lemma_ma not in result_docid_startpos["lemmas"]:
                            result_docid_startpos["lemmas"].append(query_lemma_ma)
                    resultval = True
        return resultval

    def result_query_2_result_query_sorted(self)->None:
        """Teeme otsingusõnede algus- ja lõpupositsioone sisaldavast DICTist järjestatud LISTi

        Seda teeme selleks, et oleks mugavam märgendatud otsingusõnedega HTMLi genereerida.
 
        Sisse: result_query = {"<DOCID>":{"<STARTPOS>":{"endpos":int,"token":str,"lemmas":[str]}}}
        Välja: result_query_sorted = {"<DOCID>":[{"start":int,"end":int,"lemmas":[str]}]}
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

        # Sedasi saaks edevamalt:
        # Mees <a href="" title="[peet, pidama]">peeti</a> kinni.
        html_str =  ''
        html_str += f'<h1>Otsisime: '
        for token in self.query_tokens: # morfitud päringusõnede massiiv
            html_str += f' {token["features"]["token"]}<i>[lemmad: '
            for i, mrf in enumerate(token["features"]["mrf"]):
                  if i > 0:
                      html_str += ', '
                  html_str += f'{mrf["lemma_ma"]}'
            html_str += ']</i>' 
        html_str += '</h1>'
        if len(self.result_query_sorted) == 0:
            html_str += '<h2>Päringule vastavaid dokumente ei leidunud!</h2>'
        for docid_key in self.result_query_sorted:
            docids = self.result_query_sorted[docid_key]
            if len(docids) == 0:
                continue
            doc_in = self.index["sources"][docid_key]["content"]
            html_str += f'<h2>[DOCID={docid_key}]</h2><p>'
            html_str += f'{doc_in[:docids[0]["start"]]}<b>{doc_in[docids[0]["start"]:docids[0]["end"]]}</b>'
            html_str += f'<i>[lemmad: {", ".join(docids[0]["lemmas"])}]</i>' # seda kasutame silumiseks
            for i in range(1,len(docids)):
                html_str += f'{doc_in[docids[i-1]["end"]:docids[i]["start"]]}<b>{doc_in[docids[i]["start"]:docids[i]["end"]]}</b>'
                html_str += f'<i>[lemmad: {", ".join(docids[i]["lemmas"])}]</i>' # seda kasutame silumiseks
            html_str += f'{doc_in[docids[len(docids)-1]["end"]:]}</p>'
        html_str = html_str.replace('\n\n', '<br><br>')
        return html_str
    

    def result_query_sorted_2_html_with_hover(self) -> str:
        """Päringuvastet sisaldavast LISTist teeme HTMLi 

        Returns:
            str: Päringuvastet sisaldav HTML
        """

        # Sedasi saaks edevamalt:
        # Mees <a href="" title="[peet, pidama]">peeti</a> kinni.
        html_str =  ''
        html_str += f'<h1>Otsisime:'
        for token_idx, token in enumerate(self.query_tokens): # morfitud päringusõnede massiiv
            html_str += ' ' if token_idx == 0 else ', '
            html_str += '<a href="" title="'
            for mrf_idx, mrf in enumerate(token["features"]["mrf"]):
                if mrf_idx > 0:
                    html_str += ', '
                html_str += f'{mrf["lemma_ma"]}' 
            html_str += f'">{token["features"]["token"]}</a>'
        html_str += '</h1>'
        if len(self.result_query_sorted) == 0:
            html_str += '<h2>Päringule vastavaid dokumente ei leidunud!</h2>'
        for docid_key in self.result_query_sorted:
            docids = self.result_query_sorted[docid_key]
            if len(docids) == 0:
                continue
            doc_in = self.index["sources"][docid_key]["content"]
            html_str += f'<h2>[DOCID={docid_key}]</h2><p>'
            html_str += f'{doc_in[:docids[0]["start"]]}'
            html_str += f'<a href="" title="{", ".join(docids[0]["lemmas"])}">'
            html_str += f'{doc_in[docids[0]["start"]:docids[0]["end"]]}</a>'
            #html_str += f'<i>[lemmad: {", ".join(docids[0]["lemmas"])}]</i>' # seda kasutame silumiseks
            for i in range(1,len(docids)):
                html_str += f'{doc_in[docids[i-1]["end"]:docids[i]["start"]]}'
                html_str += f'<a href="" title="{", ".join(docids[0]["lemmas"])}">'
                html_str += f'{doc_in[docids[i]["start"]:docids[i]["end"]]}</a>'
                #html_str += f'<i>[lemmad: {", ".join(docids[i]["lemmas"])}]</i>' # seda kasutame silumiseks
            html_str += f'{doc_in[docids[len(docids)-1]["end"]:]}</p>'
        html_str = html_str.replace('\n\n', '<br><br>')
        return html_str

    def dump_docs_in_html(self) -> str:
        """Dokumentidest veebileht

        Returns:
            str: kõiki dokumente sisaldav HTML
        """
        html_str = ''           
        for docid_key in self.index["sources"]:
            html_str += f'<h2>[DOCID={docid_key}]</h2><p>'
            html_str += self.index["sources"][docid_key]["content"]
        html_str = html_str.replace('\n\n', '<br><br>')
        return(html_str)

class WebServerHandler(BaseHTTPRequestHandler):
    form_html = \
        '''
        <form method='POST' enctype='multipart/form-data' action='/otsi'>
        <h2>Sisesta otsingusõned:</h2>
        <input name="message" type="text"><input type="submit" value="Otsi" >
        </form>
        '''

    form_html_cw = \
        '''
        <form method='POST' enctype='multipart/form-data' action='/otsils'>
        <h2>Sisesta otsingusõned:</h2>
        <input name="message" type="text"><input type="submit" value="Otsi (sh liitsõna osasõnadest)" >
        </form>
        '''
    
    def do_GET(self):
        try:
            if self.path.endswith("/otsi"):
                smart_search.fragments = False
                self.send_response(200)
                self.send_header('Content-type', 'text/html;charset=utf-8')
                self.end_headers()
                output = f"<html><body>{self.form_html}</body></html>"
                self.wfile.write(output.encode())
            elif self.path.endswith("/otsils"):
                smart_search.fragments = True
                self.send_response(200)
                self.send_header('Content-type', 'text/html;charset=utf-8')
                self.end_headers()
                output = f"<html><body>{self.form_html_cw}</body></html>"
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
            output += "<html><body>"
            
            smart_search.my_query(messagecontent[0])
            smart_search.result_query_2_result_query_sorted()
            #output += smart_search.result_query_sorted_2_html()
            output += smart_search.result_query_sorted_2_html_with_hover()
            
            if smart_search.fragments is True:
                output += self.form_html_cw
            else:
                output += self.form_html
            output += "</body></html>"
            self.wfile.write(output.encode())

        except:
            raise


def demo():
    try:
        print("smart_search.init_ok=", smart_search.init_ok)
        port = 7777
        print(f'Web server is running on port {port}')
        print(f'LEMMATIZER_IP={LEMMATIZER_IP}, LEMMATIZER_PORT={LEMMATIZER_PORT}')
        print("smart_search.init_ok=", smart_search.init_ok)
        server = HTTPServer(('', port), WebServerHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
    finally:
        if server:
            server.socket.close()    


smart_search = SMART_SEARCH(INDEXFILE, False)


if __name__ == '__main__':
    demo()
    

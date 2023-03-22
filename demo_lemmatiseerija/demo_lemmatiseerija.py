#!/usr/bin/python3

VERSION="2023.03.21"

'''
1. käivita lemmatiseerija konteiner (konteiner peab olema tehtud/allalaaditud)
    $ docker run -p 7000:7000 tilluteenused/lemmatizer konteiner
2. käivita lemmatiseerija konteineriga suhtlev veebiserver 
   (pythoni pakett requests peab olema installitud, ubuntu korral: sudo apt install -y python3-requests)
    $ cd demo_veebileht ; ./demo_lemmatiseerija.py

    docker run --env LEMMATIZER_IP=localhost --env LEMMATIZER_PORT=7777 tilluteenused/demo_lemmatiseerija 
3. Ava brauseris localhost:7777/lemmad ja järgi brauseris avanenud veebilehe juhiseid
    $ google-chrome http://localhost:7777/lemmad
    $ google-chrome http://localhost:7777/paring
    $ google-chrome http://localhost:7777/json
    
'''

import os
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi

LEMMATIZER_IP=os.environ.get('LEMMATIZER_IP') if os.environ.get('LEMMATIZER_IP') != None else 'localhost'
LEMMATIZER_PORT=os.environ.get('LEMMATIZER_PORT') if os.environ.get('LEMMATIZER_PORT') != None else '7000'

class WebServerHandler(BaseHTTPRequestHandler):
    form_lemmad_html = \
        '''
        <form method='POST' enctype='multipart/form-data' action='/lemmad'>
        <input name="message" type="text"><input type="submit" value="Lemmatiseeri:" >
        </form>
        '''
    form_paring_html = \
        '''
        <form method='POST' enctype='multipart/form-data' action='/paring'>
        <input name="message" type="text"><input type="submit" value="Leia päringule vastav lemmade kombinatsioon:" >
        </form>
        '''
    form_json_html = \
        '''
        <form method='POST' enctype='multipart/form-data' action='/json'>
        <input name="message" type="text"><input type="submit" value="Kuva lemmatiseerija JSON-väljund:" >
        </form>
        '''

    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/html;charset=utf-8')
            self.end_headers()
            output = ""
            if self.path.endswith("/version"):
                output += f'<html><body>{VERSION}</body></html>'
            elif self.path.endswith("/lemmad"):
                demo_lemmatiseerija.path = self.path
                output += f"<html><body>{self.form_lemmad_html}</body></html>"
            elif self.path.endswith("/paring"):
                demo_lemmatiseerija.path = self.path
                output += f"<html><body>{self.form_paring_html}</body></html>"
            elif self.path.endswith("/json"):
                demo_lemmatiseerija.path = self.path
                output += f"<html><body>{self.form_json_html}</body></html>"    
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
            if demo_lemmatiseerija.path.endswith("/lemmad"):
                output += f"<h2> {messagecontent[0]} ⇒ {demo_lemmatiseerija.lemmad(messagecontent[0])}</h2>"
                output += self.form_lemmad_html
            elif demo_lemmatiseerija.path.endswith("/paring"):
                paring = messagecontent[0].split(' ')
                output += f"<h2>({' & '.join(paring)}) ⇒ {demo_lemmatiseerija.paring(messagecontent[0])}</h2>"
                output += self.form_paring_html
            elif demo_lemmatiseerija.path.endswith("/json"):
                output += f'<b>{messagecontent[0]}  ⇒ </b><br>'
                output += f"{demo_lemmatiseerija.json_paring(messagecontent[0])}"
                output += self.form_json_html
            output += "</body></html>"
            self.wfile.write(output.encode())

        except:
            raise

class DEMO_LEMMATISEERIJA:
    path = ''

    def lemmad(self, token:str) -> str:
        """Päring lemmatiseerija veebiservelile

        Args:
            token (str): selle sõna lemmasid otsime

        Returns:
            str: leitud lemmade loend
        """
        json_token=json.dumps(token)
        json_query=json.loads(f"{{\"content\":{json_token}}}")
        json_response=json.loads(requests.post(f'http://{LEMMATIZER_IP}:{LEMMATIZER_PORT}/process', json=json_query).text)
        lemmad=""
        try:
            for tokens in json_response["annotations"]["tokens"]:
                for idx, mrf in enumerate(tokens["features"]["mrf"]):
                    lemmad += mrf["lemma_ma"] if idx==0 else f', {mrf["lemma_ma"]}'
        except:
            lemmad = "Ei suutnud lemmasid m&auml;&auml;rata"
        return lemmad

    def paring(self, token:str) -> str:
        """Päring lemmatiseerija veebiserverile

        Args: 
            token (str): selle sõna lemmasid otsime

        Returns:
            str: leitud lemmade loend
        """
        json_token=json.dumps(token)
        json_query=json.loads(f"{{\"content\":{json_token}}}")
        json_response=json.loads(requests.post(f'http://{LEMMATIZER_IP}:{LEMMATIZER_PORT}/process', json=json_query).text)
        paring=""
        try:
            for tokens_idx, tokens in enumerate(json_response["annotations"]["tokens"]):
                paring += '(' if tokens_idx == 0 else ' & ('
                for mrf_idx, mrf in enumerate(tokens["features"]["mrf"]):
                    paring += mrf["lemma_ma"] if mrf_idx==0 else f' &vee; {mrf["lemma_ma"]}'
                paring += ')'
                
        except:
            paring = "Ei suutnud p&auml;ringut genereerida"
        return paring

    def json_paring(self, token:str) -> str:
        """Päring lemmatiseerija veebiserverile

        Args: 
            token (str): selle sõna lemmasid otsime

        Returns:
            str: leitud lemmade loend
        """
        try:
            json_token=json.dumps(token)
            json_query=json.loads(f"{{\"content\":{json_token}}}")
            json_response=json.loads(requests.post(f'http://{LEMMATIZER_IP}:{LEMMATIZER_PORT}/process', json=json_query).text)
            paring=json.dumps(json_response, indent=2, ensure_ascii=False)
            paring = paring.replace('\n', '<br>').replace('  ', '&nbsp; &nbsp;') + '<br><br>'
        except:
            paring = "Ei suutnud p&auml;ringut genereerida"
        return paring

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

demo_lemmatiseerija = DEMO_LEMMATISEERIJA()

if __name__ == '__main__':
    demo()

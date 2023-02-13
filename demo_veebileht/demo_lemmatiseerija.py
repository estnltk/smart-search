#!/usr/bin/python3

'''
1. käivita lemmatiseerija konteiner (konteiner peab olema tehtud/allalaaditud)
    $ docker run -p 7000:7000 tilluteenused/lemmatizer konteiner
2. käivita lemmatiseerija konteineriga suhtlev veebiserver 
   (pythoni pakett requests peab olema installitud, ubuntu korral: sudo apt install -y python3-requests)
    $ cd demo_veebileht ; ./demo_lemmatiseerija.py
3. Ava brauseris localhost:7777/lemmad ja järgi brauseris avanenud veebilehe juhiseid
    $ google-chrome http://localhost:7777/lemmad
    
'''

import os
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi

LEMMATIZER_IP=os.environ.get('LEMMATIZER_IP')
LEMMATIZER_PORT=os.environ.get('LEMMATIZER_PORT')

class WebServerHandler(BaseHTTPRequestHandler):
    form_html = \
        '''
        <form method='POST' enctype='multipart/form-data' action='/lemmad'>
        <h2>Sisesta lemmatiseeritav s&otilde;ne</h2>
        <input name="message" type="text"><input type="submit" value="Lemmatiseeri" >
        </form>
         '''

    def do_GET(self):
        try:
            if self.path.endswith("/lemmad"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html;charset=utf-8')
                self.end_headers()
                output = f"<html><body>{self.form_html}</body></html>"
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
            output += f" <h2> S&otilde;ne <i>{messagecontent[0]}</i> v&otilde;imalikud lemmad: </h2>"
            lemmad = self.lemmatiseeri(messagecontent[0])
            output += f"<h1> {lemmad} </h1>"
            output += self.form_html
            output += "</body></html>"
            self.wfile.write(output.encode())

        except:
            raise

    def lemmatiseeri(self, token:str) -> str:
        """Päring lemmatiseerija veebiservelile

        Args:
            token (str): selle sõna lemmasid otsime

        Returns:
            str: leitud lemmade loend
        """
        json_token=json.dumps(token)
        json_query=json.loads(f"{{\"content\":{json_token}}}")
        json_response=json.loads(requests.post('http://localhost:7000/process', json=json_query).text)
        lemmad=""
        try:
            for tokens in json_response["annotations"]["tokens"]:
                for idx, mrf in enumerate(tokens["features"]["mrf"]):
                    lemmad += mrf["lemma_ma"] if idx==0 else f' {mrf["lemma_ma"]}'
        except:
            lemmad = "Ei suutnud lemmasid m&auml;&auml;rata"
        return lemmad

if __name__ == '__main__':
    try:
        port = 7777
        server = HTTPServer(('', port), WebServerHandler)
        print(f'Web server is running on port {port}')
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entered, stopping web server...")

    finally:
        if server:
            server.socket.close()

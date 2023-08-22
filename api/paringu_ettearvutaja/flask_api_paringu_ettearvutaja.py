#!/usr/bin/python3

'''Flask api, eelarvuta kõigi sisendkorpuses esinevate lemmade kõikvõimalikud vormid
ja millised neist esinevad tegelikult korpuses esinevad

----------------------------------------------

Lähtekoodist pythoni skripti kasutamine
1 Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2), veebiteenuse käivitamine pythoni koodist (1.3) ja CURLiga veebiteenuse kasutamise näited (1.4)
1.1 Lähtekoodi allalaadimine
    $ mkdir -p ~/git/ ; cd ~/git/
    $ git clone git@github.com:estnltk/smart-search.git smart_search_github
1.2 Virtuaalkeskkonna loomine
    $ cd ~/git/smart_search_github/api/paringu_ettearvutaja
    $ ./create_venv.sh
1.3 Veebiserveri käivitamine pythoni koodist
    $ cd  ~/git/smart_search_github/api/paringu_ettearvutaja
    $ OTSING_SONED='https://smart-search.tartunlp.ai/api/sonede-indeks/check' \
      TOKENIZER='https://smart-search.tartunlp.ai/api/tokenizer/process'   \
      ANALYSER='https://smart-search.tartunlp.ai/api/analyser/process'     \
      GENERATOR='https://smart-search.tartunlp.ai/api/generator/process'   \
      INDEKSEERIJA_LEMMAD='https://smart-search.tartunlp.ai/api/lemmade-indekseerija' \
        venv/bin/python3 ./flask_api_paringu_ettearvutaja.py
1.4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Presidendi kantselei."},"DOC_2":{"content":"Kuidas valitakse presidenti. Valimissüsteemi alused."}}}' \
        localhost:6602/api/paringu-ettearvutaja/json | jq | less

    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Presidendi kantselei."},"DOC_2":{"content":"Kuidas valitakse presidenti. Valimissüsteemi alused."}}}' \
        localhost:6602/api/paringu-ettearvutaja/csv | less

    $ curl --silent --request POST --header "Content-Type: application/json" \
        localhost:6602/api/paringu-ettearvutaja/version | jq

----------------------------------------------

Lähtekoodist tehtud konteineri kasutamine
2 Lähtekoodi allalaadimine (2.1), konteineri kokkupanemine (2.2), konteineri käivitamine (2.3) ja CURLiga veebiteenuse kasutamise näited  (2.4)
2.1 Lähtekoodi allalaadimine: järgi punkti 1.1
2.2 Konteineri kokkupanemine
    $ cd  ~/git/smart_search_github/api/paringu_ettearvutaja
    $ docker build -t tilluteenused/smart_search_api_paringu_ettearvutaja:2023.08.22 . 
2.3 Konteineri käivitamine
    $ docker run -p 6602:6602  \
        --env OTSING_SONED='https://smart-search.tartunlp.ai/api/sonede-indeks/check' \
        --env TOKENIZER='https://smart-search.tartunlp.ai/api/tokenizer/process' \
        --env ANALYSER='https://smart-search.tartunlp.ai/api/analyser/process' \
        --env GENERATOR='https://smart-search.tartunlp.ai/api/generator/process' \
        --env INDEKSEERIJA_LEMMAD='https://smart-search.tartunlp.ai/api/lemmade-indekseerija' \
        tilluteenused/smart_search_api_paringu_ettearvutaja:2023.08.22 
2.4 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

DockerHUBist tõmmatud konteineri kasutamine
3 DockerHUBist koneineri tõmbamine (3.1), konteineri käivitamine (3.2) ja CURLiga veebiteenuse kasutamise näited (3.3)
3.1 DockerHUBist konteineri tõmbamine
    $ docker pull tilluteenused/smart_search_api_paringu_ettearvutaja:2023.08.22 
3.2 Konteineri käivitamine: järgi punkti 2.3
3.3 CURLiga veebiteenuse kasutamise näited: järgi punkti 1.4

----------------------------------------------

TÜ pilves töötava konteineri kasutamine
4 CURLiga veebiteenuse kasutamise näited
    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Presidendi kantselei."},"DOC_2":{"content":"Kuidas valitakse presidenti. Valimissüsteemi alused."}}}' \
        https://smart-search.tartunlp.ai/api/paringu-ettearvutaja/json | jq

    $ curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Presidendi kantselei."},"DOC_2":{"content":"Kuidas valitakse presidenti. Valimissüsteemi alused."}}}' \
        https://smart-search.tartunlp.ai/api/paringu-ettearvutaja/csv

    $ curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/paringu-ettearvutaja/version | jq

----------------------------------------------

'''


import os
import sys
import json
import requests
import subprocess
import json
import argparse
from flask import Flask, request, jsonify, make_response
from typing import Dict, List, Tuple
from collections import OrderedDict

#import api_lemmade_indekseerija



class ETTEARVUTAJA:
    def __init__(self):
        """Initsialisserime muutujad: versiooninumber ja kasutatavate veebiteenuste URLid
        """
        self.VERSION="2023.08.22"

        self.otsing = os.environ.get('OTSING_SONED') # veebiteenus sõnavormide indeksis olemise kontrollimiseks
        if self.otsing is None: 
            self.OTSING_SONED_IP=os.environ.get('OTSING_SONED_IP') if os.environ.get('OTSING_SONED_IP') != None else 'localhost'
            self.OTSING_SONED_PORT=os.environ.get('OTSING_SONED_PORT') if os.environ.get('OTSING_SONED_PORT') != None else '7007'
            self.otsing = f'http://{self.OTSING_SONED_IP}:{self.OTSING_SONED_PORT}/api/sonede-indeks/check'

        self.tokenizer = os.environ.get('TOKENIZER') # veebiteenus sõnestamiseks
        if self.tokenizer is None:
            self.TOKENIZER_IP=os.environ.get('TOKENIZER_IP') if os.environ.get('TOKENIZER_IP') != None else 'localhost'
            self.TOKENIZER_PORT=os.environ.get('TOKENIZER_PORT') if os.environ.get('TOKENIZER_PORT') != None else '6000'
            self.tokenizer = f'http://{self.TOKENIZER_IP}:{self.TOKENIZER_PORT}/api/tokenizer/process'

        self.analyser = os.environ.get('ANALYSER')  # veebiteenus morf analüüsiks
        if self.analyser is None:
            self.ANALYSER_IP=os.environ.get('ANALYSER_IP') if os.environ.get('ANALYSER_IP') != None else 'localhost'
            self.ANALYSER_PORT=os.environ.get('ANALYSER_PORT') if os.environ.get('ANALYSER_PORT') != None else '7007'
            self.analyser = f'http://{self.ANALYSER_IP}:{self.ANALYSER_PORT}/api/analyser/process'

        self.generator = os.environ.get('GENERATOR') # veebiteenus morf genemiseks
        if self.generator is None:
            self.GENERATOR_IP=os.environ.get('GENERATOR_IP') if os.environ.get('GENERATOR_IP') != None else 'localhost'
            self.GENERATOR_PORT=os.environ.get('GENERATOR_PORT') if os.environ.get('GENERATOR_PORT') != None else '7000'
            self.generator = f'http://{self.GENERATOR_IP}:{self.GENERATOR_PORT}/process' # NB! generaator ei ole selle koha peal analoogiline teiste teenustega
        
        self.ignore_pos = "PZJ" # ignoreerime lemmasid, mille sõnaliik on: Z=kirjavahemärk, J=sidesõna, P=asesõna

    def morfi(self)->None:
        """Morfime sõnestatud sisendkorpuse

        Kasutame: 
            self.json_io; morf analüüsi veebiteenust.

        Raises:
            Exception: Exception({"warning":'Probleemid veebiteenusega: {self.analyser}'})

        Returns:
            None, lisab self.json_io'sse morf analüüsid
        """

        for docid in self.json_io["sources"]:
            self.json_io["sources"][docid]["params"] = {"vmetajson":["--guess"]}
            try:
                doc = json.loads(requests.post(self.analyser, json=self.json_io["sources"][docid]).text)
            except:
                raise Exception({"warning":'Probleemid veebiteenusega: {self.analyser}'})
            for idx_token, token in enumerate(doc["annotations"]["tokens"]):        # tsükkel üle sõnede (ainult üks sõne meil antud juhul on)
                tokens = []                                                             # siia korjame erinevad lemma-stringid
                for mrf in token["features"]["mrf"]:                                    # tsükkel üle sama sõne alüüsivariantide (neid võib olla mitu)
                    if self.ignore_pos.find(mrf["pos"]) != -1:                              # selle sõnaliiiga lemmasid...
                        continue                                                                # ...ignoreerime, neid ei indekseeri
                    if mrf["lemma_ma"] not in tokens:                                                   # sõne morf analüüside hulgas võib sama kujuga lemma erineda ainult käände/põõrde poolest
                        tokens.append( mrf["lemma_ma"])                                                      # lisame uue lemma-stringi, kui sellist veel polnud
                self.json_io["sources"][docid]["annotations"]["tokens"][idx_token]["features"]["tokens"] = tokens # lisame leitud lemmad tulemusse
    
    def tee_paradigmad(self, lemma:str)-> (List[str], List[str]):
        """Leiame sisendlemma kõik vormid ja nende hulgast need mis tegelikult korpuses esinesid

        Args:
            lemma (str): lemma

        Kasutame: 
            Sõnavormide genereerimise veebiteenust; veebiteenust mis ütleb millised sõnavormid tegelikult korpuses esinesid.


        Raises:
            Exception: Exception({"warning":'Probleemid veebiteenusega: {self.generator}'})
            Exception: Exception({"warning":f'Probleemid veebiteenusega: {self.paring}'})

        Returns:
            List, List: paradigma_täielik -- lemma kõik vormid, paradigma_korpuses -- lemma korpuses esinevad vormid
        """
        # gene selle lemma kõik vormid
        try:
            generator_out = json.loads(requests.post(self.generator, json={"type":"text", "content": lemma}).text)
        except:
            raise Exception({"warning":'Probleemid veebiteenusega: {self.generator}'})
        # lisa saadud vormid päringusse
        paradigma_täielik = []
        for text in generator_out["response"]["texts"]:
            for generated_form in text["features"]["generated_forms"]:
                paradigma_täielik.append(generated_form["token"].replace("_", "").replace("=", "").replace("+", ""))
        
        # leiame lemma kõigi vormide hulgast need, mis esinesid korpuses
        paradigma_korpuses = []
        if len(paradigma_täielik) > 0:
            try:
                paradigma_korpuses = json.loads(requests.post(self.otsing, json=paradigma_täielik).text)
                
                '''
                paradigma_korpuses_1 = json.loads(requests.post(self.paring, json=paradigma_täielik).text)
                paradigma_korpuses = []
                for p in paradigma_korpuses_1:
                    if p not in paradigma_korpuses:
                        paradigma_korpuses.append(p)
                '''
            except:
                raise Exception({"warning":f'Probleemid veebiteenusega: {self.otsing}'})
        return paradigma_täielik, paradigma_korpuses

    def tee_lemmade_indeks(self, json_in:Dict) -> None:
        """Tekitab lemmade indeksi

        Args:
            json_in (Dict): SisendJSON, sisaldab korpusetekste

            json_in
            {   "sources":
                {   DOCID:              // dokumendi ID
                    {   "content": str  // dokumendi tekst ("plain text", märgendus vms teraldi tõstetud)
                                        // dokumendi kohta käiv lisainfo pane siia...
                    }
                }
            }

        Raises:
            Exception: Exception({"warning":f'Probleemid veebiteenusega: {self.tokenizer}'})

        Välja: 
            self.json_io:
            {   "index":
                {   "lemmade_paradigmad": # järjestatud LEMMA järgi
                    {   LEMMA: 
                        {   "korpuses": [SÕNAVORM] # LEMMA esines korpuses SÕNAVORMides
                            "täielik":  [SÕNAVORM] # LEMMA kõikvõimalikd vormid
                        }
                    }
                    "vorm_lemmadeks":
                    {   VORM: [LEMMA]   # sõnavormile vastavad lemmad, järjestatud VORMi järgi
                    }
                }
            }
        """

        self.json_io = json_in
        for docid in self.json_io["sources"]:
            try:                                                # sõnestame kõik dokumendid
                self.json_io["sources"][docid] = json.loads(requests.post(self.tokenizer, json=self.json_io["sources"][docid]).text)
            except:                                             # sõnestamine äpardus
                raise Exception({"warning":f'Probleemid veebiteenusega: {self.tokenizer}'})
        self.morfi()                                            # leiame iga tekstisõne võimalikud sobiva sõnaliigiga tüvi+lõpud (liitsõnapiir='_', järelliite eraldaja='=')   
        if "index" not in self.json_io:                         # geneme iga lemma kõik vormid
            self.json_io["index"] = {"lemmade_paradigmad":{}}
        for docid in self.json_io["sources"]:                   # tsükkel üle tekstide
            for token in self.json_io["sources"][docid]["annotations"]["tokens"]: # tsükkel üle lemmade
                if len(token["features"]["tokens"])==0:             # kui pole ühtegi meid huvitava sõnaliigiga...
                    continue                                            # ...laseme üle
                for tkn in token["features"]["tokens"]:             # tsükkel üle leitud liitsõnapiiridega lemmade
                    puhas_tkn = tkn.replace('_', '').replace('=', '')   # terviklemma lisamine...
                    if puhas_tkn not in self.json_io["index"]["lemmade_paradigmad"]:
                        # sellist lemmat polnud, lisame genetud vormid
                        paradigma_täielik, paradigma_korpuses = self.tee_paradigmad(puhas_tkn) # leiame lemma kõik vormid ja korpuses esinenud vormid
                        assert puhas_tkn in paradigma_täielik, "Lemma ei sisaldu täisparadigmas"
                        self.json_io["index"]["lemmade_paradigmad"][puhas_tkn] = {"täielik": paradigma_täielik, "korpuses":paradigma_korpuses}

            del self.json_io["sources"][docid]["annotations"]["sentences"] # kustutame sõnaestajast ja morf analüüsist järgi jäänud mudru
            del self.json_io["sources"][docid]["annotations"]["tokens"]
            if len(self.json_io["sources"][docid]["annotations"]) == 0:
                del self.json_io["sources"][docid]["annotations"]
            del self.json_io["sources"][docid]["params"]
        del self.json_io["sources"]                                        # kustutame algdsed dokumendid

    def tee_json(self)->None:
        """Teeme valmis lõpliku väljundJSONi

        Sisse: 
            self.json_io:
            {   "index":
                {   "lemmade_paradigmad":
                    {   LEMMA: 
                        {   "korpuses": [SÕNAVORM] # LEMMA esines korpuses SÕNAVORMides
                            "täielik":  [SÕNAVORM] # LEMMA kõikvõimalikd vormid
                        }
                    }
                }
            }

        Returns:
            self.json_io:
            {   "index":
                {   "lemmade_paradigmad": # järjestatud LEMMA järgi
                    {   LEMMA: 
                        {   "korpuses": [SÕNAVORM] # LEMMA esines korpuses SÕNAVORMides
                        }
                    }
                    "vorm_lemmadeks":
                    {   VORM: [LEMMA]   # sõnavormile vastavad lemmad, järjestatud VORMi järgi
                    }
                }
            }        
        """
        self.json_io["index"]["vorm_lemmadeks"] = {}
        for lemma in self.json_io["index"]["lemmade_paradigmad"]:
            lemmade_paradigmad = self.json_io["index"]["lemmade_paradigmad"][lemma]
            for vorm in lemmade_paradigmad["täielik"]:
                if vorm not in self.json_io["index"]["vorm_lemmadeks"]:
                    self.json_io["index"]["vorm_lemmadeks"][vorm] = [lemma]
                elif lemma not in self.json_io["index"]["vorm_lemmadeks"][vorm]:
                    self.json_io["index"]["vorm_lemmadeks"][vorm].append(lemma)
            del lemmade_paradigmad["täielik"]
        self.json_io["index"]["vorm_lemmadeks"] = sorted(self.json_io["index"]["vorm_lemmadeks"].items(), key=lambda t: t[0])
        self.json_io["index"]["lemmade_paradigmad"] = sorted(self.json_io["index"]["lemmade_paradigmad"].items(), key=lambda t: t[0])
        
    def tee_csv(self)->str:
        """Teeme valmis lõpliku väljundCSV

        Sisse: 
            self.json_io:
            {   "index":
                {   "lemmade_paradigmad":
                    {   LEMMA: 
                        {   "korpuses": [SÕNAVORM] # LEMMA esines korpuses SÕNAVORMides
                            "täielik":  [SÕNAVORM] # LEMMA kõikvõimalikd vormid
                        }
                    }
                }
            }

        Returns:
            str: Read kujul "sõnavorm_täisparadigamast\\tsõnavorm_korpusest"
        """
        dct4csv = {}
        for lemma in self.json_io["index"]["lemmade_paradigmad"]:
            lemmade_paradigmad = self.json_io["index"]["lemmade_paradigmad"][lemma]
            for vorm1 in lemmade_paradigmad["täielik"]:
                for vorm2 in lemmade_paradigmad["korpuses"]:
                    key = f'{vorm1}\t{vorm2}'
                    if key not in dct4csv:
                        dct4csv[key] = {}

        csvstring = ""
        for vorm1_vorm2 in dct4csv:
            csvstring += vorm1_vorm2 + '\n'
        return csvstring


    def version_json(self) -> Dict:
        """Kuva JSONkujul versiooniinfot ja kasutatavate veebiteenuste URLe

        Returns:
            Dict: versiooninfo ja URLid
        """
        return  {"ettearvutaja.version": self.VERSION, "otsing": self.otsing  , "tokenizer": self.tokenizer, "analyser": self.analyser,  "generator:": self.generator}


lemmade_ettearvutaja = ETTEARVUTAJA()

app = Flask("api_lemmade_ettervutaja")

@app.route('/api/paringu-ettearvutaja/json', methods=['POST'])
@app.route('/json', methods=['POST'])
def api_lemmade_ettearvutaja_json():
    """Leia sisendkorpuse sõnede kõikvõimalikud vormid ja nonde hulgast need, mis esinesid korpuses

    Args:

    Sisendjson:
        SisendJSON, sisaldab korpusetekste:

        json_in
        {   "sources":
            {   DOCID:              // dokumendi ID
                {   "content": str  // dokumendi tekst ("plain text", märgendus vms teraldi tõstetud)
                                    // dokumendi kohta käiv lisainfo pane siia...
                }
            }
        }

    Returns:
        Response: VäljundJSON:

        {   "index":
            {   "lemmade_paradigmad": # järjestatud LEMMA järgi
                {   LEMMA: 
                    {   "korpuses": [SÕNAVORM] # LEMMA esines korpuses SÕNAVORMides
                    }
                }
                "vorm_lemmadeks":
                {   VORM: [LEMMA]   # sõnavormile vastavad lemmad, järjestatud VORMi järgi
                }
            }
        }  
    """
    lemmade_ettearvutaja.tee_lemmade_indeks(request.json)
    lemmade_ettearvutaja.tee_json()
    return jsonify(lemmade_ettearvutaja.json_io)

@app.route('/api/paringu-ettearvutaja/csv', methods=['POST'])
@app.route('/csv', methods=['POST'])
def api_lemmade_ettearvutaja_csv():
    """Leia sisendkorpuse sõnede kõikvõimalikud vormid ja nonde hulgast need, mis esinesid korpuses

    Args:
    
    Sisendjson:
        SisendJSON, sisaldab korpusetekste:

        json_in
        {   "sources":
            {   DOCID:              // dokumendi ID
                {   "content": str  // dokumendi tekst ("plain text", märgendus vms teraldi tõstetud)
                                    // dokumendi kohta käiv lisainfo pane siia...
                }
            }
        }

    Returns:
        str: Read kujul "sõnavorm_täisparadigamast\\tsõnavorm_korpusest"
    """
    try:
        lemmade_ettearvutaja.tee_lemmade_indeks(request.json)
        csv_str = lemmade_ettearvutaja.tee_csv()
        csv_response = make_response(csv_str)
        csv_response.headers["Content-type"] = "text/csv; charset=utf-8"
    except Exception as e:
        csv_response = e
    return csv_response

@app.route('/api/paringu-ettearvutaja/version', methods=['GET', 'POST'])
@app.route('/version', methods=['POST'])
def api_lemmade_ettearvutaja_version():
    """Kuvame versiooni ja muud infot

    Returns:
        ~flask.Response: Lemmatiseerija versioon
    """
    json_response = lemmade_ettearvutaja.version_json()
    return jsonify(json_response)

if __name__ == '__main__':
    default_port=6602
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-d', '--debug', action="store_true", help='use debug mode')
    args = argparser.parse_args()
    app.run(debug=args.debug, port=default_port)



        

        
        
    
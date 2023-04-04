#!/usr/bin/python3

import os
import json
import requests

LEMMATIZER_IP=os.environ.get('LEMMATIZER_IP') if os.environ.get('LEMMATIZER_IP') != None else 'localhost'
LEMMATIZER_PORT=os.environ.get('LEMMATIZER_PORT') if os.environ.get('LEMMATIZER_PORT') != None else '7000'

class DEMO_LEMMATISEERIJA:
    """Klass lemmatiseerija demomiseks mõeldud meetoditega.
    Kasutab lemmatiseerimise veebiteenust.
    """
    path = ''

    def lemmad(self, token:str) -> str:
        """Sõna lemmade loendiks (lemmatiseerija veebiteenuse abil)

        Args:
            token (str): selle sõna lemmasid otsime

        Returns:
            str: koma ja tühikuga eraldatud lemmade loend
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
        """Sõnad päringuks (lemmatiseerija veebiteenuse abil)

        Args: 
            token (str): selle sõna lemmasid otsime

        Returns:
            str: Sisendsõnedest tuletaud päring (lemmade kombinatsioon)
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
        """Sisendsõnede lemmatiseerimise tulemus JSON-kujul (lemmatiseerija veebiteenuse abil)

        Args: 
            token (str): selle sõna lemmasid otsime

        Returns:
            str: Lemmatiseerija veebiteenuse JSON-väljund
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

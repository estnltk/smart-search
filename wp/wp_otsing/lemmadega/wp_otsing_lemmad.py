#!/usr/bin/env python3

'''Otsingumootor (otsisõned lemmadeks ja lemmade indeksist otsimine)
'''

import os
import requests
import json
from collections import OrderedDict

class SMART_SEARCH:
    def __init__(self):
        self.VERSION="2023.05.06"

        self.idxfile = os.environ.get('IDXFILE')
        if self.idxfile is None:
            self.idxfile = 'riigiteataja-lemmad-json.idx'
        with open(self.idxfile, 'r') as file:
            self.idx_json = json.load(file)

    def otsing(self, fragments, query_json):
        """Otsing: päringus ja indeksis lemmad

        Args:
            fragments (_type_): True: vaatame liitsõna osasõnasid, False: ei vaata liitsõna osasõnasid
            query_json (_type_): päring (vastava veebiteenusega lemmade kombinatsiooniks teisendatud otsisõned)
        """
        self.fragments = fragments
        self.query_json = query_json
        self.result_json = {}
        self.otsing_rec(0, None)
        # järjestame tulemused iga dokumendi siseselt
        for docid in self.result_json:
            self.result_json[docid] = OrderedDict(sorted(self.result_json[docid].items(), key=lambda t: t[0]))

    def otsing_rec(self, query_idx, required_idx_docid):
        """Rekursiivne otsingualgoritm

        Args:
            query_idx (_type_): parajasti vaatame niimitmendat päringusõne
            required_idx_docid (_type_): otsitav lemma peab olema selles dokumendis

        Returns:
            _type_: True: leidsime midagi sobivat, False: ei leidnud midagi sobivat
        """
        if query_idx >= len(self.query_json["annotations"]["query"]):
            return True

        for token in self.query_json["annotations"]["query"][query_idx]:
            retval = False
            documents = self.idx_json["index"].get(token)
            if documents is None: # polnud üheski dokumendis, laseme üle
                continue
            for document in documents:
                if (required_idx_docid is not None) and (required_idx_docid != document):
                    continue
                for x in documents[document]:
                    if (self.fragments is False) and x["liitsõna_osa"] is True:
                        continue
                    if self.otsing_rec(query_idx+1, document) is False:
                        continue; # ei sobinud
                    # ühel või teisel moel sobis, läheb tulemusse
                    if document in self.result_json:   # selline DOCID juba oli
                        if x["start"] in self.result_json[document]: # selline stardipositsioon juba oli
                            if token not in self.result_json[document][x["start"]]["lemmas"]: # sellist lemmat polnuid, lisame
                                self.result_json[document][x["start"]]["lemmas"].append(token)
                        else:                                           # sellist stardipositsiooni polnud
                           self.result_json[document][x["start"]] = \
                                        {   "end":x["end"], "lemmas":[token],
                                            "token": self.idx_json["sources"][document]["content"][x["start"]:x["end"]]}    
                    else:
                        self.result_json[document] = \
                                        {   x["start"]: {"end":x["end"], "lemmas":[token],
                                             "token": self.idx_json["sources"][document]["content"][x["start"]:x["end"]]}}
                    retval = True
        return retval

    def koosta_vastus(self, formaat):
        """Otsingutulemus moel või teisel HTML-kujule

        Args:
            formaat (_type_): millist HTML-kuju on soovitud

        Returns:
            str: HTML-kujul otsingutulemus
        """
        if formaat == 'json':
            return self.koosta_vastus_json()
        if formaat == 'text':
            return self.koosta_vastus_text()
        return ''

    def koosta_vastus_json(self):
        """Esita otsingu JSON-tulemus HTML-kujul

        Returns:
            _type_: otsingu JSON-tulemus HTML-kujul
        """
        content = '<h2>Päring:</h2>'
        content += json.dumps(self.query_json, ensure_ascii=False, indent=2).replace(' ', '&nbsp;').replace('\n', '<br>')+'<hr>'
        content += "<h2>Tulemus:</h2>"
        content += json.dumps(self.result_json, ensure_ascii=False, indent=2).replace(' ', '&nbsp;').replace('\n', '<br>')+'<hr>'
        return content

    def koosta_vastus_text(self):
        """Esita otsingu JSON-tulemus märgendatud tekstina HTML-kujul

        Returns:
            _type_: otsingu JSON-tulemus märgendatud tekstina HTML-kujul
        """        
        if len(self.result_json) <= 0:
            return '<h2>Päringule vastavaid dokumente ei leidunud!</h2><hr>'
        content = '<hr><h2>Päring:</h2>'
        content += json.dumps(self.query_json, ensure_ascii=False, indent=2).replace(' ', '&nbsp;').replace('\n', '<br>')+'<hr><hr>'
        for dokid in self.result_json:
            links = self.result_json[dokid]
            link_prev = {"end":0}
            for idx, start in enumerate(links):
                link = links[start]
                if idx == 0:
                    content += f'<h2>DocID: {dokid}</h2>'
                content += self.idx_json["sources"][dokid]["content"][link_prev["end"]:start]
                link_prev = link
                content += f' <b>{self.idx_json["sources"][dokid]["content"][start:link["end"]]}</b>'
                content += f'<i>[{", ".join(link["lemmas"])}]</i>'
                pass
            content += self.idx_json["sources"][dokid]["content"][link_prev["end"]:] + '<hr>'

        content = content.replace('\n', '<br>')+'<hr>'
        return content
    
#!/usr/bin/env python3

'''Otsingumootor
'''

import os
import requests
import json
from collections import OrderedDict

class SMART_SEARCH:
    def __init__(self):
        self.VERSION="2023.05.07"                           # otsimootori versioon

        self.idxfile = os.environ.get('IDXFILE')            # otsime indeksfaili nime keskkonnamootujast
        if self.idxfile is None:                            # kui seal polnud...
            self.idxfile = 'riigiteataja-lemmad-json.idx'       # ...võtame vaikimisi lemmade indeksi
        with open(self.idxfile, 'r') as file:               # avame indeksfaili...
            self.idx_json = json.load(file)                 # ...loeme mällu

    def otsing(self, fragments, query_json):
        """Otsing: päringus ja indeksis lemmad

        Args:
            fragments (_type_): True: vaatame liitsõna osasõnasid, False: ei vaata liitsõna osasõnasid
            query_json (_type_): päring (vastava veebiteenusega lemmade kombinatsiooniks teisendatud otsisõned)
        """
        self.fragments = fragments                          # kas otsime liitsõna osasõndest
        self.query_json = query_json                        # jooksev päring (otsisõnade lemmad/sõnavormid)
        self.result_json = {}                               # otsingutulemus
        self.otsing_rec(0, None)                            # otsing
        for docid in self.result_json:                      # järjestame otsingutulemused iga dokumendi siseselt
            self.result_json[docid] = OrderedDict(sorted(self.result_json[docid].items(), key=lambda t: t[0]))

    def otsing_rec(self, query_idx, required_docid):
        """Rekursiivne otsingualgoritm

        Args:
            query_idx (_type_): parajasti vaatame niimitmendat päringusõne
            required_idx_docid (_type_): otsitav peab olema selles dokumendis

        Returns:
            _type_: True: leidsime midagi sobivat, False: ei leidnud midagi sobivat
        """
        if query_idx >= len(self.query_json["annotations"]["query"]):           # kõik otsinusõned on läbivaadatud
            return True                                                             # leidsime mingi sobiva kombinatsiooni tekstidest
        retval = False
        for token in self.query_json["annotations"]["query"][query_idx]:        # tsükkel üle query_idx'inda päringusõne lemmade/sõnavormide
            documents = self.idx_json["index"].get(token)                           # leiame, millistes dokumentides esines
            if documents is None: # polnud üheski dokumendis, laseme üle            # polnud üheski dokumendis...
                continue                                                                # ...laseme üle
            for docid in documents:                                                 # tsükkel üle dokumentide kus vajalik päringusõne lemmade/sõnavorm esines
                if (required_docid is not None) and (required_docid != docid):          # polnud nõutavas dokumendis...
                    continue                                                                # ...laseme üle
                for x in documents[docid]:                                              # tsükkel üle esinemiste
                    if (self.fragments is False) and x["liitsõna_osa"] is True:         # ei soovi liitsõna osasõnu, aga see on...
                        continue                                                            # laseme üle
                    if self.otsing_rec(query_idx+1, docid) is False:                    # järgmiste päringusõnede lemmade/sõnavormide seas polnud sobivat...
                        continue; # ei sobinud                                              # laseme üle
                                                                                        # ühel või teisel moel sobis, läheb tulemusse
                    if docid in self.result_json:                                       # selline DOCID on olnud
                        if x["start"] in self.result_json[docid]:                           # selline stardipositsioon juba oli
                            if token not in self.result_json[docid][x["start"]]["tokens"]:      # sellist lemmat/sõnavormi polnud...
                                self.result_json[docid][x["start"]]["tokens"].append(token)         # ...lisame
                        else:                                                                   # sellist stardipositsiooni polnud...
                           self.result_json[docid][x["start"]] = \
                            {"end":x["end"], "tokens":[token],
                             "token": self.idx_json["sources"][docid]["content"][x["start"]:x["end"]]}  # ...lisame
                    else:                                                                   # sellist DOCIDi pole olnud...
                        self.result_json[docid] = \
                        {x["start"]: {"end":x["end"], "tokens":[token],
                         "token": self.idx_json["sources"][docid]["content"][x["start"]:x["end"]]}} # ...lisame kogu kupatuse
                    retval = True                                                       # leidsime midagi sobivat
        return retval                                                           # anname teada, kas leidsime midagi sobivat

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
                content += f'<i>[{", ".join(link["tokens"])}]</i>'
                pass
            content += self.idx_json["sources"][dokid]["content"][link_prev["end"]:] + '<hr>'

        content = content.replace('\n', '<br>')+'<hr>'
        return content
    
#!/usr/bin/env python3



import os
import requests
import json
import sqlite3
from collections import OrderedDict
from typing import List, Dict, Tuple, Union
from operator import itemgetter

class SEARCH_DB:
    def __init__(self):
        self.VERSION="2023.09.16"                   # otsimootori versioon

        self.db_index = os.environ.get('DB_INDEX')  # otsime andmebaasi nime keskkonnamootujast
        if self.db_index is None:                   # kui seal polnud...
            self.db_index = './index.db'            # ...võtame vaikimisi

        # avame andmebaasi ainult lugemiseks

        try:
            self.con_index = sqlite3.connect(f'file:{self.db_index}?mode=rw', 
                                            uri=True, check_same_thread=False)
        except:
            self.con_index = None
            raise Exception({"error": 
                            f'Andmebaasi {self.db_index} avamine ebaõnnestus'})
            
        self.cur_index = self.con_index.cursor()

        self.ea_paring = os.environ.get('EA_PARING')
        if self.ea_paring is None:
            self.EA_PARING_IP=os.environ.get('EA_PARING_IP') if os.environ.get('EA_PARING_IP') != None else 'localhost'
            self.EA_PARING_PORT=os.environ.get('EA_PARING_PORT') if os.environ.get('EA_PARING_PORT') != None else '6602'
            self.ea_paring = f'http://{self.EA_PARING_IP}:{self.EA_PARING_PORT}/api/ea_paring/json'

    def __del__(self)->None:
        """Sulgeme avatud andmebaasid
        """
        if self.con_index is not None:
            self.con_index.close()

    def otsing(self, fragments:bool, query_json:Dict)->None:
        """Public: Otsing: päringus ja indeksis sõnavormid

        Args:
            fragments (bool): 
            * True: vaatame liitsõna osasõnasid, 
            * False: ei vaata liitsõna osasõnasid

            query_json (Dict): päring (vastava veebiteenusega lemmade 
            kombinatsiooniks teisendatud otsisõned)
        """
        self.fragments = fragments      # kas otsime liitsõna osasõndest
        self.query_json = query_json    # jooksev päring
        self.result_json = {}           # otsingutulemus

        self.otsing_rec(0, [])        # rekursiivne otsing, tulemus self.result_json

        # otsingutulemuste korrastamine
        #for docid in self.result_json:  #järjestame otsingutulemused iga dokumendi siseselt
        #    self.result_json[docid] = OrderedDict(sorted(self.result_json[docid].items(), key=lambda t: t[0]))

    def otsing_rec(self, query_idx:int, required_docid:List[str])->bool:
        """Private: Rekursiivne otsingualgoritm

        Args:
            query_idx (int): parajasti vaatame niimitmendat 
            päringusõne range(0, len(self.query_json["annotations"]["query"]))

            required_idx_docid (str): otsitav peab olema selles dokumendis, 
            None - suvaline dokument sobib

        Returns:
            bool: False: ei leidnud midagi sobivat; True: leidsime midagi 
            sobivat, vt self.result_json 
        """
        if query_idx >= len(self.query_json["annotations"]["query"]):           # kõik otsinusõned on läbivaadatud
            return True # kõik  päringusõned läbivaadatud                                                          # leidsime mingi sobiva kombinatsiooni tekstidest
        retval = False

        idx_list = self.korpusevormid_2_idxrec(self.lemmad_2_korpusevormid(query_idx), required_docid)
        if len(idx_list) < 1: # pole midagi otsida
            return False
        docid_list = list(set(map(itemgetter(0),idx_list)))
        pass

        for docid in docid_list:
            pass

        '''
        # tsükkel üle query_idx'inda päringusõne lemmade/sõnavormide
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
                retval = True                                                    # leidsime midagi sobivat
        '''
        return retval                                                           # anname teada, kas leidsime midagi sobivat

    def lemmad_2_korpusevormid(self, query_idx:int)->Tuple[str]:
        """Lemmadele vastavad vormid korpuses

        Args:
            query_idx (int): Niimeitmendale päringusõnele vastavaid lemmasid vaatame

        Returns:
            List[Tuple[str]]: Korpusevormid, neid hakkame indeksist otsima
        """
        lemmade_loend = f'lemma = "{self.query_json["annotations"]["query"][query_idx][0]}"'
        for lemma in self.query_json["annotations"]["query"][query_idx][1:]:
            lemmade_loend += f' OR lemma = "{lemma}"'

        res = self.cur_index.execute(f'''
            SELECT vorm FROM lemma_korpuse_vormid 
            WHERE {lemmade_loend}''')
        return sum(res.fetchall(), ())

    def korpusevormid_2_idxrec(self, korpusevormid:Tuple[str], required_docid:List[str])->List:
        if len(korpusevormid) <= 0:
            return []
        
        where_vormid = 'vorm in ("' + '","'.join(korpusevormid) + '")'
        where_liitsõna = ' AND liitsona_osa = 0' if self.fragments is False else ''
        if len(required_docid) == 0:
            
        if len(required_docid)==0:
            where_docid = ''
        else:

            where_docid = 'docid in ("' + '","'.join(required_docid) + '")'

        res = self.cur_index.execute(f'''
            SELECT docid, vorm, start, end, liitsona_osa
            FROM indeks
            WHERE {where_vormid} {where_liitsõna} {where_docid}                  
            ORDER BY docid''')

        return res.fetchall()



    def koosta_vastus(self, formaat:str, paringu_str:str)->None:
        """Public: Otsingutulemus moel või teisel HTML-kujule

        Args:
            formaat (str): päringu tulemuse esitusviis {html|html+details|json}

        Returns:
            str: Soovitud kujul otsingutulemus
        """
        self.content = '<hr><h2>Päring:</h2>'
        self.content += f'{paringu_str}<hr><hr>'
        if formaat == 'json':
            self.koosta_vastus_json()
        else:
            self.koosta_vastus_html(formaat)

    def koosta_vastus_json(self)->None:
        """Private: Esita otsingu JSON-tulemus HTML-kujul

        Returns:
            (str) self.content: otsingu JSON-tulemus HTML-kujul
        """
        self.content += "<h2>Tulemus:</h2>"
        self.content += json.dumps(self.result_json, ensure_ascii=False, indent=2).replace(' ', '&nbsp;').replace('\n', '<br>')+'<hr>'

    def koosta_vastus_html(self, formaat:str)->None:
        """Private: Esita otsingu JSON-tulemus märgendatud tekstina HTML-kujul

        Args:
            formaat (str): päringu tulemuse esitusviis {"html"|"html+details"|"json"}
        

        Returns:
            _type_: otsingu JSON-tulemus märgendatud tekstina HTML-kujul
        """      
        if len(self.result_json) <= 0:
            self.content += 'Päringule vastavaid dokumente ei leidunud!'
        else:
            for dokid in self.result_json:
                links = self.result_json[dokid]
                link_prev = {"end":0}
                for idx, start in enumerate(links):
                    link = links[start]
                    if idx == 0:
                        self.content += f'<h2>DocID: {dokid}</h2>'
                    self.content += self.idx_json["sources"][dokid]["content"][link_prev["end"]:start]
                    link_prev = link
                    #content += f' <b>{self.idx_json["sources"][dokid]["content"][start:link["end"]]}</b>'
                    self.content += f' <mark><b>{self.idx_json["sources"][dokid]["content"][start:link["end"]]}</b></mark>'
                    if formaat == 'text_details':
                        self.content += f'<i>[{", ".join(link["tokens"])}]</i>'
                self.content += self.idx_json["sources"][dokid]["content"][link_prev["end"]:] + '<hr>'

        self.content = self.content.replace('\n', '<br>')

    
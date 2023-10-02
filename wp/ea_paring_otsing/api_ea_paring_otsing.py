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

    def otsing(self, fragments:bool, query_str:str, query_json:Dict)->None:
        """Public: Otsing: päringus ja indeksis sõnavormid

        Args:
            fragments (bool): 
            * True: vaatame liitsõna osasõnasid, 
            * False: ei vaata liitsõna osasõnasid

            query_json (Dict): päring (vastava veebiteenusega lemmade 
            kombinatsiooniks teisendatud otsisõned)
        """
        self.fragments = fragments      # kas otsime liitsõna osasõndest
        self.query_str = query_str      # jokksev päringustring
        self.query_json = query_json    # jooksev päringujson
        self.result_json = {}           # otsingutulemus

        self.otsing_rec(0, [])        # rekursiivne otsing, tulemus self.result_json
        for docid in self.result_json:
            self.result_json[docid] = sorted(self.result_json[docid].items())

        # otsingutulemuste korrastamine
        #for docid in self.result_json:  #järjestame otsingutulemused iga dokumendi siseselt
        #    self.result_json[docid] = OrderedDict(sorted(self.result_json[docid].items(), key=lambda t: t[0]))

    def otsing_rec(self, query_idx:int, required_docids:List[str])->bool:
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

        docids_list, res_dct = self.leia_indeksist(query_idx, required_docids)
        if len(docids_list) < 1:
            return False # mitte ükski dokument ei sobinud
        
        if query_idx+1 >= len(self.query_json["annotations"]["query"]):
            self.result_json = res_dct  # Lisame viimase märksõnaga seotud info
            return True                 # Otsing andis tulemusi
        
        if self.otsing_rec(query_idx+1, docids_list) is False:
            return False
        
        for docid in res_dct:
            if docid in self.result_json:
                self.result_json[docid].update(res_dct[docid])

        return True                                                       # anname teada, kas leidsime midagi sobivat

    def leia_indeksist(self, query_idx:int, required_docids:List[str])->Tuple[List[str], Dict]:
        where_tingimus = 'lemma in ("' + '","'.join(self.query_json["annotations"]["query"][query_idx]) + '")'
        if self.fragments is False:
            where_tingimus += f' AND "liitsona_osa" = 0'
        if len(required_docids) > 0:
            where_tingimus += ' AND docid in ("' + '","'.join(required_docids) + '")'

        res_exec = self.cur_index.execute(f'''
            SELECT
                indeks.docid,
                indeks.start,
                indeks.end,                
                lemma_korpuse_vormid.vorm,
                lemma_korpuse_vormid.lemma,
                indeks.liitsona_osa
            FROM lemma_korpuse_vormid
            INNER JOIN indeks ON lemma_korpuse_vormid.vorm = indeks.vorm
            WHERE {where_tingimus}''')
        res_list = res_exec.fetchall()
        #           0      1      2    3     4      5             
        # res_list[(docid, start, end, vorm, lemma, liitsona_osa)]
        #  res_dct = { DOCID: { START: { "end":int, "features":[{"vorm":str, "lemma":str, liitsona_osa:int }]}}
        res_dct = {}
        docids_list = []
        for list_item in res_list:
            if list_item[0] not in docids_list:
                docids_list.append(list_item[0])
            if list_item[0] not in res_dct:  # docid
                res_dct[list_item[0]] = {}
            if list_item[1] not in res_dct[list_item[0]]: # start
                res_dct[list_item[0]][list_item[1]] = {"end":list_item[2], "features":[]}
            item = (list_item[3], list_item[4],list_item[5])
            if item not in res_dct[list_item[0]][list_item[1]]["features"]:
                res_dct[list_item[0]][list_item[1]]["features"].append(item)
        return docids_list, res_dct        



    def koosta_vastus(self, formaat:str, norm_paring:bool)->None:
        """Public: Otsingutulemus moel või teisel HTML-kujule

        Args:
            formaat (str): päringu tulemuse esitusviis {html|html+details|json}

        Returns:
            str: Soovitud kujul otsingutulemus
        """
        self.content = '<hr><h2>Päring:</h2>'
        if norm_paring is True:
            self.content += json.dumps(self.query_json, ensure_ascii=False, indent=2).replace(' ', '&nbsp;').replace('\n', '<br>')+'<hr>'
        else:
            self.content += f'{self.query_str}<hr><hr>'
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
            #  res_dct = { DOCID: { START: { "end":int, "features":[{"vorm":str, "lemma":str, liitsona_osa:int }]}}
            for docid in self.result_json:
                # võtame andmebaasist teksti
                source_content = self.cur_index.execute(
                        f'''SELECT content FROM allikad
                            WHERE docid = "{docid}"''').fetchall()[0][0]
                self.content += f'<h2>DocID: {docid}</h2>'
                prev_end = 0
                for inf in self.result_json[docid]: # (START, { "end":int, [{"vorm":str, "lemma":str, liitsona_osa:int }] })
                    self.content += source_content[prev_end:inf[0]] # eelmise lõpust jooksva alguseni
                    self.content += f' <mark><b>{source_content[inf[0]:inf[1]["end"]]}</b></mark>'
                    #if formaat == 'text_details':
                    #    self.content += f'<i>[{", ".join(link["tokens"])}]</i>'
                    prev_end = inf[1]["end"]
                self.content += f'{source_content[prev_end:]}<hr>'
        self.content = self.content.replace('\n', '<br>')

    
import os
import json
import sqlite3
import logging

from tqdm import tqdm
from typing import List, Union


class DatabaseUpdater:
    """
    Ühendub olemasoleva päringulaiendaja andmebaasiga ning uuendab seda.
    Kui andmebaas on tühi, siis lisab sinna vastavad tabelid.
    Muidu täiendab olemasolevaid tabeleid.
    """

    def __init__(self, db_name: str, tables: List[str], verbose: bool, append: bool = False) -> None:
        self.verbose = verbose
        self.db_name = db_name
        self.tables = tables

        if not append and os.path.isfile(self.db_name):
            logging.debug(f"Kustutame andmebaasi {self.db_name}")
            os.remove(self.db_name)

        logging.debug(f"Teeme/avame andmebaasi {self.db_name}")

        # Loome/avame andmebaasi
        self.con_base = sqlite3.connect(self.db_name)
        self.cur_base = self.con_base.cursor()

        # "indeks_vormid":[(VORM, DOCID, START, END, LIITSÕNA_OSA)]
        self.cur_base.execute('''CREATE TABLE IF NOT EXISTS indeks_vormid(
                vorm  TEXT NOT NULL,          -- (jooksvas) dokumendis esinenud sõnavorm
                docid TEXT NOT NULL,          -- dokumendi id
                start INT,                    -- vormi alguspositsioon tekstis
                end INT,                      -- vormi lõpupositsioon tekstis
                liitsona_osa INT,             -- 0: pole liitsõna osa; 1: on liitsõna osa
                PRIMARY KEY(vorm, docid, start, end)
                )
        ''')

        # "indeks_lemmad":[(LEMMA, DOCID, START, END, LIITSÕNA_OSA)]
        self.cur_base.execute('''CREATE TABLE IF NOT EXISTS indeks_lemmad(
                lemma  TEXT NOT NULL,         -- (jooksvas) dokumendis esinenud sõna lemma
                docid TEXT NOT NULL,          -- dokumendi id
                start INT,                    -- lemmale vastava vormi alguspositsioon tekstis
                end INT,                      -- lemmale vastava vormi lõpupositsioon tekstis
                liitsona_osa INT,             -- 0: pole liitsõna osa; 1: on liitsõna osa
                PRIMARY KEY(lemma, docid, start, end)
                )
        ''')

        # "liitsõnad":[(OSALEMMA, LIITLEMMA)]
        self.cur_base.execute('''CREATE TABLE IF NOT EXISTS liitsõnad(
            osalemma TEXT NOT NULL,     -- liitsõna osasõna lemma
            liitlemma TEXT NOT NULL,    -- liitsõna osasõna lemmat sisaldav liitsõna lemma
            PRIMARY KEY(osalemma, liitlemma)
        )''')

        # "lemma_kõik_vormid":[(VORM, KAAL, LEMMA)],
        self.cur_base.execute('''CREATE TABLE IF NOT EXISTS lemma_kõik_vormid(
            vorm TEXT NOT NULL,         -- lemma kõikvõimalikud vormid genereerijast
            kaal INT NOT NULL,          -- suurem number on sagedasem
            lemma TEXT NOT NULL,        -- korpuses esinenud sõnavormi lemma
            PRIMARY KEY(vorm, lemma)
        )''')

        # "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)]
        self.cur_base.execute('''CREATE TABLE IF NOT EXISTS lemma_korpuse_vormid(
            lemma TEXT NOT NULL,        -- dokumendis esinenud sõnavormi lemma
            kaal INT NOT NULL,          -- suurem number on sagedasem
            vorm TEXT NOT NULL,         -- lemma need sõnavormid, mis on mingis dokumendis dokumendis esinenud
            PRIMARY KEY(lemma, vorm)
        )''')

        # {"tabelid":{ "kirjavead":[[VIGANE_VORM, VORM, KAAL]] }
        self.cur_base.execute('''CREATE TABLE IF NOT EXISTS kirjavead(
            vigane_vorm TEXT NOT NULL,  -- sõnavormi vigane versioon
            vorm TEXT NOT NULL,         -- korpuses esinenud sõnavorm
            kaal REAL,                  -- kaal vahemikus [0.0,1.0]
            PRIMARY KEY(vigane_vorm, vorm)
        )''')

        # ["tabelid"]["allikad"]:[(DOCID, CONTENT)]
        self.cur_base.execute('''CREATE TABLE IF NOT EXISTS allikad(
                docid TEXT NOT NULL,        -- dokumendi id
                content TEXT NOT NULL,      -- dokumendi text
                PRIMARY KEY(docid)
                )
        ''')

    def __del__(self) -> None:
        if self.con_base is not None:
            self.con_base.close()
            logging.debug(f"Suletud andmebaas {self.db_name}")

    def import_index_file(self, index_file: str) -> None:
        """
        Kannab indeksfaili sisu SQLight andmebaasi tabelitesse.
        Indeksfail iga rida peab olema valiidne JSON-objekt kujul:
        {"tabelid": {<table_name>: [[<table_row>], ..., <table_row>]}}.
        Täpsem formaadi kirjeldus on antud advanced_indexing veebiteenuse koodis.

        Vea korral jääb andmebaas mittekooskõlalisse seisu ja visatakse ValueError erindi.
        TODO: Vea korral võiks kogu faili lisamise tagasi rullida.
        """

        with open(index_file) as f:
            try:
                for line in f:
                    json_record = json.loads(line.replace('\n', ' '))
                    for table in self.tables:
                        content = tqdm(json_record["tabelid"][table], desc=f'# {table: <25}',
                                       disable=(not self.verbose))
                        # Mingil põhjusel on kaks tabelit eri järjekorras olevate veergudega
                        # TODO: Ühildada tabeli veergude järjekord
                        if table == "lemma_kõik_vormid":
                            self.import_wordform_lemma_table(table, content)
                        elif table == "lemma_korpuse_vormid":
                            self.import_lemma_wordform_table(table, content)
                        else:
                            self.import_standard_table(table, content)
                    self.con_base.commit()
            except Exception:
                raise ValueError(f'Faili {index_file} lisamine ebaõnnestus. Andmebaas on mittekooskõlaline')

    def import_source_file(self, csv_file: str, id_col: str, text_col: str) -> None:
        """
        Kannab csv-failis oleva algteksti koos identifikaatoriga SQLight andmebaasi tabelitesse.
        Csv-failis peavad olema vastavad veerud

        Vea korral jääb andmebaas mittekooskõlalisse seisu ja visatakse ValueError erindi.
        TODO: Vea korral võiks kogu faili lisamise tagasi rullida.
        """

        from pandas import read_csv
        table = read_csv(csv_file)
        if id_col not in table.columns:
            raise ValueError(f"Failis {csv_file} puudub veerg {id_col}")
        if text_col not in table.columns:
            raise ValueError(f"Failis {csv_file} puudub veerg {text_col}")

        table_name = 'allikad'
        for _, (text_id, text) in table[[id_col, text_col]].iterrows():
            self.cur_base.execute(f"INSERT INTO {table_name} VALUES {(text_id, text)}")
        self.con_base.commit()

    def import_wordform_lemma_table(self, table_name: str, row_list: Union[list, tqdm]):
        """
        Ootab sisendiks tabelit kujul [(VORM, KAAL, LEMMA)].
        Ootamatuste korral viskab ValueError erindi ja jätab konkreetse rea lisamata.
        Transaktsiooni ei kommitita, seda tuleb eraldi teha.
        """
        for vorm, kaal, lemma in row_list:
            result = self.cur_base.execute(f"SELECT kaal FROM {table_name} WHERE vorm='{vorm}' and lemma='{lemma}'")
            result = result.fetchall()

            if len(result) == 0:
                # polnud, lisame uue
                rec = (vorm, kaal, lemma)
                self.cur_base.execute(f"INSERT INTO {table_name} VALUES {rec}")
            elif len(result) == 1:
                # selline juba oli, liidame kokku
                kaal += result[0][0]
                self.cur_base.execute(f"UPDATE {table_name} SET kaal='{kaal}' WHERE vorm='{vorm}' and lemma='{lemma}'")
            else:
                raise ValueError(f"Viga tabelis {table_name}: mitu rida vorm='{vorm}' and lemma='{lemma}'")

    def import_lemma_wordform_table(self, table_name: str, row_list: Union[list, tqdm]):
        """
        Ootab sisendiks tabelit kujul [(LEMMA, KAAL, VORM)].
        Ootamatuste korral viskab ValueError erindi ja jätab konkreetse rea lisamata.
        Transaktsiooni ei kommitita, seda tuleb eraldi teha.
        """
        for lemma, kaal, vorm in row_list:
            result = self.cur_base.execute(f"SELECT kaal FROM {table_name} WHERE vorm='{vorm}' and lemma='{lemma}'")
            result = result.fetchall()

            if len(result) == 0:
                # polnud, lisame uue
                rec = (lemma, kaal, vorm)
                self.cur_base.execute(f"INSERT INTO {table_name} VALUES {rec}")
            elif len(result) == 1:
                # selline juba oli, liidame kokku
                kaal += result[0][0]
                self.cur_base.execute(f"UPDATE {table_name} SET kaal='{kaal}' WHERE vorm='{vorm}' and lemma='{lemma}'")
            else:
                raise ValueError(f"Viga tabelis {table_name}: mitu rida vorm='{vorm}' and lemma='{lemma}'")

    def import_standard_table(self, table_name: str, row_list: Union[list, tqdm]):
        """
        Ootab sisendiks õige veergude arvuga tabelit. Kuid ei kontrolli selle õigsust.
        Kui tabelis on juba vastav rida, siis seda enam ei lisa ega uuenda.
        Transaktsiooni ei kommitita, seda tuleb eraldi teha.
        """
        for rec in row_list:
            try:
                self.cur_base.execute(f"INSERT INTO {table_name} VALUES {tuple(rec)}")
            except sqlite3.IntegrityError:
                pass

    @property
    def wordforms_without_misspellings(self) -> List[str]:
        """
        Annab välja sõnavormid millele pole veel kirjavigadega vorme leitud.
        """
        result = self.cur_base.execute(
            """
            SELECT vorm 
            FROM lemma_korpuse_vormid 
            WHERE vorm not in (SELECT DISTINCT vorm FROM kirjavead)
            """)
        return list(row[0] for row in result.fetchall())

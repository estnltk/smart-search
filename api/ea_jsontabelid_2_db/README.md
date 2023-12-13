# JSON-andmefailide kokkuliitmine ja SQLITE-andmebaasi tegemine

Seda, kuidas teha JSON-failid ja need andmebaasiks kokkuliita demonstreerib programm:
https://github.com/estnltk/smart-search/blob/main/api/ea_jsoncontent_2_jsontabelid/Makefile

## Tabelid andmebaasis

Andmebaasi ei peal lisama kõiki tabeleid, soovitud tabelid saab anda programmi parameetri kaudu käsurealt.
Osade tabelite tegemisel kasutatakse teisi juba varem tehtud tabeleid.

```sgl
indeks_vormid(
    vorm  TEXT NOT NULL,        -- (jooksvas) dokumendis esinenud sõnavorm
    docid TEXT NOT NULL,        -- dokumendi id
    start INT,                  -- vormi alguspositsioon tekstis
    end INT,                    -- vormi lõpupositsioon tekstis
    liitsona_osa,               -- 0: pole liitsõna osa; 1: on liitsõna osa
    PRIMARY KEY(vorm, docid, start, end))

indeks_lemmad(
    lemma  TEXT NOT NULL,       -- (jooksvas) dokumendis esinenud sõna lemma
    docid TEXT NOT NULL,        -- dokumendi id
    start INT,                  -- lemmale vastava vormi alguspositsioon tekstis
    end INT,                    -- lemmale vastava vormi lõpupositsioon tekstis
    liitsona_osa,               -- 0: pole liitsõna osa; 1: on liitsõna osa
    PRIMARY KEY(lemma, docid, start, end))

liitsõnad( 
    osalemma TEXT NOT NULL,     -- liitsõna osasõna lemma
    liitlemma TEXT NOT NULL,    -- liitsõna osasõna lemmat sisaldav liitsõna lemma
    PRIMARY KEY(osalemma, liitlemma))

lemma_kõik_vormid( 
        vorm TEXT NOT NULL,     -- lemma kõikvõimalikud vormid genereerijast
        kaal INT NOT NULL,      -- suurem number on sagedasem
        lemma TEXT NOT NULL,    -- korpuses esinenud sõnavormi lemma
        PRIMARY KEY(vorm, lemma))

lemma_korpuse_vormid(
    lemma TEXT NOT NULL,        -- dokumendis esinenud sõnavormi lemma
    kaal INT NOT NULL,          -- suurem number on sagedasem
    vorm TEXT NOT NULL,         -- lemma need sõnavormid, mis on mingis dokumendis dokumendis esinenud
    PRIMARY KEY(lemma, vorm))

kirjavead(
    vigane_vorm TEXT NOT NULL,  -- sõnavormi vigane versioon
    vorm TEXT NOT NULL,         -- korpuses esinenud sõnavorm
    PRIMARY KEY(vigane_vorm, vorm))

allikad(
    docid TEXT NOT NULL,        -- dokumendi id
    content TEXT NOT NULL,      -- dokumendi text
    PRIMARY KEY(docid))

```

## Kasutusnäited

https://github.com/estnltk/smart-search/blob/main/api/ea_jsontabelid_2_db/api_jsontabelid_2_db.py
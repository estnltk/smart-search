# CSV-kujul pealkirjafailidest päringulaiendaja ja otsimootori tööks vajaliku andmebaasi tegemine

## Eeldused

Operatsioonisüsteem Ubuntu 22.04 LTS (või muu kompileeritud C++ programmide mõttes ühilduv operatsioonisüsteem).

Tarkvara on GITHUBist allalaaditud

```cmdline
mkdir -p ~/git/ ; cd ~/git/
git clone git@github.com:estnltk/smart-search.git smart_search_github
```

Kui tarkvara on tõmmatud teise kataloogi või CVS-kujul pealkirjafailid on teises kataloogis tuleb skriptis kirjutada õiged rajad järgmistesse keskkonnamuutujatesse:

* `DIR_PREF` GITHUBist allalaaditud repo juurkataloog (vaikimisi `~/git/smart_search_github`)
* `DIR_HEADINGS` CSV kujul pealkirjafailide kataloog (vaikimisi `${DIR_PREF}/demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts`)
* `DIR_INDEXING` skripti `api_advanced_indexing.py` kataloog (vaikimisi `${DIR_PREF}/api/api_advanced_indexing`)
* `DIR_MISPGEN`  skripti `api_misspellings_generator.py` kataloog (vaikimisi `${DIR_PREF}/api/api_misspellings_generator`)
* `DIR_QUERYEXT` skripti `query_extender_setup.py` kataloog (vaikimisi `${DIR_PREF}/scripts/query_extender_setup/example_make_based_workflow`)
* `DIR_IGNOWFORMS` ignoreeritavate sõnavormide loendit `ignore.json` sisaldav kataloog (vaikimisi `${DIR_PREF}/demod/toovood/riigi_teataja_pealkirjaotsing/01_dokumentide_indekseerimine/inputs`)
* `DIR_WFORMS2ADD` täiendavate sõnavormide genereerimise aluseks olev JSON-faili `lisavormide_tabelid.json` sisaldav kataloog (vaikimisi `${DIR_PREF}/demod/toovood/riigi_teataja_pealkirjaotsing/01_dokumentide_indekseerimine/inputs`)

Luua pythoni skriptide tööks vajalikud virtuaalkeskkonnad (täita pythoni skriptide lähetkoodi sisaldavates kataloogides ```./create_venv.sh``` käsk).
Vaata lähemalt:

* [Pythoni skripti kasutamine: api_advanced_indexing.py](https://github.com/estnltk/smart-search/blob/main/api/api_advanced_indexing/README.md)
* [Pythoni skripti kasutamine: api_misspellings_generator.py](https://github.com/estnltk/smart-search/blob/main/api/api_misspellings_generator/README.md)
* [Pythoni skripti kasutamine: query_extender_setup.py](https://github.com/estnltk/smart-search/blob/main/scripts/query_extender_setup/example_script_based_workflow/README.md)

Töötleb kõik kataloogis ```~/git/smart-search_github/demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts``` olevad pealkirjafailid (`.csv` laiendiga failid)

## Käivitamine

```cmdline
cd ~/git/smart_search_github/scripts/query_extender_setup/example_script_based_workflow 
./pealkirjad_andmebaasi_py.sh
```

## Tulemus

Kataloogi ```~/git/smart-search_github/scripts/query_extender_setup/example_script_based_workflow``` luuakse SQLITE-andmebaas ```koond.sqlite```

Andmebaasi tegemisel saab valida, millised allkirjeldatud tabelitest andmbebaasi lisatakse.
Kui andmbeaas on juba varem tehtud, siis saab valida, milliseid tabeleid täiendatakse uue infoga.

### Tabelid

#### Dokumentides esinenud lemmade kõikvõimalikud vormid

```text
lemma_kõik_vormid( 
    lemma TEXT NOT NULL,        -- dokumentides esinenud lemma (algvorm)
    kaal INT NOT NULL,          -- suurem number on sagedasem
    vorm TEXT NOT NULL,         -- lemma kõikvõimalikud vormid genereerijast
    PRIMARY KEY(lemma, vorm))
```

#### Dokumentides esinenud lemmade korpuses esinenud vormid

```text
lemma_korpuse_vormid(
    lemma TEXT NOT NULL,        -- dokumentides esinenud sõnavormi lemma
    kaal INT NOT NULL,          -- suurem number on sagedasem            
    vorm TEXT NOT NULL,         -- lemma need sõnavormid, mis on mingis dokumendis esinenud
    PRIMARY KEY(vorm, lemma))
```

#### Korpuses esinenud liitsõnade osasõnad

```text
liitsõnad( 
    osalemma TEXT NOT NULL,     -- liitsõna osasõna lemma
    liitlemma TEXT NOT NULL,    -- osalemmat sisaldava liitsõna lemma
    PRIMARY KEY(osalemma, liitlemma))
```

#### Sõnavormid, mida päringus ignoreerida

Muuhulgas võiks sinna lisada (sagedasemate) side- ja asesõnade kõik vormid.

```text
ignoreeritavad_vormid(
    ignoreeritav_vorm  TEXT NOT NULL, -- päringus ignoreerime neid sõnavorme
    PRIMARY KEY(ignoreeritav_vorm))
```

#### Sagedasemate kirjavigade parandamiseks vajalik informatsioon

```text
kirjavead(
    vigane_vorm TEXT NOT NULL,  -- sõnavormi vigane versioon
    vorm TEXT NOT NULL,         -- dokumentides esinenud sõnavorm
    kaal REAL,                  -- kaal vahemikus [0.0,1.0]
    PRIMARY KEY(vigane_vorm, vorm))
```

#### Dokumentides esinenud sõnavormide indeks

```text
indeks_vormid(
    vorm  TEXT NOT NULL,          -- dokumentides esinenud sõnavorm
    docid TEXT NOT NULL,          -- dokumendi id
    start INT,                    -- vormi alguspositsioon tekstis
    end INT,                      -- vormi lõpupositsioon tekstis
    liitsona_osa INT,             -- 0: pole liitsõna osa; 1: on liitsõna osa
    PRIMARY KEY(vorm, docid, start, end))
```

#### Dokumentides esinenud lemmade (algvormide) indeks

```text
indeks_lemmad(
    lemma  TEXT NOT NULL,         -- dokumentides esinenud sõna lemma
    docid TEXT NOT NULL,          -- dokumendi id
    start INT,                    -- lemmale vastava vormi alguspositsioon tekstis
    end INT,                      -- lemmale vastava vormi lõpupositsioon tekstis
    liitsona_osa INT,             -- 0: pole liitsõna osa; 1: on liitsõna osa
    PRIMARY KEY(lemma, docid, start, end))
```

#### Dokumentide tekst

Lemmade ja sõnavormide indeksis viidatakse selle tabeli 'docid'idele ja nihked on arvutatud
'content'is olevast tekstist lähtudes.

```text
allikad(
    docid TEXT NOT NULL,        -- dokumendi id
    content TEXT NOT NULL,      -- dokumendi text
    PRIMARY KEY(docid)
    )
```

#### Tabelite täiendamise logi

```text
 uuendatud(
    uuendamise_aeg TEXT NOT NULL,   -- tabeli(te) uuendamise aasta.kuu.päev
    tabelid TEXT NOT NULL,          -- uuendatatud tabelite loend
    PRIMARY KEY(uuendamise_aeg, tabelid))
```

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

'''
lemma_kõik_vormid( 
            lemma TEXT NOT NULL,        -- korpuses esinenud sõnavormi lemma
            kaal INT NOT NULL,          -- suurem number on sagedasem
            vorm TEXT NOT NULL,         -- lemma kõikvõimalikud vormid genereerijast
            PRIMARY KEY(lemma, vorm))
'''

'''
lemma_korpuse_vormid(
            lemma TEXT NOT NULL,        -- dokumendis esinenud sõnavormi lemma
            kaal INT NOT NULL,          -- suurem number on sagedasem            
            vorm TEXT NOT NULL,         -- lemma need sõnavormid, mis on mingis dokumendis dokumendis esinenud
            PRIMARY KEY(vorm, lemma))
'''

'''
liitsõnad( 
            osalemma TEXT NOT NULL,     -- liitsõna osasõna lemma
            liitlemma TEXT NOT NULL,    -- liitsõna osasõna lemmat sisaldav liitsõna lemma
            PRIMARY KEY(osalemma, liitlemma))
'''

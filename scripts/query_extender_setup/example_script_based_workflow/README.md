# CSV-kujul pealkirjafailidest päringulaiendaja ja otsimootori tööks vajaliku andmebaasi tegemine

## Eeldused

Operatsioonisüsteem Ubuntu 22.04 LTS (või muu kompileeritud C++ programmide mõttes ühilduv operatsioonisüsteem).

Tarkvara on GITHUBist allalaaditud

```cmdline
mkdir -p ~/git/ ; cd ~/git/
git clone git@github.com:estnltk/smart-search.git smart_search_github
```

Kui tarkvara on tõmmatud teise kataloogi või CVS-kujul pealkirjafailid on teises kataloogis tuleb skriptis kirjutada õiged rajad järgmistesse keskkonnamuutujatesse:

* ```DIR_HEADINGS``` CSV kujul pealkirjafailide asukoht
* ```DIR_INDEXING``` skripti ```api_advanced_indexing.py``` asukoht
* ```DIR_MISPGEN```  skripti ```api_misspellings_generator.py``` asukoht
* ```DIR_QUERYEXT``` skripti ```query_extender_setup.py``` asukoht

Luua pythoni skriptide tööks vajalikud virtuaalkeskkonnad (täita pythoni skriptide lähetkoodi sisaldavates kataloogides ```./create_venv.sh``` käsk).
Vaata lähemalt:

* [Pythoni skripti kasutamine: api_advanced_indexing.py](https://github.com/estnltk/smart-search/blob/main/api/api_advanced_indexing/README.md)
* [Pythoni skripti kasutamine: api_misspellings_generator.py](https://github.com/estnltk/smart-search/blob/main/api/api_misspellings_generator/README.md)
* [Pythoni skripti kasutamine: query_extender_setup.py](https://github.com/estnltk/smart-search/blob/main/scripts/query_extender_setup/example_script_based_workflow/README.md)

Töötleb kõik kataloogis ```~/git/smart-search_github/demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts``` olevad pealkirjafailid

## Käivitamine

```cmdline
cd ~/git/smart_search_github/scripts/query_extender_setup/example_script_based_workflow 
./pealkirjad_andmebaasi_py.sh
```

## Tulemus

Kataloogi ```~/git/smart-search_github/scripts/query_extender_setup/example_script_based_workflow``` luuakse SQLITE-andmebaas ```koond.sqlite```

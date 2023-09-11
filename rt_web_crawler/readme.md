# Virtuaalkeskondade loomine ja kasutamine

## CONDA

### Keskkonna loomine

* ```create_cenv.sh``` Skritp virtuaalkeskkonna loomiseks
* ```requiremts.yml``` Pakettide loend

### Kasutamine

#### Notebook

```cmdline
cd ~/git/smart-search_github/rt_web_crawler
venv/bin/jupyter notebook 01_crawl_document_locations.ipynb
```

#### Pythoni skript

Teeme notebooki pythoni skriptiks

```cmdline
cenv/bin/jupyter nbconvert 01_crawl_document_locations.ipynb --to python
```

Käivitame pythoni skripti:

```cmdline
cenv/bin/python3 01_crawl_document_locations.py
```

## Virtual Environment

### Keskkonna loomine

* ```create_venv.sh``` Skritp virtuaalkeskkonna loomiseks
* ```requiremts.txt``` Pakettide loend

### Kasutamine

#### Notebook

```cmdline
cd ~/git/smart-search_github/rt_web_crawler
cenv/bin/jupyter notebook 01_crawl_document_locations.ipynb
```

#### Pythoni skript

Teeme notebooki pythoni skriptiks

```cmdline
cenv/bin/jupyter nbconvert 01_crawl_document_locations.ipynb --to python
```

Käivitame pythoni skripti:

```cmdline
venv/bin/python3 01_crawl_document_locations.py
```
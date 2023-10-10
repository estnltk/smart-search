

 conda create --name rt-web-crawler python=3.9
 conda activate rt-web-crawler
 conda install jupyter
 conda install lxml
 conda install pandas
 conda install tqdm
 conda install bs4
 conda install -c conda-forge rise

# Virtuaalkeskondade loomine ja kasutamine

## CONDA

### Keskkonna loomine

Failid:

* ```create_cenv.sh``` Skritp virtuaalkeskkonna loomiseks
* ```requiremts.yml``` Pakettide loend

Käsurida:

    ```cmdline
    cd ~/git/smart-search_github/rt_web_crawler
    ./create_cenv.sh
    ```

### Kasutamine

#### Notebook

Käivitame notebook'i noomoodi:

    ```cmdline
    cenv/bin/jupyter notebook 01_crawl_document_locations.ipynb
    ```

või niimoodi:

    ```cmdline
    conda activate ./cenv
    jupyter notebook 01_crawl_document_locations.ipynb
    conda deactivate
    ```

#### Pythoni skript

Teeme notebook'i pythoni skriptiks niimoodi

    ```cmdline
    cenv/bin/jupyter nbconvert 01_crawl_document_locations.ipynb --to python
    ```

või niimoodi

    ```cmdline
    conda activate ./cenv
    jupyter nbconvert 01_crawl_document_locations.ipynb --to python
    conda deactivate
    ```

Käivitame pythoni skripti:

Kas niimoodi:

    ```cmdline
    cenv/bin/python3 01_crawl_document_locations.py
    ```

või niimoodi

    ```cmdline
    conda activate ./cenv
    ./01_crawl_document_locations.py
    conda deactivate
    ```

## Virtual Environment

### Keskkonna loomine

Failid:

* ```create_venv.sh``` Skritp virtuaalkeskkonna loomiseks
* ```requiremts.txt``` Pakettide loend

Käsurida:

    ```cmdline
    cd ~/git/smart-search_github/rt_web_crawler
    ./create_venv.sh
    ```

### Kasutamine

#### Notebook

    ```cmdline
    cenv/bin/jupyter notebook 01_crawl_document_locations.ipynb
    ```

#### Pythoni skript

Teeme notebooki pythoni skriptiks

    ```cmdline
    venv/bin/jupyter nbconvert 01_crawl_document_locations.ipynb --to python
    ```

Käivitame pythoni skripti:

    ```cmdline
    venv/bin/python3 01_crawl_document_locations.py
    ```

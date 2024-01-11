# Andmebaasi kokkupanemiseks vajaliku JSON-kujul info genereerimine CSV-kujul pealkirjadest või JSON-kujul dokumentidest 

## Sisendi formaadid

### CSV

Sellisel kujul on Riigiteataja pealkirju sisaldavad .CSV failid kataloogis ```~/git/smart_search_github/demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts/```.

Veerud on:

* global_id
* document_type
* document
* xml_source

### JSON

Dokumendid on pakitud JSON-formaati:

```json
{   "sources":
    {   DOCID:                  # dokumendi unikaalne ID, string
        {   "content": string   # dokument, JSON-string
        }
    }
    "params": {"tables":[TABEL]}    # väljundisse minevate tabelite loend
                                    # vaikimisi: "indeks_vormid", "indeks_lemmad", "liitsõnad"
                                    # Võib-olla misiganes almhulk alljärgnevatest:
                                    # "indeks_vormid", "indeks_lemmad", "liitsõnad", "lemma_kõik_vormid",
                                    # "kirjavead", "allikad"
}
```

### Väljundi formaat

Parameetri abil saab määrata, mida tabelites kuvatakse

```json
   {   "tabelid":
        {   "indeks_vormid":[(VORM, DOCID, START, END, LIITSÕNA_OSA)],
            "indeks_lemmad":[(LEMMA, DOCID, START, END, KAAL, LIITSÕNA_OSA)],
            "liitsõnad":[(OSALEMMA, LIITLEMMA)],
            "lemma_kõik_vormid":[(LEMMA, KAAL, VORM)],
            "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)],
            "kirjavead":[(VIGANE_VORM, VORM, KAAL)],
            "allikad":[(DOCID, CONTENT)],
        }
    }
```


## Kasutamine

### 1 Lähtekoodist pythoni skripti kasutamine

Lähtekoodi allalaadimine (1.1), virtuaalkeskkonna loomine (1.2) ja käivitamine(1.3)

#### 1.1 Lähtekoodi allalaadimine

```cmdline
mkdir -p ~/git/ ; cd ~/git/
git clone git@github.com:estnltk/smart-search.git smart_search_github
```

#### 1.2 Virtuaalkeskkonna loomine

```cmdline
cd ~/git/smart_search_github/api/api_advanced_indexing/
./create_venv.sh
```

#### 1.3 Käivitamine

Pythoni skripti käsurealt kasutamise näited

```cmdline
cd ~/git/smart_search_github/api/api_advanced_indexing/

venv/bin/python3 ./api_advanced_indexing.py --verbose --csv_input test/test_headers.csv | gron | less

venv/bin/python3 ./api_advanced_indexing.py --verbose test/test_document.json | gron | less

venv/bin/python3 ./api_advanced_indexing.py --verbose --csv_input \
    --tables=indeks_vormid:indeks_lemmad:liitsõnad:lemma_kõik_vormid:lemma_korpuse_vormid:allikad \
    test/kokkuleppega.csv | gron | less 
```

### 2 Lähtekoodist veebiserveri käivitamine & kasutamine

Lähtekoodi allalaadimine (2.1), virtuaalkeskkonna loomine (2.2), veebiteenuse käivitamine pythoni koodist (2.3) ja CURLiga veebiteenuse kasutamise näited (2.4)

#### 2.1 Lähtekoodi allalaadimine

Järgi punkti 1.1

#### 2.2 Virtuaalkeskkonna loomine

Järgi punkti 1.2

#### 2.3 Veebiteenuse käivitamine pythoni koodist

##### 2.3.1 Vaikeseadetaga

```bash
cd ~/git/smart_search_github/api/api_advanced_indexing

./venv/bin/python3 ./flask_api_advanced_indexing.py
```

##### 2.3.2 Etteantud parameetritega

```bash
cd ~/git/smart_search_github/api/api_advanced_indexing

SMART_SEARCH_GENE_TYPOS=false SMART_SEARCH_MAX_CONTENT_LENGTH='5000000' \
    venv/bin/python3 ./flask_api_advanced_indexing.py
```

##### 2.4 CURLiga veebiteenuse kasutamise näited

```bash
cd ~/git/smart_search_github/api/api_advanced_indexing

curl --silent --request POST --header "Content-Type: application/text" \
    localhost:6602/api/advanced_indexing/version | jq

curl --silent --request POST --header "Content-Type: application/csv" \
    --data-binary @test/test_headers.csv \
    localhost:6602/api/advanced_indexing/csv_input  | jq

curl --silent --request POST --header "Content-Type: application/json" \
    --data-binary @test/test_document.json \
    localhost:6602/api/advanced_indexing/json  | jq

curl --silent --request POST --header "Content-Type: application/json" \
    --data '{"params":{"tables":["indeks_lemmad"]}, "sources":{"testdoc_1":{"content":"Presidendi kantselei."}, "testdoc_2":{"content":"Raudteetranspordiga raudteejaamas."}}}' \
    localhost:6602/api/advanced_indexing/json  | gron

curl --silent --request POST --header "Content-Type: application/json" \
    --data '{"sources":{"testdoc_1":{"content":"Presidendi kantselei."}, "testdoc_2":{"content":"Raudteetranspordiga raudteejaamas."}}}' \
    localhost:6602/api/advanced_indexing/json  | gron

curl --silent --request POST --header "Content-Type: application/json" \
    --data '{"params":{"tables":["liitsõnad"]}, "sources":{"testdoc_1":{"content":"allmaaraudtee"}}}' \     
    https://smart-search.tartunlp.ai/api/advanced_indexing/json  | gron
```

### 3 Lähtekoodist tehtud konteineri kasutamine

Lähtekoodi allalaadimine (3.1), konteineri kokkupanemine (3.2), konteineri käivitamine (3.3) ja CURLiga veebiteenuse kasutamise näited  (2.4).

#### 3.1 Lähtekoodi allalaadimine

Järgi punkti 1.1

#### 3.2 Konteineri kokkupanemine

```bash
cd ~/git/smart-search_github/api/api_advanced_indexing \
    && docker build -t tilluteenused/smart_search_api_advanced_indexing:2024.01.10 . 
```

#### 3.3 Konteineri käivitamine

```bash
docker run -p 6602:6602  \
        --env SMART_SEARCH_MAX_CONTENT_LENGTH='500000000' \
        --env SMART_SEARCH_GENE_TYPOS='false' \
        tilluteenused/smart_search_api_advanced_indexing:2024.01.10
```

#### 3.4 CURLi abil veebiteenuse kasutamise näited

Järgi punkti 1.4

### 4 DockerHUBist tõmmatud konteineri kasutamine

DockerHUBist koneineri tõmbamine (4.1), konteineri käivitamine (4.2) ja CURLiga veebiteenuse kasutamise näited (4.3)

#### 4.1 DockerHUBist konteineri tõmbamine

```bash
docker pull tilluteenused/smart_search_api_advanced_indexing:2024.01.10
```

#### 4.2 Konteineri käivitamine

Järgi punkti 3.3

#### 4.3 CURLiga veebiteenuse kasutamise näited

Järgi punkti 1.4

### 5 TÜ KUBERNETESes töötava konteineri kasutamine

CURLi abil veebiteenuse kasutamise näited

```bash
cd ~/git/smart_search_github/api/api_advanced_indexing # selles kataloogis on test_headers.csv ja test_document.json

curl --silent --request POST --header "Content-Type: application/text" \
    https://smart-search.tartunlp.ai/api/advanced_indexing/version | jq

curl --silent --request POST --header "Content-Type: application/csv" \
    --data-binary @test/test_headers.csv \
    https://smart-search.tartunlp.ai/api/advanced_indexing/csv_input  | jq

curl --silent --request POST --header "Content-Type: application/json" \
    --data-binary @test/test_document.json \
    https://smart-search.tartunlp.ai/api/advanced_indexing/json  | jq

curl --silent --request POST --header "Content-Type: application/json" \
    --data '{"params":{"tables":["indeks_lemmad"]}, "sources":{"testdoc_1":{"content":"Presidendi kantselei."}, "testdoc_2":{"content":"Raudteetranspordiga raudteejaamas."}}}' \
    https://smart-search.tartunlp.ai/api/advanced_indexing/json  | gron

curl --silent --request POST --header "Content-Type: application/json" \
    --data '{"sources":{"testdoc_1":{"content":"Presidendi kantselei."}, "testdoc_2":{"content":"Raudteetranspordiga raudteejaamas."}}}' \
    https://smart-search.tartunlp.ai/api/advanced_indexing/json  | gron

curl --silent --request POST --header "Content-Type: application/json" \
      --data '{"sources":{"testdoc_1":{"content":"Presidendi kantselei."}, "testdoc_2":{"content":"Raudteetranspordiga raudteejaamas."}}}' \
      https://smart-search.tartunlp.ai/api/advanced_indexing/json  | jq

curl --silent --request POST --header "Content-Type: application/json" \
    --data-binary @test/test_document.json \
    https://smart-search.tartunlp.ai/api/advanced_indexing/json  | gron
      
```

### 6 DockerHubis oleva konteineri lisamine oma KUBERNETESesse

Vaikeväärtustega ```deployment```-konfiguratsioonifaili loomine

```bash
kubectl create deployment smart-search-api-advanced-indexing \
  --image=tilluteenused/smart_search_api_advanced_indexing:2024.01.10
```

Vajadusel lisage konfifaili sobilike väärtustega keskkonnamuutujad

```yml
    - name: SMART_SEARCH_GENE_TYPOS
      value: "TRUE"
    - name: MART_SEARCH_MAX_CONTENT_LENGTH
      value: "100000"

```

Vaikeväärtustega ```service```-konfiguratsioonifaili loomine

```bash
kubectl expose deployment smart-search-api-advanced-indexing \
  --type=ClusterIP --port=80 --target-port=6602
```

Redigeeriga vastavat ```ingress```-konfiguratsioonifaili

```bash
kubectl edit ingress smart-search-api-ingress
```

Lisage sinna

```yml
- backend:
    service:
    name: smart-search-api-advanced-indexing
    port:
        number: 80
path: /api/advanced_indexing/?(.*)
pathType: Prefix
```

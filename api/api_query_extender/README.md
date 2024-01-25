# Päringu normaliseerija

## Sisendi JSON-kuju

```json
{       "content": SISENDÕNEDE_STRING,  // tükeldataks 'white space'ide kohalt, sõne ei saa sisaldada tühikut
        "params":                       // võib puududa, vaikimisi FALSE
        {       "otsi_liitsõnadest":"TRUE"
        }
}
```

```json
{       "tss": SISENDÕNEDE_STRING,      // tükeldataks tabulatsiooni sõmbolite kohalt, sõne võib sisaldada tühikut
        "params": {"otsi_liitsõnadest": "false" } // võib puududa, vaikimisi FALSE
}
```

## Väljundi kuju

### Kui päringus oli ```/api/query_extender/process```

```json
{       "content": SISENDÕNEDE_STRING,  // kui sisendis oli "content"
        "tss": SISENDÕNEDE_STRING,      // kui sisendis oli "tss"
        "params": {"otsi_liitsõnadest": "false" }, // võib puududa, vaikimisi FALSE
        "annotations": 
        {       "query": [[LEMMA]],  
                "ignore": [IGNORE_WORDWORM],
                "not indexed": [NOT_INDEXED_LEMMA],
                "typos": 
                {       TYPO: 
                        {       "suggestions":[SUGGESTION]
                        }
                }
        }
}
```

### Kui päringus oli ```/api/query_extender/json```

```json
{       INPUT:  // sisendsõne
        {       LEMMA:  // sisendsõne lemma
                {       WORDFORM:       // sõnavorm korpusest otsimiseks
                        {       "type": suggestion|speller_suggestion|word|compound|ignore,
                                "confidence": int
                        }
                }
        }
} 
```
### Kui päringus oli ```/api/query_extender/tsv```

Väljundiks on TSV-kujul tabel, selliste veergudega:

* location -- sõne järjekorra number päringus
* input -- päringusõne
* lemma -- päringusõne lemma
* type -- üks alljärgnevatest: suggestion, speller_suggestion, word, compound, ignore
* confidence -- ```wordform```-i esinemiste arv korpuses
* wordform -- sõne korpusest otsimiseks

## Kasutamine

### 1 Lähtekoodist pythoni veebiserveri kasutamine

#### 1.1 Lähtekoodi allalaadimine

```bash
mkdir -p ~/git/ ; cd ~/git/
git clone git@github.com:estnltk/smart-search.git smart_search_github
```

#### 1.2 Virtuaalkeskkonna loomine

```bash
cd ~/git/smart_search_github/api/api_query_extender && ./create_venv.sh
```

#### 1.3 Veebiserveri käivitamine pythoni koodist

```bash
cd  ~/git/smart_search_github/api/api_query_extender
cp ../../demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts/koond.sqlite ./smart_search.sqlite
SMART_SEARCH_QE_DBASE="./smart_search.sqlite" \
        venv/bin/python3 ./flask_api_query_extender.py
```

#### 1.4 CURLiga veebiteenuse kasutamise näited

```bash
curl --silent --request POST --header "Content-Type: application/json" \
        --data "{\"tss\":\"Strasbourg'i\\tStrasbourg'iga\\tpresidendi\\tpresident\\tpresidendiga\"}" \
        localhost:6604/api/query_extender/wordform_check | jq

curl --silent --request POST \
        --header "Content-Type: application/json" \
        --data "{\"tss\":\"presitendi\\tpresidendiga\", \"params\":{\"otsi_liitsõnadest\":\"false\"}}" \
        localhost:6604/api/query_extender/tsv
        
curl --silent --request POST \
        --header "Content-Type: application/json" \
        --data "{\"tss\":\"presitendigas\"}" \
        localhost:6604/api/query_extender/tsv
        
curl --silent --request POST --header "Content-Type: application/json" \
        --data "{\"content\":\"presitendi\\tpresidendiga\", \"params\":{\"otsi_liitsõnadest\":\"false\"}}" \
        localhost:6604/api/query_extender/process | jq
        
curl --silent --request POST --header "Content-Type: application/json" \
        --data "{\"tss\":\"presidemdiga\\tpresitendi\\tpresidendiga\", \"params\":{\"otsi_liitsõnadest\":\"false\"}}" \
        localhost:6604/api/query_extender/json | jq
        
curl --silent --request POST --header "Content-Type: application/json" \
        localhost:6604/api/query_extender/version | jq
```

### 2 Lähtekoodist tehtud konteineri kasutamine

#### 2.1 Lähtekoodi allalaadimine: järgi punkti 1.1

#### 2.2 Konteineri kokkupanemine

```bash
cd ~/git/smart_search_github/api/api_query_extender
cp ../../demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts/koond.sqlite ./smart_search.sqlite
docker-compose build
```

#### 2.3 Konteineri käivitamine

```bash
cd ~/git/smart_search_github/api/api_query_extender \
        && docker-compose up -d
```

#### 2.4 CURLiga veebiteenuse kasutamise näited

Järgi punkti 1.4

#### 2.5 Konteineri peatamine

```bash
cd ~/git/smart_search_github/api/api_query_extender \
        && docker-compose down
```

### 3 DockerHUBist tõmmatud konteineri kasutamine

#### 3.1 DockerHUBist konteineri tõmbamine

```bash
cd ~/git/smart_search_github/api/api_query_extender \
        && docker-compose pull
```

#### 3.2 Konteineri käivitamine

Järgi punkti 2.3

#### 3.3 CURLiga veebiteenuse kasutamise näited

Järgi punkti 1.4

#### 3.4 Konteineri peatamine: järgi punkti 2.5

### 4 TÜ pilves töötava konteineri kasutamine

CURLiga veebiteenuse kasutamise näited

```bash
curl --silent --request POST \
        --header "Content-Type: application/json" \
        --data "{\"tss\":\"presitendi\\tpresidendiga\", \"params\":{\"otsi_liitsõnadest\":\"false\"}}" \
        https://smart-search.tartunlp.ai/api/query_extender/tsv

curl --silent --request POST \
        --header "Content-Type: application/json" \
        --data "{\"tss\":\"presitendiga\\tpresitendiga\\tpresidendiga\"}" \
        https://smart-search.tartunlp.ai/api/query_extender/tsv
        
curl --silent --request POST --header "Content-Type: application/json" \
        --data "{\"content\":\"presitendi\\tpresidendiga\", \"params\":{\"otsi_liitsõnadest\":\"false\"}}" \
        https://smart-search.tartunlp.ai/api/query_extender/process | jq
        
curl --silent --request POST --header "Content-Type: application/json" \
        --data "{\"tss\":\"presitendi\\tpresidendiga\", \"params\":{\"otsi_liitsõnadest\":\"false\"}}" \
        https://smart-search.tartunlp.ai/api/query_extender/json | jq
        
curl --silent --request POST --header "Content-Type: application/json" \
        --data "{\"tss\":\"Strasbourg'i\\tStrasbourg'iga\\tpresidendi\\tpresident\\tpresidendiga\"}" \
        https://smart-search.tartunlp.ai/api/query_extender/wordform_check | jq

curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/query_extender/version | jq
```

### 5 DockerHubis oleva konteineri lisamine oma KUBERNETESesse

#### 5.1 Vaikeväärtustega ```deployment```-konfiguratsioonifaili loomine

```bash
kubectl create deployment smart-search-api-query-extender \
  --image=tilluteenused/smart_search_api_advanced_indexing:2024.01.21
```

Keskkonnamuutujate abil saab muuta maksimaalse lubatava päringu suurust,

Selleks redigeeriga konfiguratsioonifaili

```bash
kubectl edit deployment smart-search-api-query-extender
```

Lisades sinna soovitud keskkonnamuutujate väärtused:

```yml
    env:
    - name: MART_SEARCH_MAX_CONTENT_LENGTH
      value: "100000"
    - name: SMART_SEARCH_QE_DBASE
      value: ./smart_search.sqlite

```

#### 5.2 Vaikeväärtustega ```service```-konfiguratsioonifaili loomine

```bash
kubectl expose deployment smart-search-api-query-extender \
  --type=ClusterIP --port=80 --target-port=6604
```

#### 5.3 ```ingress```-konfiguratsioonifaili täiendamine

```bash
kubectl edit ingress smart-search-api-ingress
```

Lisage sinna

```yml
- backend:
    service:
    name: smart-search-api-query-extender
    port:
        number: 80
path: /api/query_extender/?(.*)
pathType: Prefix
```

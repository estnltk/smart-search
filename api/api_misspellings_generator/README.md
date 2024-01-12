# Kirjavigade generaator

## Sisendi formaat

Programmi sisendiks sõne real teksitfail. Igast sõnest genereeritakse tema võimalikud kirjavigade vormid.

Näiteks fail ```test.txt```

```text
Õun
kuusekäbi 
presidendi
karu saba
```

## Väljundi formaat

Väljund on JSON-kujul

```json
{   "tabelid":
    {   "kirjavead":
        [   KIRJAVEAGA_SÕNE, ALGNE_SÕNE, KAAL] // KAAL on praegu alati 1, hoiab kohta tuleviku tarbeks. 
    }
}
```

## Kasutamine

### 1 Lähtekoodist pythoni skripti kasutamine:

#### 1.1 Lähtekoodi allalaadimine

```bash
mkdir -p ~/git/ ; cd ~/git/
git clone git@github.com:estnltk/smart-search.git sqmart_search_github
```

#### 1.2 Virtuaalkeskkonna loomine

```bash
cd ~/git/smart_search_github/api/api_misspellings_generator
./create_venv.sh
```

#### 1.3 Pythoni skripti käivitamine:

```bash
venv/bin/python3 ./api_misspellings_generator.py --verbose test.txt > test.json
```

### 2 Lähtekoodist veebiserveri käivitamine & kasutamine

#### 2.1 Lähtekoodi allalaadimine

Järgi punkti 1.1.

#### 2.2 Virtuaalkeskkonna loomine

Järgi punkti 1.2

#### 2.3 Veebiteenuse käivitamine pythoni koodist

#### 2.3.1 Vaikeseadetaga

```bash
cd ~/git/smart_search_github/api/api_misspellings_generator
./venv/bin/python3 ./flask_api_misspellings_generator.py
```

#### 2.3.2 Etteantud parameetriga

```bash
SMART_SEARCH_MAX_CONTENT_LENGTH='500000' \
        venv/bin/python3 ./flask_api_misspellings_generator.py
```

#### 2.4 CURLiga veebiteenuse kasutamise näited

```bash
curl --silent --request POST --header "Content-Type: application/text" \
        localhost:6603/api/misspellings_generator/version | jq

curl --silent --request POST --header "Content-Type: application/text" \
      --data-binary @test.txt \
      localhost:6603/api/misspellings_generator/process  | jq
```

### 3 Lähtekoodist tehtud konteineri kasutamine

#### 3.1 Lähtekoodi allalaadimine

Järgi punkti 1.1

#### 3.2 Konteineri kokkupanemine

```bash
cd ~/git/smart_search_github/api/api_misspellings_generator
docker build -t tilluteenused/smart_search_api_misspellings_generator:2023.12.27 . 
```

#### 3.3 Konteineri käivitamine

```bash
docker run -p 6603:6603  \
    --env SMART_SEARCH_MAX_CONTENT_LENGTH='500000' \
    tilluteenused/smart_search_api_misspellings_generator:2023.12.27
```

#### 3.4 CURLiga veebiteenuse kasutamise näited

Järgi punkti 2.3

### 4 DockerHUBist tõmmatud konteineri kasutamine

#### 4.1 DockerHUBist konteineri tõmbamine

```bash
docker pull tilluteenused/smart_search_api_misspellings_generator:2023.12.27 
```

#### 3.2 Konteineri käivitamine

Järgi punkti 3.3

#### 3.3 CURLiga veebiteenuse kasutamise näited

Järgi punkti 2.3

### 5 TÜ pilves töötava konteineri kasutamine

CURLiga veebiteenuse kasutamise näited

```bash
cd ~/git/smart_search_github/api/api_misspellings_generator # selles kataloogis on test.txt
curl --silent --request POST --header "Content-Type: application/text" \
        --data-binary @test.txt \
        https://smart-search.tartunlp.ai/api/misspellings_generator/process | jq | less
curl --silent --request POST --header "Content-Type: application/text" \
        https://smart-search.tartunlp.ai/api/misspellings_generator/version | jq
```

### 6 DockerHubis oleva konteineri lisamine oma KUBERNETESesse

#### 6.1 Vaikeväärtustega ```deployment```-konfiguratsioonifaili loomine

```bash
kubectl create deployment smart-search-api-misspellings-generator \
  --image=tilluteenused/smart_search_api_misspellings_generator:2023.12.27
```

Keskkonnamuutujate abil saab muuta:
* maksimaalse lubatava päringu suurust,
* kas kirjavigade tabelit arvutatakse või mitte.

Selleks redigeeriga konfiguratsioonifaili

```bash
kubectl edit deployment smart-search-api-misspellings-generator
```

Lisades sinna soovitud keskkonnamuutujate väärtused:

```yml
    env:
    - name: MART_SEARCH_MAX_CONTENT_LENGTH
      value: "100000"
```

#### 6.2 Vaikeväärtustega ```service```-konfiguratsioonifaili loomine

```bash
kubectl expose deployment smart-search-api-misspellings-generator \
  --type=ClusterIP --port=80 --target-port=6603
```

#### 6.3 ```ingress```-konfiguratsioonifaili täiendamine

```bash
kubectl edit ingress smart-search-api-ingress
```

Lisage sinna

```yml
- backend:
    service:
    name: smart-search-api-misspellings-generator
    port:
        number: 80
path: /api/misspellings_generator/?(.*)
pathType: Prefix
```
# Veebileht Riigiteataja pealkirjaotsingu demonstreerimiseks

## Tarkvara paigaldaine ja kasutamine

### 1 Lähtekoodist pythoni skripti kasutamine

#### 1.1 Lähtekoodi allalaadimine

```bash
mkdir ~/git ; cd ~/git/
git clone git@github.com:estnltk/smart-search.git smart_search_github
```

#### 1.2 Virtuaalkeskkonna loomine

```bash
cd ~/git/smart_search_github/demod/veebilehed/rt_pealkirjaotsing
./create_venv.sh
```

#### 1.3.1 Vajalik eeltöö

Eeldused:

* Päringulaiendaja kohalik konteiner peab olema eelnevalt käivitatud,
[vt päringulaiendaja](https://github.com/estnltk/smart-search/blob/main/api/api_query_extender/README.md).
* Andmebaas vajalike andmetega peab olema tehtud, vt 
[andmebaasi tegemine](https://github.com/estnltk/smart-search/blob/main/scripts/query_extender_setup/example_script_based_workflow/README.md) ja kopeeritud kataloogi `~/git/smart_search_github/demod/veebilehed/rt_pealkirjaotsing` nimega `smart_search.sqlite`.

***NB! Otsimootoris ja päringulaiendajas tuleb kasutada
samade pealkirjafailide pealt tehtud andmebaasi!!!***

#### 1.3.2 Veebiserveri käivitamine pythoni koodist

```bash
cd ~/git/smart-search_github/demod/veebilehed/ea_paring_otsing
DB_INDEX=./smart_search.sqlite \
      EA_PARING=http://localhost:6604/api/query_extender/process \
      ./venv/bin/python3 ./flask_wp_ea_paring_otsing.py
```

#### 1.4 Brauseriga veebilehe poole pöördumine

```bash
google-chrome http://localhost:6605/rt_pealkirjaotsing/process &
google-chrome http://localhost:6605/rt_pealkirjaotsing/version &
```

Järgige avanenud veebilehel antud juhiseid.

### 2 Lähtekoodist tehtud konteineri kasutamine

#### 2.1 Lähtekoodi allalaadimine

Järgi punkti 1.1

#### 2.2 Konteineri kokkupanemine

```bash
cd ~/git/smart_search_github/demod/veebilehed/rt_pealkirjaotsing
docker build -t tilluteenused/smart_search_rt_pealkirjaotsing:s .
```

#### 2.3.1 Valikud eeltööd

Andmebaas vajalike andmetega peab olema tehtud, vt andmebaasi tegemine ja kopeeritud kataloogi `~/git/smart_search_github/demod/veebilehed/rt_pealkirjaotsing` nimega `smart_search.sqlite`.

NB! Otsimootoris ja päringulaiendajas tuleb kasutada samade pealkirjafailide pealt tehtud andmebaasi!!!

#### 2.3.2 Konteinerite käivitamine kohalikus arvutis

```bash
cd ~/git/smart_search_github/demod/veebilehed/rt_pealkirjaotsing
MY_IP=$(hostname -I | sed 's/ .*$//g') docker-compose up -d && docker-compose ps
```

#### 2.4 Brauseriga veebilehe poole pöördumine

Järgi punkti 1.4

#### 2.5 Konteinerite peatamine

```bash
cd ~/git/smart_search_github/demod/veebilehed/rt_pealkirjaotsing
docker-compose down && docker-compose ps
```

### 3 DockerHUBist tõmmatud konteineri kasutamine

#### 3.1 DockerHUBist konteineri tõmbamine

```bash
docker pull tilluteenused/smart_search_rt_pealkirjaotsing:2024.01.14
```

#### 3.2 Konteinerite allalaadimine ja käivitamine

Järgi punkti 2.3

#### 3.3 Brauseriga veebilehe poole pöördumine

Järgi punkti 1.4

#### 3.4 Konteinerite peatamine

Järgi punkti 2.5

### 5 TÜ KUBERNETESes töötava konteineri kasutamine

```bash
google-chrome https://smart-search.tartunlp.ai/rt_pealkirjaotsing/process &
google-chrome https://smart-search.tartunlp.ai/rt_pealkirjaotsing/version &
```

### 5 DockerHubis oleva konteineri lisamine oma KUBERNETESesse

#### 5.1 Vaikeväärtustega ```deployment```-konfiguratsioonifaili loomine

```bash
kubectl create deployment smart-search-rt-pealkirjaotsing \
  --image=tilluteenused/smart_search_rt_pealkirjaotsing:2024.01.14
```

Keskkonnamuutujate abil saab muuta maksimaalse lubatava päringu suurust ja andmebaasi nime.

Selleks redigeeriga konfiguratsioonifaili

```bash
kubectl edit deployment smart-search-rt-pealkirjaotsing
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
kubectl expose deployment smart-search-rt-pealkirjaotsing \
  --type=ClusterIP --port=80 --target-port=6605
```

#### 5.3 ```ingress```-konfiguratsioonifaili täiendamine

```bash
kubectl edit ingress smart-search-api-ingress
```

Lisage sinna

```yml
- backend:
    service:
    name: ssmart-search-rt-pealkirjaotsing
    port:
        number: 80
path: /rt_pealkirjaotsing/?(.*)
pathType: Prefix
```

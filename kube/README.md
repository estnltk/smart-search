# SMARTSEARCH

Kubernetes:
* ```deployment``` ja ```service``` on tehtud sama nimega.
* ``deployment``` ja ```service``` on tehtud vaikeseadetega ja siis lisatud vajalikug muutused (peamiselt keskkonnamuutujad).
* ```api``` ja ```wp``` teenuste jaoks on eraldi ```ingress```'i failid. Näidetes on kirjas seeosa mida juba ühe või teise teenuse
jaoks tuleb lisada.
 
---

## API

### **API SPELLER**
---

[**Juhised ja näited**](https://github.com/Filosoft/vabamorf/blob/master/docker/flask_stlspeller/flask_stlspeller.py)

**Kubernetes**

* **Sõltuvusi Kuberneteses** pole.

* **Konfi** ```deployment``` ja ```service``` analoogiliselt sõnestajaga

* **Konf** ```ingress```´is

```yaml
      - backend:
          service:
            name: smart-search-api-speller
            port:
              number: 80
        path: /api/speller/?(.*)
        pathType: Prefix
```

| port | kubernetes               | docker                           | path                                          |
|------|--------------------------|----------------------------------|-----------------------------------------------|
| 7005 | smart-search-api-speller | tilluteenused/speller:2023.06.03 | /api/speller/version<br>/api/speller/process |

Testitud: 2023-06.03

### **API SÕNESTAJA**
---

[**Juhised ja näited**](https://github.com/Filosoft/vabamorf/blob/master/docker/flask_estnltk_sentok/flask_estnltk_sentok.py)

**Kubernetes**

* **Sõltuvusi Kuberneteses** pole.

* **Konf** (```deployment```, ```service```, ```ingress```)

```commandline
kubectl create deployment smart-search-api-tokenizer --image=tilluteenused/estnltk_sentok:2023.04.18
```

```commandline
kubectl expose deployment smart-search-api-tokenizer --type=ClusterIP --port=80 --target-port=6000
```

```cmdline
kubectl edit ingress smart-search-api-ingress
```

```yaml
      - backend:
          service:
            name: smart-search-api-tokenizer
            port:
              number: 80
        path: /api/tokenizer/?(.*)
        pathType: Prefix
```

| port | kubernetes | docker | path |
|------|------------|--------|------|
| 6000 | smart-search-api-tokenizer | tilluteenused/estnltk_sentok:2023.04.18 | /api/tokenizer/version<br>/api/tokenizer/process |

**Testitud:** 2023.06.03

### **API MORF ANALÜSAATOR**
---

[**Juhised ja näited**](https://github.com/Filosoft/vabamorf/blob/master/docker/flask_vmetajson/flask_vmetajson.py)

**Kubernetes**

* **Sõltuvusi Kuberneteses** pole

* **Konf**  (```deployment```, ```service```, ```ingress```)

```commandline
kubectl create deployment smart-search-api-analyser --image=tilluteenused/vmetajson:2023.06.01 
```

```commandline
kubectl expose deployment smart-search-api-analyser --type=ClusterIP --port=80 --target-port=7007
```

```cmdline
kubectl edit ingress smart-search-api-ingress
```

```yaml
      - backend:
          service:
            name: smart-search-api-analyser
            port:
              number: 80
        path: /api/analyser/?(.*)
        pathType: Prefix
```

| port | kubernetes | docker | path |
|------|------------|--------|------|
| 7007 | smart-search-api-analyser | tilluteenused/vmetajson:2023.06.01 | /api/analyser/version<br>/api/analyser/process |

**Testitud:** 2023-06-03

### **API MORF GENERAATOR**
---

[**Juhised ja näited**](https://gitlab.com/tilluteenused/docker-elg-synth)

**Kubernetes**

* **Sõltuvusi Kuberneteses** pole

* **Konf**  (```deployment```, ```service```, ```ingress```)

```commandline
kubectl create deployment smart-search-api-elg-generator --image=tilluteenused/vabamorf_synth:2022.08.15 
```

```commandline
kubectl expose deployment smart-search-api-elg-generator --type=ClusterIP --port=80 --target-port=7000
```

```cmdline
kubectl edit ingress smart-search-api-ingress
```

```yaml
      - backend:
          service:
            name: smart-search-api-elg-generator
            port:
              number: 80
        path: /api/generator/?(.*)
        pathType: Prefix
```

| port | kubernetes | docker | path |
|------|------------|--------|------|
| 7000 | smart-search-api-elg-generator | tilluteenused/vabamorf_synth:2022.08.15  | /api/generator/process |

**Testitud:** 2023.06.03

### **API INDEKSEERIJA: LEMMAPÕHINE**
---

[**Juhised ja näited**](https://github.com/estnltk/smart-search/blob/main/api/indekseerija_lemmad/flask_api_lemmade_indekseerija.py)

**Kubernetes**

* **Sõltuvused:** deployment'i:
  * smart-search-api-tokenizer
  * smart-search-api-analyser

```yaml
      containers:
      - env:
        - name: TOKENIZER_IP
          value: $(SMART_SEARCH_API_TOKENIZER_SERVICE_HOST)
        - name: ANALYSER_IP
          value: $(SMART_SEARCH_API_ANALYSER_SERVICE_HOST)
        - name: TOKENIZER_PORT
          value: $(SMART_SEARCH_API_TOKENIZER_SERVICE_PORT)
        - name: ANALYSER_PORT
          value: $(SMART_SEARCH_API_ANALYSER_SERVICE_PORT)
        image: tilluteenused/smart_search_api_lemmade_indekseerija:2023.04.20
```

* **Konf** ```ingress```'is

```yaml
      - backend:
          service:
            name: smart-search-api-lemmade-indekseerija
            port:
              number: 80
        path: /api/lemmade-indekseerija/?(.*)
        pathType: Prefix
```

| port | kubernetes | docker | path |
|------|------------|--------|------|
| 6607 | smart-search-api-lemmade-indekseerija | tilluteenused/smart_search_api_lemmade_indekseerija:2023.04.20 | /api/lemmade-indekseerija/version<br>/api/lemmade-indekseerija/json<br> /api/lemmade-indekseerija/csv |

### **API INDEKSEERIJA: SÕNEPÕHINE**

[**Juhised ja näited**](https://github.com/estnltk/smart-search/blob/main/api/indekseerija_soned/flask_api_sonede_indekseerija.py)

**Kubernetes**

* **Sõltuvused:** ```deployment```'i
  * smart-search-api-tokenizer
  * smart-search-api-analyser

```yaml
      containers:
      - env:
        - name: TOKENIZER_IP
          value: $(SMART_SEARCH_API_TOKENIZER_SERVICE_HOST)
        - name: ANALYSER_IP
          value: $(SMART_SEARCH_API_ANALYSER_SERVICE_HOST)
        - name: TOKENIZER_PORT
          value: $(SMART_SEARCH_API_TOKENIZER_SERVICE_PORT)
        - name: ANALYSER_PORT
          value: $(SMART_SEARCH_API_ANALYSER_SERVICE_PORT)
        image: tilluteenused/smart_search_api_sonede_indekseerija:2023.04.2
```

* **Konf** ```ingress```'is

```yaml
      - backend:
          service:
            name: smart-search-api-sonede-indekseerija
            port:
              number: 80
        path: /api/sonede-indekseerija/?(.*)
        pathType: Prefix
```

| port | kubernetes | docker | path |
|------|------------|--------|------|
| 6606 | smart-search-api-sonede-indekseerija | tilluteenused/smart_search_api_sonede_indekseerija:2023.04.20 | /api/sonede-indekseerija/version<br>/api/sonede-indekseerija/json<br>/api/sonede-indekseerija/csv |

**Testitud** 2023.06.03

### **API PÄRINGU NORMALISEERIJA: LEMMAD**

[**Juhised ja näited**](https://github.com/estnltk/smart-search/blob/main/api/paring_lemmad/flask_api_paring_lemmad.py)

**Kubernetes**

* **Sõltuvused:** ```deployment```'i
  * smart-search-api-tokenizer
  * smart-search-api-analyser

```yaml
      containers:
      - env:
        - name: TOKENIZER_IP
          value: $(SMART_SEARCH_API_TOKENIZER_SERVICE_HOST)
        - name: ANALYSER_IP
          value: $(SMART_SEARCH_API_ANALYSER_SERVICE_HOST)
        - name: TOKENIZER_PORT
          value: $(SMART_SEARCH_API_TOKENIZER_SERVICE_PORT)
        - name: ANALYSER_PORT
          value: $(SMART_SEARCH_API__ANALYSER_SERVICE_PORT)
        image: tilluteenused/smart_search_api_paring_lemmad:2023.06.02
```

* **Konf** ```ingress```'is

```yaml
      - backend:
          service:
            name: smart-search-api-paring-lemmad
            port:
              number: 80
        path: /api/paring-lemmad/?(.*)
        pathType: Prefix
```

| port | Kubernetes | docker | path |
|------|------------|--------|------|
| 6608 | smart-search-api-paring-lemmad | tilluteenused/smart_search_api_paring_soned:2023.06.02 | /api/paring-lemmad/version<br>/api/paring-lemmad/json<br>/api/paring-lemmad/text |

**Testitud** 2023.06.03

### **API PÄRINGU NORMALISEERIJA: SÕNED**

[**Juhised ja näited**](https://github.com/estnltk/smart-search/blob/main/api/paring_soned/flask_api_paring_soned.py)

**Kubernetes**

* **Sõltuvused** deployment'i
  * smart-search-api-tokenizer
  * smart-search-api-analyser
  * smart-search-api-elg-generator

```yaml
      containers:
      - env:
        - name: TOKENIZER_IP
          value: $(SMART_SEARCH_API_TOKENIZER_SERVICE_HOST)
        - name: TOKENIZER_PORT
          value: $(SMART_SEARCH_API_TOKENIZER_SERVICE_PORT)
        - name: ANALYSER_IP
          value: $(SMART_SEARCH_API_ANALYSER_SERVICE_HOST)
        - name: ANALYSER_PORT
          value: $(SMART_SEARCH_API_ANALYSER_SERVICE_PORT)
        - name: GENERATOR_IP
          value: $(SMART_SEARCH_API_ELG_GENERATOR_SERVICE_HOST)
        - name: GENERATOR_PORT
          value: $(SMART_SEARCH_API_ELG_GENERATOR_SERVICE_PORT)
        image: tilluteenused/smart_search_api_paring_soned:2023.06.02
```

* **Konf** ```ingress```'is

```yaml
      - backend:
          service:
            name: smart-search-api-paring-soned
            port:
              number: 80
        path: /api/paring-soned/?(.*)
        pathType: Prefix
```

| port | Kubernetes | docker | path |
|------|------------|--------|------|
| 6609 | smart-search-api-paring-soned | tilluteenused/smart_search_api_paring_soned:2023.04.25 | /api/paring-soned/version<br>/api/paring-soned/json<br>/api/paring-soned/text|

---
---

## WP

### **WP: SPELLER**
---

[**Juhised ja näited**](https://github.com/estnltk/smart-search/blob/main/wp/wp_speller/flask_wp_speller.py)

**Kubernetes**

* **Sõltuvused** ```deployment```'i:
  * smart-search-api-speller

```yaml
      - env:
        - name: PARING_SPELLER_IP
          value: $(SMART_SEARCH_API_SPELLER_SERVICE_HOST)
        - name: PARING_SPELLER_PORT
          value: $(SMART_SEARCH_API_SPELLER_SERVICE_PORT)
        image: tilluteenused/smart_search_wp_speller:2023.05.22
```

* **Konf** ```ingress```'is

```yaml
      - backend:
          service:
            name: smart-search-wp-speller
            port:
              number: 80
        path: /wp/speller/?(.*)
        pathType: Prefix
```

| port | kubernetes | docker | path |
|------|------------|--------|------|
| 6003 | smart-search-wp-speller | tilluteenused/smart_search_wp_speller:2023.05.22 | /wp/speller/version<br>/wp/speller/process |

**Testitud** 2023.06.03


### **WP: INDEKSEERIJA**
---

[**Juhised ja näited**](https://github.com/estnltk/smart-search/blob/main/wp/wp_indekseerija/flask_wp_indekseerija.py)

**Kubernetes**

* **Sõltuvused** deployment'i:
  * smart-search-api-lemmade-indekseerija
  * smart-search-api-sonede-indekseerija

```yaml
      containers:
      - env:
        - name: INDEKSEERIJA_LEMMAD_IP
          value: $(SMART_SEARCH_API_LEMMADE_INDEKSEERIJA_SERVICE_HOST)
        - name: INDEKSEERIJA_LEMMAD_PORT
          value: $(SMART_SEARCH_API_LEMMADE_INDEKSEERIJA_SERVICE_PORT)
        - name: INDEKSEERIJA_SONED_IP
          value: $(SMART_SEARCH_API_SONEDE_INDEKSEERIJA_SERVICE_HOST)
        - name: INDEKSEERIJA_SONED_PORT
          value: $(SMART_SEARCH_API_SONEDE_INDEKSEERIJA_SERVICE_PORT)
        image: tilluteenused/smart_search_wp_indekseerija:2023.05.01.4
```

* **Konf** ```ingress```'is

```yaml
      - backend:
          service:
            name: smart-search-wp-indekseerija
            port:
              number: 80
        path: /wp/indekseerija/?(.*)
        pathType: Prefix
```

| port | kubernetes | docker | path |
|------|------------|--------|------|
| 5000 | smart-search-wp-indekseerija | tilluteenused/smart_search_wp_indekseerija:2023.05.20 | /wp/indekseerija/version<br>/wp/indekseerija/process |

**Testitud** 2023.06.03

### **WP: OTSING LEMMAPÕHINE**
---

[**Juhised ja näited**](https://github.com/estnltk/smart-search/blob/main/wp/wp_otsing/flask-wp-otsing.py)

**Kubernetes**

* **Sõltuvused** deployment'i:
  * smart-search-api-paring-lemmad

```yaml
      containers:
      - env:
        - name: OTSINGU_VIIS
          value: lemmad
        - name: IDXFILE
          value: riigiteataja-lemmad-json.idx
        - name: PARING_LEMMAD_IP
          value: $(SMART_SEARCH_API_PARING_LEMMAD_SERVICE_HOST)
        - name: PARING_LEMMAD_PORT
          value: $(SMART_SEARCH_API_PARING_LEMMAD_SERVICE_PORT)
        image: tilluteenused/smart_search_wp_otsing:2023.05.12
```

* **Konf** ```ingress```'is

```yaml
      - backend:
          service:
            name: smart-search-wp-otsing-lemmad
            port:
              number: 80
        path: /wp/otsing-lemmad/?(.*)
        pathType: Prefix
```

| port | kubernetes | docker | path |
|------|------------|--------|------|
| 6013 | smart-search-wp-otsing-lemmad | tilluteenused/smart_search_wp_otsing:2023.05.15 | /wp/otsing-lemmad/version<br>/wp/otsing-lemmad/texts<br>/wp/otsing-lemmad/process |

**Testitud** 2023.06.03

### **WP: OTSING SÕNEPÕHINE**
---

[**Juhised ja näited**](https://github.com/estnltk/smart-search/blob/main/wp/wp_otsing/flask-wp-otsing.py)

**Kubernetes**

* **Sõltuvused** deployment'i:
  * smart-search-api-paring-soned

```yaml
      containers:
      - env:
        - name: OTSINGU_VIIS
          value: soned
        - name: IDXFILE
          value: riigiteataja-soned-json.idx
        - name: PARING_SONED_IP
          value: $(SMART_SEARCH_API_PARING_SONED_SERVICE_HOST)
        - name: PARING_SONED_PORT
          value: $(SMART_SEARCH_API_PARING_SONED_SERVICE_PORT)
        image: tilluteenused/smart_search_wp_otsing:2023.05.12
```

* **Konf** ```ingress```'is

```yaml
      - backend:
          service:
            name: smart-search-wp-otsing-soned
            port:
              number: 80
        path: /wp/otsing-soned/?(.*)
        pathType: Prefix
```

| port | kubernetes | docker | path |
|------|------------|--------|------|
| 6013 | smart-search-wp-otsing-soned | tilluteenused/smart_search_wp_otsing:2023.05.15 | /wp/otsing-soned/version<br>/wp/otsing-soned/texts<br>/wp/otsing-soned/process |

**Testitud** 2023.06.03

### **WP: PARING**
---

[**Juhised ja näited**](https://github.com/estnltk/smart-search/blob/main/wp/wp_paring/flask_wp_paring.py)

**Kubernetes**

* **Sõltuvused** deployment'i:
  * smart-search-api-paring-lemmad
  * smart-search-api-paring-soned

```yaml
      containers:
      - env:
        - name: PARING_LEMMAD_IP
          value: $(SMART_SEARCH_API_PARING_LEMMAD_SERVICE_HOST)
        - name: PARING_LEMMAD_PORT
          value: $(SMART_SEARCH_API_PARING_LEMMAD_SERVICE_PORT)
        - name: PARING_SONED_IP
          value: $(SMART_SEARCH_API_PARING_SONED_SERVICE_HOST)
        - name: PARING_SONED_PORT
          value: $(SMART_SEARCH_API_PARING_SONED_SERVICE_PORT)
        image: tilluteenused/smart_search_wp_paring:2023.04.29.4
```

* **Konf** ```ingress```'is

```yaml
      - backend:
          service:
            name: smart-search-wp-paring
            port:
              number: 80
        path: /wp/paring/?(.*)
        pathType: Prefix
```

| port |  kubernetes | docker | path |
|------|-------------|--------|------|
| 5000 | smart-search-wp-paring | tilluteenused/smart_search_wp_paring:2023.05.23 | /wp/paring/version<br>/wp/paring/process |

**Testitud** 2023.06.03

---
---

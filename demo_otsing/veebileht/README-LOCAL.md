# Otsingumootori demoveebileht (proof of concept) DOCKERi konteineri abil

## Otsingumootori demoveebilehe ülesseadmine oma arvutis (DOCKERi konteinerina)

### 1. käivita lemmatiseerija konteiner ([konteiner peab olema tehtud/allalaaditud](https://github.com/estnltk/smart-search/blob/main/lemmatiseerija/README.md))

Kuna lemmatiseerija demo saab sõna võimalike lemmade kohta infot lemmetiseerija DOCKERi konteinerilt, peab see töötama.

```cmdline
docker run -p 7000:7000 tilluteenused/demo_lemmatiseerija:2023.03.21
```

### 2. käivita lemmatiseerija demo sisaldav konteiner (suhtleb lemmatiseerija konteineriga)

Selleks laadi vastav konteiner alla:

```cmdline
docker pull tilluteenused/demo_smartsearch_webpage:2023.03.21
```

Käivita konteiner:

```cmdline
# LEMMATIZER_IP väärtuseks peab olema lemmatiseerija konteineri tegelik IP
docker run --env LEMMATIZER_IP=$(hostname -I | sed 's/^\([^ ]*\) .*$/\1/') -p 7070:7070 tilluteenused/demo_smartsearch_webpage:2023.03.21
```

Märkus: Võite konteineri ka [lähtekoodist](https://github.com/estnltk/smart-search/tree/main/demo_otsing/veebileht) ise teha. Selleks peate ellnevalt:

* Allalaadima lähtekoodi

  ```commandline
  mkdir ~/git ; cd ~/git 
  git clone --depth 1 https://github.com/estnltk/smart-search.git smart_search_github
  ```

* Ehitama konteineri

  ```cmdline
  docker build -t tilluteenused/demo_smartsearch_webpage:2023.03.21 .
  ```

## Otsingumootori demoveebilehe  kasutamine

### 1. Näita demokorpuses olevaid tekste

Sisestage veebilehitseja aadressiribale ```http://localhost:7070/tekstid```.
Veebilehitseja aknas näete demokorpuse tekste. Otsimootor otsib nende tekstide seest, vaata [ekraanipilti](https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/Ekraanipilt_demo_veebileht-tekstid.png).

### 2. Märksõnade otsimine tekstist. Lihtsõnu otsitakse ka liitsõna osasõnadest

Sisestaga veebilehitseja aadressiribale
```http://localhost:7070/tekstid```. Sisestage tekstikasti otsingusõned ja klikkige
```Otsi (sh liitsõna osasõnadest)```. Avaneb veebileht otsingu tulemustega. Veebilehe alguses on kirjas milliseid lemmasid tekstist otsitakse.
Päringule vastavad sõnad tekstis on rasvases kirjas ja sulgudes algvormid.
Nagu [ekraanipildilt](https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/Ekraanipilt_demo_veebileht_otsils2.png) näha leitakse
päringusõne ```katus``` ka liitsõna ```valtskatuste``` osasõnast.

### 3. Märksõnade otsimine tekstist. Lihtsõnu ei otsita liitsõna osasõnadest

Sisestaga veebilehitseja aadressiribale
```http://localhost:7070/otsi```. Sisestage tekstikasti otsingusõned ja klikkige
```Otsi```. Avaneb veebileht otsingu tulemustega. Veebilehe alguses on kirjas milliseid lemmasid tekstist otsitakse.
Päringule vastavad sõnad tekstis on rasvases kirjas ja sulgudes algvormid.
Nagu [ekraanipildilt](https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/Ekraanipilt_demo_veebileht_otsi2.png) näha ei leita
päringusõne ```katus``` liitsõna ```valtskatuste``` osasõnast.


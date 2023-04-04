# Otsingumootori demoveebilehed (proof of concept) DOCKERi konteineri abil [versioon 2023.04.04]

## Otsingumootori demoveebilehtede ülesseadmine oma arvutis (DOCKERi konteineri abil)

### 1. käivita lemmatiseerija konteiner ([konteiner peab olema tehtud/allalaaditud](https://github.com/estnltk/smart-search/blob/main/lemmatiseerija/README.md))

Kuna lemmatiseerija demo saab sõna võimalike lemmade kohta infot lemmatiseerija DOCKERi konteinerilt, peab see töötama.

```cmdline
docker run -p 7000:7000 tilluteenused/lemmatiseerija:2023.03.30
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

* Ehitame konteineri

  ```cmdline
  docker build -t tilluteenused/demo_smartsearch_webpage:2023.03.21 .
  ```

## Otsingumootori demoveebilehtede  kasutamine

Kasutusnäiteid vaata [sealt](https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/README-CLOUD.md), kui konteinerid töötavad kohalikus masinas siis ```https://smart-search.tartunlp.ai/``` asemel kirjutage ```http://localhost:7070/```.

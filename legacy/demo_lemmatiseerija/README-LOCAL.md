# Lemmatiseerija demoveebilehed DOCKERi konteineri abil  [versioon 2023.04.04]

## Lemmatiseerija demo veebilehe ülesseadmine oma arvutis (DOCKERi konteineri abil)

### 1. käivita lemmatiseerija konteiner ([konteiner peab olema tehtud/allalaaditud](https://github.com/estnltk/smart-search/blob/main/lemmatiseerija/README.md))

Kuna lemmatiseerija demo saab sõna võimalike algvormide (lemmade) kohta infot lemmetiseerija DOCKERi konteinerilt, peab see töötama.

```cmdline
docker run -p 7000:7000 tilluteenused/lemmatiseerija:2023.03.30
```

### 2. käivita lemmatiseerija demo sisaldav konteiner (suhtleb lemmatiseerija konteineriga)

Selleks laadi vastav konteiner alla:
  
```cmdline
docker pull tilluteenused/demo_lemmatiseerija:2023.04.04
```

Käivita konteiner:

```cmdline
docker run -p 7777:7777 --env LEMMATIZER_IP=$(hostname -I | sed 's/^\([^ ]*\) .*$/\1/') --env LEMMATIZER_PORT=7000 tilluteenused/demo_lemmatiseerija:2023.04.04
```

Märkus: Võite konteineri ka [lähtekoodist](https://github.com/estnltk/smart-search/tree/main/demo_lemmatiseerija) ise teha. Selleks peate eelnevalt:

* Allalaadima lähtekoodi

  ```commandline
  mkdir ~/git ; cd ~/git 
  git clone --depth 1 https://github.com/estnltk/smart-search.git smart_search_github
  ```

* Ehitama konteineri

  ```commandline
  cd ~/git/smart_search_github/lemmatiseerija
  docker build -t tilluteenused/demo_lemmatiseerija:2023.04.04 .
  ```

* Käivitage tehtud konteiner ülalkirjeldatud viisil.

## Lemmatiseerija demoveebilehe kasutamine

Kasutusnäiteid vaata [sealt](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/README-CLOUD.md), ```https://smart-search.tartunlp.ai/``` asemel kirjutage ```http://localhost:7777/```.

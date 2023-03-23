# Lemmatiseerija demo veebilehena DOCKERi konteineris

## Lemmatiseerija demo veebilehe ülesseadmine oma arvutis (DOCKERi konteinerina)

### 1. käivita lemmatiseerija konteiner ([konteiner peab olema tehtud/allalaaditud](https://github.com/estnltk/smart-search/blob/main/lemmatiseerija/README.md))

Kuna lemmatiseerija demo saab sõna võimalike lemmede kohta infot lemmetiseerija DOCKERi konteinerilt, peab see töötama.

```cmdline
docker run -p 7000:7000 tilluteenused/demo_lemmatiseerija:2023.03.21
```

### 2. käivita lemmatiseerija demo sisaldav konteiner (suhtleb lemmatiseerija konteineriga)

Selleks laadi vastav konteiner alla:
  
```cmdline
docker pull tilluteenused/demo_lemmatiseerija:2023.03.21
```

Käivita konteiner:

```cmdline
# lemmatiseerija http://LEMMATIZER_IP:LEMMATIZER_PORT/process
docker run -p 7777:7777 --env LEMMATIZER_IP=$(hostname -I | sed 's/^\([^ ]*\) .*$/\1/') --env LEMMATIZER_PORT=7000 tilluteenused/demo_lemmatiseerija:2023.03.21
```

Märkus: Võite konteineri ka [lähtekoodist](https://github.com/estnltk/smart-search/tree/main/demo_lemmatiseerija) ise teha. Selleks peate ellnevalt:

* Allalaadima lähtekoodi

  ```commandline
  mkdir ~/git ; cd ~/git 
  git clone --depth 1 https://github.com/estnltk/smart-search.git smart_search_github
  ```

* Ehitama konteineri

  ```commandline
  cd ~/git/smart_search_github/lemmatiseerija
  docker build -t tilluteenused/lemmatiseerija:2023.03.21 .
  ```

* Käivitage tehtud konteiner ülalkirjeldatud viisil.

## Lemmatiseerija demo veebilehe kasutamine

### Leiame otsingusõnedest tuletatud päringu

Sisestatud otsingusõnede põhjal leitakse lemmade kombinatsioon, mida otsimootor peaks
hakkama tekstist otsima.

Sisestage veebibrauserisse aadress
```http://localhost:7777/paring```, avanenud veebilehel tekstikasti otsingusõned ja klikkige ```Leia päringule vastav lemmade kombinatsioon```.
Teile kuvatakse otsingusõnele vastav päring (lemmade kombinatsioon).

Näiteks:
```(katus & profiil) ⇒ (katt ∨ katus) & (profiil)```

Antud näite korral tekstis peab esinema sõne mille algvorm on üks kahest ```katt``` või ```katus``` ja samal ajal peab tekstis esinema sõne, mille algvorm on ```profiil```.

Ekraanitõmmised:

* [Pilt 1](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_demo_lemmatiseerija_paring1.png)
* [Pilt 2](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_demo_lemmatiseerija_paring2.png)

### Näita lemmatiseerija JSON-väljundit

Sisestage veebibrauserisse aadress
```http://localhost:7777/json``` avanenud veebilehel tekstikasti otsingusõne
ja klikkuge ```Kuva lemmatiseerija JSON-väljund```.
Teile kuvatekse lemmatiseerija algne [JSONväljund](https://github.com/estnltk/smart-search/blob/main/lemmatiseerija/README-CLOUD.md)

Ekraanitõmmised:

* [Pilt 1](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_demo_lemmatiseerija_json1.png)
* [Pilt 2](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_demo_lemmatiseerija_json2.png)

### 3.3 Näita sisendsõne kõiki võimalikke lemmasid (mitme võimaliku lemma korral komadega eraldatult)

Sisestage veebibrauserisse aadress
```http://localhost:7777/lemmad```, avanenud veebilehel tekstikasti sõne ja klikkige ```Lemmatiseeri```.
Teile kuvatakse sõnele vastavad algvormid (lemmade).

Näiteks: ```peeti ⇒ peet, pidama```

Sõnal ```peeti``` on kaks võimalikku algvormi: ```peet``` ja ```pidama```.

Ekraanitõmmised:

* [Pilt 1](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_demo_lemmatiseerija_lemmad1.png)
* [Pilt 2](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_demo_lemmatiseerija_lemmad2.png)

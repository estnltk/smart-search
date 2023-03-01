# DEMOLEHT

* käivita lemmatiseerija konteiner (konteiner peab olema tehtud/allalaaditud)

    ```cmdline
    docker run -p 7000:7000 tilluteenused/normaliseerija
    ```

* käivita demo otsingumootor

  * Pyytoni programm käsurealt

  ```cmdline
  cd ~/git/smart_search_github/töövoog_alpha/veebileht
  ./demo_smartsearch_webpage.py
  ```

  * Dockeri konteiner(konteiner peab olema tehtud/allalaaditud, LEMMATIZER_IP väärtuseks pange lemmatiseerija konteineri tegelik IP)

  ```cmdline
  docker run --env LEMMATIZER_IP=192.168.0.122 -p 7777:7777 tilluteenused/demo_smartsearch_webpage
  ```

* Käivita veebibrauser
  
  * Näita tekste mille hulgast saame otsida

  ```cmdline
  google-chrome http://localhost:7777/tekstid
  ```

  * Märksõnade järgi otsimine. Ei otsi päringusõnasid liitsõna osasõnadest.

  ```cmdline
  google-chrome http://localhost:7777/otsi
  ```
  * Märksõnade järgi otsimine. Otsi päringusõnasid ka liitsõna osasõnadest. Ei otsi liitsõnasid pikematest liitsõnadest (näiteks: ei vaata kas "raudtee" sisaldub "allmaaraudtees").

  ```cmdline
  google-chrome http://localhost:7777/otsils


# DEMOLEHT

* käivita lemmatiseerija konteiner (konteiner peab olema tehtud/allalaaditud)

    ```cmdline
    docker run -p 7000:7000 tilluteenused/lemmatiseerija
    ```

* käivita demo otsingumootor (käsurealt või konteinerist)

  * Pyytoni programm käsurealt

  ```cmdline
  cd ~/git/smart_search_github/töövoog_alpha/veebileht
  ./demo_smartsearch_webpage.py
  ```

  * Dockeri konteinerist
    * konteineri tegemine või allalaadimine
      * konteineri tegemine

      ```cmdline
      docker build -t tilluteenused/demo_smartsearch_webpage .
      ```

      * konteiner allalaadimine

      ```cmdline
      docker pull tilluteenused/demo_smartsearch_webpage
      ```

    * konteineri käivitamine

    ```cmdline
    # LEMMATIZER_IP väärtuseks peab olema lemmatiseerija konteineri tegelik IP
    docker run --env LEMMATIZER_IP=192.168.0.122 -p 7070:7070 tilluteenused/demo_smartsearch_webpage
    ```

* Käivita veebibrauser
  
  * Näita tekste mille hulgast saame otsida

  ```cmdline
  google-chrome http://localhost:7070/tekstid
  ```

  * Märksõnade järgi otsimine. Ei otsi päringusõnasid liitsõna osasõnadest.

  ```cmdline
  google-chrome http://localhost:7070/otsi
  ```
  
  * Märksõnade järgi otsimine. Otsi päringusõnasid ka liitsõna osasõnadest. Ei otsi liitsõnasid pikematest liitsõnadest (näiteks: ei vaata kas "raudtee" sisaldub "allmaaraudtees").

  ```cmdline
  google-chrome http://localhost:7070/otsils
  ```

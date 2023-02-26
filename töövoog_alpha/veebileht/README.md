# DEMOLEHT

* käivita lemmatiseerija konteiner (konteiner peab olema tehtud/allalaaditud)

    ```cmdline
    docker run -p 7000:7000 tilluteenused/normaliseerija
    ```

* käivita demo otsingumootor (konteiner peab olema tehtud/allalaaditud, LEMMATIZER_IP väärtuseks pange lemmatiseerija konteineri tegelik IP)

    ```cmdline
    docker run --env LEMMATIZER_IP=192.168.0.122 -p 6699:7777 tilluteenused/demo_smartsearch_webpage
    ```

* Käivita veebibrauser
  
  * Näita tekste mille hulgast saame otsida

  ```cmdline
  google-chrome http://localhost:6699/tekstid
  ```

  * Märksõnade järgi otsimine (järgi veebilehe juhendeid)

  ```cmdline
  google-chrome http://localhost:6699/otsi
  ```


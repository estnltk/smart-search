# LEMMATISEERIJA DEMOLEHT

* käivita lemmatiseerija konteiner (konteiner peab olema tehtud/allalaaditud)

    ```cmdline
    docker run -p 7000:7000 tilluteenused/lemmatizer
    ```

* käivita lemmatiseerija konteineriga suhtlev veebiserver

  ```cmdline
  cd demo_veebileht ; ./demo_lemmatiseerija.py
  ```

  ***Märkus*** Pythoni pakett requests peab eelnevalt olema installitud, ubuntu korral:

  ```cmdline
  sudo apt install -y python3-requests
  ```

* Ava brauseris ```localhost:7777/lemmad``` ja järgi brauseris avanenud veebilehe juhiseid, näiteks:

    ```cmdline
    google-chrome http://localhost:7777/lemmad
    ```

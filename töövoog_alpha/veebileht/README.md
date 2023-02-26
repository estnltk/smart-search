# NORMALISEERIJA DEMOLEHT

* käivita lemmatiseerija konteiner (konteiner peab olema tehtud/allalaaditud)

    ```cmdline
    docker run -p 7000:7000 tilluteenused/normaliseerija
    ```

* käivita lemmatiseerija konteineriga suhtlev veebiserver (pythoni skript või dockeri konteiner)
  * veebiserver pythoni programmist

  ```cmdline
  cd demo_normaliseerija ; ./demo_normaliseerija.py
  ```

  ***Märkus*** Pythoni pakett requests peab eelnevalt olema installitud, ubuntu korral:

  ```cmdline
  sudo apt install -y python3-requests
  ```

  * veebiserver dockeri konteinerist

  ```cmdline
  docker build -t tilluteenused/demo_normaliseerija .
  docker run -p 7777:7777 tilluteenused/demo_normaliseerija
  # lemmatiseerija http://LEMMATIZER_IP:LEMMATIZER_PORT/process
  docker run -p 7777:7777 --env LEMMATIZER_IP=IP --env LEMMATIZER_PORT=PORT tilluteenused/demo_normaliseerija
  ```

* Ava brauseris ```localhost:7777/lemmad``` ja järgi brauseris avanenud veebilehe juhiseid, näiteks:

    ```cmdline
    google-chrome http://localhost:7777/lemmad
    ```


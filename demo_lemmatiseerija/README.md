# LEMMATISEERIJA DEMOLEHT

## 1 käivita lemmatiseerija konteiner ([konteiner peab olema tehtud/allalaaditud](https://github.com/estnltk/smart-search/blob/main/lemmatiseerija/README.md))

```cmdline
docker run -p 7000:7000 tilluteenused/demo_lemmatiseerija
```

## 2 käivita lemmatiseerija konteineriga suhtlev veebiserver (pythoni skript või dockeri konteiner)
  
### 2.1 veebiserver pythoni programmist

```cmdline
cd demo_lemmatiseerija
LEMMATIZER_IP=localhost LEMMATIZER_PORT=7000 ./demo_lemmatiseerija.py
```

***Märkus*** Pythoni pakett requests peab eelnevalt olema installitud, ubuntu korral:

```cmdline
sudo apt install -y python3-requests
```

### 2.2 veebiserver dockeri konteinerist

#### 2.2.1 konteineri ise ehitamine

```cmdline
docker build -t tilluteenused/demo_lemmatiseerija .
```

### 2.2.2 valmis konteineri allalaadimine

```cmdline
docker pull tilluteenused/demo_lemmatiseerija
```

### 2.3 konteineri käivitamine

```cmdline
# lemmatiseerija http://LEMMATIZER_IP:LEMMATIZER_PORT/process
docker run -p 7777:7777 --env LEMMATIZER_IP=IP --env LEMMATIZER_PORT=7000 tilluteenused/demo_lemmatiseerija
```

## 3 Brauseris lemmatiseerija veebilehe avamine

### 3.1 Näita sisendsõnedest tuletatud päringut

Ekraanitõmmised:

* [Pilt 1](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_demo_lemmatiseerija_paring1.png)
* [Pilt 2](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_demo_lemmatiseerija_paring2.png)

```cmdline
google-chrome http://localhost:7777/paring
```

### 3.2 Näita lemmatiseerija JSON-väljundit

Ekraanitõmmised:

* [Pilt 1](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_demo_lemmatiseerija_json1.png)
* [Pilt 2](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_demo_lemmatiseerija_json2.png)

```cmdline
google-chrome http://localhost:7777/json
```

### 3.3 Näita sisendsõne lemmasid (mitme võimaliku lemma korral komadega eraldatult)

Ekraanitõmmised:

* [Pilt 1](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_demo_lemmatiseerija_lemmad1.png)
* [Pilt 2](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_demo_lemmatiseerija_lemmad2.png)

```cmdline
google-chrome http://localhost:7777/lemmad
```

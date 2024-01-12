# Eesti keele morfoloogilise analüsaatori konteiner [tilluteenused/smart_search_api_sl_analyser:2023.11.21]

[Filosofti eesti keele morfoloogilist analüsaatorit](https://github.com/Filosoft/vabamorf/tree/master/apps/cmdline/vmetajson) sisaldav tarkvara-konteiner.

## Mida sisaldab <a name="Mida_sisaldab"></a>

* [Filosofti eesti keele morfoloogiline analüsaator](https://github.com/Filosoft/vabamorf/tree/master/apps/cmdline/vmetajson)
* Konteineri ja liidesega seotud lähtekood

## Eeltingimused

* Peab olema paigaldatud tarkvara konteineri tegemiseks/kasutamiseks; juhised on [docker'i veebilehel](https://docs.docker.com/).
* Kui sooviks on lähtekoodi ise kompileerida või konteinerit kokku panna, siis peab olema paigaldatud versioonihaldustarkvara; juhised on [git'i veebilehel](https://git-scm.com/).

## Konteineri allalaadimine Docker Hub'ist

Valmis konteineri saab laadida alla Docker Hub'ist, kasutades Linux'i käsurida (Windows'i/Mac'i käsurida on analoogiline):

```commandline
docker pull tilluteenused/smart_search_api_analyser:2024.01.11
```

Seejärel saab jätkata osaga [Konteineri käivitamine](#Konteineri_käivitamine).

## Ise konteineri tegemine

### 1. Lähtekoodi allalaadimine

```commandline
mkdir -p ~/git; cd ~/git
git clone https://github.com/smart-search.git smart_search_github
```

Repositoorium sisaldab kompileeritud [Filosofti morfoloogilist analüsaatorit](https://github.com/Filosoft/vabamorf/blob/master/apps/cmdline/vmetajson/README.md) ja andmefaile:

* **_vmetajson_** morfoloogilise analüüsi programm.
* **_et.dct_** programmi poolt kasutatav leksikon.

Kui soovite ise programmi (**_vmetajson_**) kompileerida või leksikoni (**_et.dct_**) täiendada/muuta ja uuesti kokku panna, 
vaadake sellekohast [juhendit](https://github.com/Filosoft/vabamorf/blob/master/doc/programmid_ja_sonastikud.md).

### 2. Konteineri kokkupanemine

```commandline
cd ~/git/smart_search_github/api/analyser
docker build -t tilluteenused/smart_search_api_analyser:2024.01.11 .
```

## Konteineri käivitamine <a name="Konteineri_käivitamine"></a>

```commandline
docker run -p 7007:7007 tilluteenused/smart_search_api_analyser:2024.01.11
```

Käivitatud konteineri töö lõpetab Ctrl+C selles terminaliaknas, kust konteiner käivitati.

## Päringu json-kuju

Tasub tähele panna, et Python'i json'i teek esitab teksti vaikimisi ASCII kooditabelis;
täpitähed jms esitatakse Unicode'i koodidena, nt. õ = \u00f5.

### Variant 1

Sisendiks on tühikuga eraldatud sõnede string.

```json
{
  "content": string, /* Tühikuga eraldatud sõnede loend. Ei võimalda lipu --guesspropnames kasutamist */
}                    /* Iga tühikuga eraldatud sõne analüüsitakse eraldi, sõne sees ei saa olla tühik. */
```

### Variant 2

Sisendiks on tabulatsiooniga eraldatud sõnede string.
Sõnestaja võib võtta mitu tühikuga eraldatus stringi kokku üheks analüüsitavaks sõneks (näit telefoni number).
Et selliseid tühikut sisaldavaid sõnesid saaks morf analüsaatorile analüüsimiseks anda
on sõnede vaheliseks eraldajaks võetud tabulatsioon ja sõne sees tohib olla tühik(uid).

```json
{
  "tss": string, /* Tabulaatoriga eraldatud sõnede loend. Ei võimalda lipu --guesspropnames kasutamist */
}                /* Iga tabulatsiooniga eraldatud sõne (mis võib sisaldada tühikut) analüüsitakse eraldi */
```

### Variant 3

Sisendiks on lausestatud ja sõnestatud tekst. Selle tegemiseks saab kasutada [lausestamise-sõnestamise konteinerit](https://github.com/Filosoft/vabamorf/tree/master/docker/flask_vmetajson).

```json
{
    "content": string,  /* algne tekst, võib puududa */
    "annotations":
    {
    "sentences":        /* lausete massiiv, võib puududa, kui ei kasuta --guesspropnames lippu */
    [
        {
            "start": number,  /* lause alguspositsioon algses tekstis, võib puududa */
            "end": number,    /* lause lõpupositsioon  algses tekstis, võib puududa */
            "features":
            {
                "start": number, /* lause algusindeks tokens'ite massivis */
                "end": number,   /* lause lõpuindeks tokens'ite massivis */
            }
        }
    ],
    "tokens":           /* sõnede massiiv */
    [
        {
            "start": number,  /* sõne alguspositsioon algses tekstis, võib puududa */
            "end": number,    /* sõne lõpupositsioon  algses tekstis, võib puududa */
            "features":
            {
                "token": string,  /* sõne, võib sisaldada tühikut */
            }
        }
    ],
}
```

## Vastuse json-kuju

```json
{
    "tss": string,      /* tabulatsiooniaga eraldatud sõned, ainult siis, kui see sisendis ka oli */
    "content": string,  /* algne tekst, ainult siis, kui see sisendis ka oli */
    "annotations":
    {
    "sentences":        /* lausete massiiv, ainult siis, kui see sisendis ka oli */
    [
        {
            "start": number,  /* lause alguspositsioon algses tekstis, võib puududa */
            "end": number,    /* lause lõpupositsioon  algses tekstis, võib puududa */
            "features":
            {
                "start": number, /* lause algusindeks tokens'ite massivis */
                "end": number,   /* lause lõpuindeks tokens'ite massivis */
            }
        }
    ],
    "tokens":           /* sõnede massiiv */
    [
        {
            "start": number,  /* sõne alguspositsioon algses tekstis, võib puududa */
            "end": number,    /* sõne lõpupositsioon  algses tekstis, võib puududa */
            "features":
            {
                "token": SÕNE,  /* algne morf analüüsitav sõne */
                "classic": str, /* sõne morf analüüsistring vmeta-kujul, ainult --classic lipu korral */
                "complexity": KEERUKUS,
                "mrf" :           /* sisendsõne analüüsivariantide massiiv */
                [
                    {
                        "lisamärkideta": LISAMÄRKIDETA_TÜVI_VÕI_LEMMA,  /* kui ei sisaldanud lisamärke == "lemma_ma" */
                        "komponendid": [LIITSÕNA_OSASÕNEDE_MASSIIV],    /* kui ei olnud liitsaõna, siis [] */
                        "stem":     TÜVI,     /* --stem lipu korral */
                        "lemma":    LEMMA,    /* --stem lipu puudumise korral */
                        "lemma_ma": LEMMA_MA, /* --stem lipu puudumise korral, verbilemmale on lisatud ```ma```, muudel juhtudel sama mis LEMMA */
                        "ending":   LÕPP,    
                        "kigi":     KIGI,
                        "pos":      SÕNALIIK,
                        "fs":       KATEGOORIAD,
                        "gt":       KATEGOORIAD,  /* --gt lipu korral */
                        "source":   ALLIKAS,      /* P:põhisõnastikust, L:lisasõnastikust, O:sõnepõhisest oletajast, S:lausepõhisest oletajast, X:ei tea kust */
                    }
                ],                
            }
        }
    ],
}
```

Morf analüüsi tulemuste selgutust vaata programmi [vmetajson](https://github.com/Filosoft/vabamorf/blob/master/apps/cmdline/vmetajson/README.md) kirjeldusest.

## Kasutusnäide

Kui kasutame kohalikus masinas töötavat konteinerit:

```bash
export HOST4ANALYSER='localhost:7007'
```

Kui kasutame TÜ pilves töötavat konteinerit:

```bash
export HOST4ANALYSER='https://smart-search.tartunlp.ai'
```


### Näide 1

Analüüsime tabulatsiooniga eraldatud sõnesid. Väljundisse analüüsitavate 
sõnede tüved, lõpud jms. Leksikonist puuduvate sõnede võimalikud analüüsid
oletame sõnakujust lähtuvalt.

```bash
curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--stem", "--guess"]} ,"tss":"punameremaoga\tlambiõliga\tpeeti\t_a"}' \
        ${HOST4ANALYSER}/api/analyser/process | jq       
```

```json
{
  "annotations": {
    "tokens": [
      {
        "features": {
          "complexity": 6,
          "mrf": [
            {
              "ending": "ga",
              "fs": "sg kom",
              "kigi": "",
              "komponendid": [
                "puna",
                "mere",
                "mao"
              ],
              "lisamärkideta": "punameremao",
              "pos": "S",
              "source": "P",
              "stem": "puna_mere_mao"
            }
          ],
          "token": "punameremaoga"
        }
      },
      {
        "features": {
          "complexity": 1,
          "mrf": [
            {
              "ending": "ga",
              "fs": "sg kom",
              "kigi": "",
              "komponendid": [
                "lambi",
                "õli"
              ],
              "lisamärkideta": "lambiõli",
              "pos": "S",
              "source": "P",
              "stem": "lambi_õli"
            }
          ],
          "token": "lambiõliga"
        }
      },
      {
        "features": {
          "complexity": 1,
          "mrf": [
            {
              "ending": "ti",
              "fs": "ti",
              "kigi": "",
              "komponendid": [],
              "lisamärkideta": "pee",
              "pos": "V",
              "source": "P",
              "stem": "pee"
            },
            {
              "ending": "0",
              "fs": "adt",
              "kigi": "",
              "komponendid": [],
              "lisamärkideta": "peeti",
              "pos": "S",
              "source": "P",
              "stem": "peeti"
            },
            {
              "ending": "0",
              "fs": "sg p",
              "kigi": "",
              "komponendid": [],
              "lisamärkideta": "peeti",
              "pos": "S",
              "source": "P",
              "stem": "peeti"
            }
          ],
          "token": "peeti"
        }
      },
      {
        "features": {
          "complexity": 0,
          "mrf": [
            {
              "ending": "0",
              "fs": "?",
              "kigi": "",
              "komponendid": [],
              "lisamärkideta": "a",
              "pos": "Y",
              "source": "O",
              "stem": "a"
            }
          ],
          "token": "_a"
        }
      }
    ]
  },
  "params": {
    "vmetajson": [
      "--stem",
      "--guess"
    ]
  },
  "tss": "punameremaoga\tlambiõliga\tpeeti\t_a"
}
```

### Näide 2

Analüüsime tabulatsiooniga eraldatud sõnesid. Väljundisse analüüsitavate 
sõnede lemmad, lõpud jms. Leksikonist puuduvate sõnede võimalikud analüüsid
oletame sõnakujust lähtuvalt.

```bash
curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"vmetajson":["--guess"]} ,"tss":"punameremaoga\tlambiõliga\tpeeti\t_a"}' \
        ${HOST4ANALYSER}/api/analyser/process | jq       
```

```json
{
  "annotations": {
    "tokens": [
      {
        "features": {
          "complexity": 6,
          "mrf": [
            {
              "ending": "ga",
              "fs": "sg kom",
              "kigi": "",
              "komponendid": [
                "puna",
                "mere",
                "madu"
              ],
              "lemma": "puna_mere_madu",
              "lemma_ma": "puna_mere_madu",
              "lisamärkideta": "punameremadu",
              "pos": "S",
              "source": "P"
            },
            {
              "ending": "ga",
              "fs": "sg kom",
              "kigi": "",
              "komponendid": [
                "puna",
                "mere",
                "magu"
              ],
              "lemma": "puna_mere_magu",
              "lemma_ma": "puna_mere_magu",
              "lisamärkideta": "punameremagu",
              "pos": "S",
              "source": "P"
            }
          ],
          "token": "punameremaoga"
        }
      },
      {
        "features": {
          "complexity": 1,
          "mrf": [
            {
              "ending": "ga",
              "fs": "sg kom",
              "kigi": "",
              "komponendid": [
                "lambi",
                "õli"
              ],
              "lemma": "lambi_õli",
              "lemma_ma": "lambi_õli",
              "lisamärkideta": "lambiõli",
              "pos": "S",
              "source": "P"
            }
          ],
          "token": "lambiõliga"
        }
      },
      {
        "features": {
          "complexity": 1,
          "mrf": [
            {
              "ending": "0",
              "fs": "adt",
              "kigi": "",
              "komponendid": [],
              "lemma": "peet",
              "lemma_ma": "peet",
              "lisamärkideta": "peet",
              "pos": "S",
              "source": "P"
            },
            {
              "ending": "ti",
              "fs": "ti",
              "kigi": "",
              "komponendid": [],
              "lemma": "pida",
              "lemma_ma": "pidama",
              "lisamärkideta": "pidama",
              "pos": "V",
              "source": "P"
            },
            {
              "ending": "0",
              "fs": "sg p",
              "kigi": "",
              "komponendid": [],
              "lemma": "peet",
              "lemma_ma": "peet",
              "lisamärkideta": "peet",
              "pos": "S",
              "source": "P"
            }
          ],
          "token": "peeti"
        }
      },
      {
        "features": {
          "complexity": 0,
          "mrf": [
            {
              "ending": "0",
              "fs": "?",
              "kigi": "",
              "komponendid": [],
              "lemma": "a",
              "lemma_ma": "a",
              "lisamärkideta": "a",
              "pos": "Y",
              "source": "O"
            }
          ],
          "token": "_a"
        }
      }
    ]
  },
  "params": {
    "vmetajson": [
      "--guess"
    ]
  },
  "tss": "punameremaoga\tlambiõliga\tpeeti\t_a"
}
```

## Vaata lisaks

* [Eesti keele lausestaja-sõnestaja konteiner](https://github.com/Filosoft/vabamorf/tree/2022_09_09/docker/flask_estnltk_sentok)
* [Eesti keele morfoloogilise analüsaatori konteiner](https://github.com/Filosoft/vabamorf/tree/2022_09_09/docker/flask_vmetajson)

## Autorid

Konteineri autorid: Tarmo Vaino, Heiki-Jaan Kaalep

Konteineri sisu autoreid vt. jaotises [Mida sisaldab](#Mida_sisaldab) toodud viidetest.

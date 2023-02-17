# Eestikeelsete sõnede normaliseerija

## Mida sisaldab <a name="Mida_sisaldab"></a>

* [Filosofti eesti keele lemmatisaatorit](https://github.com/Filosoft/vabamorf/tree/master/apps/cmdline/vmetltjson) ```vmetltjson``` ja sõnastik ```et.dct```.
* Konteineri ja liidesega seotud lähtekoodi

<!---
## Konteineri allalaadimine Docker Hub'ist

Valmis konteineri saab laadida alla Docker Hub'ist, kasutades Linux'i käsurida (Windows'i/Mac'i käsurida on analoogiline):

```commandline
docker pull tilluteenused/lemmatizer
```

Seejärel saab jätkata osaga [Konteineri käivitamine](#Konteineri_käivitamine).
--->

## Konteineri allalaadimine Docker Hub'ist

Valmis konteineri saab laadida alla Docker Hub'ist, kasutades Linux'i käsurida (Windows'i/Mac'i käsurida on analoogiline):

```commandline
# TODO
# docker pull tilluteenused/normaliseerija
```

Seejärel saab jätkata osaga [Konteineri käivitamine](#Konteineri_käivitamine).

## Ise konteineri tegemine

### Lähtekoodi allalaadimine

<!---
Lähtekood koosneb 2 osast
1. json liides, veebiserver ja konteineri tegemise asjad
2. FSi lemmatisaator
---->

```commandline
mkdir ~/git ; cd ~/git 
git clone --depth 1 https://github.com/estnltk/smart-search.git smart-search_github
```

Repositoorium sisaldab kompileeritud [Filosofti morfoloogilist lemmatisaatorit](https://github.com/Filosoft/vabamorf/tree/master/apps/cmdline/vmetltjson) ja andmefaile:

* **_vmetltjson_** lemmatisaator
* **_et.dct_** programmi poolt kasutatav leksikon.

Kui soovite ise programmi (**_vmetltjson_**) kompileerida või leksikoni (**_et.dct_**) täiendada/muuta ja uuesti kokku panna,
vaadake sellekohast [juhendit](https://github.com/Filosoft/vabamorf/blob/master/doc/programmid_ja_sonastikud.md).

### Konteineri kokkupanemine

```commandline
cd ~/git/smart-search_github/normaliseerija
docker build -t tilluteenused/normaliseerija .
```

## Konteineri käivitamine <a name="Konteineri_käivitamine"></a>

```commandline
docker run -p 7000:7000 tilluteenused/normaliseerija
```

Käivitatud konteineri töö lõpetab Ctrl+C selles terminaliaknas, kust konteiner käivitati.

## Päringu json-kuju

Tasub tähele panna, et Python'i json'i teek esitab teksti vaikimisi ASCII kooditabelis;
täpitähed jms esitatakse Unicode'i koodidena, nt. õ = \u00f5.

```json
{
  "content": string, /* Tühikuga eraldatud lemmatiseeritavate sõnede loend. */
  "params": {"vmetltjson":["parameetrid",...]}
}
```

* Parameetrite kohta vaata [Lemmatisaatori kirjeldust](https://github.com/Filosoft/vabamorf/edit/master/apps/cmdline/vmetltjson/LOEMIND.md).
* Konteineris olev lemmatiseerija käivitatakse vaikimisi ```--guess``` lipuga (vt
[lemmatiseerja kirjaldust](https://github.com/Filosoft/vabamorf/edit/master/apps/cmdline/vmetltjson/LOEMIND.md))

## Vastuse json-kuju

Kui programmi töö katkes töö jätkamist mittevõimaldava vea tõttu on väljund kujul:

```json
{
  "failure":{"errors":["array of status messages"]}
  ... /* algne sisendjson, kui vea tekkimise hetkeks oli sisendjson õnnestunult parsitud */
}
```

Kui sisend-jsoni  käsitlemine polnud mingi veasituatsiooni tõttu võimalik, aga programm on valmis järgmisi päringuid käsitlema, on väljundjson kujul:

```json
{
  "warnings":["array of status messages"],
  ... /* algne sisendjson, kui vea tekkimise hetkeks oli sisendjson õnnestunult parsitud */
}
```

Väljundis JSONi sõnedele lisatakse lemmaga seotud info. Muus osas sjääb sisen-JSON samaks.
Kui sõne ei õnnestunud lemmatiseerida, siis selle sõne juurde lemmaga seotud väljasid ei lisata.

```json
{
  "content": string, /* Tühikuga eraldatud lemmatiseeritavate sõnede loend. */
  "params": {"vmetltjson":["parameetrid",...]},
  "annotations":    
  {
    "features":
    {
        "tokens":
        [
            {
                "token": SÕNE,  /* algne morf analüüsitav sõne */
                "complexity": KEERUKUS,
                "mrf" :           /* sisendsõne lemmade massiiv */
                [
                    {
                        "lemma":    LEMMA,    /* lemma */
                        "lemma_ma": LEMMA_MA, /* verbilemmale on lisatud ```ma```, muudel juhtudel sama mis LEMMA */
                        "source":   ALLIKAS,  /* P:põhisõnastikust, L:lisasõnastikust, O:sõnepõhisest oletajast, S:lausepõhisest oletajast, X:ei tea kust */
                    }
                ]
            }
        ]
    }
  }
}
```

Täpsemalt vaata näiteid.

### ```SÕNE``` <a name=mrf_sone>

Lemmatiseeritav sõne. Sõnega kleepunud punktuatsiooni ignoreeritakse. Reeglina peaks sõnaga kokkukleepunud punktuatsioon olema eelneva sõnestamise/lausestamise 
käigus juba lahkutõstetud.

### ```LEMMA``` <a name="mrf_LEMMA"></a>

Algvorm. Kui sõna on liitmoodustis, siis eelnevast komponente eraldab alakriips ```_``` ja järelliidet võrdusmärk ```=```.
Liitsõna puhul on ainult viimane  komponent algvormina.

###  ```LEMMA_MA``` <a name="mrf_LEMMA"></a>

Verbi lemmadele on lisatud ```ma```, muudel juhtudel ```LEMMA```.

### ```ALLIKAS```

**_"P"_** - põhisõnastikust, **_"L"_** - lisasõnastikust, **_"O"_** - sõnepõhisest oletajast, **_"S"_** - lausepõhisest oletajast, **_"X"_** - määratlemata.

### ```KEERUKUS```

Numbriline hinnand sellele, kui "keeruline" oli sõne analüüsi leida. Suurem number tähistab "keerulisemat" analüüsi. (Näiteks liitsõna analüüs on lihtsõna analüüsist "keerulisem".)

## Kasutusnäited

### Lemmatiseerija sõnastikust puuduvate sõnade oletamisega

```cmdline
curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"peeti keaks"}' localhost:7000/process|jq
```

```json
{
  "annotations": {
    "tokens": [
      {
        "features": {
          "complexity": 1,
          "mrf": [
            {
              "lemma": "peet",
              "lemma_ma": "peet",
              "source": "P"
            },
            {
              "lemma": "pida",
              "lemma_ma": "pidama",
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
              "lemma": "kea",
              "lemma_ma": "kea",
              "source": "O"
            },
            {
              "lemma": "keaks",
              "lemma_ma": "keaks",
              "source": "O"
            }
          ],
          "token": "keaks"
        }
      }
    ]
  },
  "content": "peeti keaks"
}
```

### Lemmatiseerija sõnastikust puuduvate sõnade oletamiseta

```cmdline
curl --silent  --request POST --header "Content-Type: application/json" --data '{"content":"peeti keaks","params":{"vmetltjson":[]}}' localhost:7000/process|jq
```

```json
{
  "annotations": {
    "tokens": [
      {
        "features": {
          "complexity": 1,
          "mrf": [
            {
              "lemma": "peet",
              "lemma_ma": "peet",
              "source": "P"
            },
            {
              "lemma": "pida",
              "lemma_ma": "pidama",
              "source": "P"
            }
          ],
          "token": "peeti"
        }
      },
      {
        "features": {
          "token": "keaks"
        }
      }
    ]
  },
  "content": "peeti keaks",
  "params": {
    "vmetltjson": []
  }
}
```

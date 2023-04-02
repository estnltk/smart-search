# Eestikeelsete sõnede lemmatiseerija Tartu Ülikooli veebiteenusena

## Lähtekood

* [Filosofti eesti keele lemmatisaator](https://github.com/Filosoft/vabamorf/tree/master/apps/cmdline/vmetltjson).
* [Konteineri ja liidesega seotud lähtekood](https://github.com/estnltk/smart-search/tree/main/lemmatiseerija)

## Kasutusnäited

Näidetes on kasutatud käsurea programmi ```curl``` (olemas Linuxis, Windowsis ja Macis).
Pythoni puhul sobib päringute tegemiseks ```requests``` pakett.

### Lemmatiseerime sõnastikust puuduvate sõnade oletamisega

```cmdline
curl --silent  --request POST --header "Content-Type: application/json" --data "{\"content\":\"raudteed peeti keaks\"}" https://smart-search.tartunlp.ai/api/lemmatizer/process | jq
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
              "lemma_ma": "raud_tee",
              "pos": "S",
              "source": "P"
            }
          ],
          "token": "raudteed"
        }
      },
      {
        "features": {
          "complexity": 1,
          "mrf": [
            {
              "lemma_ma": "peet",
              "pos": "S",
              "source": "P"
            },
            {
              "lemma_ma": "pidama",
              "pos": "V",
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
              "lemma_ma": "kea",
              "pos": "S",
              "source": "O"
            },
            {
              "lemma_ma": "keaks",
              "pos": "S",
              "source": "O"
            }
          ],
          "token": "keaks"
        }
      }
    ]
  },
  "content": "raudteed peeti keaks",
}

```

### Lemmatiseerime sõnastikust puuduvate sõnade oletamiseta, lisaks küsime lemmatiseerimisprogrammi versiooni

```cmdline
curl --silent  --request POST --header "Content-Type: application/json" --data "{\"params\":{\"vmetltjson\":[\"--version\"]},\"content\":\"raudteed peeti keaks\"}" https://smart-search.tartunlp.ai/api/lemmatizer/process | jq

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
              "lemma_ma": "raud_tee",
              "pos": "S",
              "source": "P"
            }
          ],
          "token": "raudteed"
        }
      },
      {
        "features": {
          "complexity": 1,
          "mrf": [
            {
              "lemma_ma": "peet",
              "pos": "S",
              "source": "P"
            },
            {
              "lemma_ma": "pidama",
              "pos": "V",
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
  "content": "raudteed peeti keaks",
  "params": {
    "vmetltjson": [
      "--version"
    ]
  },
  "version": "2023.03.21"
}
```

### Lemmatiseerimisprogrammi veebiliidese versioon

```cmdline
curl --silent  --request POST --header "Content-Type: application/json"  https://smart-search.tartunlp.ai/api/lemmatizer/version | jq  
```

```json
{
  "version": "2023.03.21"
}
```

## Päringus kasutatava JSONi kirjeldus

Pilveteenus saab sisendinfo JSON-kujul.

```json
{
  "content": string, /* Tühikuga eraldatult lemmatiseeritad sõnede. */
  "params": {"vmetltjson":["parameetrid",...]}
}
```

**Märkused:**

* Tasub tähele panna, et Python'i JSONi teek esitab teksti vaikimisi ASCII kooditabelis;
  täpitähed jms esitatakse Unicode'i koodidena, nt. õ = \u00f5. Täpitähtede esitamiseks sobib ka UTF8.
  Tollimärgi, reavahetus jms sümbolite esitus peab vastama JSONformaadi nõuetele.

* Parameetrite kohta vaata [Lemmatisaatori kirjeldust](https://github.com/Filosoft/vabamorf/edit/master/apps/cmdline/vmetltjson/LOEMIND.md).

* Konteineris olev lemmatiseerija käivitatakse vaikimisi ```--guess``` lipuga (vt
[lemmatiseerja kirjeldust](https://github.com/Filosoft/vabamorf/edit/master/apps/cmdline/vmetltjson/LOEMIND.md))

## Vastuses kasutatava JSONi kirjeldus

Väljundis JSONi sõnedele lisatakse lemmaga seotud info. Muus osas sjääb sisen-JSON samaks.
Kui sõne ei õnnestunud lemmatiseerida, siis selle sõne juurde lemmaga seotud väljasid ei lisata.

```json
{
  "content": string, /* Tühikuga eraldatud lemmatiseeritavate sõnede loend. */
  "params": {"vmetltjson":["parameetrid",...]}, /* Pole kohustuslik osa */
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
                        "pos":    SÕNALIIK ,  /* sõnaliik */
                        "lemma_ma": LEMMA_MA, /* lemma, verbilemmal on lõpus ```ma``` */
                        "source":   ALLIKAS,  /* P:põhisõnastikust, L:lisasõnastikust, O:sõnepõhisest oletajast, X:ebamäärasest kohast */
                    }
                ]
            }
        ]
    }
  }
}
```

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

### ```SÕNE``` <a name=mrf_sone></a>

Lemmatiseeritav sõne. Sõnega kleepunud punktuatsiooni ignoreeritakse.
Reeglina peaks sõnaga kokkukleepunud punktuatsioon olema eelneva sõnestamise/lausestamise
käigus juba lahkutõstetud.

### ```SÕNALIIK``` <a name="mrf_LEMMA"></a>

Lemma (algvormi) sõnaliik. Vaata lähemalt: [Morfoloogilised kategooriad](https://github.com/Filosoft/vabamorf/blob/master/doc/kategooriad.md)

###  ```LEMMA_MA``` <a name="mrf_LEMMA"></a>

Lemma (algvorm). Kui sõna on liitmoodustis, siis eelnevast komponente eraldab alakriips ```_``` ja järelliidet võrdusmärk ```=```.
Liitsõna puhul on ainult viimane  komponent algvormina. Verbi lemmadel on lõpus ```ma```.

### ```ALLIKAS```

**_"P"_** - põhisõnastikust, **_"L"_** - lisasõnastikust, **_"O"_** - sõnepõhisest oletajast, **_"S"_** - lausepõhisest oletajast, **_"X"_** - määratlemata.

### ```KEERUKUS```

Numbriline hinnang sellele, kui "keeruline" oli sõne analüüsi leida. Suurem number tähistab "keerulisemat" analüüsi. Näiteks liitsõna analüüs on lihtsõna analüüsist "keerulisem". Hetkel me seda teadmist ei kasuta kuskil. On pigem igaks-juhuks, äkki läheb  hiljem vaja.

## Mida uut

* **_versioon 2023.03.21_**

  * lisatud võimalus küsida veebiliidest korraldava kestprogrammi versiooni:

  ```cmdline
  curl --silent  --request POST --header "Content-Type: application/json" localhost:7000/version|jq
  ```

  * Hoiatus, kui sisendjsonis puudub "content"
  

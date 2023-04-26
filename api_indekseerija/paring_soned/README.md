# Päringusõnede lemmatiseerimine ja neist morf. sünteesi abil sõnavormide päringu koostamine  [versioon 2023.04.24]

Kasutatud on:

* sõnestajat, punktuatsiooni jms sõnast lahkutõstmiseks ja kokkukleepunud sõnede lahutamiseks ("Sarved&Sõrad" -> "Sarved", "&", "Sõrad"),
  selleks et päringusõned oleksid indeksiga samamoodi tükeldatud.
* morfoloogilist analüsaatorit:
  * lemmade leidmiseks
  * ebaoluliste sõnede ignoreerimiseks:
    * punktuatsioon
    * asesõnad
    * sidesõnad
* morfoloogilist sünteesi lemmast kõigi (käändes/pöördes) sõnavormide genereerimiseks

## Päringu koostamise näited

Päringu kuju:

```json
{   "content": str // päringusõned
}
```

### Näide 1 - JSON-kujul päringu koostamine

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"content": "katus profiil"}' \
  https://smart-search.tartunlp.ai/api/paring-soned/json
```

```json
{
  "annotations": {
    "query": [
      [
        "katt",
        "katte",
        "kattu",
        "kattu",
        "kattude",
        "kattudega",
        "kattudeks",
        "kattudel",
        "kattudele",
        "kattudelt",
        "kattudena",
        "kattudeni",
        "kattudes",
        "kattudesse",
        "kattudest",
        "kattudeta",
        "kattusid",
        "katu",
        "katud",
        "katuga",
        "katuks",
        "katul",
        "katule",
        "katult",
        "katuna",
        "katuni",
        "katus",
        "katusse",
        "katust",
        "katuta",
        "katus",
        "katust",
        "katuste",
        "katustega",
        "katusteks",
        "katustel",
        "katustele",
        "katustelt",
        "katustena",
        "katusteni",
        "katustes",
        "katustesse",
        "katustest",
        "katusteta",
        "katuse",
        "katused",
        "katusega",
        "katuseid",
        "katuseiks",
        "katuseil",
        "katuseile",
        "katuseilt",
        "katuseina",
        "katuseini",
        "katuseis",
        "katuseisse",
        "katuseist",
        "katuseks",
        "katusel",
        "katusele",
        "katuselt",
        "katusena",
        "katuseni",
        "katuses",
        "katusesse",
        "katusest",
        "katuseta"
      ],
      [
        "profiil",
        "profiile",
        "profiileks",
        "profiilel",
        "profiilele",
        "profiilelt",
        "profiiles",
        "profiilesse",
        "profiilest",
        "profiili",
        "profiili",
        "profiili",
        "profiilid",
        "profiilide",
        "profiilidega",
        "profiilideks",
        "profiilidel",
        "profiilidele",
        "profiilidelt",
        "profiilidena",
        "profiilideni",
        "profiilides",
        "profiilidesse",
        "profiilidest",
        "profiilideta",
        "profiiliga",
        "profiiliks",
        "profiilil",
        "profiilile",
        "profiililt",
        "profiilina",
        "profiilini",
        "profiilis",
        "profiilisid",
        "profiilisse",
        "profiilist",
        "profiilita"
      ]
    ]
  },
  "content": "katus profiil"
}
```

### Näide 2 - Loogilise avaldise kujul päringu koostamine

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"content": "katus profiil"}' \
  https://smart-search.tartunlp.ai/api/paring-soned/text 
```

```text
(katt ∨ katte ∨ kattu ∨ kattu ∨ kattude ∨ kattudega ∨ kattudeks ∨ kattudel ∨ kattudele ∨ kattudelt ∨ kattudena ∨ kattudeni ∨ kattudes ∨ kattudesse ∨ kattudest ∨ kattudeta ∨ kattusid ∨ katu ∨ katud ∨ katuga ∨ katuks ∨ katul ∨ katule ∨ katult ∨ katuna ∨ katuni ∨ katus ∨ katusse ∨ katust ∨ katuta ∨ katus ∨ katust ∨ katuste ∨ katustega ∨ katusteks ∨ katustel ∨ katustele ∨ katustelt ∨ katustena ∨ katusteni ∨ katustes ∨ katustesse ∨ katustest ∨ katusteta ∨ katuse ∨ katused ∨ katusega ∨ katuseid ∨ katuseiks ∨ katuseil ∨ katuseile ∨ katuseilt ∨ katuseina ∨ katuseini ∨ katuseis ∨ katuseisse ∨ katuseist ∨ katuseks ∨ katusel ∨ katusele ∨ katuselt ∨ katusena ∨ katuseni ∨ katuses ∨ katusesse ∨ katusest ∨ katuseta) & (profiil ∨ profiile ∨ profiileks ∨ profiilel ∨ profiilele ∨ profiilelt ∨ profiiles ∨ profiilesse ∨ profiilest ∨ profiili ∨ profiili ∨ profiili ∨ profiilid ∨ profiilide ∨ profiilidega ∨ profiilideks ∨ profiilidel ∨ profiilidele ∨ profiilidelt ∨ profiilidena ∨ profiilideni ∨ profiilides ∨ profiilidesse ∨ profiilidest ∨ profiilideta ∨ profiiliga ∨ profiiliks ∨ profiilil ∨ profiilile ∨ profiililt ∨ profiilina ∨ profiilini ∨ profiilis ∨ profiilisid ∨ profiilisse ∨ profiilist ∨ profiilita)
```

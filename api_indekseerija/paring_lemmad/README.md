# Päringusõnede lemmatiseerimine ja neist lemma-päringu koostamine  [versioon 2023.04.21]

Kasutatud on:

* sõnestajat, punktuatsiooni jms sõnast lahkutõstmiseks ja kokkukleepunud sõnede lahutamiseks ("Sarved&Sõrad" -> "Sarved", "&", "Sõrad"),
  selleks et päringusõned oleksid indeksiga samamoodi tükeldatud.
* morfoloogilist analüsaatorit:
  * lemmade leidmiseks
  * ebaoluliste sõnede ignoreerimiseks:
    * punktuatsioon
    * asesõnad
    * sidesõnad

## Päringu koostamise näited

Päringu kuju:

```json
{   "content": str // päringusõned
}
```

### Näide 1 - JSON-kujul päringu koostamine

Märkused:

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"content": "katus profiil"}' \
  https://smart-search.tartunlp.ai/api/paring-lemmad/json
```

```json
{
  "annotations": {
    "query": [
      [             // esimese päringusõna lemmad, need ühendame loogilise võiga
        "katt",
        "katus"
      ],
      [
        "profiil"   // teise päringusõna lemmad, need ühendame loogilise või-ga
      ]
    ]               // esimese ja teise õhendame loogilise ja-ga
  },
  "content": "katus profiil"
}
```

### Näide 2 - Loogilise avaldise kujul päringu koostamine

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"content": "katus profiil"}' \
  https://smart-search.tartunlp.ai/api/paring-lemmad/text 
```

```text
(katt ∨ katus) & (profiil)
```

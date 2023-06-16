# Morfoloogise analüüsi veebiteenus

[JSON-sisendi kirjeldus](https://github.com/Filosoft/vabamorf/tree/master/docker/flask_vmetajson)

Päringu kuju

```commandline
curl --silent --request POST --header "Content-Type: application/json" --data JSON-DATA https://smart-search.tartunlp.ai/api/analyser/process
```

Näited:

* Morf analüüs koos üldkeelesõnastikust puuduvate sõnade oletamisega

```cmdline
curl --silent --request POST --header "Content-Type: application/json" --data "{\"params\": {\"vmetajson\": [\"--guess\"]}, \"content\":\"asendusteenistuslane teenistuslane teenistus asendusteenistus\"}" https://smart-search.tartunlp.ai/api/analyser/process | jq
```

```json
{
  "annotations": {
    "tokens": [
      {
        "features": {
          "complexity": 0,
          "mrf": [
            {
              "ending": "0",
              "fs": "sg n",
              "kigi": "",
              "lemma": "asendusteenistuslane",
              "lemma_ma": "asendusteenistuslane",
              "pos": "S",
              "source": "O"
            }
          ],
          "token": "asendusteenistuslane"
        }
      },
      {
        "features": {
          "complexity": 0,
          "mrf": [
            {
              "ending": "0",
              "fs": "sg n",
              "kigi": "",
              "lemma": "teenistuslane",
              "lemma_ma": "teenistuslane",
              "pos": "S",
              "source": "O"
            }
          ],
          "token": "teenistuslane"
        }
      },
      {
        "features": {
          "complexity": 1,
          "mrf": [
            {
              "ending": "0",
              "fs": "sg n",
              "kigi": "",
              "lemma": "teenistus",
              "lemma_ma": "teenistus",
              "pos": "S",
              "source": "P"
            }
          ],
          "token": "teenistus"
        }
      },
      {
        "features": {
          "complexity": 4,
          "mrf": [
            {
              "ending": "0",
              "fs": "sg n",
              "kigi": "",
              "lemma": "asendus_teenistus",
              "lemma_ma": "asendus_teenistus",
              "pos": "S",
              "source": "P"
            }
          ],
          "token": "asendusteenistus"
        }
      }
    ]
  },
  "content": "asendusteenistuslane teenistuslane teenistus asendusteenistus",
  "params": {
    "vmetajson": [
      "--guess"
    ]
  }
}
```

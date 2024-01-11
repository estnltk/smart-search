# Morfoloogiline lemmatiseerija

## Sisendi JSON-kuju

```json
{ "tss":string // Tabulatsiooniga eraldatud sisendsõned
}
```

## Väljundi TSV-kuju

Väljundi esimene rida sisaldab veerunimesid.
Veerud on:
* location -- sama numbriga ridadel on sama sisendsõne "input"
* token -- sisendsõne
* stem -- sisendsõne tüvi
* is_component
  * True -- lemmad on sisendsõnes sisalduva liitsõna osalemmad
  * False -- lemmad on terviksõne lemmad
* weight
  * 1 terviksõna korral
  * 1/(liitsõnakomponentide arv) iga liitsõna osasõna jaoks
* lemmas -- sisendsõne/osasõne võimalikud lemmad

## Kasutusnäited

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
    --data '{"tss":"kinnipeetuga\tpeeti\tallmaaraudteejaamas"}' \
    https://smart-search.tartunlp.ai/api/sl_lemmatizer/tsv
```

```tsv
location        token   stem    is_component    weight  lemmas
0       kinnipeetuga    kinnipeetu      False   1.0     ['kinnipeetu', 'kinnipeetud']
0       kinnipeetuga    kinni   True    0.5     ['kinni']
0       kinnipeetuga    peetu   True    0.5     ['peetu', 'peetud', 'peetuma']
1       peeti   pee     False   1.0     ['pee']
1       peeti   peeti   False   1.0     ['peet', 'pidama']
2       allmaaraudteejaamas     allmaaraudteejaama      False   1.0     ['allmaaraudteejaam']
2       allmaaraudteejaamas     all     True    0.2     ['all']
2       allmaaraudteejaamas     jaama   True    0.2     ['jaam']
2       allmaaraudteejaamas     maa     True    0.2     ['maa']
2       allmaaraudteejaamas     raud    True    0.2     ['raud']
2       allmaaraudteejaamas     tee     True    0.2     ['tegema', 'tee']
```

```cmdline
 curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/sl_lemmatizer/version | jq
```

```json
{
  "version": "2023.12.02"
}
```

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"kinnipeetuga\tpeeti\tallmaaraudteejaamas"}' \  
        https://smart-search.tartunlp.ai/api/sl_lemmatizer/json | jq
```

```json
{
  "allmaaraudteejaamas": {
    "all": {
      "component": true,
      "lemmas": [
        "all"
      ],
      "weight": 0.2
    },
    "allmaaraudteejaama": {
      "component": false,
      "lemmas": [
        "allmaaraudteejaam"
      ],
      "weight": 1
    },
    "jaama": {
      "component": true,
      "lemmas": [
        "jaam"
      ],
      "weight": 0.2
    },
    "maa": {
      "component": true,
      "lemmas": [
        "maa"
      ],
      "weight": 0.2
    },
    "raud": {
      "component": true,
      "lemmas": [
        "raud"
      ],
      "weight": 0.2
    },
    "tee": {
      "component": true,
      "lemmas": [
        "tegema",
        "tee"
      ],
      "weight": 0.2
    }
  },
  "kinnipeetuga": {
    "kinni": {
      "component": true,
      "lemmas": [
        "kinni"
      ],
      "weight": 0.5
    },
    "kinnipeetu": {
      "component": false,
      "lemmas": [
        "kinnipeetud",
        "kinnipeetu"
      ],
      "weight": 1
    },
    "peetu": {
      "component": true,
      "lemmas": [
        "peetuma",
        "peetud",
        "peetu"
      ],
      "weight": 0.5
    }
  },
  "peeti": {
    "pee": {
      "component": false,
      "lemmas": [
        "pee"
      ],
      "weight": 1
    },
    "peeti": {
      "component": false,
      "lemmas": [
        "peet",
        "pidama"
      ],
      "weight": 1
    }
  }
```
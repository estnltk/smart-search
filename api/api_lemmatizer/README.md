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

```bash
curl --silent --request POST --header "Content-Type: application/json" \
    --data '{"tss":"kinnipeetuga\tpeeti\tallmaaraudteejaamas"}' \
    https://smart-search.tartunlp.ai/api/lemmatizer/tsv
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

```bash
curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/lemmatizer/version | jq
```

```json
{
  "api_version": "2024.01.10",
  "flask_liidese_versiooon": "2024.01.10"
}
```

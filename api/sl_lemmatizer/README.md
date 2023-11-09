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
* input -- sisendsõne
* lemma -- sisendsõne lemma
* is_sublemma
  * True -- lemma on sisendsõnes sisalduva liitsõna osalemma
  * False -- lemma on terviksõne

## Kasutusnäited

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"kinnipeetuga\tpeeti\tallmaaraudteejaamas"}' \
        https://smart-search.tartunlp.ai/api/sl_lemmatizer/tsv   
location        input   lemma   is_sublemma
0       kinnipeetuga    kinni   True
0       kinnipeetuga    kinni   True
0       kinnipeetuga    kinnipeetu      False
0       kinnipeetuga    kinnipeetud     False
0       kinnipeetuga    peetu   True
0       kinnipeetuga    peetud  True
1       peeti   peet    False
1       peeti   pidama  False
2       allmaaraudteejaamas     all     True
2       allmaaraudteejaamas     allmaa  True
2       allmaaraudteejaamas     allmaaraud      True
2       allmaaraudteejaamas     allmaaraudtee   True
2       allmaaraudteejaamas     allmaaraudteejaam       False
2       allmaaraudteejaamas     jaam    True
2       allmaaraudteejaamas     maa     True
2       allmaaraudteejaamas     maaraud True
2       allmaaraudteejaamas     maaraudtee      True
2       allmaaraudteejaamas     maaraudteejaam  True
2       allmaaraudteejaamas     raud    True
2       allmaaraudteejaamas     raudtee True
2       allmaaraudteejaamas     raudteejaam     True
2       allmaaraudteejaamas     tee     True
2       allmaaraudteejaamas     teejaam True
```

```cmdline
 curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/sl_lemmatizer/version | jq
{
  "version": "2023.10.26"
}
```
# Morfoloogiline genereerija

## Sisendi JSON-kuju

```json
{   "tss":string,                // Tabulatsiooniga eraldatud sõned sünteesimiseks, soovitatavalt lemmad
    "params":["with_apostrophe"] // Võib puududa, genereerib lisaks vormid kus käändelõpp on eraldatud ülakoma ja miinusmärgiga. 
                                 // Lähtub sõne eestipärasest häälduskujust, Seega võõrsõnade korral võib genereerida täiesti valed vormis-lõpud. 
}
```

UTF8 kooditabelis on suur hulk erinevaid ülakomasid ja sidekriipse, kogu seda mitmekesisust siin ei arvestata.
See millised lõpud käivad ülakoma taha sõltub hääldusest, mitte kirjapildist.
Sünteesiprogramm ei tea võõrsõnade hääldusest midagi, seega on suur võimalus genereerida valed vormid.
Võõrsõnade puhul soovitus genereerida sarnaselt hääldatava muutüübiga eesti sõna vormid ja selle
tagant tõsta lõpud võõrsõna taha.

## Väljundi TSV-kuju

Väljundi esimeses read on veerunimed.

Veerud on:

* location -- sama numbriga read sisaldavad sama sisendsõna (genereerimse aluseks olevat lemmat)
* input -- genereerime aluseks oleva sõne (soovitatavalt lemma)
* stem  -- genereerutud sõnavormi tüvi (sellest on tuletatud (osa) vorme)
* wordform -- genereerutud sõnavorm

## Kasutusnäited

```bash
curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"tere\ttalv"}' \
        https://smart-search.tartunlp.ai/api/generator/tss
```

```tsv
location        input   stem    wordform
0       tere    tere    tere
0       tere    tere    tered
0       tere    tere    terede
0       tere    tere    teredega
0       tere    tere    teredeks
0       tere    tere    teredel
0       tere    tere    teredele
0       tere    tere    teredelt
0       tere    tere    teredena
0       tere    tere    teredeni
0       tere    tere    teredes
0       tere    tere    teredesse
0       tere    tere    teredest
0       tere    tere    teredeta
0       tere    tere    terega
0       tere    tere    tereks
0       tere    tere    terel
0       tere    tere    terele
0       tere    tere    terelt
0       tere    tere    terena
0       tere    tere    tereni
0       tere    tere    teres
0       tere    tere    teresid
0       tere    tere    teresse
0       tere    tere    terest
0       tere    tere    teret
0       tere    tere    tereta
1       talv    talv    talv
1       talv    talv    talvi
1       talv    talv    talviks
1       talv    talv    talvil
1       talv    talv    talvile
1       talv    talv    talvilt
1       talv    talv    talvis
1       talv    talv    talvisse
1       talv    talv    talvist
1       talv    talve   talve
1       talv    talve   talved
1       talv    talve   talvede
1       talv    talve   talvedega
1       talv    talve   talvedeks
1       talv    talve   talvedel
1       talv    talve   talvedele
1       talv    talve   talvedelt
1       talv    talve   talvedena
1       talv    talve   talvedeni
1       talv    talve   talvedes
1       talv    talve   talvedesse
1       talv    talve   talvedest
1       talv    talve   talvedeta
1       talv    talve   talvega
1       talv    talve   talveks
1       talv    talve   talvel
1       talv    talve   talvele
1       talv    talve   talvelt
1       talv    talve   talvena
1       talv    talve   talveni
1       talv    talve   talves
1       talv    talve   talvesid
1       talv    talve   talvesse
1       talv    talve   talvest
1       talv    talve   talveta
```

```bash
curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/generator/version
```

```json
{"version":"2023.11.33"}
```

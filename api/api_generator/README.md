# Morfoloogiline genereerija

## Sisendi JSON-kuju

```json
{   "tss":string, // Tabulatsiooniga eraldatud sõned sünteesimiseks, soovitatavalt lemmad
    "params":["with_apostrophe"] // võib puududa, genereerib lisaks vormid kus käändelõpp on eraldatud ülakoma ja miinusmärgiga. 
}

```

UTF8 kooditabelis on suur hulk erinevaid ülakomasid ja sidekriipse, kogu seda mitmekesisust siin ei arvestata.
See millised lõpud käivad ülakoma taha sõltub hääldusest, mitte kirjapildist.
Sünteesiprogramm ei tea hääldusest midagi, seega on suur võimalus.
Võõrsõnade puhul soovitus genereerida sarnaselt hääldatava eesti sõna vormid ja selle
tagant tõsta lõpud võõrsõna taha. 

## Väljundi TSV.kuju

Väljundi esimeses read on veerunimed.

Veerud on:
* location -- sama numbriga read sisaldavad sama sisendsõna (genereerimse aluseks olevat lemmat)
* input -- genereerime aluseks oleva sõne (soovitatavalt lemma)
* stem  -- genereerutud sõnavormi tüvi (sellest on tuletatud (osa) vorme)
* wordform -- genereerutud sõnavorm

## Kasutusnäited

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"tere\ttalv"}' \
        https://smart-search.tartunlp.ai/api/sl_generator/tss
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

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":["with_apostrophe"], "tss":"Strassbourg"}' \
        https://smart-search.tartunlp.ai/api/sl_generator/tss
location        input   stem    wordform
0       Strassbourg     Strassbourg     Strassbourg
0       Strassbourg     Strassbourg     Strassbourg'e
0       Strassbourg     Strassbourg     Strassbourg'eks
0       Strassbourg     Strassbourg     Strassbourg'el
0       Strassbourg     Strassbourg     Strassbourg'ele
0       Strassbourg     Strassbourg     Strassbourg'elt
0       Strassbourg     Strassbourg     Strassbourg'es
0       Strassbourg     Strassbourg     Strassbourg'esse
0       Strassbourg     Strassbourg     Strassbourg'est
0       Strassbourg     Strassbourg     Strassbourg-e
0       Strassbourg     Strassbourg     Strassbourg-eks
0       Strassbourg     Strassbourg     Strassbourg-el
0       Strassbourg     Strassbourg     Strassbourg-ele
0       Strassbourg     Strassbourg     Strassbourg-elt
0       Strassbourg     Strassbourg     Strassbourg-es
0       Strassbourg     Strassbourg     Strassbourg-esse
0       Strassbourg     Strassbourg     Strassbourg-est
0       Strassbourg     Strassbourg     Strassbourge
0       Strassbourg     Strassbourg     Strassbourgeks
0       Strassbourg     Strassbourg     Strassbourgel
0       Strassbourg     Strassbourg     Strassbourgele
0       Strassbourg     Strassbourg     Strassbourgelt
0       Strassbourg     Strassbourg     Strassbourges
0       Strassbourg     Strassbourg     Strassbourgesse
0       Strassbourg     Strassbourg     Strassbourgest
0       Strassbourg     Strassbourgi    Strassbourgi
0       Strassbourg     Strassbourgi    Strassbourgi'd
0       Strassbourg     Strassbourgi    Strassbourgi'de
0       Strassbourg     Strassbourgi    Strassbourgi'dega
0       Strassbourg     Strassbourgi    Strassbourgi'deks
0       Strassbourg     Strassbourgi    Strassbourgi'del
0       Strassbourg     Strassbourgi    Strassbourgi'dele
0       Strassbourg     Strassbourgi    Strassbourgi'delt
0       Strassbourg     Strassbourgi    Strassbourgi'dena
0       Strassbourg     Strassbourgi    Strassbourgi'deni
0       Strassbourg     Strassbourgi    Strassbourgi'des
0       Strassbourg     Strassbourgi    Strassbourgi'desse
0       Strassbourg     Strassbourgi    Strassbourgi'dest
0       Strassbourg     Strassbourgi    Strassbourgi'deta
0       Strassbourg     Strassbourgi    Strassbourgi'ga
0       Strassbourg     Strassbourgi    Strassbourgi'ks
0       Strassbourg     Strassbourgi    Strassbourgi'l
0       Strassbourg     Strassbourgi    Strassbourgi'le
0       Strassbourg     Strassbourgi    Strassbourgi'lt
0       Strassbourg     Strassbourgi    Strassbourgi'na
0       Strassbourg     Strassbourgi    Strassbourgi'ni
0       Strassbourg     Strassbourgi    Strassbourgi's
0       Strassbourg     Strassbourgi    Strassbourgi'sid
0       Strassbourg     Strassbourgi    Strassbourgi'sse
0       Strassbourg     Strassbourgi    Strassbourgi'st
0       Strassbourg     Strassbourgi    Strassbourgi'ta
0       Strassbourg     Strassbourgi    Strassbourgi-d
0       Strassbourg     Strassbourgi    Strassbourgi-de
0       Strassbourg     Strassbourgi    Strassbourgi-dega
0       Strassbourg     Strassbourgi    Strassbourgi-deks
0       Strassbourg     Strassbourgi    Strassbourgi-del
0       Strassbourg     Strassbourgi    Strassbourgi-dele
0       Strassbourg     Strassbourgi    Strassbourgi-delt
0       Strassbourg     Strassbourgi    Strassbourgi-dena
0       Strassbourg     Strassbourgi    Strassbourgi-deni
0       Strassbourg     Strassbourgi    Strassbourgi-des
0       Strassbourg     Strassbourgi    Strassbourgi-desse
0       Strassbourg     Strassbourgi    Strassbourgi-dest
0       Strassbourg     Strassbourgi    Strassbourgi-deta
0       Strassbourg     Strassbourgi    Strassbourgi-ga
0       Strassbourg     Strassbourgi    Strassbourgi-ks
0       Strassbourg     Strassbourgi    Strassbourgi-l
0       Strassbourg     Strassbourgi    Strassbourgi-le
0       Strassbourg     Strassbourgi    Strassbourgi-lt
0       Strassbourg     Strassbourgi    Strassbourgi-na
0       Strassbourg     Strassbourgi    Strassbourgi-ni
0       Strassbourg     Strassbourgi    Strassbourgi-s
0       Strassbourg     Strassbourgi    Strassbourgi-sid
0       Strassbourg     Strassbourgi    Strassbourgi-sse
0       Strassbourg     Strassbourgi    Strassbourgi-st
0       Strassbourg     Strassbourgi    Strassbourgi-ta
0       Strassbourg     Strassbourgi    Strassbourgid
0       Strassbourg     Strassbourgi    Strassbourgide
0       Strassbourg     Strassbourgi    Strassbourgidega
0       Strassbourg     Strassbourgi    Strassbourgideks
0       Strassbourg     Strassbourgi    Strassbourgidel
0       Strassbourg     Strassbourgi    Strassbourgidele
0       Strassbourg     Strassbourgi    Strassbourgidelt
0       Strassbourg     Strassbourgi    Strassbourgidena
0       Strassbourg     Strassbourgi    Strassbourgideni
0       Strassbourg     Strassbourgi    Strassbourgides
0       Strassbourg     Strassbourgi    Strassbourgidesse
0       Strassbourg     Strassbourgi    Strassbourgidest
0       Strassbourg     Strassbourgi    Strassbourgideta
0       Strassbourg     Strassbourgi    Strassbourgiga
0       Strassbourg     Strassbourgi    Strassbourgiks
0       Strassbourg     Strassbourgi    Strassbourgil
0       Strassbourg     Strassbourgi    Strassbourgile
0       Strassbourg     Strassbourgi    Strassbourgilt
0       Strassbourg     Strassbourgi    Strassbourgina
0       Strassbourg     Strassbourgi    Strassbourgini
0       Strassbourg     Strassbourgi    Strassbourgis
0       Strassbourg     Strassbourgi    Strassbourgisid
0       Strassbourg     Strassbourgi    Strassbourgisse
0       Strassbourg     Strassbourgi    Strassbourgist
0       Strassbourg     Strassbourgi    Strassbourgita        
```

```cmdline
 curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/sl_generator/version
{"version":"2023.11.33"}
```


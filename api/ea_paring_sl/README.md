# Päringu normaliseerija

## Sisendi JSON-kuju

```json
{   "tss":string,   // Tabulatsiooniga eraldatud päringusõned
    "params":{"otsi_liitsõnadest":bool} 
                    // true:  päringusõned võivad olla liitsõnade osasõnad (vaikimisi)
                    // false: päringusõned ei või olla liitsõnade osasõnad 
}
```

## Väljundi TSV-kuju

Esimeses reas on veerupealirjad. Veerud on:
* location -- sama numbriga read käivad sama päringusõne kohta
* input -- päringusõne (kuna sisendis oli eraldajaks TAB võib sisaldada tühikut, sõnestajad vahel teevad tõhikut sisaldavaid sõnesid)
* lemma -- päringusõne lemma
* type
  * "word" -- terviksõne
  * "compound" -- (päringusõne on liitsõne "wordform" osa)
  * "suggestion" -- päringusõne võis olla kirjaviga, "wordform" on soovitatud "õige" sõnavorm
* confidence -- täisarv, suurem numbriga "wordform" on sagedasem
* wordform -- sõnavorm tekstist otsimiseks

## Kasutusnäited

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"params":{"otsi_liitsõnadest":false}, "tss":"presidendiga\tpalk\tbresident"}' \
        https://smart-search.tartunlp.ai/api/ea_paring_sl/tsv
location        input   lemma   type    confidence      wordform
0       presidendiga    president       word    18      presidendi
0       presidendiga    president       word    2       president
1       palk    palk    word    726     palga
1       palk    palk    word    3       palgad
1       palk    palk    word    1       palgaga
1       palk    palk    word    1       palgata
1       palk    palk    word    5       palk
1       palk    palk    word    15      palkade
2       bresident       president       suggestion      18      presidendi
2       bresident       president       suggestion      2       president
2       bresident       president       compound        18      presidendi
2       bresident       president       compound        2       president
```

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"tss":"presidendiga\tpalk\tbresident"}' \
        https://smart-search.tartunlp.ai/api/ea_paring_sl/tsv
location        input   lemma   type    confidence      wordform
0       presidendiga    president       word    18      presidendi
0       presidendiga    president       word    2       president
0       presidendiga    president       compound        1       asepresidendi
1       palk    palk    word    726     palga
1       palk    palk    word    3       palgad
1       palk    palk    word    1       palgaga
1       palk    palk    word    1       palgata
1       palk    palk    word    5       palk
1       palk    palk    word    15      palkade
1       palk    palk    compound        6       ametipalga
1       palk    palk    compound        8       ametipalkade
1       palk    palk    compound        1       kuupalgamäärad
1       palk    palk    compound        1       kuupalgamäärade
1       palk    palk    compound        4       kuupalga
1       palk    palk    compound        1       muutuvpalga
1       palk    palk    compound        1       palgaandmete
1       palk    palk    compound        5       palgaarvestuse
1       palk    palk    compound        1       palgaastme
1       palk    palk    compound        3       palgaastmed
1       palk    palk    compound        6       palgaastmete
1       palk    palk    compound        4       palgaastmetele
1       palk    palk    compound        6       palgaastmestik
1       palk    palk    compound        6       palgaastmestiku
1       palk    palk    compound        1       palgaastmestikule
1       palk    palk    compound        1       palgagrupid
1       palk    palk    compound        328     palgajuhend
1       palk    palk    compound        27      palgajuhendi
1       palk    palk    compound        1       palgajuhendite
1       palk    palk    compound        15      palgakorraldus
1       palk    palk    compound        35      palgakorralduse
1       palk    palk    compound        47      palgamäärad
1       palk    palk    compound        111     palgamäärade
1       palk    palk    compound        1       palgaseadus
1       palk    palk    compound        5       palgaskaalad
1       palk    palk    compound        1       palgasüsteem
1       palk    palk    compound        9       palgatingimused
1       palk    palk    compound        25      palgatingimuste
1       palk    palk    compound        1       palgavahemike
1       palk    palk    compound        1       palgavahemiku
1       palk    palk    compound        1       palgavahenditeks
1       palk    palk    compound        2       põhipalga
1       palk    palk    compound        1       põhipalk
1       palk    palk    compound        2       tunnipalk
2       bresident       president       suggestion      18      presidendi
2       bresident       president       suggestion      2       president
```

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/ea_paring_sl/version | jq
{
  "DB_LEMATISEERIJA": "./1024-koond.sqlite",
  "version": "2023.10.14"
}

```

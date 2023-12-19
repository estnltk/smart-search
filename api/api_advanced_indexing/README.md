# Andmebaasi kokkupanemiseks vajaliku info leidmine CSV-kujul pealkirjadest või JSON-kujul dokumentidest 

## Kasutamine

Vaata:
* https://github.com/estnltk/smart-search/blob/main/api/api_advanced_indexing/flask_api_advanced_indexing.py
* https://github.com/estnltk/smart-search/blob/main/api/api_advanced_indexing/api_advanced_indexing.py

## Tulemus

JSON-kujul informatsioon

```json
{   "tabelid":
    {   "indeks_vormid":
        [   (   VORM,           // sõnavorm tekstist
                DOCID,          // dokumendi id
                START,          // alguspos tekstis
                END,            // lõpupos tekstis
                LIITSÕNA_OSA    // VORM on tekstis oleva liitsõna osasõna 
            )
        ],
        "indeks_lemmad":
        [   (   LEMMA,          // algvorm
                DOCID,          // dokumendi id
                START,          // algvormile vastava tekstisõne alguspos tekstis
                END,            // algvormile vastava tekstisõne lõpupos tekstis
                LIITSÕNA_OSA    // LEMMA on tekstis oleva liitsõna osasõna 
            )
        ],
        "liitsõnad":
        [   (   OSALEMMA,       // OSALEMMA on LIITLEMMA osa, näit raudteejaam -> raud, tee, jaam, raudtee, teejaam
                LIITLEMMA
            )
        ],
        "lemma_kõik_vormid":
        [   (   LEMMA,          // LEMMAst genereeritud sõnaVORM, genereeritud on LEMMA kõikvõimalikud VORMid
                KAAL,           // suurem kaaluga _sõnavorme_ on tekstis rohkem, KAAL==0 kui ei esine tekstis
                VORM            // algvorm
            )
        ],
        "lemma_korpuse_vormid":
        [   (   LEMMA,          // LEMMA
                KAAL,           // suurem kaaluga _sõnavorme_ on tekstis rohkem, KAAL>0
                VORM            // LEMMA need vormid, mis tekstis esinesid
            )
        ],
        "kirjavead":
        [   (   VIGANE_VORM,    // VORMist tuletatud kirjavigane vorm
                VORM            // korrektne sõnaVORM
            )
        ],
        "allikad":
    [   (   DOCID,              // ID
            CONTENT             // pealkirja/dokumendi "plain text"
            )
        ],
    }
}
```

## Mida uut

* 2023.12.19 Tabelites "lemma_korpuse_vormid" ja "lemma_kõik_vormid" veergude järjekord samaks: [(LEMMA, KAAL, VORM)]

## Mida edasi

* [Kirjavigade genereerimine](https://github.com/estnltk/smart-search/tree/main/api/api_misspellings_generator)
* [Saadud JSON-andmefailid saab SQLITE-andmebaasi lisamine](https://github.com/estnltk/smart-search/tree/main/scripts/script_query_extender_setup)


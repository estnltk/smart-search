# Andmebaasi kokkupanemiseks vajaliku info leidmine CSV-kujul pealkirjadest või JSON-kujul dokumentidest 

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
        [   (   VORM,           // LEMMAst genereeritud sõnaVORM, genereeritud on LEMMA kõikvõimalikud VORMid
                KAAL,           // suurem kaaluga _sõnavorme_ on tekstis rohkem, KAAL==0 kui ei esine tekstis
                LEMMA           // algvorm
            )
        ],
        "lemma_korpuse_vormid":
        [   (   LEMMA,          // LEMMA
                KAAL,           // suurem kaaluga _sõnavorme_ on tekstis rohkem, KAAL!=0
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

## Mida edasi

Saadud JSON-andmefailid saab omavahel kokkuliita ja SQLITE-andmebaasik teha programmiga:
https://github.com/estnltk/smart-search/blob/main/api/ea_jsontabelid_2_db/api_jsontabelid_2_db.py


Seda, kuidas teha JSON-failid ja need andmebaasiks kokkuliita näitab programm:
https://github.com/estnltk/smart-search/blob/main/api/ea_jsoncontent_2_jsontabelid/Makefile
 
# Tekstidest lemmade ning liitsõna osasõnade lemmade leidmine ja indekseerimine [versioon 2023.04.20]

Lihtsuse ja arusaadavuse huvides on näitetekstid ülilühikesed (mõnesõnalised).

Indekseerijas on kasutatud:

* sõnestajat, punktuatsiooni jms sõnast lahkutõstmiseks.
* morfoloogilist analüsaatorit:
  * liitsõnapiiride leidmiseks
  * ebaoluliste sõnade ignoreerimiseks:
    * punktuatsioon (alljärgnevas näites '.')
    * asesõnad (alljärgnevas näites 'tema')
    * sidesõnad (alljärgnevas näites 'ja')

## Näited JSON-kujul indeksi tegemine

Märkused:

* Dokumendi ID-ed peavad olema unikaalsed
* Dokumendi sisu on JSON-string formaadis. Sõnestamise seisukohalt on oluline, et algse teksti reavahetuste ja tabulatsioonide abil lõikudeks jagunemine oleks säilinud.

Kommenteeritud sisendjson:

```json
{
  "sources": {
    "DOC_1": { // dokumendi ID 
      "content": "Jahimehed jahikoertega."                // Dokumendi tekst
    },
    "DOC_2": { // dokumendi ID 
      "content": "Daam sülekoeraga ja mees jahikoeraga."  // Dokumendi tekst
    }
  }
}
```

### Näide 1 - Sisendtekst JSON-kujul lemmade indeksiks

Märkused:

* Liitsõna osasõna korral on viide algse liitsõna alguse- ja lõpupostsioonile (vt näide allpool).

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"sources": {"DOC_1":{"content":"Jahimehed jahikoertega."},"DOC_2":{"content":"Daam sülekoeraga ja mees jahikoeraga."}}}' \
  https://smart-search.tartunlp.ai/api/lemmade-indekseerija/json | jq
```

```json
{
  "sources": {
    "DOC_1": {
      "content": "Jahimehed jahikoertega."
    },
    "DOC_2": {
      "content": "Daam sülekoeraga ja mees jahikoeraga."
    }
  }
  "index": {
    "daam": {
      "DOC_2": [
        {
          "end": 4,
          "liitsõna_osa": false,
          "start": 0
        }
      ]
    },
    "jahikoer": {
      "DOC_1": [
        {
          "end": 22,
          "liitsõna_osa": false,
          "start": 10
        }
      ],
      "DOC_2": [
        {
          "end": 36,
          "liitsõna_osa": false,
          "start": 25
        }
      ]
    },
    "jahimees": {
      "DOC_1": [
        {
          "end": 9,
          "liitsõna_osa": false,
          "start": 0
        }
      ]
    },
    "jaht": {
      "DOC_1": [
        {
          "end": 9,
          "liitsõna_osa": true,
          "start": 0
        },
        {
          "end": 22,
          "liitsõna_osa": true,
          "start": 10
        }
      ],
      "DOC_2": [
        {
          "end": 36,
          "liitsõna_osa": true,
          "start": 25
        }
      ]
    },
    "jahtima": {
      "DOC_1": [
        {
          "end": 9,
          "liitsõna_osa": true,
          "start": 0
        },
        {
          "end": 22,
          "liitsõna_osa": true,
          "start": 10
        }
      ],
      "DOC_2": [
        {
          "end": 36,
          "liitsõna_osa": true,
          "start": 25
        }
      ]
    },
    "koer": {
      "DOC_1": [
        {
          "end": 22,
          "liitsõna_osa": true,
          "start": 10
        }
      ],
      "DOC_2": [
        {
          "end": 16,
          "liitsõna_osa": true,
          "start": 5
        },
        {
          "end": 36,
          "liitsõna_osa": true,
          "start": 25
        }
      ]
    },
    "mees": {
      "DOC_1": [
        {
          "end": 9,
          "liitsõna_osa": true,
          "start": 0
        }
      ],
      "DOC_2": [
        {
          "end": 24,
          "liitsõna_osa": false,
          "start": 20
        }
      ]
    },
    "mesi": {
      "DOC_2": [
        {
          "end": 24,
          "liitsõna_osa": false,
          "start": 20
        }
      ]
    },
    "sülekoer": {
      "DOC_2": [
        {
          "end": 16,
          "liitsõna_osa": false,
          "start": 5
        }
      ]
    },
    "süli": {
      "DOC_2": [
        {
          "end": 16,
          "liitsõna_osa": true,
          "start": 5
        }
      ]
    }
  },
}

```

### Näide 2 - Sisendtekst CSV-kujul indeksiks

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"sources": {"DOC_1":{"content":"Jahimehed jahikoertega."},"DOC_2":{"content":"Daam sülekoeraga ja mees jahikoeraga."}}}' \
  https://smart-search.tartunlp.ai/api/lemmade-indekseerija/csv
```

```csv
daam    False   Daam    DOC_2   0       4
jahikoer        False   jahikoertega    DOC_1   10      22
jahikoer        False   jahikoeraga     DOC_2   25      36
jahimees        False   Jahimehed       DOC_1   0       9
jaht    True    Jahimehed       DOC_1   0       9
jaht    True    jahikoertega    DOC_1   10      22
jaht    True    jahikoeraga     DOC_2   25      36
jahtima True    Jahimehed       DOC_1   0       9
jahtima True    jahikoertega    DOC_1   10      22
jahtima True    jahikoeraga     DOC_2   25      36
koer    True    jahikoertega    DOC_1   10      22
koer    True    sülekoeraga     DOC_2   5       16
koer    True    jahikoeraga     DOC_2   25      36
mees    True    Jahimehed       DOC_1   0       9
mees    False   mees    DOC_2   20      24
mesi    False   mees    DOC_2   20      24
sülekoer        False   sülekoeraga     DOC_2   5       16
süli    True    sülekoeraga     DOC_2   5       16
```

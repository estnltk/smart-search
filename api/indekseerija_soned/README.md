# Tekstidest sõnede ning liitsõna osasõnade leidmine ja neist indeksi koostamine [versioon 2023.04.20]

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

### Näide 1 - Sisendtekst JSON-kujul tekstisõnede indeksiks

Märkused:

* Liitsõna osasõna korral on viide algse liitsõna alguse- ja lõpupostsioonile (vt näide allpool).

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \                                                           
  --data '{"sources": {"DOC_1":{"content":"Jahimehed jahikoertega."},"DOC_2":{"content":"Daam sülekoeraga ja mees jahikoeraga."}}}' \
  https://smart-search.tartunlp.ai/api/sonede-indekseerija/json | jq
```

```json
{
  "sources": {   // sisendtekstid (vt kommentaare ülalpool)
    "DOC_1": {
      "content": "Jahimehed jahikoertega."
    },
    "DOC_2": {
      "content": "Daam sülekoeraga ja mees jahikoeraga."
    }
  }
  "index": {                        // sõnede indeks
    "daam": {                       // tekstisõne
      "DOC_2": [                    // dokumendi ID, kus sõne esines, selles tekstis esines 1 kord
        {
          "end": 4,                 // sõne lõpupositsioon tekstis
          "liitsõna_osa": false,    // sõne polnud liitsõna osa
          "start": 0                // sõne alguspositsioon tekstis
        }
      ]
    },
    "jahi": {                    // dokumendi ID, kus sõne esines, selles tekstis esines 2 korda
      "DOC_1": [
        {
          "end": 9,                 // sõne lõpupositsioon tekstis
          "liitsõna_osa": true,     // sõne oli liitsõna osa
          "start": 0                // sõne alguspositsioon tekstis
        },
        {
          "end": 22,                // sõne lõpupositsioon tekstis
          "liitsõna_osa": false,    // sõne polnud liitsõna osa
          "start": 10               // sõne alguspositsioon tekstis
        }
      ],
      "DOC_2": [                    // dokumendi ID, kus sõne esines, selles tekstis esines 1 kord
        {
          "end": 36,                // sõne lõpupositsioon tekstis
          "liitsõna_osa": true,     // sõne oli liitsõna osa
          "start": 25               // sõne alguspositsioon tekstis
        }
      ]
    },
    "jahikoeraga": {
      "DOC_2": [
        {
          "end": 36,
          "liitsõna_osa": false,
          "start": 25
        }
      ]
    },
    "jahikoertega": {
      "DOC_1": [
        {
          "end": 22,
          "liitsõna_osa": false,
          "start": 10
        }
      ]
    },
    "jahimehed": {
      "DOC_1": [
        {
          "end": 9,
          "liitsõna_osa": false,
          "start": 0
        }
      ]
    },
    "koeraga": {
      "DOC_2": [
        {
          "end": 16,
          "liitsõna_osa": true,
          "start": 5
        },
        {
          "end": 36,
          "liitsõna_osa": false,
          "start": 25
        }
      ]
    },
    "koertega": {
      "DOC_1": [
        {
          "end": 22,
          "liitsõna_osa": true,
          "start": 10
        }
      ]
    },
    "mees": {
      "DOC_2": [
        {
          "end": 24,
          "liitsõna_osa": false,
          "start": 20
        }
      ]
    },
    "mehed": {
      "DOC_1": [
        {
          "end": 9,
          "liitsõna_osa": true,
          "start": 0
        }
      ]
    },
    "süle": {
      "DOC_2": [
        {
          "end": 16,
          "liitsõna_osa": true,
          "start": 5
        }
      ]
    },
    "sülekoeraga": {
      "DOC_2": [
        {
          "end": 16,
          "liitsõna_osa": false,
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
  https://smart-search.tartunlp.ai/api/sonede-indekseerija/csv 
```

```csv
daam    False   Daam    DOC_2   0       4
jahi    True    Jahimehed       DOC_1   0       9
jahi    False   jahikoertega    DOC_1   10      22
jahi    True    jahikoeraga     DOC_2   25      36
jahikoeraga     False   jahikoeraga     DOC_2   25      36
jahikoertega    False   jahikoertega    DOC_1   10      22
jahimehed       False   Jahimehed       DOC_1   0       9
koeraga True    sülekoeraga     DOC_2   5       16
koeraga False   jahikoeraga     DOC_2   25      36
koertega        True    jahikoertega    DOC_1   10      22
mees    False   mees    DOC_2   20      24
mehed   True    Jahimehed       DOC_1   0       9
süle    True    sülekoeraga     DOC_2   5       16
sülekoeraga     False   sülekoeraga     DOC_2   5       16
```

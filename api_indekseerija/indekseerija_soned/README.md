# Tekstidest sõnede ning liitsõna osasõnade leidmine ja indekseerimine.

Lihtsuse ja arusaadavuse huvides on näitetekstid ülilühikesed (mõnesõnalised).

Indekseerijas on kasutatud:

* sõnestajat, punktuatsiooni jms sõnast lahkutõstmiseks.
* morfoloogilist analüsaatorit:
  * liitsõnapiiride leidmiseks
  * ebaoluliste sõnade ignoreerimiseks:
    * punktuatsioon (alljärgnevas näites '.')
    * asesõnad (alljärgnevas näites 'tema')
    * sidesõnad (alljärgnevas näites 'ja')

## Näited JSON-kujul indeksi tegemine.

Märkused:

* Dokumendi ID-ed peavad olema unikaalsed
* Dokumendi sisu on JSON-string formaadis. Sõnestamise seisukohalt on oluline, et algse teksti reavahetuste ja tabulatsioonide abil lõikudeks jagunemine oleks säilinud.

Kommenteeritud sisendjson:

```json
{
  "sources": {
    "DOC_1": {  // dokumendi ID          
      "content": "Daam koerakesega." // Dokumendi tekst
    },
    "DOC_2": {  // dokumendi ID 
      "content": "Härra ja daam. Daam sülekoeraga ja härra hundikoeraga." // Dokumendi tekst
    }
  }
}
```

### Näide 1 - Sisendtekst JSON-kujul indeksiks

Märkused:

* Liitsõna osasõna korral on viide algse liitsõna alguse- ja lõpupostsioonile (vt näide allpool).

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"sources": {"DOC_1":{"content":"Daam koerakesega."},"DOC_2":{"content":"Härra ja daam. Daam sülekoeraga ja härra hundikoeraga."}}}' \
  http://127.0.0.1:6606/json | jq
```

```json

{
  "sources": {  // sisendtekstid (vt kommentaare ülalpool)
    "DOC_1": {
      "content": "Daam koerakesega."
    },
    "DOC_2": {
      "content": "Härra ja daam. Daam sülekoeraga ja härra hundikoeraga."
    }
  }
  "index": {                        // sõnede indeks
    "daam": {                       // tekstisõne
      "DOC_1": [                    // dokumendi ID, kus sõne esines, selles tekstis esines 1 kord
        {
          "end": 4,                 // sõne lõpupositsioon tekstis
          "liitsõna_osa": false,    // sõne polnud liitsõna osa
          "start": 0                // sõne alguspositsioon tekstis
        }
      ],
      "DOC_2": [                    // dokumendi ID, kus sõne esines, selles tekstis esines 2 korda
        {                           
          "end": 13,                // sõne lõpupositsioon tekstis
          "liitsõna_osa": false,    // sõne polnud liitsõna osa
          "start": 9                // sõne alguspositsioon tekstis
        },
        {
          "end": 19,                // sõne lõpupositsioon tekstis
          "liitsõna_osa": false,    // sõne polnud liitsõna osa
          "start": 15               // sõne alguspositsioon tekstis
        }
      ]
    },
    "hundi": {                      // tekstisõne
      "DOC_2": [                    // dokumendi ID, kus sõne esines
        {                           // NB! liitsõna osasõna korral on viide algse liitsõna alguse- ja lõpupostsioonile
          "end": 53,                // sõne lõpupositsioon tekstis
          "liitsõna_osa": true,     // sõne oli liitsõna osa
          "start": 41               // sõne alguspositsioon tekstis
        }
      ]
    },
"hundikoeraga": {                   // tekstisõne  
      "DOC_2": [                    // dokumendi ID, kus sõne esines
        {
          "end": 53,                // sõne lõpupositsioon tekstis
          "liitsõna_osa": false,    // sõne oli liitsõna osa
          "start": 41               // sõne alguspositsioon tekstis
        }
      ]
    },
    "härra": {
      "DOC_2": [
        {
          "end": 5,
          "liitsõna_osa": false,
          "start": 0
        },
        {
          "end": 40,
          "liitsõna_osa": false,
          "start": 35
        }
      ]
    },
    "koeraga": {
      "DOC_2": [
        {
          "end": 31,
          "liitsõna_osa": true,
          "start": 20
        },
        {
          "end": 53,
          "liitsõna_osa": false,
          "start": 41
        }
      ]
    },
    "koerakesega": {
      "DOC_1": [
        {
          "end": 16,
          "liitsõna_osa": false,
          "start": 5
        }
      ]
    },
    "süle": {
      "DOC_2": [
        {
          "end": 31,
          "liitsõna_osa": true,
          "start": 20
        }
      ]
    },
    "sülekoeraga": {
      "DOC_2": [
        {
          "end": 31,
          "liitsõna_osa": false,
          "start": 20
        }
      ]
    }
  },
}
```

### Näide 2 - Sisendtekst CSV-kujul indeksiks

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
  --data '{"sources": {"DOC_1":{"content":"Daam koerakesega."},"DOC_2":{"content":"Härra ja daam. Daam sülekoeraga ja härra hundikoeraga."}}}' \
  http://127.0.0.1:6606/csv
```

```csv
daam    False   Daam    DOC_1   0       4
daam    False   daam    DOC_2   9       13
daam    False   Daam    DOC_2   15      19
hundi   True    hundikoeraga    DOC_2   41      53
hundikoeraga    False   hundikoeraga    DOC_2   41      53
härra   False   Härra   DOC_2   0       5
härra   False   härra   DOC_2   35      40
koeraga True    sülekoeraga     DOC_2   20      31
koeraga False   hundikoeraga    DOC_2   41      53
koerakesega     False   koerakesega     DOC_1   5       16
süle    True    sülekoeraga     DOC_2   20      31
sülekoeraga     False   sülekoeraga     DOC_2   20      31
daam    False   Daam    DOC_1   0       4
daam    False   daam    DOC_2   9       13
daam    False   Daam    DOC_2   15      19
hundi   True    hundikoeraga    DOC_2   41      53
hundikoeraga    False   hundikoeraga    DOC_2   41      53
härra   False   Härra   DOC_2   0       5
härra   False   härra   DOC_2   35      40
koeraga True    sülekoeraga     DOC_2   20      31
koeraga False   hundikoeraga    DOC_2   41      53
koerakesega     False   koerakesega     DOC_1   5       16
süle    True    sülekoeraga     DOC_2   20      31
sülekoeraga     False   sülekoeraga     DOC_2   20      31

```

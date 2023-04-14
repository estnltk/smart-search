# Sõnede leidmine ja nende tükeldamine liitsõnas osadeks.

Lihtsuse ja arusaadavuse huvides on näitetekstid ülilühikesed (mõnesõnalised).

Programm sisaldab ESTNLTK sõnestajat, st programmi, mis tõstab punktuatsiooni sõnast lahku.

Lemmade leidmise programm ignoreerib:

* punktuatsiooni (näites '.')
* asesõnasid (näites 'tema')
* sidesõnasid (näites 'ja')

## Näide
---

Vaatame teksti "Daam ja härra. Daam sülekoeraga ja härra hundikoeraga."

Programmi väljund on selline:

```json
{
    "Daam": {                   // sõne
        "count": 2,             // esines tekstis 2 korda
        "liitsõna_osa": false   // pole liitsõna osa
    },
    "_koeraga": {               // sõne
        "count": 2,             // esines liitsõnas 2 korda
        "liitsõna_osa": true    // liitsõna osa
    },
    "hundi_": {                 // sõne
        "count": 1,             // esines liitsõnades 1 kord
        "liitsõna_osa": true    // liitsõna osa
    },
    "hundikoeraga": {           // sõne
        "count": 1,             // esines tekstis 1 kord
        "liitsõna_osa": false   // pole liitsõna osa
    },
    "härra": {                  // sõne
        "count": 2,             // esines tekstis 2 korda
        "liitsõna_osa": false   // pole liitsõna osa
    },
    "süle_": {                  // sõne
        "count": 1,             // esines tekstis 1 kord
        "liitsõna_osa": true    // liitsõna osa
    },
    "sülekoeraga": {            // sõne
        "count": 1,             // esines tekstis 1 kord
        "liitsõna_osa": false   // pole liitsõna osa
    }
}
```

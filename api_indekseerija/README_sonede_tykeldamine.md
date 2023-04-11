# Sõnede leidmine ja nende tükeldamine liitsõnas osadeks.

Lihtsuse ja arusaadavuse huvides on näitetekstid ülilühikesed (mõnesõnalised).

Programm sisaldab ESTNLTK sõnestajat, st programmi, mis tõstab punktuatsiooni sõnast lahku.

Lemmade leidmise programm ignoreerib:

* punktuatsiooni (näites '.')
* asesõnasid (näites 'tema')
* sidesõnasid (näites 'ja')

## Näide
---

Vaatame teksti "Daam sülekoeraga ja härra hundikoeraga."

Programmi väljund on selline:

```json
{
    "Daam": {                   // tekstisõne
        "count": 1,             // esines 1 kord
        "liitsõna_osa": false   // ei ole liitsõna osa
    },
    "hundi": {                  // 
        "count": 1,             // 
        "liitsõna_osa": true    //
    },
    "hundikoeraga": {
        "count": 1,
        "liitsõna_osa": false
    },
    "härra": {
        "count": 1,
        "liitsõna_osa": false
    },
    "koeraga": {
        "count": 2,
        "liitsõna_osa": true
    },
    "süle": {
        "count": 1,
        "liitsõna_osa": true
    },
    "sülekoeraga": {
        "count": 1,
        "liitsõna_osa": false
    }
}

```
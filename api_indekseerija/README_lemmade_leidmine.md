# Teksti sõnedele algvormide leidmine

Lihtsuse ja arusaadavuse huvides on näitetekstid ülilühikesed (mõnesõnalised).

See programm on esimene samm indeksi tegemise programmis, kus me saame
etteantud algvormi kohta küsida:

* milliste tekstide millistes sõnedes otsitav algvorm esines
* milliste tekstide millistes sõnedes see algvorm esines liitsõna osana (näiteks algvormid "raud", "tee" või "raudtee" tekstisõnas "raudteejaamas")
* milliste tekstide millistes sõnedes see algvorm esines järelliitega sõna osana (näiteks algvorm "jaam" tekstisõnas "jaamalik" või algvorm "raudteejaam" tekstisõnas "raudteejaamalik")

Kogutud informatsioon võimaldab liitsõnade ja järelliitega sõnade "seest" otsimist soovi korral sisse/välja lülitada.

## Näited lihtsõnadega
---

Vaatame teksti "Mees ja tema koerad." Sõnestamise tulemusena saame selliste sõnede massiivi:

```json
["Mees", "ja", "tema", "koerad", "."]
```

Tasub tähel panna, et punktuatsioon on sõnast lahku tõstetud.

Lemmade leidmise programm ignoreerib:

* punktuatsiooni (näites '.')
* asesõnasid (näites 'tema')
* sidesõnasid (näites 'ja')

Algvormide leidmise programmi (kommenteeritud) JSON-väljund ülaltoodud näiteteksti korral:

```json
{
  "koer": {             // algvorm sõnast "koer"
    "cnt": 1,           // selliseid sõnasid, mille algvorm on "koer" esines tekstis  1 kord
    "fragments": [],    // sellest räägime järgmistes näidetes
"tokens": [             // nende tekstis esinevate sõnavormide loend, mille algvorm on "koer"
      {
        "end": 19,        // lõpupositsioon tekstis
        "start": 13,      // alguspositsioon tekstis
        "token": "koerad" // oli sellises sõnavormis 
      }
    ]
  },
"mees": {               // algvorm sõnast "Mees" (meessoost isik nimetavas käändes)
    "cnt": 1,           // selliseid sõnasid, mille algvorm on "mees" esines tekstis  1 kord
    "fragments": [],    // sellest räägime järgmistes näidetes
    "tokens": [ // nende tekstis esinevate sõnavormide loend, mille algvorm on "mees"
      {
        "end": 4,       // lõpupositsioon tekstis
        "start": 0,     // alguspositsioon tekstis
        "token": "Mees" // oli sellises sõnavormis 
      }
    ]
  },
  "mesi": {             // algvorm sõnast "Mees" ("mesi" sisseütlevas käändes)
    "cnt": 1,           // selliseid sõnasid, mille algvorm on "mesi" esines tekstis  1 kord
    "fragments": [],
    "tokens": [ // nende tekstis esinevate sõnavormide loend, mille algvorm on "mees"
      {
        "end": 4,       // lõpupositsioon tekstis
        "start": 0,     // alguspositsioon tekstis
        "token": "Mees" // oli sellises sõnavormis 
      }
    ]
  }
}
```

Veel selgitusi:

* Me näeme, et tekstisõnal "Mees" on kaks võimalikku algvormi: "mees" (meessoost isik nimetavas käändes) ja "mesi" ("mesi" sisseütlevas käändes).
* Programm vaatab üksiksõnasid ja ei oska öelda, kas lauses "Mees ja koerad." on mõeldud meest või mett.

## Näited liitsõnadega
---
Vaatame ühest liitsõnast koosnevat teksti "Õhupallipumbaga".

Algvormide leidmise programmi (kommenteeritud) JSON-väljund ülaltoodud näiteteksti korral:

```json
{
  "õhu_palli_pump": { // sõna "Õhupallipumbaga" algvorm, liitsõna osasõnade eraldataja '_'
    "cnt": 1,
    "fragments": [    // liitsõnast leitud osasõnade massiiv
      {
        "lemma": "õhk",             // liitsõna esimese osasõna "õhu" algvorm on "õhk"
        "liide_eemaldatud": false,  // järelliidet ei ole eemaldatud (seda ei olnudki)
        "liitsõna_osa": true        // on liitsõna osa
      },
      {
        "lemma": "õhu_pall",        // algsest kolme osasõnaga liitsõnast saadud kahesõnaline liitsõna
        "liide_eemaldatud": false,  // järelliidet ei ole eemaldatud (seda ei olnudki)
        "liitsõna_osa": true        // on liitsõna osa
      },
      {
        "lemma": "pall",            // sõnavormi "palli" nimisõnaline algvorm "pall" 
        "liide_eemaldatud": false,
        "liitsõna_osa": true
      },
      {
        "lemma": "pallima",         // sõnavormi "palli" tegusõnaline algvorm "pallima"
        "liide_eemaldatud": false,
        "liitsõna_osa": true
      },
      {
        "lemma": "palli_pump",      // algsest kolme osasõnaga liitsõnast saadud kahesõnaline liitsõna
        "liide_eemaldatud": false,
        "liitsõna_osa": true
      },
      {
        "lemma": "pump",            // algse liitsõna kolmanda osasõna algvorm
        "liide_eemaldatud": false,
        "liitsõna_osa": true
      }
    ],
    "tokens": [ // nende tekstis esinevate sõnavormide loend, mille algvorm on "õhupallipump"
      {
        "end": 15,
        "start": 0,
        "token": "Õhupallipumbaga"
      }
    ]
  }
}

```

Veel selgitusi:

* Liitsõna osasõnad pole alati algvormis, seega vastavad algvormid tuleb leida.
* Kolme ja enama komponendiga liitsõnast tuletatud lühemad liitsõnad tunduvad vahel mõistlikud, vahel ebmõistlikud.
  Näiteks "raudteejaam" korral "raudtee" on normaalne liitsõna, aga "teejaam" pigem mitte. 
  Meil ei ole head algoritmi, et õelda, kas pika liitsõna eest/tagant osasõnade äralõikamisega saame mõistliku või pigem ebamõistliku liitsõna.
  Sellised "ebamõistlikud" liitsõnad koormavad indeksit, aga ei halvenda päringu
  kvaliteeti, suure tõenäosusega "maajaama" keegi ei otsi.

## Näited järelliidetega sõnadest
---

Vaatame kahest liitsõnast koosnevat teksti "pallilik õhupallilik".

Algvormide leidmise programmi (kommenteeritud) JSON-väljund ülaltoodud näiteteksti korral:

```json
{
  "palli=lik": {        // järelliite eraldaja on '='
    "cnt": 1,
    "fragments": [
      {
        "lemma": "pall",            // algvorm sõnast "palli" (eemaldatud "lik" liide), sõna "palli" nimisõnaline algvorm "pall"
        "liide_eemaldatud": true,   // enne algvormi(de) leidmist on järelliide kustutud
        "liitsõna_osa": false       // ei ole liitsõna osa
      },
      {
        "lemma": "pallima",         // algvorm sõnast "palli" (eemaldatud "lik" liide), sõna "palli" tegusõnaline algvorm "pallima"
        "liide_eemaldatud": true,   // enne algvormi(de) leidmist on järelliide kustutud
        "liitsõna_osa": false       // ei ole liitsõna osa
      }
    ],
    "tokens": [
      {
        "end": 8,
        "start": 0,
        "token": "pallilik"
      }
    ]
  },
  "õhu_palli=lik": {
    "cnt": 1,
    "fragments": [
      {
        "lemma": "õhk",
        "liide_eemaldatud": false,
        "liitsõna_osa": true
      },
      {
        "lemma": "palli=lik",
        "liide_eemaldatud": false,
        "liitsõna_osa": true
      },
      {
        "lemma": "pall",            // algvorm liitsõna osasõnast "palli" (eemaldatud "lik" liide), sõna "palli" nimisõnaline algvorm "pall"
        "liide_eemaldatud": true,   // enne algvormi(de) leidmist on järelliide kustutud
        "liitsõna_osa": true        // on liitsõna osa
      },
      {
        "lemma": "pallima",         // algvorm liitsõna osasõnast "palli" (eemaldatud "lik" liide), sõna "palli" tegusõnaline algvorm "pallima"
        "liide_eemaldatud": true,   // enne algvormi(de) leidmist on järelliide kustutud
        "liitsõna_osa": true        // on liitsõna osa
      },
      {
        "lemma": "õhu_pall",
        "liide_eemaldatud": true,
        "liitsõna_osa": false
      }
    ],
    "tokens": [
      {
        "end": 20,
        "start": 9,
        "token": "õhupallilik"
      }
    ]
  }
}
```

## TODO
1. Kaota ära kaust `documentation` (SL)
2. Vii kõik kybernetese asjad ühe kausta alla. Seal võiks olla mingid reteptid (TV, vajalik osa on tehtud. Laiendada dokumentatsiooni)
3. Vaata läbi `legacy` kaust ja tõsta selle sisu ümber või kustuta ära
4. Liiguta kaust `lemmatiseerija` õigesse kohta (?api?)
5. Kaota ära kaust `rt_web_crawler`
6. Liiguta kaust `testkorpused` kataloogi ``tests` ja kaasajasta see või siis liiguta see `scripts` kausta õigesse kohta.
7. Lahenda kõik muud TODO.md failid

## Uus kataloogipuu (eskiis):
* api
  * ```api_advanced_indexing``` teisendab algsed dokumendi- või pealkirjafailid
  andmebaasi lisamiseks sobivale JSON kujule (curl/python)
  * ```api_misspellings_generator``` genereerib etteantud sõnaloendist võimalikud
  kirjavead andmebaasi lisamiseks sobival kujul (curl/python)
  * ```api_query_extender``` lisab kahe eelmise programmi töö tulemusena
  saadud JSONi andmebaasi (TV versioon) (python)
  * ```ea_paring``` koostab algsetest päringusõnedest andmebaasist otsimiseks
  sobiva päringu
  * ```ea_paring_sl``` Selle funktsionaalsuse lisame programmi ```ea_paring```
  ja selle kataloogi kustutame ära
  * ```sl_analyser``` selle projekti jaoks kohandatud morf analüüsi programm (curl/python)
  * ```sl_generator``` selle projekti jaoks kohandatud morf genereerimise programm (curl/puthon)
  * ```sl_lemmatizer``` selle projekti jaoks kohandatud morf lemmatiseerimise programm (curl/python)
  * legacy -- TV kustutame ära?
    * ```indekseerija_lemmad``` algne sisendtekstidest JSON kujul lemmade indeksi tegemine.
    See funktsionaalsus on integreeritud ```api_advanced_indexing``` programmi.
    * ```indekseerija_soned``` algne sisendtekstist JSON kujul sõnede indeksi tegemine.
    See funktsionaalsus on integreeritud ```api_advanced_indexing``` programmi.
    * ```paring_lemmad``` algne päringusõnedest päringu koostamise programm.
    Sobib kokku programmiga ```indekseerija_lemmad```.
    * ```paring_soned``` algne päringusõnedest päringu koostamise programm.
    Sobib kokku programmiga ```indekseerija_soned```. 
    See funktsionaalsus on integreeritud ```ea_paring``` programmi.

* ```demod```
  * ```toovood``` SL
  * ```veebilehed```
    * ```ea_paring_otsing``` veebileht, mis demontreerib ettaervutad sünteesil
    põhinevat otsingut
  * ```wp_*``` legacy asju demontreerivad veebilehed -- TV kustutame ära?

* ```documentation``` -- kustutame ära

* ```kube``` Iga allasjäänud teenuse kohta info:
  * konteineri poolt kasutatav port
  * tööks vajalikud keskkonnamuutujad

* ```legacy``` -- TV kustutame ära?

* ```minikube```  -- TV kustutame ära?

  -- SL: Mulle meedib see, et siin on olemas mingi bash, mis reaalselt vajalikud asjad püsti panevad (lykka_pysti.sh)
     Kas sa saad  kube kausta ka mingi seda tüüpi näitefaili püsti panna? Kui on tüütu siis ära tee.
  -- kaustadest kube ja minikube peab alles jääma vaid üks
  -- Kuigi sa ütled, et kube ülesse panemine on triviaalne või väga tehniline, siis mulle meeldib olukord, 
     kus kõik on commititud. Seega kui sul endal on mingi kaust nende teenuste ülikooli pilve üles laskmiseks, mis
     ei sisalsa paroole, siis võiks see kaust olla commititud, aga ma ei hakka seda suruma. 

* ```rt_web_crawler``` -- TV kasutab sealt peakirjade CSV faile.
Kuhu need oleks õige paigutada? Ülejäänu kustu?

  -- Need failid on juba tõstetud kausta  https://github.com/estnltk/smart-search/tree/main/demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts
  -- kustuta ära need failid ja kataloogid, mida sina tegid. Ma kustutan omad. 
   

* ```scripts```
  * ```query_extender_setup``` Sveni versioon ```api/api_query_extender``` programmist.
  TODO: Tabelis "lemma_kõik_vormid" veergude järjekord õigeks.

* ```testkorpused``` praeguseks legacy asjade testimisel kasutatud korpused.
TV kustutame ära?

  -- Kas meil mingeid teste sellele kupatusele ei ole. Kui neid saab kasutada olemasolevate teenuste testimiseks,
     siis ma tõstaks vastava teenuse alla kausta tests

* ```tests``` TV kustutame ära?

   -- Ei. Ma dokumenteerin, miks me selle testi tegime ja jätab alles, see on informatiivne.

* ```lemmatiseerija``` Kustutame ära, see funktsionaalsus selle projekti jaoks
kohandatud kujul sisaldub ```sl_lemmatizer``` programmis.

   -- Ok.

* Meil on veebiteenused lemmatise/generate/ mis on võetud tilluteenuste konteinerist.
  Selle kohta peaks api kaustas olema mingisugune info. api kaust peaks peegeledama smartsearch veebiteenuste
  struktuuri. Midagi ei tohiks sealt puudu olla. 

## TODO4TV

* Kooskõlastatud kataloogipuu implementeerida
* ```ea_paring``` ja ```ea_paring_sl``` kokkumiksida.'
* ```query_extender_setup``` tabelis "lemma_kõik_vormid" veerud õigeks.
* Pealkirjad uuesti läbilasta ja uus andmebaas lisada ```ea_paring_sl``` ja
demoveebilehe ```ea_paring_otsing``` konteineritesse.
* README.md failid ülevaadata ja TODO.md failid kustu.
* Andmebaasi kokkupanija SL versiooni setup täpsustada.

## TODO
1. Kaota ära kaust `documentation`
2. Vii kõik kybernetese asjad ühe kausta alla. Seal võiks olla mingid reteptid
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
  ```sl_analyser``` selle projekti jaoks kohandatud morf analüüsi programm (curl/python)
  ```sl_generator``` selle projekti jaoks kohandatud morf genereerimise programm (curl/puthon)
  ```sl_lemmatizer``` selle projekti jaoks kohandatud morf lemmatiseerimise programm (curl/python)
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

* ```rt_web_crawler``` -- TV kasutab sealt peakirjade CSV faile.
Kuhu need oleks õige paigutada? Ülejäänu kustu?

* ```scripts```
  * ```query_extender_setup``` Sveni versioon ```api/api_query_extender``` programmist.
  TODO: Tabelis "lemma_kõik_vormid" veergude järjekord õigeks.

* ```testkorpused``` praeguseks legacy asjade testimisel kasutatud korpused.
TV kustutame ära?

* ```tests``` TV kustutame ära?

* ```wp``` sealt alt ```ea_paring_otsing``` läks ```veebilehtede``` alla.
Kustutame ära.

* ```lemmatiseerija``` Kustutame ära, see funktsionaalsus selle projekti jaoks
kohandatud kujul sisaldub ```sl_lemmatizer``` programmis.

## TODO4TV

* Kooskõlastatud kataloogipuu implementeerida
* ```ea_paring``` ja ```ea_paring_sl``` kokkumiksida.'
* ```query_extender_setup``` tabelis "lemma_kõik_vormid" veerud õigeks.
* Pealkirjad uuesti läbilasta ja uus andmebaas lisada ```ea_paring_sl``` ja
demoveebilehe ```ea_paring_otsing``` konteineritesse.
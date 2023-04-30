# SMARTSEARCH

## Miks?

Tihti on olemasolevale infosüsteemile raske lisada otsingufunktsionaalsust, mis arvestaks eestikeele eripäradega:

* Reeglina soovitakse leida dokumentidest kõiki otsingufraaside vorme (näiteks president, presidendi, presidenti, ...)
* Tihti soovitakse korrigeerida kasutaja poolt otsisõna kirjutamisel tehtud trüki- ja ortograafiavigu (arhidekt, reeglisdtik, ...) 
* Tihti on kasulik teisendada kasutaja otsisõnad dokumentides kasutatavateks teminoloogiaks (üksratas, hoverboard &rarr; tasakaaluliikur, jalgrattatee &rarr; kergliiklustee)
*  Vahel soovitakse automaatset sõnalõpetust, mis piisava arvu tähtede sisestamisel pakub ise  välja võimalikud otsisõnade kandidaadid.

Antud projekti eesmärgiks on luua nende eesmärkide saavutamiseks vajalikud tarkvarakomponendid, mida saab suhteliselt lihtsalt liidestada olemasolevate infosüsteemidega.

## Kuidas?

<div style="text-align: center">
<img width=80% src="summary.png" alt="Raamistiku ülevaade" align="center">
</div>

Iga otsigu saab jagada neljaks faasiks:

* otsisisendi normaliseerimine;
* andmebaasi päringu koostamine; 
* dokumentide andmebaasist otsimine;
* leitud dokumentide filtreerimine ja dekoreerimine.  

Ülal toodud eesmärkide saavutamiseks piisab enamasti joonisel toodud komponentide lisamisest olemasolevasse otsingumoodulisse. 

Antud projekti raames loome me kõik vajalikud komponendid veebiteenustena ning näitame lihtsate demorakendustega, kuidas vastavaid komponente kasutada.

## Demorekendused

### I. Dokumentide indekseerimine

Toimiva otsingu aluseks on korrektselt indekseeritud dokumendid. Standardsed andmebaasilahendused ei arvesta eestikeelsete tekstide omapära ning seetõttu on otsingutulemused tihti kehvapoolsed.

Antud demo eesmärk on näidata kuidas saab kasutada keeletehnoloogilise vahendeid oluliselt sisukama indeksi moodustamiseks ning millist informatsiooni on otstarbekas indeksis esitada. 

* näiterakendused
  * [lemmadest koosneva indeksi tegemine](https://github.com/estnltk/smart-search/tree/main/api/indekseerija_lemmad)
  * [sõnavormidest koosneva indeksi tegemine](https://github.com/estnltk/smart-search/tree/main/api/indekseerija_soned)
* [selgitused näiterakenduste kohta](https://github.com/estnltk/smart-search/tree/main/api)

### II. Otsisisendi normaliseerimine

Antud demo näitab kuidas saab kasutada lemmatiseerimise ja sõnavormide sünteesimise veebiteenust otsingisisendis olevate sõnadest päringu genereerimseks. Kui indeksis on lemmad, peab päring sisaldama
otsisõnede lemmasid. Kui indeksis on (algsed) tekstisõned, peab päringusõned lemmatiseerima ja siis
genereerima neist kõikvõimaliku vormid.

Antud demo näitab kuidas saab kasutada lemmatiseerimise veebiteenust otsingisisendis olevate sõnade algvormide leidmiseks, mida on lihtsam indeksist otsida.

* [näiterakendus](https://smart-search.tartunlp.ai/wp/paring/process)
* [rakenduse lähtekood](https://github.com/estnltk/smart-search/tree/main/wp/wp_paring).
* [selgitused näiterakenduse kohta](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/README-CLOUD.md)

### III. Nutika otsingu demorakendus

Antud demo näitab, kuidas eelmisestes punktides korpuse põhjal tehtud indeksfailis olevat informatsiooni ja lemmatiseerimsteenust kombineerides päringusõnedele vastavad tekstid ja päringusõned tekstis märgendada.

* [näiterakendus](https://smart-search.tartunlp.ai/otsils)
* [näiterakenduse lähtekood](https://github.com/estnltk/smart-search/tree/main/demo_otsing/veebileht)
* [selgitused näiterakenduse kohta](https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/README-CLOUD.md)

## Veebiteenused

Programmeerija jaoks mõeldud liidesega veebiteenused:

* [Tekstide põhjal lemmasid sisaldava indeksi koostamine](https://github.com/estnltk/smart-search/tree/main/api/indekseerija_lemmad)
* [Tekstide põhjal sõnavorme sisaldava indeksi koostamine](https://github.com/estnltk/smart-search/tree/main/api/indekseerija_soned)
* [Päringusõnest lemmade indeksiga sobiva päringu genereerimine](https://github.com/estnltk/smart-search/tree/main/api/paring_lemmad)
* [Päringusõnedest tekstisõnede indeksiga sobiva päringu genereerimine](https://github.com/estnltk/smart-search/tree/main/api/paring_soned)
<!---
* [Sõnestamise ja lausestamise veebiteenus](https://github.com/estnltk/smart-search/blob/main/api/README-tokenizer.md)
* [Morfoloogilise analüüsi veebiteenus](https://github.com/estnltk/smart-search/blob/main/api/README-analyser.md)
* [Morfoloogilise genereerimise veebiteenus](https://github.com/estnltk/smart-search/blob/main/api/README-generator.md)
-->

## Repo kataloogistruktuur

* **_documentation_** -- nimi ise ütleb.
* **_lemmatiseerija_** -- lemmatiseerimise veebiteenuse lähtekood.
* **_demo_lemmatiseerija_** -- veebiserver, mis kuvab mitmel erineval moel lemmatiseerija veebiteenuse tulemusi.
* **_demo_otsing_** -- tillukese demokorpuse indekseerimise ja indeksist otsimise demo
  * **_korpus_ruukki_** -- tillukene demokorpus ja selle indekseerimisskriptid ("proof of concept" versioon) koos vahetulemustega
  * **_veebileht_** -- otsingumootori demo ("proof of concept" versioon)
* **_minikube_** -- lemmatiseerija ja demodega minikube-s askeldamine (juhend, skript)


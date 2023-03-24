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

Ülal toodud eesmärkide saavutamiseks piisab enamasti joonisel toodud komponentide lisamiks olemasolevasse otsingumoodulisse. 

Antud projekti raames loome me kõik vajalikud komponendid veebiteenustena ning näitame lihtsate demorakendustega, kuidas vastavaid komponente kasutada.

## Demorekendused

### I. Dokumentide indekseerimine

Toimiva otsingu aluseks on korrektselt indekseeritud dokumendid. Standardsed andmebaasilahendused ei arvesta eestikeelsete tekstide omapära ning seetõttu on otingutulemused tihti kehvapoolsed.

Antud demo eesmärk on näidata kuidas saab kasutada keeletehnoloogilise vahendeid oluliselt sisukama indeksi moodustamiseks ning millist informatsiooni on otstarbekas indeksis esitada. 

* [näiterakendus](???)
* [näitekood](https://github.com/estnltk/smart-search/tree/main/demo_otsing/korpus_ruukki)


### II. Otsisisendi normaliseerimine

Antud demo näitab kuidas saab kasutada lemmatiseerimise veebiteenust otsingisisendis olevate sõnade algvormide leidmiseks, mida on lihsam indeksist otsida.

* [näiterakendus](https://smart-search.tartunlp.ai/lemmad)
* [rakenduse lähtekood](https://github.com/estnltk/smart-search/tree/main/demo_lemmatiseerija).
* [veebiteenusega liidestumise näitekood](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/demo_lemmatiseerija.py).


### III. Nutika otsingu demorakendus 

Antud demo näitab, kuidas eelmisestes punktides korpuse põhjal tehtud indeksfailis olevat informatsiooni ja lemmatiseerimsteenust kombineerides päringusõnedele vastavad tekstid ja päringusõned tekstis märgendada.

* [näiterakendus](https://smart-search.tartunlp.ai/otsils)
* [selgitused näiterakenduse kohta](https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/README-CLOUD.md)
* [näiterakenduse lähtekood](https://github.com/estnltk/smart-search/tree/main/demo_otsing/veebileht)

 
## Veebiteenused

### Lemmatiseerimine

Programmeerija vaade ja liides **eesti keele sõnadele algvormi (lemma) leidmise veebiteenusele** on esitatud [lemmatiseerija veebiteenuse kirjelduses](https://github.com/estnltk/smart-search/tree/main/lemmatiseerija).


## Repo kataloogistruktuur

* **_documentation_** -- nimi ise ütleb.
* **_lemmatiseerija_** -- lemmatiseerimise veebiteenuse lähtekood.
* **_demo_lemmatiseerija_** -- veebiserver, mis kuvab mitmel erineval moel lemmatiseerija veebiteenuse tulemusi.
* **_demo_otsing_** -- tillukese demokorpuse indekseerimise ja indeksist otsimise demo
  * **_korpus_ruukki_** -- tillukene demokorpus ja selle indekseerimisskriptid ("proof of concept" versioon) koos vahetulemustega
  * **_veebileht_** -- otsingumootori demo ("proof of concept" versioon)
* **_minikube_** -- lemmatiseerija ja demodega minikube-s askeldamine (juhend, skript)


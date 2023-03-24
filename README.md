# SMARTSEARCH

* Programmeerija vaade ja liides
  **eesti keele sõnadele algvormi (lemma) leidmise veebiteenusele** on esitatud 
  [lemmatiseerija veebiteenuse kirjelduses](https://github.com/estnltk/smart-search/tree/main/lemmatiseerija).

* Seda kuidas antud otsingusõnedest saab tuletada tekstidest otsitavad 
  algvormid näitab
  [lemmatiseerimisteenuse demo](https://github.com/estnltk/smart-search/tree/main/demo_lemmatiseerija).
  Algoritmilist poolt esitab
  [pythoni skript](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/demo_lemmatiseerija.py).

* See kuidas lemmatiseerija veebiteenust saab kasutada demokorpuse indekseerimiseks
  on realiseeritud
  [indekseerimise demos](https://github.com/estnltk/smart-search/tree/main/demo_otsing/korpus_ruukki).
  See on pigem "proov of concept" mille peamiseks eesmärgiks on 
  võimalikult lihtsal moel näidata kuidas ja mis informatsioon on tekstidest indeksisse vaja kokku korjata. 
  "Päris" otsimgumootoris võiks olla otstarbekas informatsiooni hoidmiseks kasutada andmebaasi (MySQL vms). 
  Siin on indeks esitatud näitlikuse/lihtsuse huvides JSON formaadis.

* Seda kuidas eelmises punktis korpuse põhjal tehtud indeksfailis olevat informatsiooni
  ja lemmatiseerimsteenust kombineerides päringusõnedele vastavad tekstid ja päringusõned tekstis märgendada on esitatud
  [otsingumootori demos](https://github.com/estnltk/smart-search/tree/main/demo_otsing/veebileht).
  Sealsamas on ka vastav lähtekood. Lähtekoodi eesmärk on võimalikult
  näitlikul/lihtsal moel esitada põhiprintsiipe ja seega 
  rohkem "proof of concept" lahendus.

## Repo kataloogistruktuur

* **_documentation_** -- nimi ise ütleb.
* **_lemmatiseerija_** -- lemmatiseerimise veebiteenuse lähtekood.
* **_demo_lemmatiseerija_** -- veebiserver, mis kuvab mitmel erineval moel lemmatiseerija veebiteenuse tulemusi.
* **_demo_otsing_** -- tillukese demokorpuse indekseerimise ja indeksist otsimise demo
  * **_korpus_ruukki_** -- tillukene demokorpus ja selle indekseerimisskriptid ("proof of concept" versioon) koos vahetulemustega
  * **_veebileht_** -- otsingumootori demo ("proof of concept" versioon)
* **_minikube_** -- lemmatiseerija ja demodega minikube-s askeldamine (juhend, skript)


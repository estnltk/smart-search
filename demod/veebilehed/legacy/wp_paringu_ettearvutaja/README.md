# TODO täitsa pooleli, hetkel veel, ära kohe üldse vaata

[Link veebilehele TÜ serveris](https://smart-search.tartunlp.ai/wp/indekseerija/process)

Tegemist on pealisehitusega kahele veebiteenusele:

* [Tekstist lemmade indeksi tegemise veebiteenus](https://github.com/estnltk/smart-search/tree/main/api/indekseerija_lemmad)
* [Tekstist sõnede indeksi tegemise veebiteenus](https://github.com/estnltk/smart-search/tree/main/api/indekseerija_soned)

[Pealisehituse lähtekoodi](https://github.com/estnltk/smart-search/tree/main/wp/wp_indekseerija) leiab GITHUBist

Teksti indekseerimiseks tuleb teha 3 valikut:

* Indekseeritava teksti valimine oma arvutist.
  * Kui sisendfail sisaldab JSONit, siis:
    * sisendfaili nimi peab lõppema ```.json``` laiendiga
    * sisendJSONi kirjelduse leiate vastavate indekseerimise veebiteenuste kirjelduste juurest.
  * Kui sisendiks on tekstifail, siis:
    * sisendfaili nimi peab lõppema ```.txt``` laiendiga
    * tekstifail ei tohi sisaldada html-märgendust jms (st peab olema nn "plain text" formaadis)
    * väljundis dokumendi identifikaatoriks on sisendfaili nimi.
* Kas soovite moodustada [lemmasid sisaldava indeksi](https://github.com/estnltk/smart-search/tree/main/api/indekseerija_lemmad) või [sõnavorme sisaldava indeksi](ttps://github.com/estnltk/smart-search/tree/main/api/indekseerija_soned)
* Kas indekseerimise tulemust soovite veebilehel näha JSON- või CSV-kujul.

## Näited JSON-kujul sisendiga

Sisendiks on JSON kujul korpust sisaldav fail ```microcorpus.json```.
Tegemist on korpuste mõttes nanoskoopilise suurusega tekstiga,
eesmärk on näidetes illustreerida põhimõtteid.

```json
{"sources": {"DOC_1": {"content":"Daam\nkoerakesega."},"DOC_2": {"content":"Härra ja daam. Daam sülekoeraga ja härra hundikoeraga."}}}
```

### 1.1 Teeme lemmasid sisaldava indeksi ja kuvame seda JSON-kujul
---

 <img width=55% src="Ekraanipilt_indekseerija_lemmad_json_json_1.png">

Peale ```Indekseeri``` klikkimist näete ekraanil JSON-kujul lemmasid sisaldavat indeksit.

<img width=55% src="Ekraanipilt_indekseerija_lemmad_json_json_2.png">

### 1.2 Teeme lemmasid sisaldava indeksi ja kuvame seda CSV-kujul
---

<img width=55% src="Ekraanipilt_indekseerija_lemmad_csv_json_1.png">

Peale ```Indekseeri``` klikkimist näete ekraanil CSV-kujul lemmasid sisaldavat indeksit.

<img width=55% src="Ekraanipilt_indekseerija_lemmad_csv_json_2.png">

Veerud CSV failis:
<ol>
<li> veerg -- lemma (algvorm)
<li> veerg -- True kui liitsõna osa, False kui terviksõna
<li> veerg -- algne tekstisõne
<li> veerg -- dokumendi id
<li> veerg -- algse tekstisõne algusposotsioon tekstis
<li> veerg -- algse tekstisõne lõpupositsioon tekstis
</ol>

### 2.1 Teeme tekstisõnesid sisaldava indeksi ja kuvame seda JSON-kujul
---

<img width=55% src="Ekraanipilt_indekseerija_soned_json_json_1.png">

Peale ```Indekseeri``` klikkimist näete ekraanil CSV-kujul sõnesid sisaldavat indeksit.

<img width=55% src="Ekraanipilt_indekseerija_soned_json_json_2.png">

### 2.2 Teeme lemmasid sisaldava indeksi ja kuvame seda CSV kujul
---

<img width=55% src="Ekraanipilt_indekseerija_soned_csv_json_1.png">

Peale ```Indekseeri``` klikkimist näete ekraanil CSV-kujul lemmasid sisaldavat indeksit.

<img width=55% src="Ekraanipilt_indekseerija_soned_csv_json_2.png">

Veerud CSV failis:
<ol>
<li> veerg -- tekstisõne
<li> veerg -- True kui liitsõna osa, False kui terviksõna
<li> veerg -- algne tekstisõne
<li> veerg -- dokumendi id
<li> veerg -- algse tekstisõne algusposotsioon tekstis
<li> veerg -- algse tekstisõne lõpupositsioon tekstis
</ol>


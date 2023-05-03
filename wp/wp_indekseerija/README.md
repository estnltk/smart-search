# Veebileht tekstide indekseerimisteenuste demonstreerimiseks

Tegemist on pealisehitusega kahele veebiteenusele:
* [Tekstist lemmade indeksi tegemise veebiteenus](https://github.com/estnltk/smart-search/tree/main/api/indekseerija_lemmad)
* [Tekstist sõnede indeksi tegemise veebiteenus](https://github.com/estnltk/smart-search/tree/main/api/indekseerija_soned)

Veebilehel on 3 valikut:

* Indekseeritava teksti valimine oma arvutist. Kui 
  * sisendiks on tekstifail, siis:
    * sisendfaili nimi peab lõppema ```.txt``` laiendiga
    * tekstifail ei tohi sisaldada html-märgendust jms (st peab olema nn "plain text" formaadis)
    * väljundis dokumendi identifikaatoriks pannakse sisendfaili nimi.
  * Kui sisendfail sisaldab JSONit, siis:
    * sisendfaili nimi peab lõppema ```.json``` laiendiga
    * sisendJSONi kirjelduse leiate vastavate indekseerimise veebiteenuste kirjelduste juurest.
* Kas soovite moodustada [lemmasid sisaldava indeksi](https://github.com/estnltk/smart-search/tree/main/api/indekseerija_lemmad) või [sõnavorme sisaldava indeksi](ttps://github.com/estnltk/smart-search/tree/main/api/indekseerija_soned)
* Kas väljundina soovite veebilehel näha indeksi JSON- või CSV-kuju.


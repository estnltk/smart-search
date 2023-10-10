# Programmid

## Kui me ei taha päringu normaliseerimise ajal kasutada morfoloogilist genereerimist ja lemmatiseerimist

Töövoog on sellisel juhul järgmine:

Eeltöö
  * Pealkirju siseldavate CSV failide töötlemine JSON kujule.
  * Saadud JSON kujul failidest andmebaasi tegemine.

Kui eeltöö on tehtud saame vastavate andmebaaside, päringulaiendaja ja otsimootori abil 
abil leida kasutaja antud otsõnedele vastavad pealkirjad koos märgendatud otsõnedega
 
Nende programmide eripäraks on see, et morf analüüsi ja genereerimist kasutatakse
ainult andmebaasi ettevalmistamisel.

Otsinguprotsessis kasutatakse ainult andmebaasi ettearvutad informatsiooni.

### Pealkirjade CSV failide teisendamine ja esialgne töötlemine JSON kujule

Programmi sisendiks on pealkirjade kohta käivat infot sisaldavad CSV failid kataloogis
https://github.com/estnltk/smart-search/tree/main/rt_web_crawler/results.

Failinimed on:
* government_orders.csv
* government_regulations.csv
* local_government_acts.csv
* state_laws.csv

Programmi väljundiks on JSON kujul andmed, millest tehakse järgmise programmiga SQLITE andmebaasid.

Programmi lähtekood: https://github.com/estnltk/smart-search/tree/main/api/ea_jsoncontent_2_jsontabelid.

Programmi sisaldava konteineri saab allalaadida ja kasutada oma masinast/kubernatese klastrist või kasutada Tartu Ülikooli kubernatese klastris olevat versiooni.
Erivad kasutus-stenaariumid on kirjeldatud failis
https://github.com/estnltk/smart-search/blob/main/api/ea_jsoncontent_2_jsontabelid/flask_api_ea_jsoncontent_2_jsontabelid.py.

Tartu Ülikooli kubernatese klastris oleva programmi kasutusnäited:

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
        --data '{"sources": {"DOC_1":{"content":"Presidendi kantselei."}}}' \
        https://smart-search.tartunlp.ai/api/ea_jsoncontent_2_jsontabelid/json | jq | less
        
curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/ea_jsoncontent_2_jsontabelid/version | jq
```

### JSON-kujul andmetest SQLITE andmebaasi tegemine

Programmi sisendiks on eelmise programmiga tehtud JSON failid ja tulemuseks SQLITE
andmebaasid. Neid kasutab päringu laiendaja ja pealkirjadest otsingu demoprogramm.

Programmi lähtekood: https://github.com/estnltk/smart-search/tree/main/api/ea_jsontabelid_2_db.

Programm on Pythoni skript, kasutusnäited programmi alguskommentaarides:
https://github.com/estnltk/smart-search/blob/main/api/ea_jsontabelid_2_db/api_jsontabelid_2_db.py

### Veebiteenus: päringu normaliseerija

Veebiteenus, mille sisendiks on JSONi abil esitud päringusõned ja väljundiks
lemmade kombinatsioon, mida saab kasutada pealkirjade indekseeritud andmebaasist
päringusõnedele vastavate pealkirjade otsimiseks.

Programmi lähtekood: https://github.com/estnltk/smart-search/tree/main/api/ea_paring.

Programmi sisaldava konteineri saab allalaadida ja kasutada oma masinast/kubernatese klastrist või kasutada Tartu Ülikooli kubernatese klastris olevat versiooni.
Erivad kasutus-stenaariumid on kirjeldatud failis
https://github.com/estnltk/smart-search/blob/main/api/ea_paring/flask_api_ea_paring.py.

Tartu Ülikooli kubernatese klastris oleva programmi kasutusnäited:

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
    --data "{\"content\":\"presitendi ja polekorpuses kantseleis\"}" \
    https://smart-search.tartunlp.ai/api/ea_paring/json

curl --silent --request POST --header "Content-Type: application/json" \
    https://smart-search.tartunlp.ai/api/ea_paring/version | jq
```

### Veebiteenus peakirjade otsimootori demonstreerimiseks

Veebilehel saate sisestada otsisõned ja Teile kuvatakse otsisõnedele vastavad
pealkirjad. Otsisõnedele vastavad osad pealkirjades on esiletoodud teise taustavärviga.

Kasutatakse varem tehtud andmebaasi sõna lemmade ja vormide kohta. 

Programmi lähtekood: https://github.com/estnltk/smart-search/tree/main/wp/ea_paring_otsing.

Programmi sisaldava konteineri saab allalaadida ja kasutada oma masinast/kubernatese klastrist või kasutada Tartu Ülikooli kubernatese klastris olevat versiooni.
Erivad kasutus-stenaariumid on kirjeldatud failis
https://github.com/estnltk/smart-search/blob/main/wp/ea_paring_otsing/flask_wp_ea_paring_otsing.py

Tartu Ülikooli kubernatese klastris olev demo:
https://smart-search.tartunlp.ai/wp/ea_paring_otsing/process 

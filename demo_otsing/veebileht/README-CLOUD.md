# Otsingumootori demoveebileht (proof of concept) Tartu Ülikooli serveris

## Lähtekood

[Demo lähtekood](https://github.com/estnltk/smart-search/tree/main/demo_otsing/veebileht)

## Kasutusnäited

### 1. Näita demokorpuses olevaid tekste

Sisestage veebilehitseja aadressiribale ```https://smart-search.tartunlp.ai/tekstid```.
Veebilehitseja aknas näete demokorpuse tekste. Otsimootor otsib nende tekstide seest, vaata [ekraanipilti](https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/Ekraanipilt_smart-search.tartunlp.ai_tekstid.png).

### 2. Märksõnade otsimine tekstist. Lihtsõnu otsitakse ka liitsõna osasõnadest

Sisestaga veebilehitseja aadressiribale 
```https://smart-search.tartunlp.ai/otsils```. Sisestage tekstikasti otsingusõned ja klikkige
```Otsi (sh liitsõna osasõnadest)```. Avaneb veebileht otsingu tulemustega. Veebilehe alguses on kirjas milliseid lemmasid tekstist otsitakse.
Päringule vastavad sõnad tekstis on rasvases kirjas ja sulgudes algvormid.
Nagu [ekraanipildilt](https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/Ekraanipilt_demo_veebileht_otsils2.png) näha leitakse
päringusõne ```katus``` ka liitsõna ```valtskatuste``` osasõnast.

### 3. Märksõnade otsimine tekstist. Lihtsõnu ei otsita liitsõna osasõnadest

Sisestaga veebilehitseja aadressiribale
```https://smart-search.tartunlp.ai/otsi```. Sisestage tekstikasti otsingusõned ja klikkige
```Otsi```. Avaneb veebileht otsingu tulemustega. Veebilehe alguses on kirjas milliseid lemmasid tekstist otsitakse.
Päringule vastavad sõnad tekstis on rasvases kirjas ja sulgudes algvormid.
Nagu [ekraanipildilt](https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/Ekraanipilt_demo_veebileht_otsi2.png) näha ei leita
päringusõne ```katus``` liitsõna ```valtskatuste``` osasõnast.

# Otsingumootori demoveebileht (proof of concept) Tartu Ülikooli serveris

## Lähtekood

[Demo lähtekood](https://github.com/estnltk/smart-search/tree/main/demo_otsing/veebileht)

## Kasutusnäited

### 1. Näita demokorpuses olevaid tekste

Otsimootori demo otsib [nende tekstide](https://smart-search.tartunlp.ai/tekstid) seest.

### 2. Märksõnade otsimine tekstist. Lihtsõnu otsitakse ka liitsõna osasõnadest

Avage [veebileht](https://smart-search.tartunlp.ai/otsils) ja sisestage tekstikasti otsingusõned ja klikkige
```Otsi (sh liitsõna osasõnadest)``` nuppu. Avaneb veebileht otsingu tulemustega. Veebilehe alguses on kirjas milliseid lemmasid tekstist otsitakse.
Päringule vastavad sõnad tekstis on rasvases kirjas ja kandilistes sulgudes algvormid.
[Ekraanipildilt](https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/Ekraanipilt_demo_veebileht_otsils2.png) on näha,  et päringusõne ```katus``` leitakse liitsõna ```valtskatuste``` osasõnast.

### 3. Märksõnade otsimine tekstist. Lihtsõnu ei otsita liitsõna osasõnadest

Avage [veebileht](https://smart-search.tartunlp.ai/otsi) ja sisestage tekstikasti otsingusõned ja klikkige
```Otsi``` nuppu. Avaneb veebileht otsingu tulemustega. Veebilehe alguses on kirjas milliseid lemmasid tekstist otsitakse.
Päringule vastavad sõnad tekstis on rasvases kirjas ja kandilistes sulgudes algvormid.
[Ekraanipildilt](https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/Ekraanipilt_demo_veebileht_otsi2.png) on näha, et päringusõne ```katus``` ei leita liitsõna ```valtskatuste``` osasõnast. Selline otsing võib olla mõistlik, kui üks päringusõnedest osaleb üliproduktiivselt liitsõnamoodustuses ja liitsõna osasõnadest otsimine toob kaasa ebamõistlikul hulgal valepositiivseid juhtumeid.

### 3. Kuva päringule vastav JSONkujul info indeksist. Lihtsõnu otsitakse ka liitsõna osasõnadest

Avage [veebileht](https://smart-search.tartunlp.ai/otsilsjson) ja sisestage tekstikasti otsingusõned ja klikkige
```Otsi (sh liitsõna osasõnadest)``` nuppu. Avaneb veebileht otsingu JSONkujul tulemustega. Veebilehe alguses on kirjas milliseid lemmasid tekstist otsitakse.
[Ekraanipildilt](https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/Ekraanipilt_demo_veebileht_otsilsjson2.png) on näha,  et päringusõne ```katus``` leitakse liitsõna ```valtskatuste``` osasõnast.

### 4. Kuva päringule vastav JSONkujul info indeksist. Lihtsõnu ei otsita liitsõna osasõnadest

Avage [veebileht](https://smart-search.tartunlp.ai/otsijson) ja sisestage tekstikasti otsingusõned ja klikkige
```Otsi``` nuppu. Avaneb veebileht otsingu JSONkujul tulemustega.
[Ekraanipildilt](https://github.com/estnltk/smart-search/blob/main/demo_otsing/veebileht/Ekraanipilt_demo_veebileht_otsijson2.png) on näha, et päringusõne ```katus``` ei leita liitsõna ```valtskatuste``` osasõnast. Selline otsing võib olla mõistlik, kui üks päringusõnedest osaleb üliproduktiivselt liitsõnamoodustuses ja liitsõna osasõnadest otsimine toob kaasa ebamõistlikul hulgal valepositiivseid juhtumeid.


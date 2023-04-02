# Lemmatiseerija demoveebilehed Tartu Ülikooli serveris

## Lähtekood

* [Demo lähtekood](https://github.com/estnltk/smart-search/tree/main/demo_lemmatiseerija)

## Kasutusnäited

### Sisendsõnad komadega eraldatud lemmade loendiks

Avage [veebileht](https://smart-search.tartunlp.ai/lemmad), tekstilahtrisse kirjutage eestikeelne sõna ja klikkige ```Lemmatiseeri``` nuppu. Teile kuvatakse sisendsõne võimalikud lemmad.

Näiteks:

```text
katus ⇒ katt, katus
peeti ⇒ peet, pidama
```

Vaata vastavaid ekraanipilte:

* [Sõna ```katus``` lemmatiseerimise tulemus](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_smart-search.tartunlp.ai_lemmad_katus.png)
* [Sõna ```peeti``` lemmatiseerimise tulemus](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_smart-search.tartunlp.ai_lemmad_peeti.png)

### Sisendsõnadest päringu tuletamine

Avage [veebileht](https://smart-search.tartunlp.ai/paring), tekstilahtrisse kirjutage päringusõnad ja klikkige ```Leia päringule vastav lemmade kombinatsioon``` nuppu. Teile kuvatakse sisendõnadest tuletatud päring.

Näiteks

```text
(katus & profiil) ⇒ (katt ∨ katus) & (profiil)
```

Vaata vastavaid ekraanipilte:

* [Sõnadele ```katus profiil``` vastav päring](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_demo_lemmatiseerija_paring2.png)

### Lemmatiseerija JSON-väljund

Avage [veebileht](https://smart-search.tartunlp.ai/json), tekstilahtrisse kirjutage päringusõnad ja klikkige ```Kuva lemmatiseerija JSON-väljund``` nuppu. Teile kuvatakse [lemmatiseerija](https://github.com/estnltk/smart-search/tree/main/lemmatiseerija) JSON-väljundit.

Näiteks

```text
peeti ⇒
{
   "annotations": {
      "tokens": [
         {
            "features": {
               "complexity": 1,
               "mrf": [
                  {
                     "lemma_ma": "peet",
                     "pos": "S",
                     "source": "P"
                  },
                  {
                     "lemma_ma": "pidama",
                     "pos": "V",
                     "source": "P"
                  }
               ],
               "token": "peeti"
            }
         }
      ]
   },
   "content": "peeti",
   "version": "2023.03.21"
}
```

Vaata vastavaid ekraanipilte:

* [Sõnale ```peeti``` vastav lemmatiseerija väljund](https://github.com/estnltk/smart-search/blob/main/demo_lemmatiseerija/Ekraanipilt_smart-search.tartunlp.ai_lemmad_peeti.png)

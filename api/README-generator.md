# Morfoloogilise genereerimise veebiteenus

[JSON-sisendi kirjeldus](https://gitlab.com/tilluteenused/docker-elg-synth)

Veebiteenuse taga olev tarkvara on orienteeritud väikese hulga suuremahuliste päringute töötlemiseks.

Ei ole optimeeritud suure hulga väiksemahuliste päringute töötlemiseks. Selleks sobiv teenus on arenduses.

Päringu kuju

```commandline
curl --silent --request POST --header "Content-Type: application/json" --data JSON-DATA https://smart-search.tartunlp.ai/api/generator/process
```

Päringu näide

```cmdline
curl --silent --request POST --header "Content-Type: application/json" --data '{"type": "text", "content": "Terre ÜRO saadik."}' https://smart-search.tartunlp.ai/api/generator/process | jq
```

# Päringu normaliseerija

## Kasutusnäited

```cmdline
curl --silent --request POST --header "Content-Type: application/json" \
        --data "{\"content\":\"presitendi ja polekorpuses kantseleis\"}" \
        https://smart-search.tartunlp.ai/api/ea_paring/json
curl --silent --request POST --header "Content-Type: application/json" \
        https://smart-search.tartunlp.ai/api/ea_paring/version | jq

```

#!/bin/bash

DIR_HEADINGS=../../../demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts
DIR_QUERY_EXTENDER=.

docker-compose up -d
INDEXING=localhost:6602

#INDEXING=https://smart-search.tartunlp.ai

teeme_json_tabelid()
{
    echo $FUNCNAME '--------------------'
    for f in ${DIR_HEADINGS}/*.csv
    do
        echo -n == ${f}' -> '
        echo curl \
            --silent --request POST --header "Content-Type: application/json" \
            --data-binary @${f} \
            ${INDEXING}/api/advanced_indexing/headers \
    

    #> ${f}.json
    echo ${f}.json
    done
}

teeme_sonavormide_loendi()
{
    echo $FUNCNAME '--------------------'
    for f in ${DIR_HEADINGS}/*.csv.json
    do
        echo -n == ${f}' -> '
        cat ${f} \
        | gron \
        | grep 'json.tabelid.indeks_vormid\[[0-9]*\]\[0\]' \
        | sed 's/^.* = "\(.*\)";/\1/g' \
        > ${f/.csv.json/.kv-txt}
        echo ${f/.csv.json/.kv-txt}
    done
    echo ''
    echo -n ${DIR_HEADINGS}/*.kv-txt' -> '
    cat ${DIR_HEADINGS}/*.kv-txt \
    | sort \
    | uniq \
    > ${DIR_HEADINGS}/sonavormid.txt
    echo ${DIR_HEADINGS}/sonavormid.txt
}

teeme_kirjavigade_tabeli()
{
    echo $FUNCNAME '--------------------'
    echo -n ${DIR_HEADINGS}/sonavormid.txt' -> '
    curl   --silent --request POST --header "Content-Type: application/csv" \
            --data-binary @${DIR_HEADINGS}/sonavormid.txt \
            localhost:6603/api/misspellings_generator/process \
    > ${DIR_HEADINGS}/kirjavead.kv.json
    echo ${DIR_HEADINGS}/kirjavead.kv.json
}

teeme_andmebaasi()
{
    echo $FUNCNAME '--------------------'
    ${DIR_QUERY_EXTENDER}/venv/bin'/python ${DIR_QUERY_EXTENDER}/query_extender_setup.py \
        --verbose \
        --db_name=koond.sqlite
        --tables=lemma_kõik_vormid:lemma_korpuse_vormid:indeks_vormid:indeks_lemmad:liitsõnad:allikad \
        ${DIR_HEADINGS}/*.csv.json

     ${DIR_QUERY_EXTENDER}/venv/bin'/python ${DIR_QUERY_EXTENDER}/query_extender_setup.py \
        --verbose \
        --append \
        --db_name=koond.sqlite
        --tables=kirjavead \
        ${DIR_HEADINGS}/kirjavead.kv.json
}

teeme_json_tabelid
#teeme_sonavormide_loendi
#teeme_kirjavigade_tabeli
#teeme_andmebaasi

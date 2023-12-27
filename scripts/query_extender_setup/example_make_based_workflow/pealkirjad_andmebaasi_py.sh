#!/bin/bash

DIR_HEADINGS=~/git/smart-search_github/demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts
DIR_INDEXING=~/git/smart-search_github/api/api_advanced_indexing
DIR_MISPGEN=~/git/smart-search_github/api/api_misspellings_generator
DIR_QUERYEXT=~/git/smart-search_github/scripts/query_extender_setup/example_make_based_workflow

teeme_json_tabelid()
{
    echo '#' $FUNCNAME '--------------------'
    pushd ${DIR_INDEXING} >& /dev/null
    for f in ${DIR_HEADINGS}/*.csv
    do
        ./venv/bin/python3 ./api_advanced_indexing.py --verbose --csvpealkirjad ${f} > ${f}.json
    done
    popd >& /dev/null
}

teeme_sonavormide_loendi()
{
    echo '#' $FUNCNAME '--------------------'
    for f in ${DIR_HEADINGS}/*.csv.json
    do
        echo -n '# ' ${f}' -> '
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
    echo '#' $FUNCNAME '--------------------'
    pushd ${DIR_MISPGEN} >& /dev/null
    ./venv/bin/python3 ./api_misspellings_generator.py \
        --verbose \
        ${DIR_HEADINGS}/sonavormid.txt \
    > ${DIR_HEADINGS}/kirjavead.kv.json
    popd >& /dev/null
}

teeme_andmebaasi()
{
    echo '#' $FUNCNAME '--------------------'
    pushd ${DIR_QUERY_EXTENDER} >& /dev/null
    ./venv/bin/python3 ./query_extender_setup.py \
        --verbose \
        --db_name=${DIR_HEADINGS}/koond.sqlite \
        --tables=lemma_kõik_vormid:lemma_korpuse_vormid:indeks_vormid:indeks_lemmad:liitsõnad:allikad \
        ${DIR_HEADINGS}/*.csv.json

    ./venv/bin/python3 ./query_extender_setup.py \
        --verbose \
        --append \
        --db_name=${DIR_HEADINGS}/koond.sqlite \
        --tables=kirjavead \
        ${DIR_HEADINGS}/kirjavead.kv.json
    popd >& /dev/null
}

teeme_json_tabelid
teeme_sonavormide_loendi
teeme_kirjavigade_tabeli
teeme_andmebaasi

#!/bin/bash
 
# cd  ~/git/smart-search_github/scripts/query_extender_setup/example_script_based_workflow

DIR_PREF=~/git/smart-search_github
DIR_HEADINGS=${DIR_PREF}/demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts
DIR_INDEXING=${DIR_PREF}/api/api_advanced_indexing
DIR_MISPGEN=${DIR_PREF}/api/api_misspellings_generator
DIR_QUERYEXT=${DIR_PREF}/scripts/query_extender_setup/example_make_based_workflow
DIR_IGNOWFORMS=${DIR_PREF}/demod/toovood/riigi_teataja_pealkirjaotsing/01_dokumentide_indekseerimine/inputs
DIR_WFORMS2ADD=${DIR_PREF}/demod/toovood/riigi_teataja_pealkirjaotsing/01_dokumentide_indekseerimine/inputs

teeme_json_tabelid()
{
    # .csv -> .csv.json
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
    # .csv.json -> .kv-txt -> sonavormid.txt
    echo '#' $FUNCNAME '--------------------'
    for f in ${DIR_HEADINGS}/*.csv.json
    do
        echo -n '# ' ${f}' -> '
        cat ${f} \
        | gron \
        | grep 'lemma_kõik_vormid\[[0-9]*\]\[2\]' \
        | sed 's/^.* = "\(.*\)";/\1/g' \
        | sort \
        | grep -v '^[0-9.,%]*$' \
        > ${f/.csv.json/.kv-txt}
        echo ${f/.csv.json/.kv-txt}
    done
    echo ''
    echo -n '#' ${DIR_HEADINGS}/*.kv-txt' -> '
    cat ${DIR_HEADINGS}/*.kv-txt \
    | sort \
    | uniq \
    > ${DIR_HEADINGS}/sonavormid.txt
    echo ${DIR_HEADINGS}/sonavormid.txt
}

teeme_kirjavigade_tabeli()
{
    # sonavormid.txt -> kirjavead.kv.json
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
    # .csv.json, kirjavead.kv.json -> .sqlite
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
        
    ./venv/bin/python3 ./query_extender_setup.py \
        --verbose \
        --append \
        --db_name=${DIR_HEADINGS}/koond.sqlite \
        --tables=ignoreeritavad_vormid \
        ${DIR_IGNOWFORMS}/ignore.json

    ./venv/bin/python3 ./semi_automatic_word_form_generator.py \
        --jsonfile=${DIR_WFORMS2ADD}wordforms2addmanually.json \
        --db_name=${DIR_HEADINGS}/koond.sqlite
        > ${DIR_HEADINGS}/lisavormide_tabelid.json

    ./venv/bin/python3 ./query_extender_setup.py \
        --verbose \
        --db_name=${DIR_HEADINGS}/koond.sqlite \
        --tables=lemma_kõik_vormid:lemma_korpuse_vormid \
        ${DIR_HEADINGS}/lisavormide_tabelid.json    

    popd >& /dev/null
}

#teeme_json_tabelid
#teeme_sonavormide_loendi
#teeme_kirjavigade_tabeli
teeme_andmebaasi


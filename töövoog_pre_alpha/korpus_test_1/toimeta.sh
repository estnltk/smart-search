#!/bin/bash

FILES="proov1.txt proov2.txt proov3.txt"

for F in $FILES
do
    ./sonesta-lausesta.py --docid=_${F/.txt/}_ --heading=${F/.txt/} $F
done

#./sonesta-lausesta.py --docid=000 --heading="Classic C" Classic-C.txt
#./sonesta-lausesta.py --docid=001 --heading="Katuseprofiilid" Katuseprofiilid.txt
#./sonesta-lausesta.py --docid=002 --heading="Katuse turvatooted" Katuse-turvatooted.txt
#./sonesta-lausesta.py --docid=003 --heading="Mida tuleks katuseprojekti plaanimisel arvesse votta?" Mida-tuleks-katuseprojekti-plaanimisel-arvesse-votta.txt
#./sonesta-lausesta.py --docid=004 --heading="Miks turvatoodete arvelt ei tohiks kokku hoida?" Miks-turvatoodete-arvelt-ei-tohiks-kokku-hoida.txt
#./sonesta-lausesta.py --docid=005 --heading="Milline pinnakate valida?" Milline-pinnakate-valida.txt
#./sonesta-lausesta.py --docid=006 --heading="Millised on katuse renoveerimiskulud?" Millised-on-katuse-renoveerimiskulud.txt
#./sonesta-lausesta.py --docid=007 --heading="Teraskatustest lähemalt" Teraskatustest-lahemalt.txt
#./sonesta-lausesta.py --docid=008 --heading="Uudised " Uudised.txt



echo '============================'
# *.tokens
 ./morfi.py *.tokens

# *.lemmas

./lemmade_indeks.py --indexout=rannila.index *.lemmas

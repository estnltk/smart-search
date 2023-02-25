#!/bin/bash

INDEX=rannila.index
FILES="Classic-C.txt Katuseprofiilid.txt Katuse-turvatooted.txt Mida-tuleks-katuseprojekti-plaanimisel-arvesse-votta.txt Miks-turvatoodete-arvelt-ei-tohiks-kokku-hoida.txt Milline-pinnakate-valida.txt Millised-on-katuse-renoveerimiskulud.txt Teraskatustest-lahemalt.txt Uudised.txt"
#FILES="proov1.txt proov2.txt proov3.txt"

for F in $FILES
do
    ./sonesta-lausesta.py --docid=docid_${F/.txt/}_ --heading=${F/.txt/} $F
done

echo '============================'

./morfi.py ${FILES//.txt/.tokens}

echo '============================'

./lemmade_indeks-2.py --indexout=${INDEX} ${FILES//.txt/.lemmas}

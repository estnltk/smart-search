#!/bin/bash

# Need konteinerid peavad käima:
# $ docker run -p 6000:6000 tilluteenused/estnltk_sentok:2022.09.09
# $ docker run -p 6666:7000 tilluteenused/vmetajson:2022.09.09

INDEX=rannila.index
FILES=$(ls *.txt)

echo ==kustutame vanad vahefailid==
rm -f ${FILES//.txt/.tokens}
rm -f ${FILES//.txt/.lemmas}
rm -f ${INDEX}

echo ==sõnestame==
for F in $FILES
do
    ./sonesta-lausesta.py --docid=docid_${F/.txt/} --heading="$(echo $F | sed 's/.txt//g' | tr '-' ' ')" $F
done

echo '==morfime=='
./morfi.py ${FILES//.txt/.tokens}

echo '==indeks=='
./lemmade_indeks.py --indexout=${INDEX} ${FILES//.txt/.lemmas}

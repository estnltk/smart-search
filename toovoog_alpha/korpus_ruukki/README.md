# Korpuse indekseerimise demo

## Programmid
---

* ```toimeta.sh``` teeb algsetest korpusefailidest indeksfaili ```rannila.index```
mida kasutab otsingu demoveebileht. ```toimeta.sh``` skript kasutab sõnestaja ja morf analüsaatori konteinereid: 
  ```cmdline
  docker run -p 6000:6000 tilluteenused/estnltk_sentok:2022.09.09
  ```
  ```cmdline
  docker run -p 6666:7000 tilluteenused/vmetajson:2022.09.09
  ```

* ```sonesta-lausesta.py``` skripti kasutab ```toimeta.sh``` algsete korpusefailide sõnestamiseks.

* ```morfi.py``` skripti kasutab ```toimeta.sh``` sõnestatud failide morf analüüsimiseks

* ```lemmade_indeks.py``` skripti kasutab ```toimeta.sh``` morfitud failidest otsingumootori jaoks indeksfaili tegemiseks.

Programmid hoiavad praeguses prototüübis informatsiooni json-vorminguga failides.
Hilisemas realisatsioonis oleks otstarbekas kasutada informatsiooni hoidmiseks andmbebaasi (MySQL vms).

## .txt laiendiga failid
---

Demokorpuse lähtefailid on .txt laiendiga. Need indekseerime ära ja nende hulgast saame pärast otsida.

## .tokens laiendiga failid
---
Saame algsetest tekstifailidest sõnestamise käigus. See tükeldab algse teksti
mõistlikeks osadeks (punktuatsioon sõnade küljest lahti jne). Sõnestamiseks
kasutasime ```sonesta-lausesta.py``` skripti mis omakorda kasutab ESTNLTK sõnestajat
dockeri konteineris
(vt [Eesti keele lausestaja-sõnestaja konteiner](https://github.com/Filosoft/vabamorf/tree/master/docker/flask_estnltk_sentok)).

## .lemmas laiendiga failid
---
Saame ```morfi.py``` skriptiga sõnestust sisaldavatest korpusefailidest kasutates
[Eesti keele morfoloogilise analüsaatori konteinerit](https://github.com/Filosoft/vabamorf/tree/master/docker/flask_vmetajson). Morfoloogilisest infost kasutame
hiljem lemmasid (algvorme) ja sõnaliike (pole mõtet indekseerida kirjavahemärke, asesõnasid ja sidesõnasid).

## .indeks laiendiga fail
---
Saame ```lemmade_indeks.py``` skriptiga morf analüüsitud korpusefailist.
Sisaldab iga lemma kohta informatsiooni millistes dokumentides ja kuskohal asuvad lemmale vastavad tekstisõned.

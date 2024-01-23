# Näitetöövoog pealkirjaotsingu realiseerimiseks

Riigi Teataja dokumendi pealkirjaotsingu realiseerimiseks on vaja teada:

* Millised sõnad üldse esinevad pealkirjades.
* Milliseid kirjavigu tuleb parandada.
* Milliseid terminite hierarhiad tuleks jälgida.
* Kui tõenäoline on konkreetne kirjaviga.
* Milliseid otsinguid võimaldab Riigi Teataja veebiteenus.
* Mida teha kui Riigi Teataja sisu uueneb.

Sarnastele küsimustele on vaja vastata, kui on soov toetada otsingut üle 
ükskõikmillliste eestikeelsete tekstide.   
Siinjuures on oluline tähele panna, et ühele sõnavormile võib vastata mitu
algvormi ning ka kirjavigastele sõnadele võib vastata palju algvorme.
See võib tekitada olukorra, kus võimalike vastete hulk on liiga suur ning
seetõttu tuleb vastuste hulka piirata.

Alljärgnev näitetöövoog on realiseeritud Pythonis ja esitatud Jupyteri
töölehtedena. Sealjuures kasutatakse keeletehnoloogiliste operatsioonide jaoks
Riigi Teataja otsingu jaoks loodud veebiteenuseid. Selle näitekoodi najal on
lihtne realiseerida vastav töövoog mõnes teises keeles (**Java** või **JavaScript**).
Kuna töövoo loomisel on peamiseks eesmärgiks materjali esitamise selgus, siis
oleme jätnud kõrvale praktilisel juurutamisel lisanduvad aspektid.  

## I. Dokumentide indekseerimine

Kuigi Riigi Teatajal on olemas eraldi infosüsteem dokumentide salvestamiseks ja
otsimiseks, on meil tarvis leida igas dokumendis olevate sõnavormide algvormid.
Selleks on esmalt vaja viia kõik dokumendid vormindamata teksti kujule.
Seejärel saab neid keeletehnoloogiliste töövahenditega analüüsida ja saadud
vahetulemused salvestada. Dokumentide indekseerimine koosneb neljast põhiülesandest

* Dokumentide viimine vormindamata teksti kujule.

* Tekstide esmane analüüs ja töövahendite kohandamine.

* Tekstide indekseerimine ja täiendavate nimistute moodustamine.

[Vastav näitetöövoog](01_dokumentide_indekseerimine/README.md)


## II. Päringulaiendaja seadistamine

Teksti indeksite põhjal saab luua või täiendada päringulaiendaja andmebaasi.
See andmebaas peab arvet tektsides esinevate sünavormide üle ning arvutab ette sagedasemad kirjavead.
Päringulaiendaja seadistamine koosneb kolmest sammust:

* Päringulaiendaja anmdmebaasi uuendamisest
* Uuendatud andmebaasi valideerimisest ja päringukvaliteedi hindamisest.
* Veebiteenuses oleva andmebaasi uuendamisest ja teenuse taaskäivitamisest.    

[Vastav näitetöövoog](02_paringulaiendaja_seadistamine/README.md)

## III. Nutika otsingu veebilehega liidestamine 

Nutika otsingu kasutamiseks tuleb päringulaiendaja veebiteenus liidestada veebilehega. 
Kuigi tavaliselt tehakse seda veebilehe **JavaSkript**-i  koodis, siis meie teeme ühtsuse mõttes seda Pyhtonis.
Olenemata kasutatavast keelest tuleb liidestestamiseks vastata järgmistele küsimustele:

* Milline on otsingu kasutusloogika?
* Kuidas informeeritakse kasutajat erinevat tüüpi tulemustest.

[Vastav näitekood](03_nutikas_otsing/README.md)
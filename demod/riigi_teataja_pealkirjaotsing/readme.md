# Näitetöövoog pealkirjaotsingu realiseerimiseks

Riigi Teataja dokumendi pealkirjaotsingu realiseerimiseks on vaja:
* Teada millised sõnad üldse esinevad pealkirjades.
* Teada milliseid kirjavigu tuleb parandada.
* Teada milliseid terminite hierarhiad tuleks jälgida.
* Teada kui tõenäoline on konkreetne kirjaviga.
* Teada milliseid otsinguid võimaldab Riigi Teataja veebiteenus.
* Teada mida teha kui Riigi Teataja sisu uueneb.

Sarnastele küsimustele on vaja vastata, kui on soov toetada otsingut, mis
võimaldaks otsida dokumentides sõna kõiki vorme määrates vaid sõna algvorimi
ning parandaks ära sagedasemad kirjavead kasutaja poolt sisestatud otsingusõnas.
Siinjuures on oluline tähele panna, et ühele sõnavormile võib vastata mitu
algvormi ning ka kirjavigastele sõnadele võib vastata palju algvorme.
See võib tekitada olukorra, kus võimalike vastete hulk on liiga suur ning
seetõttu tuleb vastuste hulka piirata.

Alljärgnev näitetöövoog on realiseeritud Pythonis ja esitatud Jupyteri
töölehtedena. Sealjuures kasutatakse keeletehnoloogiliste operatsioonide jaoks
Riigi Teataja otsingu jaoks loodud veebiteenuseid. Selle näitekoodi najal on
lihtne realiseerida vastav töövoog mõnes teises keeles (Java või JavaScript).  
Töövoo loomisel on peamiseks eesmärgiks materjali esitamise selgus ning me
oleme jätnud kõrvale praktilisel juurutamisel lisanduvad aspektid.  

## I. Dokumentide indekseerimine

Kuigi Riigi Teatajal on olemas eraldi infosüsteem dokumentide salvestamiseks ja
otsimiseks, on meil tarvis leida igas dokumendis olevate sõnavormide algvormid.
Selleks on esmalt vaja viia kõik dokumendid vormindamata teksti kujule.
Seejärel saab neid keeletehnoloogiliste töövahenditega analüüsida ja saadud
vahetulemused salvestada.


### I.A. Dokumentide viimine vormindamata teksti kujule

Kuigi Riigi Teataja veebiteenus annab välja dokumentide pealkirju vormindamata
kujul, tuleb tekste siiski valideerida ja puhastada. Piisavalt suures andmekogus
on alati vigu ja ootamatusi.

**Kuidas ülesannet püstitada:**
TBA

**Kuidas tulemust kontrollida:**
TBA

**Viited**

### I.B. Tekstide indekseerimine

[Valikud]
[Seosed RT weebiliidesega]

**Kuidas ülesannet püstitada:**
TBA

**Kuidas tulemust kontrollida:**
TBA

**Viited**


## II. Indeksite kasutamine päringulaiendaja loomiseks

[Milliseid üledsandeid saab lahendada]

TBA

## III. Targa otsingu loomine

[UI]
[Funktsionaalsus]
[Liidestus]

TBA

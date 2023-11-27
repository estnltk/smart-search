# Näitetöövoog pealkirjaotsingu realiseerimiseks

Riigi Teataja dokumendi pealkirjaotsingu realiseerimiseks on vaja:

* Teada millised sõnad üldse esinevad pealkirjades.
* Teada milliseid kirjavigu tuleb parandada.
* Teada milliseid terminite hierarhiad tuleks jälgida.
* Teada kui tõenäoline on konkreetne kirjaviga.
* Teada milliseid otsinguid võimaldab Riigi Teataja veebiteenus.
* Teada mida teha kui Riigi Teataja sisu uueneb.

Sarnastele küsimustele on vaja vastata, kui on soov toetada otsingut, mis
võimaldaks otsida dokumentides sõnade kõiki vorme määrates vaid sõna algvorimi
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

**Kuidas ülesannet püstitada.**
Antud ülesande lahendamise juures on kõige olulisem määrata, milliseid dokumente
tuleb töödelda. See määrab ära üle milliste dokumentide tulevane otsing töötab.
Antud kontekstis tuleb meil vastata järgmistele küsimustele:

* Kas otsing peab toimima üle kõigi dokumeniversioonide või ainult üle hetkel
  kehtivate dokumendiversioonide?
* Kas otsing peab toimima üle küigi dokumendiliikide või üle konkreetse
  dokumendiliigi näiteks seaduste?

Teiseks tuleb määrata, millistele tingimustele peab vastama puhastatud kujul
olev tekst. Seda on *apriori* raske määrata. Kindlasti saab esitada hulga
vormilisi nõudeid:

* Tekst peaks olema UTF8 kodeeringus (*unicode*) ja sisaldama vaid eesti keeles
  kasutatavaid sümboleid.
  * Riigi Teataja tekstide korral pole kodeeringu probleem nii oluline, aga
    teistes infosüsteemides on tekste `Latin-1` ja `Windows-1257` kodeeringus.
    Selliste kodeeringute korral on täpitähtede bitiesitus teine ja kodeeringuga
    mitte arvestamine tekitab tekstidesse vigu.
  * Eestikeelsed sõnad on tüüpiliselt kirjutatud eesti tähestiku tähtedega.
    Teistsuguste sümbolite esinemine viitab tavaliselt mingitele erijuhtudele
    või tekstitöötlusvigadele.
* Tekstis olevad sõnad peaksid olema üksteisest eraldatud tühikutega.
  * Eestikeelsed sõnad ei sisalda tavaliselt numbreid ja muid erisümboleid.
    Nende esinemine sõnades viitab erijuhtudele (lühendid) või sõnastusvigadele.
  * Vahetevahel eraldatakse sõnu tekstides teiste sümbolitega nagu reavahetus,
    tabulatsioonimärk või erikujulised tühikusümbolid. Teksti edasise analüüsi
    lihtsustamiseks tuleks need sümbolid tekstis asendada.       

**Kuidas tulemust kontrollida.**
Tulemuse kontrollimiseks on tarvis fikseerida hulk näitetekste nii, et kõik
erijuhud oleks kaetud. Seejärel saab kontrollida, kas tekstide puhastamine
toimib, nii nagu me eeldame.  

* Tellija peaks fikseerima esialgse näitetekstide andmestiku
* Arendaja peaks seda jooksvalt täiendama ning selle koos koodiga üle andma.


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

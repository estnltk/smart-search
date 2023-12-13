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


### I.B. Otsingus leitavate sõnavormide määramine

Puhastamisest hoolimata võivad tekstid sisaldada sõnesid (tühikutega eraldatud 
tähekombinatsioone), mida tuleks otsimisel ignoreerida. Otsingus leitavate
sõnavormide nimistu, määrab suuresti ära kasutajakogemuse. Kui nimekiri on 
liiga lühike, siis kasutaja tunneb ennast piiratuna ning ei pruugi leida 
otsitavat teksti isegi siis kui ta kasutab õigeid otsisõnu. Samas ei tohiks 
nimekirjas olla sõesid, mida kunagi otsimisel ei kasutata või mille kasutamine
ei ole mõistlik.


**Kuidas ülesannet püstitada:**
Antud ülesande lahendamisel tuleb läheneda mitmest küljest. Ühelt poolt oleks 
mõistlik koguda sõnade algvormide esinemissagedust. Sealjuures on hea vahet 
teha üldise esinemissageduse ning sõna sisaldavate dokumentide arvu vahel.
Kuna ühele sõnavormile võib vastata mitu algvormi (lemmat), siis võivad 
mõlemad numbrid olla murdarvulised. Vastava sagedustabeli moodustamiseks 
tuleb vastata järgmistele küsimustele:

*  Kas ja milliseid sõna alamosasid saab otsida. Antud kontekstis on kolm 
   põhimõttelist lahendust. 
   * Esiteks saab otsida vaid kogu sõnavormi.
     Näiteks sõna `tuumaohutuse` leitaks  ülesse algvormi otsingu `tuumaohutus` korral.
   * Teiseks saab otsida suvalisi tähekombinatsioone sõnavormi sees.
     Enamasti on selline otsing liiga lai. Näiteks sõna `tuumaohutuse` leitaks
     ülesse algvormi otsingu `tuumaohutus`, `tuum`, `madu`, `agu`, `hutu`, `ohutus` 
     korral, millest enamusel pole seost antud sõnavormiga.
   * Kolmandaks saab otsida vaid liitsõna alamosi. Näiteks sõna `tuumaohutuse`
     leitaks üleks algvormi otsingu `tuumaohutus`, `tuum`, `ohutus` korral.
   * Tehniliselt saaks otsida ka sõna juure järgi. Näiteks sõna `arvestuslik` 
     juureks on `arvestus`. Kuid see on liiga keeruline ja seda tüüpi laiendused
     oleks mõstlik anda otsisüsteemi eraldi otsisõnade laiendussõnastiku abil.
    
* Milliseid sõnavorme otsingus täielikult ignoreerida. Siin on valikuid palju.
  * Võib ignoreerida arve ja kuupäevi. Siis ei saa otsida 20% maksutõusu või
    01.09.2007. a. kehtima hakkavat korda. Sõltuvalt kontekstist võib see 
    olla mõistlik kitsendus.
  * Võib ignoreerida viiteid dokumendiosadele või roomanumbritega määratud 
    järgarvusid.
  * Võib ignoreerida initsiaalidega pärisnime initsiaali osa kui alamsõna.
    Näiteks ei saa leida sõnavormi `A. H. Tammsaare` otsides alamsõna `A. H.`

* Kuidas muuta lühendid ja trükivigadega kirjuatavad sõnad leitavaks.
  Otsing `Euroopa Liit` võiks leida üles ka sagedase lühendvormi `EL`.
  Otsing `register` võiks leida ülesse ka dokumendi 
  `Kaitseministeeriumi valitsemisel oleva riigivara regisrisse ... kord`, 
  kus sõna `register` on valesti kirjutatud.           
 
**Kuidas tulemust kontrollida:**
Tulemuse kontrollimiseks on vaja fikseerida hulk otsingusõnu ja neile vastavaid tulemusi, 
mis kataksid kõik esmalt ette kujutatavad põhimõttelised variandid.

* Tellija peaks fikseerima esialgse näitetulemuste andmestiku. Siin piisab tabelist
  sõnavorm ja teda katvad otsisõnade algvormid või ka täpsed sõnavormid.
* Arendaja peaks seda jooksvalt täiendama ning vajadusel kommunikeerima eriliste 
  sõnavormide nimekirju, mille korral peaks tellija tegema täpsema otsuse. 

**Millised võiksid olla lõpptulemused:** Analüüsi tulemusena peaks tekkima järgmised tabelid

* Lemmade sagedustabel

|Lemma | Osasõna |Esinemiste arv | Dokumentide arv|  
|:--|:--|---:|--:|
|kord  | - | 14730| 14452|
|põhi  | + |  8181| 7831 |
|määrus| + | 7173 | 7166 |
|põhimäärus| - |6949|6942|

* Osaliselt täidetud lühendite sõnastik

|Lühend | Täisnimetus|  
|:--|:--|
|AIDS | ???
|EL   | Euroopa Liit
|ÜRO  | Ühinenud Rahvaste Organisatsioon 

Sõnastik peaks katma kõiki huvitavaid lühendeid, aga selle täisneimetuste veer ei pea olema täidetud.
Selle täitmine on suuresti tellija teha nagu ka sõnastiku lühendamine või täiendamine.
 
* Osaliselt täidetud kirjavigadega sõnavprmide sõnastik

|Sõnavorm | Korrektne algvorm|  
|:--|:--|
|regisri| registri|
|ööbim  | ???|
|vereül | ???

Jällegi ei pea sõnastik olema täielik ja korrektne, aga see võiks anda ülevaate milliseid 
kirjavigadega sõnavorme tektides esineb. Ja kõik sõnad ei pea olema ka kirjvigadega.
Piisab kui sõnastik on piisavlt lühike ja sisukas, et seda oleks võimalik käsitsi kureerida.
  
### I.C. Tekstide indekseerimine

Tekstide põhjal tehtud sõnavormide ja lemmade indeksit saab kasutada kahel moel. 

* Esiteks võib seda kasutada Riigi Teataja infosüsteemis oleva otsinguteenuse parandamiseks.
Sisuliselt tähendaks see, et igast dokumendist moodustatakse lemmade ja osa-lemmade indeksfail 
ning otsingteenus ei vaata originaaltekste vaid indeksfaile. Tehniliselt oleks see kõige 
õigem lahendus, aga selle realiseerimise eeldab muutusi infosüsteemis endas ja on seega riskantne.

* Teiseks saab indeksit kasutada päringulaiendaja sisendi moodustamiseks. 
See võimaldab jätta Riigi Teataja infosüsteemis oleva otsinguteenuse samaks, 
kuid saavutada paremad otsingutulemused asendandes originaalotsingu mitme eri 
sõnavormi otsinguga. Antud lahendus on ebaefektiivsem, kuid ei eelda muutusi 
Riigi Teataja infosüsteemis.

**Kuidas ülesannet püstitada:** 
Päringute laiendamiseks on tarvis teada kõiki sõnavorme, mis dokumentides esinevad.
Teiseks oleks vaja teada ka igale sõnavormile vastavat algvormi. Kui on soov otsida 
pealkirju liitsõna osadesõnade järgi (tuumaohutus → tuum, ohutus), siis on tarvis teada ka,
millised on iga dokumentides oleva liitsõna alamvormid. 

Vastav indeks võib olla realiseeritud failidena või andmebaasi tabelitena. 
Täpne tehniline lahenduse valiku võib jätte arendajale. Olulised nüded lahendusel on:

* Indeksi põhjal oleks võimalik leida alamülesande I.B väljunditena oodatavad tabelid: 
  * lemmade sagedustabel,
  * osaliselt täidetud lühendite sünastik,
  * osaliselt täidetud kirjavigadega sõnavormide sõnastik
  
* Süsteemi administraator saaks indeksit saaks perioodiliselt uuendada andes ette 
lisandunnud dokumendid. Seda on vaja päringulaiendaja sisendi täiendamiseks.      
 
**Kuidas tulemust kontrollida:**
Indeksi loomine on tehniline töö, mille korrektsust eraldi pole mõtet kontrollida.
Selle korrektsus ilmneb läbi sellest sõltuvate kompomentide korrektsuse. 
Kindlasti tuleks sealjuures läbi mängida dokumentide lisamise.
     
     
### I.D. Otsingus leitavate algvormide nimistu lühendamine

Kõik otsisõnad pole ü
  
**Kuidas ülesannet püstitada:** 

**Kuidas tulemust kontrollida:**
  
**Millised võiksid olla lõpptulemused:** 
  



## II. Indeksite kasutamine päringulaiendaja loomiseks

[Milliseid üledsandeid saab lahendada]




TBA

## III. Targa otsingu loomine

[UI]
[Funktsionaalsus]
[Liidestus]

TBA

# Päringulaiendaja seadistamine ja selle täiendamine

## I. Käsurea programmid ja nende kasutamine

* Kõik siin kataloogis olevad skriptid eeldavad Pyhton 3.8 interpretaatori ning failides `requirements.txt` ja `packages-list.txt` olevate moodulite olemasolu ja kättesaadavust. 

* Skript `create_venv.sh` loob asvatav virtuaalkeskonna, mis tuleb teiste scriptide kasutamiseks aktiveerida. Ülejäänud skriptide kasutamiseks on tarvis luua konfiguratsioonifail, mis fikseerib olulised valikud. 

### Päringulaiendaja seadistamiseks vajalikud skriptid

* `create_venv.sh`: Pyhtoni virtuaalkeskkonna loomine.* `import_index_files.sh`: Indeksfailide importimine päringulaiendaja sisendandmebaasi. * `import_misspellings.sh`: Kirjavigadega sõnavormide lisamine päringulaiendaja sisendandmebaasi. * [`basic_configuration.ini`](./basic_configuration.ini): Eeltäidetud ja dokumenteeritud näitekonfiguratsioonifail.### Eraldiseisva otsinguteenuse sisendandmebaasi loomiseks vajalikud skriptid* `import_source_files.sh`: Tekstifailide importimine sisendaandmebaasi.
*  TBA



## II. Baaskonfiguratsioon
 
Päringulaiendaja kasutab otsisõnade laiendamiseks tekstide indekseerimisel saadud tabeleid. 
Minimaalselt on vaja täita neli tabelit. 

###  Tabelid `lemma_kõik_vormid` ja `lemma_korpuse_vormid`

```sql
lemma_kõik_vormid
( 
	vorm TEXT NOT NULL,     -- lemma kõikvõimalikud vormid genereerijast
	kaal INT NOT NULL,      -- suurem number on sagedasem
	lemma TEXT NOT NULL,    -- korpuses esinenud sõnavormi lemma
	PRIMARY KEY(vorm, lemma)
)

lemma_korpuse_vormid
(
    lemma TEXT NOT NULL,        -- dokumendis esinenud sõnavormi lemma
    kaal INT NOT NULL,          -- suurem number on sagedasem
    vorm TEXT NOT NULL,         -- lemma need sõnavormid, mis on mingis dokumendis dokumendis esinenud
    PRIMARY KEY(lemma, vorm)
)
```

Need tabelid kirjeldavad korpuses olevaid sõnavorme ning nende lemmadest (algvormidest) genereeritavaid sõnavorme.
Viimast on vaja sellepärast, et pole teada, mis sõnavormi otsingus kasutatakse.   

### Tabel `kirjavead` 

```sql
kirjavead
(
	vigane_vorm TEXT NOT NULL,  -- sõnavormi vigane versioon
	vorm TEXT NOT NULL,         -- korpuses esinenud sõnavorm
	kaal REAL,                  -- kaal vahemikus [0.0,1.0]
	PRIMARY KEY(vigane_vorm, vorm)
)
```

See tabel saadakse tekstides olevate lemmade kõikidest sõnavormidest kirjavigadega vormide genereerimisel. 
Kuna võimalikke lemmasid ja sõnavorme on lõplik hulk, siis on ka neile vastavaid kirjavigadega vorme lõplik hulk ja me saame arvutusmahuka ennustamisprotsessi asendada lihtsa tabelipäringuga.

### Tabel `liitsõnad`

```sql
liitsõnad
( 
    osalemma TEXT NOT NULL,     -- liitsõna osasõna lemma
    liitlemma TEXT NOT NULL,    -- liitsõna osasõna lemmat sisaldav liitsõna lemma
    PRIMARY KEY(osalemma, liitlemma)
)
```

See tabel võimaldab otsida liitsõna osi. Tavaline andmebaasipäring lubab otsida kas täissõnu või sõnas olevat suvalist tähejärjendit. 
Viimane annab välja vägapalju valesid vasteid. 
Antud tabel võimaldab otsisõna laiendada kõigile tekstides esinevatele liitsõnadele ja otsida seejärel täissõnu.    


## III. Lisavõimalused

```sql
ignoreeritavad_vormid
(
	ignoreeritav_vorm TEXT NOT NULL,  -- sellist sõnavormi ignoreerime päringus
	paritolu INT NOT NULL,            -- 0:korpusest tuletatud, 1:etteantud vorm                       
	PRIMARY KEY(ignoreeritav_vorm)
)
```

## IV. Otsinguteenuse konfiguratsioon

Tekstide indekseerimise järel on tegelikult piisavalt informatsiooni selleks, et vastata kõikidele päringutele otse.
Vastav demorakendus [???](???) kasutab sarnast andmebaasifaili, millesse on lisatud kolm lisatabelit   

### Tabelid `indeks_vormid` ja `indeks_lemmad`

```sql
indeks_vormid
(
    vorm  TEXT NOT NULL,        -- (jooksvas) dokumendis esinenud sõnavorm
    docid TEXT NOT NULL,        -- dokumendi id
    start INT,                  -- vormi alguspositsioon tekstis
    end INT,                    -- vormi lõpupositsioon tekstis
    liitsona_osa,               -- 0: pole liitsõna osa; 1: on liitsõna osa
    PRIMARY KEY(vorm, docid, start, end)
)

indeks_lemmad
(
    lemma  TEXT NOT NULL,       -- (jooksvas) dokumendis esinenud sõna lemma
    docid TEXT NOT NULL,        -- dokumendi id
    start INT,                  -- lemmale vastava vormi alguspositsioon tekstis
    end INT,                    -- lemmale vastava vormi lõpupositsioon tekstis
    liitsona_osa,               -- 0: pole liitsõna osa; 1: on liitsõna osa
    PRIMARY KEY(lemma, docid, start, end)
)
```

Need tabelid sisaldavad infot selle kohta, millised sõnavormid dokumentides asuvad ja mis on nende täpne lokatsioon.
See võimaldab leida otsisõnu sisadavaid dokumente otse ilma täiendavaid päringuid tegemata.

### Tabel `allikad `

```sql
allikad
(
    docid TEXT NOT NULL,        -- dokumendi id
    content TEXT NOT NULL,      -- dokumendi text
    PRIMARY KEY(docid)
)
```

See tabel sisaldab kõiki tekste. Eelmise tabeli infot kombineerides, saab päringule anda vastu kogu teksti ja märkida ära selles esinevad otsisõnade vormid.

### Lahenduse skoop

Antud lahendus on loodud demonstreerimaks, et dokumentide indekseerimisteenus on piisav otsinguteenuse loomiseks.
Praktikas pole antud lahendus otseselt rakendatav:

* SQLight pole mõeldud suurte andmemahutude töötlemiseks.
* Andmebaasi sisu uuendamine on nõuab eraldi integratsiooni.   
* Riigi Teataja kasutab keerukat süsteemi tuvastamaks, millised dokumendiversioonid on kehtivad.     

Samas saab antud lahendust suvalisele andmebaasisüsteemile üldistades saada oluliselt efektiivsema otsinguteenuse. 



## Leftovers

https://github.com/estnltk/smart-search/blob/main/api/ea_jsoncontent_2_jsontabelid/Makefile

https://github.com/estnltk/smart-search/blob/main/api/ea_jsontabelid_2_db/api_jsontabelid_2_db.py
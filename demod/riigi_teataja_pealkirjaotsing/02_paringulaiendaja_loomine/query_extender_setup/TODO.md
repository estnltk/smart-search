TODO:
* Täiendada readme.md
* Parandada import_misspellings.py
* Lisada import_stopword_list.py
* Lisada conf orsinguteenuse enda jaoks
* Lisad script find_misspelligs_conflicts


Probleemid
* Lühend --> Otsisõna (EL --> Euroopa Liit)
  Seda saab teha nii Lühend --> Otsisõna eeldusel, et otsisõna indekseeritakse ära.
  Seda indekseerimisteenus ei tee, sest see vajab lokaalset listi
  * Indeksi loomisel on vaja lisada pärisnimed indeksisse. Seda saab teha kahel moel
    a) selle teenusesse keevitamine
    b) lokaalse skripti tegemine
    c) eraldi pärisnimede indekseerimise teenuse tegemine (braindead, aga võibolla vajalik)

* Valesti kirjutatud sõnad originaaltekstis
  Seda saab lahendada lisades uue kirjed lemma korpuse vormidesse alajaam1 -> alajaam

* Ignoreeritavad otsisõnad. Need on sõnad, mida peaks otsingus vältima
  Quick hack: on kustutada vastavad vormid sõnastikust ära
  Õige lahendus on panna otsingus filter peale ja ignoreerida vastavat sõna. 
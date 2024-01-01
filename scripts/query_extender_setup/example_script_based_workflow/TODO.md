* Korrigeerida kataloogid Makefile-s
* Kui võimalik asendada `query_extender_setup.py`-s kasutatud klass DB klassiga DatabaseUpdater.
  - See ei pruugi olla võimalik kuna DatabaseUpdater on ../bin kataloogis
  - Ainus viis on muuta PYTHONPATH-i. Seda kõige ohutum teha lisades koodi
  ```
  import sys
  sys.path.append("../bin/")
  ```
  - Kui see ei tööta, siis võib vastava faili siia kataloogi kopeerida.
    Kaks erinevat viisi andmebaasi muutmiseks tekitab kindlasti probleeme.
* Konfifaile ei ole vaja kasutada
* Uuenda README.md faili. Siia peaks jääma MakeFile töövoo käivitamise ja kohandamise kirjeldus

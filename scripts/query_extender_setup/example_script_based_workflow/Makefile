PREF=20240101-
PREF_HEADINGS=../../../demod/toovood/riigi_teataja_pealkirjaotsing/results/source_texts
PREF_ADVIDX=../../../api/api_advanced_indexing/
PREF_MISPGEN=../../../api/api_misspellings_generator/
DIR_IGNOWFORMS=./

all: $(PREF)koond.sqlite

json: $(PREF)state_laws.json $(PREF)government_orders.json $(PREF)government_regulations.json $(PREF)local_government_acts.json

kv-txt: $(PREF)state_laws.kv-txt $(PREF)government_orders.kv-txt $(PREF)government_regulations.kv-txt $(PREF)local_government_acts.kv-txt

#----

$(PREF)state_laws.json : $(PREF_HEADINGS)state_laws.csv
	$(PREF_ADVIDX)venv/bin/python3 $(PREF_ADVIDX)api_advanced_indexing.py --csvpealkirjad $< > $@

$(PREF)government_orders.json : $(PREF_HEADINGS)government_orders.csv
	$(PREF_ADVIDX)venv/bin/python3 $(PREF_ADVIDX)api_advanced_indexing.py --csvpealkirjad $< > $@

$(PREF)government_regulations.json : $(PREF_HEADINGS)government_regulations.csv
	$(PREF_ADVIDX)venv/bin/python3 $(PREF_ADVIDX)api_advanced_indexing.py --csvpealkirjad $< > $@

$(PREF)local_government_acts.json : $(PREF_HEADINGS)local_government_acts.csv
	$(PREF_ADVIDX)venv/bin/python3 $(PREF_ADVIDX)api_advanced_indexing.py --csvpealkirjad $< > $@

#----

$(PREF)state_laws.sv-txt : $(PREF)state_laws.json
	cat $< | gron | grep 'lemma_kõik_vormid\[[0-9]*\]\[2\]' | sed 's/^.* = "\(.*\)";/\1/g' | sort | grep -v '^[0-9.,%]*$' > $@

$(PREF)government_orders.sv-txt : $(PREF)government_orders.json
	cat $< | gron | grep 'lemma_kõik_vormid\[[0-9]*\]\[2\]' | sed 's/^.* = "\(.*\)";/\1/g' | sort | grep -v '^[0-9.,%]*$' > $@

$(PREF)government_regulations.sv-txt : $(PREF)government_regulations.json
	cat $< | gron | grep 'lemma_kõik_vormid\[[0-9]*\]\[2\]' | sed 's/^.* = "\(.*\)";/\1/g' | sort | grep -v '^[0-9.,%]*$' > $@

$(PREF)local_government_acts.sv-txt : $(PREF)local_government_acts.json
	cat $< | gron | grep 'lemma_kõik_vormid\[[0-9]*\]\[2\]' | sed 's/^.* = "\(.*\)";/\1/g' | sort | grep -v '^[0-9.,%]*$' > $@

#-----

$(PREF)sonavormid.txt : $(PREF)state_laws.sv-txt $(PREF)government_orders.sv-txt $(PREF)government_regulations.sv-txt $(PREF)local_government_acts.sv-txt
	cat $^ | sort | uniq > $@

$(PREF)kirjavead.json : $(PREF)sonavormid.txt
	$(PREF_MISPGEN)venv/bin/python3 $(PREF_MISPGEN)api_misspellings_generator.py  $< > $@

#-----

$(PREF)koond.sqlite : $(PREF)kirjavead.json $(PREF)state_laws.json $(PREF)government_orders.json $(PREF)government_regulations.json $(PREF)local_government_acts.json
	../../scripts/script_query_extender_setup/venv/bin/python3 ../../scripts/script_query_extender_setup/query_extender_setup.py \
		--db_name=$(PREF)koond.sqlite \
	    --tables=lemma_kõik_vormid:lemma_korpuse_vormid:indeks_vormid:indeks_lemmad:liitsõnad:allikad \
		$(PREF)state_laws.json $(PREF)government_orders.json $(PREF)government_regulations.json $(PREF)local_government_acts.json
	../../scripts/script_query_extender_setup/venv/bin/python3 ../../scripts/script_query_extender_setup/query_extender_setup.py \
		--verbose \
		--append \
		--db_name=$(PREF)koond.sqlite \
	    --tables=kirjavead \
		$(PREF)kirjavead.json
	../../scripts/script_query_extender_setup/venv/bin/python3 ../../scripts/script_query_extender_setup/query_extender_setup.py \
		--verbose \
		--append \
		--db_name=$(PREF)koond.sqlite \
	    --tables=ignoreeritavad_vormid \
		$(DIR_IGNOWFORMS)ignoreeritavad_vormid.json
		
#----

clean:
	-rm $(PREF)*.json
	-rm $(PREF)*.sv-txt
	-rm $(PREF)sonavormid.txt
	-rm $(PREF)kirjavead.json
	-rm $(PREF)koond.sqlite

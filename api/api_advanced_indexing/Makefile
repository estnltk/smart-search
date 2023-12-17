PREF=1217-

all: $(PREF)koond.sqlite

json: $(PREF)state_laws.json $(PREF)government_orders.json $(PREF)government_regulations.json $(PREF)local_government_acts.json

kv-txt: $(PREF)state_laws.kv-txt $(PREF)government_orders.kv-txt $(PREF)government_regulations.kv-txt $(PREF)local_government_acts.kv-txt

#----

$(PREF)state_laws.json : ../../rt_web_crawler/results/state_laws.csv
	venv/bin/python3 ./api_advanced_indexing.py --csvpealkirjad $< > $@

$(PREF)government_orders.json : ../../rt_web_crawler/results/government_orders.csv
	venv/bin/python3 ./api_advanced_indexing.py --csvpealkirjad $< > $@

$(PREF)government_regulations.json : ../../rt_web_crawler/results/government_regulations.csv
	venv/bin/python3 ./api_advanced_indexing.py --csvpealkirjad $< > $@

$(PREF)local_government_acts.json : ../../rt_web_crawler/results/local_government_acts.csv
	venv/bin/python3 ./api_advanced_indexing.py --csvpealkirjad $< > $@

#----

$(PREF)state_laws.kv-txt : $(PREF)state_laws.json
	cat $< | gron | grep 'json.tabelid.indeks_vormid\[[0-9]*\]\[0\]' | sed 's/^.* = "\(.*\)";/\1/g' > $@

$(PREF)government_orders.kv-txt : $(PREF)government_orders.json
	cat $< | gron | grep 'json.tabelid.indeks_vormid\[[0-9]*\]\[0\]' | sed 's/^.* = "\(.*\)";/\1/g' > $@

$(PREF)government_regulations.kv-txt : $(PREF)government_regulations.json
	cat $< | gron | grep 'json.tabelid.indeks_vormid\[[0-9]*\]\[0\]' | sed 's/^.* = "\(.*\)";/\1/g' > $@

$(PREF)local_government_acts.kv-txt : $(PREF)local_government_acts.json
	cat $< | gron | grep 'json.tabelid.indeks_vormid\[[0-9]*\]\[0\]' | sed 's/^.* = "\(.*\)";/\1/g' > $@

#-----

$(PREF)kirjavead.txt : $(PREF)state_laws.kv-txt $(PREF)government_orders.kv-txt $(PREF)government_regulations.kv-txt $(PREF)local_government_acts.kv-txt
	cat $^ | sort | uniq > $@

$(PREF)kirjavead.json : $(PREF)kirjavead.txt
	venv/bin/python3 ../api_misspellings_generator/api_misspellings_generator.py  $< > $@

#-----

$(PREF)koond.sqlite : $(PREF)kirjavead.json $(PREF)state_laws.json $(PREF)government_orders.json $(PREF)government_regulations.json $(PREF)local_government_acts.json
	../ea_jsontabelid_2_db/api_jsontabelid_2_db.py \
		--verbose \
		--db_name=$(PREF)koond.sqlite \
	    --tables=lemma_kõik_vormid:lemma_korpuse_vormid:indeks_vormid:indeks_lemmad:liitsõnad:allikad \
		$(PREF)state_laws.json $(PREF)government_orders.json $(PREF)government_regulations.json $(PREF)local_government_acts.json
	../ea_jsontabelid_2_db/api_jsontabelid_2_db.py \
		--verbose \
		--append \
		--db_name=$(PREF)koond.sqlite \
	    --tables=kirjavead \
		$(PREF)kirjavead.json
		
#----

clean:
	-rm $(PREF)state_laws.json
	-rm $(PREF)government_orders.json
	-rm $(PREF)government_regulations.json
	-rm $(PREF)local_government_acts.json
	-rm $(PREF)state_laws.kv-txt
	-rm $(PREF)government_orders.kv-txt
	-rm $(PREF)government_regulations.kv-txt
	-rm $(PREF)local_government_acts.kv-txt
	-rm $(PREF)kirjavead.txt
	-rm $(PREF)kirjavead.json
	-rm $(PREF)koond.sqlite
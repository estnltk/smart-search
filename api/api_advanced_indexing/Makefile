PREF=1212-

all: $(PREF)koond.sqlite

json: $(PREF)state_laws.json $(PREF)government_orders.json $(PREF)government_regulations.json $(PREF)local_government_acts.json

$(PREF)state_laws.json : ../../rt_web_crawler/results/state_laws.csv
	venv/bin/python3 ./api_ea_jsoncontent_2_jsontabelid_2.py --csvpealkirjad --kirjavead $< > $@

$(PREF)government_orders.json : ../../rt_web_crawler/results/government_orders.csv
	venv/bin/python3 ./api_ea_jsoncontent_2_jsontabelid_2.py --csvpealkirjad --kirjavead $< > $@

$(PREF)government_regulations.json : ../../rt_web_crawler/results/government_regulations.csv
	venv/bin/python3 ./api_ea_jsoncontent_2_jsontabelid_2.py --csvpealkirjad --kirjavead $< > $@

$(PREF)local_government_acts.json : ../../rt_web_crawler/results/local_government_acts.csv
	venv/bin/python3 ./api_ea_jsoncontent_2_jsontabelid_2.py --csvpealkirjad --kirjavead $< > $@

$(PREF)koond.sqlite : $(PREF)state_laws.json $(PREF)government_orders.json $(PREF)government_regulations.json $(PREF)local_government_acts.json
	../ea_jsontabelid_2_db/api_jsontabelid_2_db.py \
		--verbose \
		--db_name=$(PREF)koond.sqlite \
	    --tables=lemma_kõik_vormid:lemma_korpuse_vormid:indeks_vormid:indeks_lemmad:liitsõnad:kirjavead:allikad \
		$^

clean:
	-rm $(PREF)state_laws.json
	-rm $(PREF)government_orders.json
	-rm $(PREF)government_regulations.json
	-rm $(PREF)local_government_acts.json
	-rm $(PREF)koond.sqlite
	
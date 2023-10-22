PREF=1019

all: $(PREF)-state_laws.json $(PREF)-government_orders.json $(PREF)-government_regulations.json $(PREF)-local_government_acts.json

$(PREF)-state_laws.json : ../../rt_web_crawler/results/state_laws.csv
	venv/bin/python3 ./api_ea_jsoncontent_2_jsontabelid_2.py --csvpealkirjad $< > $@

$(PREF)-government_orders.json : ../../rt_web_crawler/results/government_orders.csv
	venv/bin/python3 ./api_ea_jsoncontent_2_jsontabelid_2.py --csvpealkirjad $< > $@

$(PREF)-government_regulations.json : ../../rt_web_crawler/results/government_regulations.csv
	venv/bin/python3 ./api_ea_jsoncontent_2_jsontabelid_2.py --csvpealkirjad $< > $@

$(PREF)-local_government_acts.json : ../../rt_web_crawler/results/local_government_acts.csv
	venv/bin/python3 ./api_ea_jsoncontent_2_jsontabelid_2.py --csvpealkirjad $< > $@

clean:
	-rm $(PREF)-state_laws.json
	-rm $(PREF)-government_orders.json
	-rm $(PREF)-government_regulations.json
	-rm $(PREF)-local_government_acts.json
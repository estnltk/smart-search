#!/usr/bin/env python
# coding: utf-8

# In[1]:


import math
import time
import requests
import datetime
import urllib.parse

from datetime import date
from pandas import DataFrame 
from tqdm.auto import tqdm

# In[2]:


BASE_URL = 'https://www.riigiteataja.ee/api/oigusakt_otsing/1'

ARG_STRUCTURE = \
{
    'leht': (int, 1),
    'limiit': (int, 500),
    'kehtiv': (date, None),
    'tulemused': (bool, True),
    'kehtivKehtetus': (bool, False),
    'mitteJoustunud': (bool, False),
    'kov': (bool, False),
    'dokument': (str, 'seadus')
}

def get_search_query(**kwargs):
    result = {}
    for key, value in kwargs.items():
        arg_type, default_value = ARG_STRUCTURE.get(key, (None, None))
        if arg_type is None:
            raise ValueError(f'Unknown argument: {key}')
        elif not isinstance(value, arg_type):
            raise ValueError(f'Argument {key} must be of type {arg_type}')
            
        if arg_type is bool:
            result[key] = str(value).lower()
        else:
            result[key] = urllib.parse.quote(str(value))
    return f"{BASE_URL}/otsi?{'&'.join(f'{key}={value}' for key, value in result.items())}"


# ## I. Crawl all state laws

# In[3]:


current_date = date.today()
query = get_search_query(leht=1, kehtiv=current_date, dokument='seadus', limiit=500)

response = requests.get(query)
assert response.status_code == 200, 'GET request failed'
response = response.json()

assert 'aktid' in response, 'Missing payload'
assert 'metaandmed' in response, 'Missing meta field'
assert 'kokku' in response['metaandmed'], 'Missing meta field'
assert 'limiit' in response['metaandmed'], 'Missing meta field'

total_count = response['metaandmed']['kokku']
document_limit = response['metaandmed']['limiit']
max_page = math.ceil(total_count/document_limit)


# In[4]:


query_results = [None] * max_page 
for page in tqdm(range(1, max_page + 1)):

    time.sleep(0.5)
    idx = page - 1
    query = get_search_query(leht=page, kehtiv=current_date, dokument='seadus', limiit=500)
    response = requests.get(query)
    assert response.status_code == 200, 'GET request failed'
    response = response.json()

    assert 'aktid' in response, 'Missing payload'
    document_count = len(response['aktid'])
    query_results[idx] = DataFrame({
        'global_id': [None] * document_count, 
        'document_type': [None] * document_count, 
        'document_title': [None] * document_count, 
        'xml_source': [None] * document_count
    })

    assert 'aktid' in response, 'Missing payload'
    for i, document in enumerate(response['aktid']):
        assert 'url' in document, 'Missing URL field'
        assert 'pealkiri' in document, 'Missing header field'
        assert 'liik' in document, 'Missing document type fields' 
        assert 'globaalID' in document, 'Missing global ID field'
    
        query_results[idx].loc[i, 'global_id'] = document['globaalID']
        query_results[idx].loc[i, 'document_type'] = document['liik']
        query_results[idx].loc[i, 'document_title'] = document['pealkiri']
        query_results[idx].loc[i, 'xml_source'] = f"https://www.riigiteataja.ee{document['url']}"

    
# Save results to csv-file
query_results = concat(query_results, axis=0)
query_results.to_csv('results/state_laws.csv', header=False)


# ## II. Crawl all government regulations

# In[ ]:


current_date = date.today()
query = get_search_query(leht=1, kehtiv=current_date, dokument='määrus', kov=False, limiit=500)

response = requests.get(query)
assert response.status_code == 200, 'GET request failed'
response = response.json()

assert 'aktid' in response, 'Missing payload'
assert 'metaandmed' in response, 'Missing meta field'
assert 'kokku' in response['metaandmed'], 'Missing meta field'
assert 'limiit' in response['metaandmed'], 'Missing meta field'

total_count = response['metaandmed']['kokku']
document_limit = response['metaandmed']['limiit']
max_page = math.ceil(total_count/document_limit)


# In[ ]:


query_results = [None] * max_page 
for page in tqdm(range(1, max_page + 1)):

    time.sleep(0.5)
    idx = page - 1
    query = get_search_query(leht=page, kehtiv=current_date, dokument='määrus', kov=False, limiit=500)
    response = requests.get(query)
    assert response.status_code == 200, 'GET request failed'
    response = response.json()

    assert 'aktid' in response, 'Missing payload'
    document_count = len(response['aktid'])
    query_results[idx] = DataFrame({
        'global_id': [None] * document_count, 
        'document_type': [None] * document_count, 
        'document_title': [None] * document_count, 
        'xml_source': [None] * document_count
    })

    assert 'aktid' in response, 'Missing payload'
    for i, document in enumerate(response['aktid']):
        assert 'url' in document, 'Missing URL field'
        assert 'pealkiri' in document, 'Missing header field'
        assert 'liik' in document, 'Missing document type fields' 
        assert 'globaalID' in document, 'Missing global ID field'
    
        query_results[idx].loc[i, 'global_id'] = document['globaalID']
        query_results[idx].loc[i, 'document_type'] = document['liik']
        query_results[idx].loc[i, 'document_title'] = document['pealkiri']
        query_results[idx].loc[i, 'xml_source'] = f"https://www.riigiteataja.ee{document['url']}"

    
# Save results to csv-file
query_results = concat(query_results, axis=0)
query_results.to_csv('results/government_regulations.csv', header=False)


# ## III. Crawl all local government acts

# In[ ]:


current_date = date.today()
query = get_search_query(leht=1, kehtiv=current_date, kov=True, limiit=500)

response = requests.get(query)
assert response.status_code == 200, 'GET request failed'
response = response.json()

assert 'aktid' in response, 'Missing payload'
assert 'metaandmed' in response, 'Missing meta field'
assert 'kokku' in response['metaandmed'], 'Missing meta field'
assert 'limiit' in response['metaandmed'], 'Missing meta field'

total_count = response['metaandmed']['kokku']
document_limit = response['metaandmed']['limiit']
max_page = math.ceil(total_count/document_limit)


# In[ ]:


query_results = [None] * max_page 
for page in tqdm(range(1, max_page + 1)):

    time.sleep(0.5)
    idx = page - 1
    query = get_search_query(leht=page, kehtiv=current_date, kov=True, limiit=500)
    response = requests.get(query)
    assert response.status_code == 200, 'GET request failed'
    response = response.json()

    assert 'aktid' in response, 'Missing payload'
    document_count = len(response['aktid'])
    query_results[idx] = DataFrame({
        'global_id': [None] * document_count, 
        'document_type': [None] * document_count, 
        'document_title': [None] * document_count, 
        'xml_source': [None] * document_count
    })

    assert 'aktid' in response, 'Missing payload'
    for i, document in enumerate(response['aktid']):
        assert 'url' in document, 'Missing URL field'
        assert 'pealkiri' in document, 'Missing header field'
        assert 'liik' in document, 'Missing document type fields' 
        assert 'globaalID' in document, 'Missing global ID field'
    
        query_results[idx].loc[i, 'global_id'] = document['globaalID']
        query_results[idx].loc[i, 'document_type'] = document['liik']
        query_results[idx].loc[i, 'document_title'] = document['pealkiri']
        query_results[idx].loc[i, 'xml_source'] = f"https://www.riigiteataja.ee{document['url']}"

    
# Save results to csv-file
query_results = concat(query_results, axis=0)
query_results.to_csv('results/local_government_acts.csv', header=False)


# ## IV. Crawl all government orders

# In[ ]:


current_date = date.today()
query = get_search_query(leht=1, kehtiv=current_date, dokument='korraldus', kov=False, limiit=500)

response = requests.get(query)
assert response.status_code == 200, 'GET request failed'
response = response.json()

assert 'aktid' in response, 'Missing payload'
assert 'metaandmed' in response, 'Missing meta field'
assert 'kokku' in response['metaandmed'], 'Missing meta field'
assert 'limiit' in response['metaandmed'], 'Missing meta field'

total_count = response['metaandmed']['kokku']
document_limit = response['metaandmed']['limiit']
max_page = math.ceil(total_count/document_limit)


# In[ ]:


query_results = [None] * max_page 
for page in tqdm(range(1, max_page + 1)):

    time.sleep(0.5)
    idx = page - 1
    query = get_search_query(leht=page, kehtiv=current_date, dokument='korraldus', kov=False, limiit=500)
    response = requests.get(query)
    assert response.status_code == 200, 'GET request failed'
    response = response.json()

    assert 'aktid' in response, 'Missing payload'
    document_count = len(response['aktid'])
    query_results[idx] = DataFrame({
        'global_id': [None] * document_count, 
        'document_type': [None] * document_count, 
        'document_title': [None] * document_count, 
        'xml_source': [None] * document_count
    })

    assert 'aktid' in response, 'Missing payload'
    for i, document in enumerate(response['aktid']):
        assert 'url' in document, 'Missing URL field'
        assert 'pealkiri' in document, 'Missing header field'
        assert 'liik' in document, 'Missing document type fields' 
        assert 'globaalID' in document, 'Missing global ID field'
    
        query_results[idx].loc[i, 'global_id'] = document['globaalID']
        query_results[idx].loc[i, 'document_type'] = document['liik']
        query_results[idx].loc[i, 'document_title'] = document['pealkiri']
        query_results[idx].loc[i, 'xml_source'] = f"https://www.riigiteataja.ee{document['url']}"

    
# Save results to csv-file
query_results = concat(query_results, axis=0)
query_results.to_csv('results/government_orders.csv', header=False)


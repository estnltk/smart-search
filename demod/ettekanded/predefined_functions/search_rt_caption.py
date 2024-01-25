import math
import requests

from datetime import date
from pandas import concat
from pandas import DataFrame


# noinspection SpellCheckingInspection
def search_rt_caption(wordform: str, match_type: str = 'koik_sonad', **kwargs):
    """
    Potential match types are:
    * autocomplete – leiab aktid, mille pealkirjas on suvalises järjekorras sõnad, mis algavad otsitud sõnadega
    * koik_sonad – leiab aktid, mille pealkirjas esinevad kõik otsitud sõnad suvalises järjekorras
    * täpne – leiab aktid, mille pealkirjas esineb otsitud fraas
    """

    search_query = 'https://www.riigiteataja.ee/api/oigusakt_otsing/1/otsi'

    arg_structure = \
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

    # Check that keyword arguments are correct and have right type
    payload = kwargs.copy()
    for key, value in payload.items():
        arg_type, default_value = arg_structure.get(key, (None, None))
        if arg_type is None:
            raise ValueError(f'Unknown argument: {key}')
        elif not isinstance(value, arg_type):
            raise ValueError(f'Argument {key} must be of type {arg_type}')

    # Update important payload arguments
    payload['leht'] = 1
    payload['kehtiv'] = date.today()
    payload['pealkiri'] = wordform
    payload['pealkiriOtsinguTyyp'] = match_type
    payload['filter'] = True
    payload['grupeeri'] = False
    payload['limiit'] = payload.get('limiit', 500)
    payload['dokument'] = payload.get('dokument', 'seadus')

    response = requests.get(search_query, params=payload)
    assert response.status_code == 200, 'GET request failed'
    response = response.json()

    # Get the number of responce pages
    assert 'aktid' in response, 'Missing payload'
    assert 'metaandmed' in response, 'Missing meta field'
    assert 'kokku' in response['metaandmed'], 'Missing meta field'
    assert 'limiit' in response['metaandmed'], 'Missing meta field'

    total_count = response['metaandmed']['kokku']
    document_limit = response['metaandmed']['limiit']
    max_page = math.ceil(total_count/document_limit)

    if total_count == 0:
        return DataFrame(columns=['document_type', 'document_title', 'commencement_date', 'global_id'])

    # Iterate over responce sheets
    query_results = [None] * max_page
    for page in range(max_page):

        payload['leht'] = page + 1
        response = requests.get(search_query, params=payload)
        assert response.status_code == 200, 'GET request failed'
        response = response.json()

        document_count = len(response['aktid'])
        # noinspection PyTypeChecker
        query_results[page] = DataFrame({
            'document_type': [None] * document_count,
            'document_title': [None] * document_count,
            'commencement_date': [None] * document_count,
            'global_id': [None] * document_count})

        for i, document in enumerate(response['aktid']):
            query_results[page].loc[i, 'global_id'] = document['globaalID']
            query_results[page].loc[i, 'document_title'] = document['pealkiri']
            query_results[page].loc[i, 'document_type'] = document['liik']
            query_results[page].loc[i, 'commencement_date'] = document['kehtivus'].get('algus')

    # noinspection PyTypeChecker
    return (concat(query_results, axis=0)
            .sort_values(['document_title', 'commencement_date'], ascending=[True, False])
            .reset_index(drop=True))

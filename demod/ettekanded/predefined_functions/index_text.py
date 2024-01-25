import requests

from pandas import DataFrame

from typing import List


TABLE_COLUMNS = {
    'indeks_vormid': ['wordform', 'doc_id', 'start', 'end', 'is_sublemma'],
    'indeks_lemmad': ['wordform', 'doc_id', 'start', 'end', 'weight', 'is_sublemma'],
    'liitsõnad': ['sublemma', 'compound'],
    'lemma_kõik_vormid': ['lemma', 'weight', 'wordform'],
    'lemma_korpuse_vormid': ['lemma', 'weight', 'wordform'],
    'allikad': ['doc_id', 'content']
}


def index_text(doc_id: str, text: str, output_tables: List[str] = None):
    """
    Uses web service to index document for further processing.

    Returns a JSON object that can be further modified or serialised to text.
    All indices are inside the field 'tabelid' which contains up to five subfields.
    The argument output_tables specifies which of them are present in the output.

    Two out of these correspond to actual word locations:
    - Subfield 'indeks_lemmad' contains information about lemmas in an unspecified order.
    - Subfield 'indeks_vormid' contains information about wordforms in an unspecified order.

    The remaining three contain aggregated information about the document:
    - Subfield 'liitsõnad' contains what subwords compound words in the document contain.
    - Subfield 'lemma_kõik_vormid' contains all potential wordform for each lemma.
    - Subfield 'lemma_korpuse_vormid' contains all wordform for each lemma that exists in the document.
    """
    if output_tables is None:
        output_tables = ['lemma_kõik_vormid', 'lemma_korpuse_vormid', 'liitsõnad']
    elif isinstance(output_tables, str):
        output_tables = [output_tables]

    analyzer_query = "https://smart-search.tartunlp.ai/api/advanced_indexing/json"
    headers = {"Content-Type": "application/json"}
    post_data_template = {"params": {"tables": output_tables}, "sources": {str(doc_id): {"content": text}}}

    response = requests.post(analyzer_query, json=post_data_template, headers=headers)
    assert response.ok, "Webservice failed"

    response = response.json()['tabelid']
    response = [DataFrame(response[table], columns=TABLE_COLUMNS[table]) for table in output_tables]
    return response[0] if len(response) == 1 else response
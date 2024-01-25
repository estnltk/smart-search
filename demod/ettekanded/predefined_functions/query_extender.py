import requests

from io import BytesIO
from pandas import read_csv

from typing import List
from typing import Union


def generate_wordforms_with_query_extender(
        words: Union[List[str], str],
        case: bool = True,
        search_sublemmas: bool = False):
    """
    Uses web service to get all wordforms existing in the documents for a list of lemmas.
    By default, the extender keeps track of in which case the characters are, e.g. Euroopa and euroopa are different.
    Returns a two column table with columns input, input_lemma, extension_type, score and search_wordform.
    The score shows the likelihood of the search wordform. The higher, the better.

    If the flag search_sublemmas is set returns also compound words containing.
    if the flag case is false extension is done in case-insensitive manner.
    """
    words = [words] if isinstance(words, str) else words
    if not all(map(lambda x: x.find('\t') == -1, words)):
        raise ValueError("Inputs cannot contain '\\t' character. It corrupts the output")

    analyser = "https://smart-search.tartunlp.ai/api/query_extender/tsv"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    compound_search_status = 'true' if search_sublemmas else 'false'
    post_data_template = {"params": {"otsi_liitsõnadest": compound_search_status}, "tss": "\t".join(words)}

    response = requests.post(analyser, json=post_data_template, headers=headers)
    assert response.ok, "Webservice failed"

    return (
        read_csv(BytesIO(response.content), delimiter='\t')
        .rename(columns={
        'lemma': 'input_lemma',
        'type': 'extension_type',
        'confidence': 'score',
        'wordform': 'search_wordform'})
        [['input', 'input_lemma', 'extension_type', 'score', 'search_wordform']])
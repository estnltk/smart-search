import requests

from io import BytesIO

from pandas import DataFrame
from pandas import read_csv


def analyze_text(text: str):
    """
    Uses morphological analyser to find lemmas of space separated words.
    Returns a dataframe with columns wordform, lemma and sublemmas.
    """

    # Webservice call
    analyzer_query = "https://smart-search.tartunlp.ai/api/analyser/process"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    post_data_template = {'params': {"vmetajson": ["--guess"]}, 'content': text}
    response = requests.post(analyzer_query, json=post_data_template, headers=headers)
    assert response.ok, "Webservice failed"
    response = response.json()

    # Count the number of analyses over all tokens
    analysis_count = sum(map(lambda x: len(x['features']['mrf']), response['annotations']['tokens']))
    tbl = DataFrame({
        'index': [None] * analysis_count,
        'wordform': [None] * analysis_count,
        'lemma': [None] * analysis_count,
        'sublemmas': [None] * analysis_count})

    # Unwind list of list into table
    row = 0
    for idx, token in enumerate(response['annotations']['tokens']):
        for annotation in token['features']['mrf']:
            tbl.loc[row, 'index'] = idx
            tbl.loc[row, 'wordform'] = token['features']['token']
            tbl.loc[row, 'lemma'] = annotation['lisamärkideta']
            tbl.loc[row, 'sublemmas'] = tuple(annotation['komponendid'])
            row += 1

    tbl = tbl.drop_duplicates().reset_index(drop=True)
    tbl['sublemmas'] = tbl['sublemmas'].map(list)

    # Assign lemma if there is no sublemmas for uniformity
    idx = tbl['sublemmas'].map(len) == 0
    tbl.loc[idx, 'sublemmas'] = tbl.loc[idx, 'lemma'].map(lambda x: [x])
    return tbl


def spell_text(text: str):
    """
    Uses speller to find correct forms of space separated words.
    Returns a dataframe with columns index, wordform and suggestion
    """

    # Webservice call
    speller_query = "https://smart-search.tartunlp.ai/api/speller/process"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    post_data_template = {"content": text}
    response = requests.post(speller_query, json=post_data_template, headers=headers)
    assert response.ok, "Webservice failed"
    response = response.json()

    # Output reshaping
    token_count = len(response['annotations']['tokens'])
    tbl = DataFrame({'wordform': [None] * token_count, 'suggestion': [None] * token_count})
    for i, token in enumerate(response['annotations']['tokens']):
        features = token['features']
        tbl.loc[i, 'wordform'] = features['token']
        tbl.loc[i, 'suggestion'] = features.get('suggestions', features['token'])

    return tbl.reset_index().explode('suggestion')


def generate_all_wordforms(lemma: str):
    """
    Generates all possible wordforms for input wordform.
    Returns a dataframe with columns input, wordform
    """

    # Webservice call
    generator_query = "https://smart-search.tartunlp.ai/api/generator/tss"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    post_data_template = {'tss': lemma}
    response = requests.post(generator_query, json=post_data_template, headers=headers)

    # Reshaping. Let us drop the confusing stem columns
    tbl = read_csv(BytesIO(response.content), sep='\t')
    return tbl[['input', 'wordform']]
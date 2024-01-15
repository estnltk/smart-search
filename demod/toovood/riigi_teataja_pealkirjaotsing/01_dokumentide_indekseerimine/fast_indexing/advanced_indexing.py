from estnltk import Text
from pandas import merge
from pandas import concat
from pandas import DataFrame

from estnltk_patches.rt_text_analyzer import RTTextAnalyzer
from estnltk_patches.form_synthesis import generate_all_forms
from fast_indexing.fast_indexing import get_lemma
from fast_indexing.fast_indexing import extract_wordform_index
from fast_indexing.fast_indexing import extract_lemma_index

from typing import Union
from typing import List


class AdvancedIndexer:

    def __init__(self, text_analyzer=None):
        self.ignore_pos = ['J', 'Z']
        self.text_analyser = text_analyzer or RTTextAnalyzer()

    def __call__(self, doc_id: Union[str, List[str]],  text: Union[str, List[str]]):
        if isinstance(text, str) and isinstance(doc_id, str):
            text = [text]
            doc_id = [doc_id]

        if not isinstance(doc_id, list) or not isinstance(text, list):
            raise ValueError('Invalid input')

        if len(doc_id) != len(text):
            raise ValueError('Invalid input')

        subword_table = [None] * len(text)
        lemma_wordform_index = [None] * len(text)
        for i, (idx, txt) in enumerate(zip(doc_id, text)):

            text_obj = self.text_analyser(Text(txt))
            subword_table[i] = create_subword_table(text_obj)
            lemma_wordform_index[i] = create_lemma_wordform_index(idx, text_obj)

        # noinspection PyTypeChecker
        subword_table = concat(subword_table, axis=0).drop_duplicates()

        # noinspection PyTypeChecker
        lemma_wordform_index = (concat(lemma_wordform_index, axis=0)
                                .groupby(['lemma', 'wordform'], as_index=False)
                                .aggregate(weight=('weight', 'sum')))

        # noinspection PyTypeChecker
        lemma_wordform_table = create_lemma_wordform_table(lemma_wordform_index)

        # Flattern the result
        return dict(
            # "lemma_korpuse_vormid":[(LEMMA, KAAL, VORM)],
            lemma_korpuse_vormid=lemma_wordform_index[['lemma', 'weight', 'wordform']].values.tolist(),
            # "lemma_kõik_vormid":[(LEMMA, KAAL, VORM)],
            lemma_kõik_vormid=lemma_wordform_table[['lemma', 'weight', 'wordform']].values.tolist(),
            # "liitsõnad":[(OSALEMMA, LIITLEMMA)]
            liitsõnad=subword_table[['sublemma', 'lemma']].values.tolist()
        )


def create_lemma_wordform_index(doc_id: str, text: Text):
    """
    Creates lemma-wordform index based on the analysed input text
    """
    if 'morph_analysis' not in text.layers:
        ValueError('Expecting a Text object with morph_analysis layer')

    return (
        DataFrame(
            extract_wordform_index(doc_id, text),
            columns=['wordform', 'doc_id', 'start', 'end', 'is_subword']
        )
        .assign(lemma=lambda df: df['wordform'].map(get_lemma))
        .explode('lemma')
        .groupby(['wordform', 'lemma'], as_index=False)
        .aggregate(weight=('wordform', len))
        [['lemma', 'weight', 'wordform']])


def create_lemma_wordform_table(lw_index: DataFrame) -> DataFrame:
    """
    Adds all possible wordforms to the lemma-wordform index.
    TODO: Does not resolve palk/palgi/palga problem
    """
    if ['lemma', 'wordform', 'weight'] != list(lw_index.columns):
        raise ValueError('Expecting a DataFrame with columns lemma, weight and wordform')

    lemma_forms = (lw_index[['lemma']].drop_duplicates()
                   .assign(wordform=lambda df: df['lemma'].map(
                            lambda x: list(set(sum(generate_all_forms(x).values(), [])))))
                   .explode('wordform'))
    return (merge(lemma_forms, lw_index, how='left', on=['lemma', 'wordform'])
            .assign(weight=lambda df: df['weight'].fillna(0).astype(int))
            [['lemma', 'weight', 'wordform']])


def create_subword_table(text: Text):
    if 'morph_analysis' not in text.layers:
        ValueError('Expecting a Text object with morph_analysis layer')

    lemma_index = DataFrame(
        extract_lemma_index('doc_id', text), columns=['lemma', 'doc_id', 'start', 'end', 'weight', 'is_sublemma'])

    return merge(
        lemma_index.loc[~lemma_index['is_sublemma'], ['doc_id', 'start', 'end', 'lemma']],
        lemma_index[lemma_index['is_sublemma']]
        .groupby(['doc_id', 'start', 'end'])
        .aggregate(sublemma=('lemma', lambda x: tuple(set(x)))),
        how='inner', on=['doc_id', 'start', 'end'])[['lemma', 'sublemma']].drop_duplicates().explode('sublemma')
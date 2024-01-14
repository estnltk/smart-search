from estnltk import Text
from pandas import DataFrame

from estnltk_patches.rt_text_analyzer import RTTextAnalyzer
from fast_indexing.fast_indexing import get_lemma
from fast_indexing.fast_indexing import extract_wordform_index


class AdvancedIndexer:

    def __init__(self, text_analyzer=None):
        self.ignore_pos = ['J', 'Z']
        self.text_analyser = text_analyzer or RTTextAnalyzer()

    def __call__(self, doc_id: str,  text: str, *args, **kwargs):
        text_obj = self.analyse_text(text)
        lemma_wordform_index = create_lemma_wordform_index(doc_id, text_obj)
        lemma_wordform_table = create_lemma_wordform_table(lemma_wordform_index)
        subword_table = self.create_subword_table()
        return dict(
            kala=lemma_wordform_index,
            sala=lemma_wordform_table,
            jala=subword_table
        )

    def analyse_text(self, text: str) -> Text:
        return self.text_analyser(Text(text))

    def create_subword_table(self):
        pass


def create_lemma_wordform_index(doc_id: str, text: Text):
    """
    Creates lemma-wordform index based on the analysed input text
    """
    return (
        DataFrame(
            extract_wordform_index(doc_id, RT_ANALYZER(Text(text))),
            columns = ['wordform', 'doc_id', 'start', 'end', 'is_subword'])
            .assign(lemma = lambda df: df['wordform'].map(get_lemma))
            .explode('lemma')
            .groupby(['wordform', 'lemma'], as_index=False)
            .aggregate(weight=('wordform', len))
        [['lemma', 'weight', 'wordform']])

def create_lemma_wordform_table(self, tbl: DataFrame) -> DataFrame:
    pass

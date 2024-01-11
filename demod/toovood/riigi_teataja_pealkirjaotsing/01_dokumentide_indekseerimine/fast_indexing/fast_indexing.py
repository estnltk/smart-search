from estnltk import Text
from estnltk import Layer
from estnltk import Span
from estnltk import EnvelopingBaseSpan
from estnltk.taggers import VabamorfAnalyzer

from typing import List


VM_ANALYZER = VabamorfAnalyzer(propername=False)


def get_lemma(word: str) -> List[str]:
    """
    Analyses the word as it is with Vabamorf and returns the list of lemmas.
    """
    text = Text(word)
    text.add_layer(Layer(name='words', attributes=['normalized_form'], ambiguous=True))
    text.add_layer(Layer(name='sentences', enveloping='words', ambiguous=False))
    text['words'].add_annotation((0, len(word)))
    text['sentences'].add_annotation(EnvelopingBaseSpan([text['words'][0].base_span]))
    return list(set(VM_ANALYZER.tag(text)['morph_analysis'][0]['lemma']))


def extract_sub_wordforms(word: Span, ignore_pos: List[str] = ()):
    """
    Extracts all possible decompositions of a word into its sub-words.
    Returns an empty list if the word is not a compound word.
    If the decomposition is ambiguous returns all variants.
    All analyses with part-of-speech tags in ignore_pos list are omitted.
    """
    result = []
    for annotation in word.annotations:
        if annotation['partofspeech'] in ignore_pos:
            continue
        if len(annotation['root_tokens']) <= 1:
            continue

        split_point = sum(list(map(len, annotation['root_tokens']))[:-1])
        result.append(tuple(map(lambda x: x.lower(), [*annotation['root_tokens'][:-1], word.text[split_point:]])))
    return list(set(result))


def extract_wordform_index(text_id: str, text: Text, ignore_pos: List[str] = None):
    """
    Returns a table with columns VORM, DOCID, START, END, LIITSÕNA_OSA.
    Result is packed as a list of lists.
    All analyses with part-of-speech tags in ignore_pos list are omitted.
    By default, this list is set to ['Z','J']" (punctuation marks and conjunctions)
    """
    if 'morph_analysis' not in text.layers:
        raise ValueError("Argument text does not have 'morph_analysis' layer")

    result = []
    ignore_pos = ignore_pos or ['Z', 'J']
    for token in text['morph_analysis']:
        if set(token['partofspeech']).issubset(ignore_pos):
            continue
        result.append([token.text.lower(), text_id, token.start, token.end, True])

        subwords = set()
        for word_split in extract_sub_wordforms(token, ignore_pos):
            subwords.update(word_split)

        result.extend([[word, text_id, token.start, token.end, False] for word in subwords])

    return result
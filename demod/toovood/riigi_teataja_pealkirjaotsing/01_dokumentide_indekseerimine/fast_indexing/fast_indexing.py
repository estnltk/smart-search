from estnltk import Text
from estnltk import Layer
from estnltk import Span
from estnltk import EnvelopingBaseSpan
from estnltk.taggers import VabamorfAnalyzer

from typing import List


VM_ANALYZER = VabamorfAnalyzer(propername=False)


def get_lemma(word: str, ignore_pos: List[str] = ()) -> List[str]:
    """
    Analyses the word as it is with Vabamorf and returns the list of lemmas.
    """
    text = Text(word)
    text.add_layer(Layer(name='words', attributes=['normalized_form'], ambiguous=True))
    text.add_layer(Layer(name='sentences', enveloping='words', ambiguous=False))
    text['words'].add_annotation((0, len(word)))
    text['sentences'].add_annotation(EnvelopingBaseSpan([text['words'][0].base_span]))

    if len(ignore_pos) == 0:
        return list(set(VM_ANALYZER.tag(text)['morph_analysis'][0]['lemma']))

    result = set()
    for annotation in VM_ANALYZER.tag(text)['morph_analysis'][0].annotations:
        if annotation['partofspeech'] in ignore_pos:
            continue
        result.add(annotation['lemma'])
    return list(result)


def extract_spans_of_sub_wordforms(word, ignore_pos: List[str] = (), combine: bool = True):
    """
    Extracts all possible decompositions of a word into its sub-words.
    Returns an empty list if the word is not a compound word.
    If the decomposition is ambiguous returns all variants.
    All analyses with part-of-speech tags in ignore_pos list are omitted.
    If the combine flag is set then sequentual subwords are combined into
    bigrams, trigrams and tetragrams.
    """
    spans = set()
    for annotation in word.annotations:
        if annotation['partofspeech'] in ignore_pos:
            continue
        if len(annotation['root_tokens']) <= 1:
            continue

        split_points = [0] * (len(annotation['root_tokens']) + 1)
        for i, sub_word in enumerate(annotation['root_tokens'][:-1]):
            split_points[i + 1] = len(sub_word) + split_points[i]
        split_points[-1] = len(word.text)

        for i in range(1, len(split_points)):
            spans.add((split_points[i - 1], split_points[i]))

        if not combine or len(split_points) <= 3:
            continue

        for i in range(2, len(split_points)):
            spans.add((split_points[i-2], split_points[i]))

        if not combine or len(split_points) <= 4:
            continue

        for i in range(3, len(split_points)):
            spans.add((split_points[i-3], split_points[i]))

        if not combine or len(split_points) <= 5:
            continue

        for i in range(4, len(split_points)):
            spans.add((split_points[i-3], split_points[i]))

    return spans


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
        ##? respect letters
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


def extract_lemma_index(text_id: str, text: Text, ignore_pos: List[str] = None):
    """
    Returns a table with columns LEMMA, DOCID, START, END, KAAL, LIITSÕNA_OSA.
    Result is packed as a list of lists.
    All analyses with part-of-speech tags in ignore_pos list are omitted.
    By default, this list is set to ['Z','J']" (punctuation marks and conjunctions)
    """
    if 'morph_analysis' not in text.layers:
        raise ValueError("Argument text does not have 'morph_analysis' layer")

    result = []
    ignore_pos = ignore_pos or ['Z', 'J']
    for token in text['morph_analysis']:

        lemmas = set()
        for annotation in token.annotations:
            if annotation['partofspeech'] in ignore_pos:
                continue
            lemmas.add(annotation['lemma'])

        if len(lemmas) == 0:
            continue

        # Assign weights for the lemmas of the full word
        weight = 1/len(lemmas)
        result.extend([[lemma, text_id, token.start, token.end, weight, False] for lemma in lemmas])

        word_splits = extract_sub_wordforms(token, ignore_pos)
        if len(word_splits) == 0:
            continue
        # TODO: liitsõnade genereerimine word_split --> compounds--> get_lemma
        # Analyse all possible lemmas of the sub-words
        weights = dict()
        prob = 1/len(word_splits)
        for word_split in extract_sub_wordforms(token, ignore_pos):
            for subword in word_split:
                sublemmas = get_lemma(subword, ignore_pos)
                if len(sublemmas) == 0:
                    continue

                subprob = prob * 1/len(sublemmas)
                for sublemma in sublemmas:
                    weights[sublemma] = weights.get(sublemma, 0) + subprob

        result.extend([[word, text_id, token.start, token.end, weight, True] for word, weight in weights.items()])

    return result
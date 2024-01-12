from estnltk import Text
from estnltk import Layer
from estnltk import Span
from estnltk import Annotation
from estnltk import EnvelopingBaseSpan
from estnltk.taggers import VabamorfAnalyzer

from typing import List
from typing import Union


VM_ANALYZER = VabamorfAnalyzer(propername=False)
DASH_SYMBOLS = '-−‒'

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


def extract_spans_of_sub_wordforms(word: Span, annotation: Annotation = None, ignore_pos: List[str] = (), combine: bool = True):
    """
    Extracts all possible decompositions of a word into its sub-words.
    Returns an empty list if the word is not a compound word.
    If the decomposition is ambiguous returns all variants.
    All analyses with part-of-speech tags in ignore_pos list are omitted.
    If the combine flag is set then sequential subwords are combined into
    bigrams, trigrams and tetragrams.
    """
    spans = set()
    # Specific analysis
    if annotation is not None:
        if annotation['partofspeech'] in ignore_pos or len(annotation['root_tokens']) <= 1:
            return spans

        split_points = [0] * (len(annotation['root_tokens']) + 1)
        for i, sub_word in enumerate(annotation['root_tokens'][:-1]):
            split_points[i + 1] = len(sub_word) + split_points[i]
        split_points[-1] = len(word.text)

        for i in range(1, len(split_points)):
            spans.add((split_points[i - 1], split_points[i]))

        if not combine or len(split_points) <= 3:
            return spans

        for i in range(2, len(split_points)):
            spans.add((split_points[i-2], split_points[i]))

        if len(split_points) <= 4:
            return spans

        for i in range(3, len(split_points)):
            spans.add((split_points[i-3], split_points[i]))

        if len(split_points) <= 5:
            return spans

        for i in range(4, len(split_points)):
            spans.add((split_points[i-3], split_points[i]))

        return spans

    # Standard case
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

        if len(split_points) <= 4:
            continue

        for i in range(3, len(split_points)):
            spans.add((split_points[i-3], split_points[i]))

        if len(split_points) <= 5:
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
        if len(token.text) == 0:
            continue

        wordforms = set()
        subwords = dict()
        for annotation in token.annotations:
            if annotation['partofspeech'] in ignore_pos:
                continue

            # We lower the case when the root is in lowercase
            # This does not happen only for pos tags H and Y
            token_text = token.text.lower() if annotation['partofspeech'] not in ['H','Y'] else token.text

            # Erase trailing dashes like nalja- ja pullimees
            if token_text[-1] in DASH_SYMBOLS and len(token_text) > 1:
                token_text = token_text[:-1]

            wordforms.add(token_text)

            # Siim says that for very rare occasions the analysis of subwords fails, since the first compound changes
            # for a lemma,  but it does not crash the code.
            # TODO: Consult Tarmo about this
            for span in extract_spans_of_sub_wordforms(
                    token, annotation=annotation, ignore_pos=ignore_pos, combine=True):
                if span not in subwords:
                    subwords[span] = set()
                subwords[span].add(token_text[span[0]:span[1]])

        # Add all lines for the token simultaneously
        result.extend([word, text_id, token.start, token.end, False] for word in wordforms)
        result.extend([[word, text_id, token.start, token.end, True] for words in subwords.values() for word in words])

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

        # Siim says that for very rare occasions the analysis of subwords fails, since the first compound changes
        # for a lemma,  but it does not crash the code.
        # TODO: Consult Tarmo about this
        weights = dict()
        subword_spans = extract_spans_of_sub_wordforms(token, ignore_pos=ignore_pos, combine=True)
        for start, end in subword_spans:
            subword = token.text[start:end]
            sublemmas = get_lemma(subword, ignore_pos)
            if len(sublemmas) == 0:
                continue

            delta_w = 1/len(sublemmas)
            for sublemma in sublemmas:
                weights[sublemma] = weights.get(sublemma, 0) + delta_w

        result.extend([[word, text_id, token.start, token.end, weight, True] for word, weight in weights.items()])

    return result
from estnltk.vabamorf.morf import synthesize

from typing import Dict
from typing import List


# Nouns and adjectives
PLURALITY = ('sg', 'pl')
CASES = ('ab', 'abl', 'ad', 'adt', 'all', 'el', 'es', 'g', 'ill', 'in', 'kom', 'n', 'p', 'ter', 'tr')
NOUN_FORMS = tuple(f'{plurality} {case}' for plurality in PLURALITY for case in CASES)

# Verbs
# noinspection SpellCheckingInspection
POS_VERB_FORMS = (
    'b', 'd', 'da', 'des', 'ge', 'gem', 'gu', 'ks', 'ksid', 'ksime', 'ksin', 'ksite', 'ma', 'maks',
    'mas', 'mast', 'mata', 'me', 'n', 'nud', 'nuks', 'nuksid', 'nuksime', 'nuksin', 'nuksite', 'nuvat',
    'o', 's', 'sid', 'sime', 'sin', 'site', 'ta', 'tagu', 'taks', 'takse', 'tama', 'tav', 'tavat', 'te',
    'ti', 'tud', 'tuks', 'tuvat', 'v', 'vad', 'vat')

# Olema verb
# noinspection SpellCheckingInspection
NEG_VERB_FORMS = (
    'neg', 'neg ge', 'neg gem', 'neg gu', 'neg ks', 'neg me', 'neg nud', 'neg nuks', 'neg o', 'neg vat', 'neg tud'
)


def generate_all_forms(word: str) -> Dict[str, List[str]]:

    if word == 'olema':
        return {word: list(set(sum([synthesize(word, form) for form in POS_VERB_FORMS + NEG_VERB_FORMS], [])))}

    result = dict()
    # Lemma is a verb
    for hint in synthesize(word, 'b'):
        result[hint] = list(set(sum([synthesize(word, form, hint=hint) for form in POS_VERB_FORMS], [])))

    # Lemma is not a verb
    for hint in synthesize(word, 'sg g'):
        result[hint] = list(set(sum([synthesize(word, form, hint=hint) for form in NOUN_FORMS], [])))

    return result
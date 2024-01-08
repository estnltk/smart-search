import regex as re
from estnltk import Text
from estnltk import EnvelopingSpan
from estnltk import EnvelopingBaseSpan
from estnltk.taggers import VabamorfAnalyzer
from estnltk.taggers import PostMorphAnalysisTagger

from estnltk_patches.rt_token_splitter import RTTokenSplitter


def is_ordinal(span: EnvelopingSpan) -> bool:
    return (len(span) == 2) and (span[1].text == '.') and re.match('^[0-9]+$', span[0].text)


def is_percent(span) -> bool:
    if len(span) == 2 and span[1].text == '%':
        return re.match('^[0-9]+$', span[0].text)
    if len(span) == 4 and span[3].text == '%' and re.match('\.|,', span[1].text):
        return re.match('^[0-9]+$', span[0].text) and re.match('^[0-9]+$', span[2].text)
    return False


class RTTextAnalyzer:
    """
    Dedicated analysis pipeline for Riigi Teataja texts.
    Resolves some tokenization quirks that EstNLTK does not do by default.
    """

    def __init__(self):
        self.token_splitter = RTTokenSplitter()
        self.white_space_string = re.compile('^(\s|[\u200e\ufeff])+$')
        self.morph_analyzer = VabamorfAnalyzer()
        self.post_morph_analyzer = PostMorphAnalysisTagger()

    def __call__(self, text: Text) -> Text:
        # Improve default tokenization
        text.tag_layer('tokens')
        self.token_splitter.retag(text)

        # Remove whitespace spans
        for span in [span for span in text['tokens'] if self.white_space_string.match(span.text)]:
            text['tokens'].remove_span(span)

        text.tag_layer('compound_tokens')

        # Remove ordinals like 1984. and 17. and percentages like 5% and 1.1%
        decimal_fractions = []
        for span in [span for span in text['compound_tokens'] if is_ordinal(span) or is_percent(span)]:
            if len(span) == 4 and is_percent(span):
                decimal_fractions.append([
                    EnvelopingBaseSpan(subs_span.base_span for subs_span in span.spans[:3]),
                    {'type': ['numeric']}])
            text['compound_tokens'].remove_span(span)

        for span, annotation in decimal_fractions:
            text['compound_tokens'].add_annotation(span, annotation)

        # Apply standard morph analysis without disambiguation
        text.tag_layer(['words', 'sentences'])
        self.morph_analyzer.tag(text)
        self.post_morph_analyzer.retag(text)

        return text

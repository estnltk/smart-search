import regex as re

from estnltk.taggers.standard.morph_analysis.proxy import MorphAnalyzedToken

from estnltk_patches.local_token_splitter import LocalTokenSplitter


class RTTokenSplitter(LocalTokenSplitter):
    """
    Dedicated token splitter for Riigi Teataja texts.
    Resolves some quirks that EstNLTK does not do by default.
    """
    def __init__(self):
        cre_number = re.compile('^[0-9]+$')
        subscript_symbols = '[₀₁₂₃₄₅₆₇₈₉₊₋]'
        superscript_symbols = '[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]'

        def split_if_prefix_is_word_or_number(text, match):
            return match.start() if MorphAnalyzedToken(text[0:match.start()]).is_word else -1

        def split_if_prefix_is_word(text, match):
            if cre_number.match(text[0:match.start()]) or text[0:match.start()].isupper():
                return -1
            return match.start() if MorphAnalyzedToken(text[0:match.start()]).is_word else -1

        split_rules = [
            # Separate unexpected symbols from the start
            (re.compile("^(\.-|ˮ|’\))"), lambda x, y: 1),
            # Separate unexpected symbols from the end
            (re.compile("ˮ$"), lambda x, y: y.start()),
            # Chop off sub- and superscripts symbols
            (re.compile(f'({superscript_symbols}|{subscript_symbols})+$'), split_if_prefix_is_word_or_number),
            # Chop off trailing numbers that act as superscripts symbols
            (re.compile('[0-9]+$'), split_if_prefix_is_word)
        ]

        super().__init__(split_rules=split_rules)

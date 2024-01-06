import regex as re

from copy import copy

from estnltk import Text
from estnltk import Layer
from estnltk.taggers import Retagger

from typing import List
from typing import Tuple
from typing import Callable
from typing import MutableMapping


class LocalTokenSplitter(Retagger):
    """
    Splits tokens into smaller tokens based on regular expression patterns.
    One token can be split only once. No recursive splitting strategies are supported.
    If several patterns match then the first in the pattern list is applied.
    Decisions to split or not can depend only on the token itself and not general context.
    """

    output_layer = 'tokens'
    input_layers = ['tokens']
    output_attributes = ()
    conf_param = ['split_patterns']

    def __init__(self,
                 split_rules: List[Tuple[re.Pattern, Callable[[str, re.regex.Match], int]]],
                 output_layer: str = 'tokens'):
        """Initializes LocalTokenSplitter.

        Parameters
        ----------
        split_rules: List[re.Pattern]
            A list of precompiled regular expression Patterns together
            with function that determines the split point.
            If match occurs but split_point == -1 then the match is
            discarded and other patterns are tested.

            The function gets two inputs:
            - token text
            - match object
            and has to compute the split point based on this information.

        output_layer: str (default: 'tokens')
            Name of the layer which contains tokenization results
        """
        # Set input/output layers
        self.output_layer = output_layer
        self.input_layers = [output_layer]
        self.output_attributes = ()

        # Assert that all patterns are in the valid format
        if not isinstance(split_rules, list):
            raise TypeError('(!) patterns should be a list of compiled regular expressions.')

        # TODO: Add more detailed checks or define SplitRules class
        self.split_patterns = copy(split_rules)

    def _change_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        """Rewrites the tokens layer by splitting its tokens into
           smaller tokens where necessary.

           Parameters
           ----------
           text: str
              Text object which annotations will be changed;

           layers: MutableMapping[str, Layer]
              Layers of the text. Contains mappings from the name
              of the layer to the Layer object. Must contain
              the tokens layer.

           status: dict
              This can be used to store metadata on layer tagging.
        """
        # Get changeble layer
        changeble_layer = layers[self.output_layer]
        # Iterate over tokens
        add_spans = []
        remove_spans = []
        for span in changeble_layer:
            token_str = text.text[span.start:span.end]
            for pat, split_point in self.split_patterns:
                match = pat.search(token_str)
                if match is None:
                    continue

                delta = split_point(token_str, match)
                if delta < 0 or delta >= len(token_str):
                    continue

                # Make split
                add_spans.append((span.start, span.start + delta))
                add_spans.append((span.start + delta, span.end))
                remove_spans.append(span)
                # Once a token has been split, then break and move on to
                # the next token ...
                break

        if add_spans:
            assert len(remove_spans) > 0
            for old_span in remove_spans:
                changeble_layer.remove_span( old_span )
            for new_span in add_spans:
                changeble_layer.add_annotation( new_span )
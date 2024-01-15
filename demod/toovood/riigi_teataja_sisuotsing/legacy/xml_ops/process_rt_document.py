
import re
import itertools

from bs4 import BeautifulSoup
from pandas import DataFrame


def extract_text_from_sisutext(content_block) -> str:
    """Extracts texts from an <sisuTekst> element"""

    assert content_block.tag == 'sisuTekst', 'Expecting a <sisuTekst> element'

    result = [None] * len(content_block)
    for i, subentry in enumerate(content_block):
        assert subentry.tail is None or re.match('^\s*$', subentry.tail) is not None, f'Unexpected mixed content {subentry.tail}'
        if subentry.tag == 'tavatekst':
            # Simple case without mixed content
            if len(subentry) == 0:
                result[i] = subentry.text
            # Mixed-content that starts with an element
            else:
                # Handle prefix separately to avoid leading space
                prefix = f'{subentry.text} ' if subentry.text is not None else ''
                # Process all subtree nodes
                elements = list(subentry.xpath('*'))
                texts = [None] * len(elements)
                for j, element in enumerate(elements):
                    if element.tag == 'reavahetus':
                        texts[j] = f"\n{element.tail if element.tail else ''}"
                    else:
                        texts[j] = f"{element.text if element.text else ''} {element.tail if element.tail else ''} "
                result[i] = f"{prefix}{''.join(texts)}"
        elif subentry.tag == 'HTMLKonteiner':
            result[i] = BeautifulSoup(subentry.text, features='lxml').get_text('\n\n', strip=True)
        elif subentry.tag == 'viide':
            text_element = subentry.xpath('kuvatavTekst')
            assert len(text_element) == 1, 'Expecting single element'
            result[i] = text_element[0].text
        elif subentry.tag == 'muutmismarge':
            # Ignore as it is not a part of text. It is a reference mark
            continue
        else:
            assert False, f'Unexpected content element {subentry.tag}'

    # Keep only non-empty blocks in the output
    return '\n\n\n'.join(block for block in result if block is not None)

def extract_references_from_document(xml_doc, base_url:str = 'https://www.riigiteataja.ee/akt/'):
    """Extract references to other RT documents"""

    # Extract sources from metadata
    source_elements = xml_doc.xpath('metaandmed/avaldamismarge/aktViide')
    meta_sources = [source.text for source in source_elements]

    # Extract sources from <sisu> element
    source_elements = xml_doc.xpath('//sisu//viide//viideURI')
    content_sources = [source.text for source in source_elements]

    # Extract embedded links from <HTMLKonteiner>
    hrefs = [re.findall('<a\s+href\s*=\s*(?:"|'').*?>', html_block.text) for html_block in xml_doc.xpath('//HTMLKonteiner')]
    hrefs = list(itertools.chain(*hrefs))
    href_sources = list(map(lambda x:  re.sub('(?:"|'')\s*>$', '', re.sub('^<a\s+href\s*=\s*(?:"|'')', '', x)), hrefs))

    # Resolve local references
    result = DataFrame(meta_sources + content_sources + href_sources, columns = ['references'])

    idx = result['references'].str.contains('^\./[0-9]', regex=True)
    result.loc[idx, 'references'] = result.loc[idx, 'references'].str.replace('^\./', base_url, regex=True)
    result['references'] = result['references'].str.replace('^\./', base_url, regex=True)

    idx = result['references'].str.contains('^[0-9]+$', regex=True)
    result.loc[idx, 'references'] = result.loc[idx, 'references'].map(lambda x: base_url + x)

    # Drop some garbage references: #o
    result = result[~result['references'].str.contains('^#o$', regex=True)]


    return result.drop_duplicates().reset_index(drop=True)

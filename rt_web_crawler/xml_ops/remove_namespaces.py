from lxml import etree
from copy import deepcopy


def remove_namespaces(arg_tree) -> etree.ElementTree:
    """
    Remove all namespaces.
    """
    result = deepcopy(arg_tree)
    for el in result.iter('*'):
        
        if el.tag.startswith('{'):
            el.tag = el.tag.split('}', 1)[1]
            
        # loop on element attributes also
        for an in el.attrib.keys():
            if an.startswith('{'):
                el.attrib[an.split('}', 1)[1]] = el.attrib.pop(an)
        # remove namespace declarations
        etree.cleanup_namespaces(result)

    return result
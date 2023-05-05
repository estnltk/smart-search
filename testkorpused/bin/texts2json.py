#!/usr/bin/env python3

import sys
import os
import json

if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('file', nargs='*', help="Sisendfailid")                       
    args = argparser.parse_args()

    json_out = {"sources":{}}
    for f in args.file:
        with open(f, 'r') as file:
            text = file.read()
            filename, ext = os.path.splitext(f)
            json_out["sources"][filename] = {"content":text}
    json.dump(json_out, sys.stdout, ensure_ascii=False)

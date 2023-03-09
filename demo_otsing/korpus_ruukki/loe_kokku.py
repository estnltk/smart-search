#!/usr/bin/python3

import os
import sys
import json
import requests

class LOE_KOKKU:
    tokens = []
    def lisa(self, sisend):
        self.tokens += sisend["annotations"]["tokens"]
        print(f' {len(sisend["annotations"]["tokens"])}, {len(self.tokens)}')
    pass

if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('FILES', nargs='*', help='sisendfailid')                       
    args = argparser.parse_args()

    loe_kokku = LOE_KOKKU()
    for filename_in in args.FILES:
      with open(filename_in, 'r') as file_in:
          sys.stdout.write(f'\n: {filename_in}')
          loe_kokku.lisa(json.loads(file_in.read()))
    pass

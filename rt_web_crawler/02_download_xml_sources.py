#!/usr/bin/env python

'''
Käsurelt kastumiseks kohendatud 02_download_xml_sources.ipynb
'''

import time
from random import uniform
from pandas import read_csv
from tqdm.auto import tqdm
from urllib.request import urlretrieve

class DOWNLOAD_RT:
    def __init__(self, verbose:bool, sleep_min:str, sleep_max:str)->None:
        self.verbose = verbose
        self.SLEEP_MIN = 0.5
        self.SLEEP_MAX = 2.5
        if sleep_min is not None:
            self.SLEEP_MIN = float(sleep_min)
        if sleep_max is not None:
            self.SLEEP_MAX = float(sleep_max)
        self.liigid = ['state_laws','government_regulations','local_government_acts','government_orders']

    def download_all(self):
        for liik in self.liigid:
            if self.verbose:
               print(f'\n-----------\n{liik}')
            self. download(f'results/{liik}.csv', f'results/xml_sources/{liik}')

    def download(self, source_file, target_path)->None:
        sources = read_csv(source_file, header=0)
        pbar = tqdm(sources.iterrows(), total=len(sources), disable=not self.verbose)
        for idx, row in pbar:
            input_file = row['xml_source']
            output_file = f"{target_path}/{input_file.split('/')[-1]}"
            pbar.set_description(f"{input_file}→{output_file}")
            _, status = urlretrieve(input_file, output_file) 
            time.sleep(uniform(self.SLEEP_MIN, self.SLEEP_MAX))

if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(allow_abbrev=False)
    argparser.add_argument('-v', '--verbose', action='store_false', help='kuva ohtralt progressinfot')
    argparser.add_argument('-n', '--sleep_min', type=str, help='minimalne päringute vahe') 
    argparser.add_argument('-x', '--sleep_max', type=str, help='maksimaalne päringute vahe') 
    args = argparser.parse_args()
    tr = DOWNLOAD_RT(args.verbose, args.sleep_min, args.sleep_max)
    tr.download_all()

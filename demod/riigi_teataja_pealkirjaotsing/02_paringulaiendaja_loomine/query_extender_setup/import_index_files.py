import os
import sys
import glob
import json

from tqdm.auto import tqdm
from configparser import ConfigParser

from database_updater import DatabaseUpdater

def read_config(fname: str):
    config = ConfigParser()
    config.read(fname)
    if 'database' not in config.sections():
        raise ValueError(f"Konfiguratsiooni failis {fname} puudub sektsioon 'database'")
    if 'import' not in config.sections():
        raise ValueError(f"Konfiguratsiooni failis {fname} puudub sektsioon 'import'")

    if 'db_file' not in config['database']:
        raise ValueError(f"Konfiguratsiooni faili {fname} sektsioonis 'database' on määramata väli 'db_file'")
    if 'db_tables' not in config['database']:
        raise ValueError(f"Konfiguratsiooni faili {fname} sektsioonis 'database' on määramata väli 'db_tables'")
    if 'input_dir' not in config['import']:
        raise ValueError(f"Konfiguratsiooni faili {fname} sektsioonis 'import' on määramata väli 'input_dir'")
    if 'verbose' not in config['import']:
        raise ValueError(f"Konfiguratsiooni faili {fname} sektsioonis 'import' on määramata väli 'verbose'")

    return dict(
        db_file=config['database']['db_file'],
        db_tables=json.loads(config['database']['db_tables']),
        input_dir=config['import']['input_dir'],
        verbose=json.loads(config['import']['verbose'].lower()))

def print_help(prog: str):
    print(
        """
        Skript indeksfailide importimiseks päringulaiendaja andmebaasi.
        Kasutus: {prog} --conf_file CONF_FAIL

        Konfiguratsiooni fail CONF_FAIL on ini fail, mis määrab ära:
        - andmebaasi faili asukoha ning uuendatavad tabelid
        - imporditavate indeksfailide kataloogi
        - impordi tüübi

        Detailsemad juhendid on skriptide koodi kõrval oolevas README.md failis.
        """.format(prog=prog)
    )


if __name__ == '__main__':
    import argparse
    import logging

    argparser = argparse.ArgumentParser(allow_abbrev=False, add_help=False)
    argparser.add_argument('-h', '--help',  action="store_true")
    argparser.add_argument('-c', '--conf_file',  type=str)
    args = argparser.parse_args()

    if args.help or args.conf_file is None:
        print_help(argparser.prog)
        sys.exit(0)

    try:
        config = read_config(args.conf_file)
    except ValueError as e:
        print(f"Viga konfiguratsioonifaili {conf_file} parsimisel")
        print(e)
        sys.exit(-1)

    log_level = logging.DEBUG if config['verbose'] else logging.WARNING
    logging.basicConfig(format='%(levelname)s:%(message)s', level=log_level)

    db = DatabaseUpdater(config['db_file'], config['db_tables'], config['verbose'])

    if not os.path.exists(config['input_dir']):
        print(f"Viga! Sisendkataloog {config['input_dir']} puudub")
        sys.exit(-1)

    for file in tqdm(glob.glob(f"{config['input_dir']}*.json")):
        db.toimeta(file)

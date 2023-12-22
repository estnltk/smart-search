import os
import sys
import glob
import argparse
import logging


from read_config import read_config
from database_updater import DatabaseUpdater


def print_help(prog: str):
    print(
        """
        Skript indeksfailide importimiseks päringulaiendaja andmebaasi.
        Kasutus: {prog} --conf_file CONF_FAIL [--append] [--verbose]

        Konfiguratsiooni fail CONF_FAIL on ini fail, mis määrab ära:
        - andmebaasi faili asukoha ning uuendatavad tabelid
        - imporditavate indeksfailide kataloogi
        - impordi tüübi

        Kui --append lipp on seatud, siis uuendab olemasolevat andmebaasifaili.
        Muidu kustutab andmebaasifaili ja teeb uue puhta impordi.
        
        Kui --verbose lipp on seatud, siis näitab progressi ja logiteateid.
        
        Detailsemad juhendid on skriptide koodi kõrval olevas README.md failis.
        """.format(prog=prog)
    )


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(allow_abbrev=False, add_help=False)
    arg_parser.add_argument('-h', '--help', action="store_true")
    arg_parser.add_argument('-c', '--conf_file', type=str)
    arg_parser.add_argument('-a', '--append', action="store_true")
    arg_parser.add_argument('-v', '--verbose', action="store_true")

    args = arg_parser.parse_args()

    if args.help or args.conf_file is None:
        print_help(arg_parser.prog)
        sys.exit(0)

    try:
        config = read_config(args.conf_file)
        config['append'] |= args.append
        config['verbose'] |= args.verbose

    except ValueError as e:
        print(f"Viga konfiguratsioonifaili {args.conf_file} parsimisel")
        print(e)
        sys.exit(-1)

    log_level = logging.DEBUG if config['verbose'] else logging.WARNING
    logging.basicConfig(format='%(message)s', level=log_level)

    db = DatabaseUpdater(config['db_file'], config['db_tables'], verbose=config['verbose'], append=config['append'])

    if not os.path.exists(config['index_dir']):
        print(f"Viga! Sisendkataloog {config['index_dir']} puudub")
        sys.exit(-1)

    for file in glob.glob(f"{config['index_dir']}*.json"):
        logging.info(file)
        db.import_index_file(file)

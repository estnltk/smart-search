import sys
import argparse
import logging
import requests

from tqdm.auto import tqdm
from read_config import read_config
from database_updater import DatabaseUpdater


def print_help(prog: str):
    print(
        """
        Skript kirjavigadega sõnavormide importimiseks päringulaiendaja andmebaasi.
        Kasutus: {prog} --conf_file CONF_FAIL [--verbose]

        Konfiguratsiooni fail CONF_FAIL on ini fail, mis määrab ära:
        - andmebaasi faili asukoha ning uuendatavad tabelid
        - imporditavate indeksfailide kataloogi
        - kirjavigasid genereeriva veebiteenuse aadress

        Kui --verbose lipp on seatud, siis näitab progressi ja logiteateid.
        
        Detailsemad juhendid on skriptide koodi kõrval olevas README.md failis.
        """.format(prog=prog)
    )


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(allow_abbrev=False, add_help=False)
    arg_parser.add_argument('-h', '--help', action="store_true")
    arg_parser.add_argument('-c', '--conf_file', type=str)
    arg_parser.add_argument('-v', '--verbose', action="store_true")

    args = arg_parser.parse_args()

    if args.help or args.conf_file is None:
        print_help(arg_parser.prog)
        sys.exit(0)

    try:
        config = read_config(args.conf_file)
        config['append'] = True
        config['verbose'] |= args.verbose

    except ValueError as e:
        print(f"Viga konfiguratsioonifaili {args.conf_file} parsimisel")
        print(e)
        sys.exit(-1)

    if config['misspellings_generator'] is None:
        print(f"Viga: Konfiguratsioonifailis {args.conf_file} pole määratud kirjavigade genereerimise"
              " veebiteenus 'misspellings_generator'")
        sys.exit(-1)

    log_level = logging.DEBUG if config['verbose'] else logging.WARNING
    logging.basicConfig(format='%(message)s', level=log_level)

    db = DatabaseUpdater(config['db_file'], config['db_tables'], verbose=config['verbose'], append=config['append'])

    logging.info(f"Teeme päringu kirjavigade genereerimisteenusele {config['misspellings_generator']}")

    HEADERS = {"Content-Type": "application/json; charset=utf-8"}
    try:
        response = requests.post(
            config['misspellings_generator'], data='\n'.join(db.wordforms_without_misspellings), headers=HEADERS)
    except Exception as e:
        logging.error(f'Viga veebiteenusega')
        logging.error(e)
        sys.exit(-1)
    if not response.ok:
        logging.error(f'Viga veebiteenusega. Vastus puudub.')
        sys.exit(-1)

    response = response.json()
    logging.info('Lisame saadud kirjavigade tabeli andmebaasi')
    try:
        table = 'kirjavead'
        content = tqdm(response["tabelid"][table], desc=f'# {table: <25}', disable=(not db.verbose))
        db.import_standard_table(table_name=table, row_list=content)
        db.con_base.commit()
    except Exception as e:
        print('Viga kirjavigade impordil andmebaasi')
        print(e)
        sys.exit(-1)

    logging.info('Andmete import edukalt lõpetatud')

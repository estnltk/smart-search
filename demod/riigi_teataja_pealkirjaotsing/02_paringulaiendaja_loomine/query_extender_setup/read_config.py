import json
from configparser import ConfigParser


def read_config(conf_file: str):
    conf = ConfigParser()
    conf.read(conf_file)
    if 'database' not in conf.sections():
        raise ValueError(f"Konfiguratsiooni failis {conf_file} puudub sektsioon 'database'")
    if 'import' not in conf.sections():
        raise ValueError(f"Konfiguratsiooni failis {conf_file} puudub sektsioon 'import'")

    if 'db_file' not in conf['database']:
        raise ValueError(f"Konfiguratsiooni faili {conf_file} sektsioonis 'database' on määramata väli 'db_file'")
    if 'db_tables' not in conf['database']:
        raise ValueError(f"Konfiguratsiooni faili {conf_file} sektsioonis 'database' on määramata väli 'db_tables'")
    if 'input_dir' not in conf['import']:
        raise ValueError(f"Konfiguratsiooni faili {conf_file} sektsioonis 'import' on määramata väli 'input_dir'")
    if 'verbose' not in conf['import']:
        raise ValueError(f"Konfiguratsiooni faili {conf_file} sektsioonis 'import' on määramata väli 'verbose'")

    return dict(
        db_file=conf['database']['db_file'],
        db_tables=json.loads(conf['database']['db_tables']),
        input_dir=conf['import']['input_dir'],
        verbose=json.loads(conf['import']['verbose'].lower()))
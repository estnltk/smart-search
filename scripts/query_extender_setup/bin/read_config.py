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
    if 'index_dir' not in conf['import']:
        raise ValueError(f"Konfiguratsiooni faili {conf_file} sektsioonis 'import' on määramata väli 'index_dir'")

    output = dict(
        db_file=conf['database']['db_file'],
        db_tables=json.loads(conf['database']['db_tables']),
        index_dir=conf['import']['index_dir'],
        source_dir=conf['import'].get('source_dir', None),
        source_id=conf['import'].get('source_id', None),
        source_text=conf['import'].get('source_text', None),
        verbose=json.loads(conf['import'].get('verbose', 'False').lower()),
        append=json.loads(conf['import'].get('append', 'False').lower()),
    )

    if 'web-services' in conf.sections():
        output['misspellings_generator'] = conf['web-services'].get('misspellings_generator', None)
    else:
        output['misspellings_generator'] = None

    return output

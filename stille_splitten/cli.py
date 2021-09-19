#!/usr/bin/env python3

import click
import logging
from pathlib import Path
from .settings import SETTINGS
from .split_silence import run, run_batch

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
exec_name = 'stille_splitten' # 'stille.exe'

def start_processing(**kwargs):
    global SETTINGS
    SETTINGS['cli_input'] = kwargs
    if kwargs['debug']:
        SETTINGS['log_level'] = logging.DEBUG
    if kwargs['batch_processing']:
        run_batch(from_dir=kwargs['verzeichnis'])
    else:
        if kwargs['erwartung'] is None:
            kwargs['erwartung'] = 0
        paired_files = [(Path(kwargs['datei']), kwargs['erwartung'])]
        run(paired_files)

   

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.0.3', help='Version anzeigen und beenden.')
def cli(**kwargs):
    """Findet länger anhaltende Stille in Audiofiles und generiert daraus Sequenzen."""
    pass


@cli.command(short_help=f'''\bBeginnt Stapelverarbeitung mit allen Files im Stapelverzeichnis.\n
 \b
 * Default-Verzeichnis:
  - `{SETTINGS["dir_batch_processing"]}`.
 * Namenskonvention der Dateien im Verzeichnis:
  - `<Erwartung>-W5023536.mp2` (z. B.: 13-W5023536.mp2)
 * Gibt es keine mit einem Bindestrich getrennte Zahl im Dateinamen,
   wird ohne Erwartung gesucht.
 
 Beispielaufruf: `{exec_name} stapel`
 Durchsuche anderes Verzeichnis: `{exec_name} stapel "aus_diesem_verzeichnis"`
 \n
 ''')
@click.argument('verzeichnis', required=False, type=click.Path(exists=True))
@click.option('--debug', is_flag=True, help='Logge ausführlich.')
def stapel(**kwargs):
    '''Beginnt Stapelverarbeitung mit allen Files im Stapelverzeichnis. 
    Wenn ein Wert für <Verzeichnis> angegeben wird, wird in diesem Verzeichnis gesucht.'''
    kwargs['batch_processing'] = True
    start_processing(**kwargs)

@cli.command(short_help=f'''Sucht in <Datei> nach Sequenzen, optional mit der Angabe der Anzahl der erwarteten Sequenzen (<Erwartung>).\n
\b
Beispielaufruf: `{exec_name} datei "abc.mp3"`
Aufruf mit Erwartung: `{exec_name} datei "abc.mp3" 13`
\b\n
''')
@click.argument('datei', type=click.Path(exists=True))
@click.argument('erwartung', type=click.INT, required=False)
@click.option('--debug', is_flag=True, help='Logge ausführlich.')
def datei(**kwargs):
    """Sucht in <Datei> nach Sequenzen, optional mit der Angabe der Anzahl der erwarteten Sequenzen (<Erwartung>)"""
    kwargs['batch_processing'] = False
    start_processing(**kwargs)

"""
"""


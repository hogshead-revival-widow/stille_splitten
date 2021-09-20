import logging
import random
import string
from pathlib import Path

from timecode import Timecode
from .settings import SETTINGS


def setup():
    global SETTINGS
    SETTINGS['run_id'] = get_run_id()
    setup_directories()
    setup_logger()

def setup_directories():
    """ Prüft ob die in `SETTINGS` genannten Verzeichnisse existieren,
    wenn nicht, werden sie angelegt. """
    all_dirs = [key for key in SETTINGS if key.startswith('dir')]
    for dir in all_dirs:
        Path(SETTINGS[dir]).mkdir(parents=True, exist_ok=True)


def setup_logger():
    """ Initalisiert den Logger mit Werten aus:

        * `SETTINGS['log_level']`
        * `SETTINGS['log_file'])` (Path)
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(SETTINGS['log_level'])
    fh = logging.FileHandler(SETTINGS['log_file'])
    fh.setLevel(SETTINGS['log_level'])
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(funcName)s |  %(lineno)04d | %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info(f'Setup erfolgreich. Laufe mit den folgenden Einstellungen: {SETTINGS}')


def check_input(from_file, expectation):
    logger = logging.getLogger(__name__)
    logger.debug(f'input: {from_file, expectation, from_file}')

    if not Path(from_file).is_file():
        is_not_file = f'Die angegebene Audiodatei ("{from_file}") ist keine Datei.'
        raise Exception(is_not_file)
    if not isinstance(expectation, int):
        is_not_number = f'Der angegebene Wert erwarteter Korpusse ("{expectation}") ist keine Zahl.'
        raise Exception(is_not_number)


def is_plausible_result(found_sequences, expectation):
    """ Das Ergebnis ist plausibel, wenn genau so viele
    Sequenzen gefunden wurden, wie erwartet wurde.

    Args:
        * found_sequences: int/iterable
        * expectation: int

    Returns:
        * bool
    """
    logger = logging.getLogger(__name__)
    logger.debug(
        f'input: {found_sequences, expectation}')

    if not isinstance(found_sequences, int):
        found_sequences = len(found_sequences)

    if found_sequences == expectation:
        logger.info(f'Plausibel!')
        return True
    logger.info(
        f'Unplausibel. Erwartet: {expectation}. Gefunden: {found_sequences}')
    return False

def get_batch_files(from_dir):
    """ Liest alle Dateien mit ggf. im Dateinamen vermerkter
    Erwartung an Sequenzen in Datei aus `SETTINGS['dir_batch_processing']`.

    Args:
        * from_dir: Verzeichnis, das durchsucht werden soll
    Returns:
        * paired_files: [(Datei:Path, Erwartete_Sequenzen:int)]  
    """
    logger = logging.getLogger(__name__)
    logger.debug('Stapelverarbeitung: Suche Files')

    def get_expectation(file_name):
        file_name = str(file_name.stem)
        if '-' in file_name:
            expectation = int(file_name.split('-')[0])
            logger.debug(f'Gefundene Erwartung: {expectation}')
            return expectation
        return 0
            
        
    paired_files = [(item, get_expectation(item)) for item in Path(from_dir).glob('**/*.*')
                    if item.is_file() and not item.stem.startswith('.')]
    logger.info(
        f'Stapelverarbeitung: Files gefunden \n Gefundene Files:\n{paired_files}')
    return paired_files

def get_run_id(length=8):
    """ Generiert eine ID der Länge `length`."""
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))

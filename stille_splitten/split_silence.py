import logging
from pathlib import Path
from .consts import SUCCESS, NO_RESULT, UNWEIGHTED_RESULTS, NAME
from .settings import SETTINGS
from .sequences import search_sequences, display_sequences
from .helper import get_batch_files, setup


def display_results(file_name_analyzed, expectation, sequences, plausibility):
    """ Zeigt gefundene Ergebnisse mit weiterführenden Informationen an.

    Args:
        * file_name_analyzed: str/Path 
        * expectation: int
        * sequences: [dict,..]
        * plausibility: int: SUCCESS, <Relative Häufigkeit>, UNWEIGHTED_RESULTS, NO_RESULT
    """
    logger = logging.getLogger(NAME)
    logger.debug(
        f'input: {file_name_analyzed, expectation, sequences, plausibility}')

    file_name = Path(file_name_analyzed).stem
    if plausibility == SUCCESS:
        print(
            f'''Sicherer Fund für: {file_name}. 
            Gefundene Sequenzen: {len(sequences)} (erwartet: {expectation})''')
        display_sequences(file_name_analyzed, plausibility, sequences)
    elif UNWEIGHTED_RESULTS < plausibility < SUCCESS:
        str_expectation = f'(erwartet: {expectation})'
        if expectation == 0:
            str_expectation = '(keine Erwartung angegeben)'
        print(f'''Wahrscheinlicher Fund für: {file_name}.
            Gefundene Sequenzen: {len(sequences)} {str_expectation}
            Zuverlässigkeit: {plausibility}x (bei {len(SETTINGS['ffmpeg_options'])} Durchläufen) die gleiche Sequenz-Menge gefunden.''')
        display_sequences(file_name_analyzed, plausibility, sequences)
    elif plausibility == UNWEIGHTED_RESULTS:
        print(f'''Achtung!
            Keine Bewertung der Funde für: {file_name} möglich.
            Zeige alle unbewerteten Funde mit Sequenzmengen:''')
        for number, sequences in enumerate(sequences, 1):
            print(f'''
            {number}: Gefundene Sequenzen: {len(sequences)}''')
            display_sequences(file_name_analyzed, plausibility, sequences)
        if SETTINGS['batch_processing']:
            print(f'''\nHinweis: Diese Sequenzen werden zur näheren Prüfung alle in eine separate Dateien (Präfix: "unschluessig") geschrieben.''')
    elif plausibility == NO_RESULT:
        print(f'''Achtung!
            Kein Fund für: {file_name}.
            Es wurden hier keinerlei separierende Stillemomente gefunden.''')
    else:
        raise ValueError(
            f'Unerwartetes Ergebnis in plausibility: {plausibility}')


def run(files_from, cli_input=None):
    """ Beginnt Suchprozess in `paired_files`.

    Args:
        * files_from: 
            * entweder: [(Datei:Path, Erwartete_Sequenzen:int)]  
            * oder: Path/str
        * cli_input: None / dict
    """

    setup(cli_input)

    logger = logging.getLogger(NAME)
    paired_files = files_from

    if not isinstance(paired_files, list):
        logger.info(f'Nehme an, dass Stapelverarbeitung')
        logger.debug(f'files_from input: {files_from}')
        print('Bereite Stapelverarbeitung vor.')
        paired_files = get_batch_files(files_from)
    else:
        logger.info(f'Nehme an, dass Einzeldatei-Verarbeitung')

    if len(paired_files) == 0:
        logger.info(f'Beende: Keine Datei gefunden.\n\n')
        print('Problem: Keine Dateien gefunden.')
        if SETTINGS['batch_processing']:
            print(
                f'Sind Dateien im Verzeichnis `{SETTINGS["dir_batch_processing"]}`?')
        exit('Beeendet.')

    logger.info(f'Beginne Suche (Lauf-ID: {SETTINGS["run_id"]}).')
    print(f'Beginne Suche (Lauf-ID: {SETTINGS["run_id"]}).')
    for file_counter, (file_name, expectation) in enumerate(paired_files, 1):
        try:
            nr_of = ''
            if file_counter != len(paired_files):
                nr_of = f'({file_counter}/{len(paired_files)})'
            print(f'Durchsuche: {file_name} {nr_of}')
            print('Das kann einen Moment dauern, bitte warten.')
            all_sequences, plausibility = search_sequences(
                file_name, expectation)
            display_results(file_name, expectation,
                            all_sequences, plausibility)
        except Exception as error:
            logger.debug(f'input: {paired_files}')
            logger.warning(error, exc_info=True)
            print(
                f'Breche Suche für {file_name.stem} ab.\nGrund: {error} (vgl. Log).')
        print('---\n')
        logger.info(f'Beende Durchlauf für {file_name.stem}.')
    done = f"Fertig! (Lauf-ID: {SETTINGS['run_id']})"
    logger.info(done)
    print(done)

import logging
from pathlib import Path
from .consts import SUCCESS, NO_RESULT, UNWEIGHTED_RESULTS
from .settings import SETTINGS
from .sequences import search_sequences, display_sequences
from .helper import setup, get_batch_files

def display_results(file_name_analyzed, expectation, sequences, plausibility):
    """ Zeigt gefundene Ergebnisse mit weiterführenden Informationen an.
    
    Args:
        * file_name_analyzed: str/Path 
        * expectation: int
        * sequences: [dict,..]
        * plausibility: int: SUCCESS, <Relative Häufigkeit>, UNWEIGHTED_RESULTS, NO_RESULT
    """
    logger = logging.getLogger(__name__)
    logger.debug(
        f'input: {file_name_analyzed, expectation, sequences, plausibility}')
    
    file_name = Path(file_name_analyzed).stem
    if plausibility == SUCCESS:
        print(
            f'''Sicherer Fund für: {file_name}. 
            Gefundene Sequenzen: {len(sequences)} (erwartet: {expectation})''')
        display_sequences(file_name_analyzed, plausibility, sequences)
    elif UNWEIGHTED_RESULTS < plausibility < SUCCESS:
        print(f'''Wahrscheinlicher Fund für: {file_name}.
            Gefundene Sequenzen: {len(sequences)} (erwartet: {expectation})
            Zuverlässigkeit: {plausibility}x (bei {len(SETTINGS['ffmpeg_options'])} Gesamtdurchläufen) die gleiche Sequenz-Menge gefunden.''')
        display_sequences(file_name_analyzed, plausibility, sequences)
    elif plausibility == UNWEIGHTED_RESULTS:
        print(f'''Achtung!
            Keine Bewertung der Funde für: {file_name} möglich.
            Zeige alle unbewerteten Funde:''')
        for number, sequences in enumerate(sequences, 1):
            print(f'''{number}: Gefundene Sequenzen: {len(sequences)}''')
            display_sequences(file_name_analyzed, plausibility, sequences)
    elif plausibility == NO_RESULT:
        print(f'''Achtung!
            Kein Fund für: {file_name}.
            Es wurden hier keinerlei separierende Stillemomente gefunden.''')
    else:
        raise ValueError(
            f'Unerwartetes Ergebnis in plausibility: {plausibility}')
    print('\n---')

def run_batch(from_dir):
    """ Beginnt die Stapelverarbeitung.
    
    Args:
        * from_dir: str/Path
    """
    setup()
    
    logger = logging.getLogger(__name__)
    logger.info(f'Stapelverarbeitung: Ergebnisaufgabe auf Sammeldatei gesetzt.')
    SETTINGS['batch_processing'] = True

    if from_dir is None:
        from_dir = SETTINGS["dir_batch_processing"]
    paired_files = get_batch_files(from_dir)

    run(paired_files)


def run(paired_files):
    """ Beginnt Suchprozess in `paired_files`.

    Args:
        * paired_files: [(Datei:Path, Erwartete_Sequenzen:int)]  
    """
    setup()
    
    logger = logging.getLogger(__name__)
    logger.debug(f'Stapelverarbeitung: input: {paired_files}')
    logger.info(f'Beginne Suche (Lauf-ID: {SETTINGS["run_id"]}).')
    print(f'Beginne Suche (Lauf-ID: {SETTINGS["run_id"]}).')
    for file_name, expectation in paired_files:
        try:
            print(f'Durchsuche: {file_name}')
            print('Das kann einen Moment dauern, bitte warten.')
            all_sequences, plausibility = search_sequences(file_name, expectation)
            display_results(file_name, expectation, all_sequences, plausibility)
        except Exception as critical_error:
                logger = logging.getLogger(__name__)
                logger.debug(f'input: {paired_files}')
                logger.debug(critical_error, exc_info=True)
                logger.error(f'Breche Suche für {file_name.stem} ab.\nGrund: {critical_error} (vgl. Log).')

    print('Beendet!')

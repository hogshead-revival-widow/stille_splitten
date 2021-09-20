import logging
import copy
from timecode import Timecode
from .consts import SUCCESS, NO_RESULT, UNWEIGHTED_RESULTS
from .settings import SETTINGS
from .ffmpeg import run_ffmpeg, get_formatted_sequence_info
from .helper import is_plausible_result, check_input
from .export import write_results


def display_sequences(file_name_analyzed, plausibility, sequences):
    """ Zeigt Sequenzmengen an und löst für diese ggf. weiterführen Export-Prozess aus.

    Args:
        * file_name_analyzed: Path 
        * expectation: int
        * sequences: [dict,..]
        * plausibility: int: SUCCESS, <Relative Häufigkeit>, UNWEIGHTED_RESULTS, NO_RESULT
    
    """
    logger = logging.getLogger(__name__)
    logger.debug(f'input: {file_name_analyzed, plausibility, sequences}')

    if SETTINGS['write_results_to_dir']:
        write_results(file_name_analyzed, plausibility, sequences)

    if SETTINGS['print_full_sequences']:
        for sequence in sequences:
            print(f'''
            Korpus #{sequence['korpus_nr']}
                In:     {sequence['start']}
                Out:    {sequence['end']}
                Dauer:  {sequence['duration']}''')

def guess_most_plausible_sequences(all_tries):
    """ Gibt die (grob) plausiblste Sequenzmenge zurück.

    Args:
        * all_tries: [[dict,...],..]
    
    Returns:
        * wenn plausible Sequenzmenge gefunden:
            * Sequenzmenge: [dict,...]
            * Häufigkeit (int>1),
        * wenn nicht:
            * all_tries: [[dict,...],..]
            * 1
    """
    in_all_tries = all_tries
    all_tries = copy.deepcopy(all_tries)

    for tried in all_tries:
        for sequence in tried:
            for key in sequence:
                if isinstance(sequence[key], Timecode):
                    # Vergleichsgenauigkeit auf ~zehn Sekunden reduzieren:
                    # 00:10:12.300 -> 00:10:1
                    sequence[key] = str(sequence[key])[:7]

    weighted_tries = dict()

    for index, sequences in enumerate(all_tries, 0):
        occurence = all_tries.count(sequences)
        weighted_tries[occurence] = in_all_tries[index]

    max_occurence = max(weighted_tries.keys())

    if max_occurence > UNWEIGHTED_RESULTS:
        return (weighted_tries[max_occurence], max_occurence)
    return (in_all_tries, UNWEIGHTED_RESULTS)


def generate_sequences(from_file, expectation):
    """ Generiert mögliche Sequenzmengen aus `from_file`.

    Args:
        * from_file: Pfad zur Datei
        * expectation: int

    Returns:
        * wenn eindeutig
            * found_sequences: [dict(start, ende, dauer, korpus_nr)] (wenn gefunden)
            * True
        * wenn es Versuche gab, die ein Ergebnis hatten
            * all_tries: [found_sequences, found_sequences,...] (wenn nicht gefunden)
            * False
        * wenn alle Versuche kein Ergebnis hatten
            * None
            * False
    """
    logger = logging.getLogger(__name__)
    logger.debug(f'input: {from_file, expectation}')

    all_tries = list()

    for option in SETTINGS['ffmpeg_options']:
        ffmpeg_output = run_ffmpeg(from_file, *option)
        formated_ffmpeg_output = get_formatted_sequence_info(ffmpeg_output)
        if formated_ffmpeg_output is None:
            logger.info(f'Skippe Weiterverarbeitung für Option: {option}.')
            continue
        found_sequences = get_sequences(*formated_ffmpeg_output)

        if is_plausible_result(found_sequences, expectation):
            logger.info('Gefunden!')
            logger.debug(f'Gefunden! Sequenzen: {found_sequences}')
            return found_sequences, True
        else:
            logger.debug(
                f'Zunächst verworfen (Option: {option}): {found_sequences}')
            if len(found_sequences) == 0:
                logger.info(
                    f'Keine Sequenzen gefunden. Nehme nicht in `all_tries` auf.')
            else:
                all_tries.append(found_sequences)

    if len(all_tries) == 0:
        logger.info('Keinerlei Ergebnisse')
        return None, False
    logger.info(f'Kein eindeutige Ergebnisse')
    return all_tries, False


def get_sequences(full_duration, silence_sequences):
    """ Strukturiert die gefundenen Sequenzdaten,
    gibt geordnete Sequenzmenge zurück. 

    Args:
        * full_duration: Timecode
        * timecode_list: [Timecode, Timecode,...]

    Returns:
        * paired_sequences: [dict(start, ende, dauer, korpus_nr)]
    """
    logger = logging.getLogger(__name__)
    logger.debug(f'input: {full_duration, silence_sequences}')
    first_timecode = Timecode(1000, 0)
    last_timecode = full_duration
    all_sequences = list()

    all_sequences.insert(0, first_timecode)
    all_sequences.extend(silence_sequences)
    all_sequences.append(last_timecode)
    paired_sequences = list()

    for korpus_nr, (start, end) in enumerate(zip(*[iter(all_sequences)] * 2), 1):
        logger.debug(f'korpus_nr, (start, end): {korpus_nr, (start, end)}')
        korpus = dict(
            start=start,
            end=end,
            duration=end - start,
            korpus_nr=korpus_nr
        )
        paired_sequences.append(korpus)
    logger.debug(f'output: {paired_sequences}')
    return paired_sequences


def search_sequences(from_file, expectation):
    """ Gibt finale Sequenzmengen mit Bewertung für `from_file` aus.

    Args:
        * from_file: str/Path
        * expectation: int

    Returns:
        * wenn eindeutiges Ergebnis
            * all_sequences: [dict(start, ende, dauer, korpus_nr)]
            * SUCCESS
        * wenn keinerlei Ergebnis
            * None
            * NO_RESULT
        * wenn keine Gewichtung innerhalb Versuche möglich
            * [[dict(start, ende, dauer, korpus_nr)],...]
            * UNWEIGHTED_RESULTS
        * wenn mögliches Ergebnis
            * most_plausible_sequences: [dict(start, ende, dauer, korpus_nr)]
            * <Plausibilität: int> (entspricht der relativen Häufgkeit, bezogen auf Gesamtdurchläufe)
    """
    logger = logging.getLogger(__name__)
    expectation = int(expectation)

    logger.info(
        f'\n\nStarte Suche nach {expectation} Beiträgen für {from_file}\n\n')
    logger.debug(f'Genutzte Settings: {SETTINGS}')
    logger.debug(f'input: {from_file, expectation}')

    check_input(from_file, expectation)

    found_sequences, was_success = generate_sequences(
        from_file, expectation)

    if found_sequences is None:
        logger.info('Keinerlei Ergebnis')
        return None, NO_RESULT

    if was_success:
        logger.debug(f'output: ({found_sequences}, {SUCCESS})')
        return found_sequences, SUCCESS  # eindeutiges ergebnis

    most_plausible_sequences = guess_most_plausible_sequences(found_sequences)
    logger.debug(f'output: ({most_plausible_sequences})')
    return most_plausible_sequences  # (guessed_sequences, occurence)

import logging
import itertools
import math
from timecode import Timecode
from .consts import SUCCESS, NO_RESULT, UNWEIGHTED_RESULTS, NAME
from .settings import SETTINGS
from .ffmpeg import run_ffmpeg, get_formatted_sequence_info
from .helper import is_plausible_result, check_input
from .export import write_results


def display_sequences(file_name_analyzed, plausibility, sequences):
    """ Zeigt Sequenzmengen an und löst für diese ggf. weiterführen Export-Prozess aus.

    Args:
        * file_name_analyzed: Path 
        * plausibility: int: SUCCESS, <Relative Häufigkeit>, UNWEIGHTED_RESULTS, NO_RESULT
        * sequences: [dict,..]
    """

    logger = logging.getLogger(NAME)
    logger.debug(f'input: {file_name_analyzed, plausibility, sequences}')

    if SETTINGS['write_results_to_dir']:
        write_results(file_name_analyzed, plausibility, sequences)

    if SETTINGS['print_full_sequences']:
        for sequence in sequences:
            print(f'''
            Korpus #{sequence['sequence_nr']}
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
            * Häufigkeit (>`UNWEIGHTED_RESULTS`),
        * wenn nicht:
            * all_tries: [[dict,...],..]
            * `UNWEIGHTED_RESULTS`
    """
    compare_list = list()

    for sequences in all_tries:
        compare_sequences = list()
        compare_list.append(compare_sequences)
        for sequence in sequences:
            start = float(sequence['start'].frames / 1000)
            end = float(sequence['end'].frames / 1000)
            compare_sequences.append(start)
            compare_sequences.append(end)


    confirmed_in_different_runs = dict((key,1) for key, _ in enumerate(all_tries))

    compare_list_by_len = dict()
    for index_inner_list, inner_list in enumerate(all_tries):
        compare_list_by_len.setdefault(len(inner_list), list()).append(index_inner_list)

    for _, same_len_lists in compare_list_by_len.items():
        if len(same_len_lists) > 1:
            for a, b in itertools.combinations(same_len_lists, 2):
                if all((math.isclose(that, other, abs_tol=SETTINGS['tolerance']) for that, other in zip(compare_list[a], compare_list[b]))):
                    confirmed_in_different_runs[a] += 1
                    confirmed_in_different_runs[b] += 1


    max_confirmed = max(confirmed_in_different_runs.values())
    index_most_plausible_sequences = dict((v,k) for k,v in confirmed_in_different_runs.items())[max_confirmed]

    if max_confirmed > UNWEIGHTED_RESULTS:
        return all_tries[index_most_plausible_sequences], max_confirmed
    return all_tries, UNWEIGHTED_RESULTS


def generate_sequences(from_file, expectation):
    """ Generiert mögliche Sequenzmengen aus `from_file`.

    Args:
        * from_file: Pfad zur Datei
        * expectation: int

    Returns:
        * wenn eindeutig
            * found_sequences: [dict(start, end, duration, sequence_nr)] (wenn gefunden)
            * True
        * wenn es Versuche gab, die ein Ergebnis hatten
            * all_tries: [found_sequences, found_sequences,...] (wenn nicht gefunden)
            * False
        * wenn alle Versuche kein Ergebnis hatten
            * None
            * False
    """
    logger = logging.getLogger(NAME)
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
        * silence_sequences: [Timecode, Timecode,...]

    Returns:
        * paired_sequences: [dict(start, end, duration, sequence_nr)]
    """
    logger = logging.getLogger(NAME)
    logger.debug(f'input: {full_duration, silence_sequences}')
    first_timecode = Timecode(1000, 0)
    last_timecode = full_duration
    all_sequences = list()

    all_sequences.insert(0, first_timecode)
    all_sequences.extend(silence_sequences)
    all_sequences.append(last_timecode)
    paired_sequences = list()

    for sequence_nr, (start, end) in enumerate(zip(*[iter(all_sequences)] * 2), 1):
        logger.debug(f'sequence_nr, (start, end): {sequence_nr, (start, end)}')
        korpus = dict(
            start=start,
            end=end,
            duration=end - start,
            sequence_nr=sequence_nr
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
            * all_sequences: [dict(start, ende, dauer, sequence_nr)]
            * SUCCESS
        * wenn keinerlei Ergebnis
            * None
            * NO_RESULT
        * wenn keine Gewichtung innerhalb Versuche möglich
            * [[dict(start, end, duration, sequence_nr)],...]
            * UNWEIGHTED_RESULTS
        * wenn mögliches Ergebnis
            * most_plausible_sequences: [dict(start, end, duration, sequence_nr)]
            * <Plausibilität: int> (entspricht der relativen Häufgkeit, bezogen auf Gesamtdurchläufe)
    """
    logger = logging.getLogger(NAME)
    expectation = int(expectation)

    if expectation > 0:
        logger.info(
            f'\n\nStarte Suche nach {expectation} Beiträgen für {from_file}\n\n')
    else:
        logger.info(f'\n\nStarte Suche nach Beiträgen für {from_file} (ohne Erwartung) \n\n')
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

import logging
import json
from pathlib import Path
from timecode import Timecode
import pandas as pd
from .settings import SETTINGS
from .consts import UNWEIGHTED_RESULTS

def serialize_timecode(tc):
    if not isinstance(tc, Timecode):
        return tc
    return tc.__str__()


def write_batch_results(file_name_analyzed, plausibility, sequences):
    """ Schreibt errechnete Ergebnisse in Sammeldateien (JSON/Excel),
    je eine für alle in diesem Stapelverarbeitungsprozess analysierten Dateien.
    
    Args:
        * file_name_analyzed: Path
        * plausibility: int
        * sequences: [dict,..]
    """

    logger = logging.getLogger(__name__)
    logger.info('Schreibe Ergebnis in Sammeldatei')

    to_dir = SETTINGS['dir_results']

    file_name_id = SETTINGS['run_id']
    
    if plausibility == UNWEIGHTED_RESULTS:
        file_name_results = f'unschluessig_{file_name_analyzed.stem}_{file_name_id}'
    else:
        file_name_results = f'ergebnisse_{file_name_id}'

    excel_file = Path(to_dir) / Path(f'{file_name_results}.xlsx')
    json_file = Path(to_dir) / Path(f'{file_name_results}.json')

    

    for item in sequences:
        item.update(
            dict(sicherheit=plausibility,
                 datei=str(file_name_analyzed.stem))
        )

    results = pd.DataFrame(sequences)

    if Path(excel_file).is_file():
        df_excel = pd.read_excel(excel_file)
        result = pd.concat([df_excel, results], ignore_index=True)
        result.to_excel(excel_file, index=False)
    else:
        writer = pd.ExcelWriter(excel_file)
        results.to_excel(writer, index=False)
        writer.save()

    if Path(json_file).is_file():
        with open(json_file, 'r') as f:
            file_data = json.load(f)
        file_data.append(sequences)
        with open(json_file, 'w') as f:
            json_out = json.dump(file_data, f, indent=4, default=serialize_timecode)
    else:
        with open(json_file, 'w') as f:
            json.dump([sequences], f, indent=4, default=serialize_timecode)


def write_single_results(file_name_analyzed, plausibility, sequences):
    """ Schreibt errechnete Ergebnisse in Einzeldateien (JSON/Excel)
    pro zu analysierende Datei.
    
    Args:
        * file_name_analyzed: Path
        * plausibility: int
        * sequences: [dict,..]
    """
    
    logger = logging.getLogger(__name__)
    logger.info('Schreibe Ergebnis in Einzeldateien')

    to_dir = SETTINGS['dir_results']

    file_name_id = SETTINGS['run_id']
    file_name_results = f'{Path(file_name_analyzed).stem}_{file_name_id}'


    excel_file = Path(to_dir) / Path(f'{file_name_results}.xlsx')
    json_file = Path(to_dir) / Path(f'{file_name_results}.json')

    for item in sequences:
        item.update(
            dict(sicherheit=plausibility,
                 datei=str(file_name_analyzed.stem)
        ))

    results = pd.DataFrame(sequences)

    writer = pd.ExcelWriter(excel_file)
    results.to_excel(writer, index=False)
    writer.save()

    with open(json_file, 'w') as f:
            json_out = json.dumps([sequences], indent=4, default=serialize_timecode)
            f.write(json_out)
    

    

def write_results(file_name_analyzed, plausibility, sequences):
    """ Löst entweder Sammel- oder Einzeldateien-Export der Ergebnisse aus
    (abhängig von SETTINGS['batch_processing']).

    Args:
        * file_name_analyzed: Path
        * plausibility: int
        * sequences: [dict,..]
    """
    logger = logging.getLogger(__name__)
    logger.debug(
        f'input: {file_name_analyzed, plausibility, sequences}')

    if plausibility == UNWEIGHTED_RESULTS:
        write_batch_results(file_name_analyzed, plausibility, sequences)
        return None

    if SETTINGS['batch_processing']:
        write_batch_results(file_name_analyzed, plausibility, sequences)
        return None

    write_single_results(file_name_analyzed, plausibility, sequences)


import re
import logging
import ffmpeg
from timecode import Timecode
from .settings import SETTINGS


def run_ffmpeg(from_file, threshold, min_duration):
    """ Sucht per FFMPEG in `from_file` nach Stille,
    wobei Stille dann ist, wenn sie:

        * mindestens `min_duration` lang ist (Sekunden)
        * und die Lautstärke dort maximal `threshold` dBFS (0=maximale Lautsärke)
        beträgt.
    
    Args:
        threshold: int
        min_duration: int/float
    
    Returns: 
        * ffmpeg_output: str
    """
    logger = logging.getLogger(__name__)

    logger.info(
        f'FFMPEG-Durchlauf: Optionen: Schwellert: {threshold}dBFS; Mindestdauer: {min_duration} Sekunden')
    ffmpeg_output = (
        ffmpeg
        .input(from_file)
        .filter('silencedetect', n=f'{threshold}dB', d=f'{str(min_duration)}')
        .output('pipe:, ''-', format='null')
        .run(capture_stdout=True, quiet=True, cmd=str(SETTINGS['ffmpeg_binary']))
    )
    logger.debug(f'FFMPEG-Durchlauf: output ffmpeg: {ffmpeg_output}')
    return str(ffmpeg_output)

def get_formatted_sequence_info(from_ffmpeg_output):
    """ Puhlt Timecodes für Gesamtdauer und Stille-Sequenzen aus `ffmpeg´-Ausgabe.

    Args:
        * from_ffmpeg_output: str

    Returns:
        * wenn gefunden
            * full_duration: Timecode
            * silence_sequences: [Timecode,...]
        * wenn nicht
            * None

    """
    from_ffmpeg_output = str(from_ffmpeg_output)
    logger = logging.getLogger(__name__)
    logger.debug(f'input {from_ffmpeg_output}')

    # Gesamtdauer (File)
    full_duration = from_ffmpeg_output.rindex('time=')
    full_duration = from_ffmpeg_output[full_duration:]
    pattern = r'(\d\d:\d\d:\d\d.\d+)\sbitrate'
    full_duration = re.search(pattern, full_duration)
    if full_duration is None:
        raise Exception(
            'Die Gesamtdauer des Audiofiles konnte nicht bestimmt werden.')
    full_duration = Timecode(1000, full_duration.group(1))
    logger.debug(f'Full duration: {full_duration}')

    silence_sequences = list()
    pattern = r'(?:silence_start:|silence_end:)\W(\d+.\d+)'
    pattern = re.compile(pattern)
    matches = re.findall(pattern, from_ffmpeg_output)

    logger.debug(f'Matches: {matches}')

    if len(matches) == 0:
        logger.info('Keine Stille gefunden.')
        return None
    # Duplikate sind möglich, wenn Threshold zu hoch/Duration zu gering ist
    if len(matches) != len(set(matches)):
        logger.info('Duplikate in Matches.')
        return None

    if len(matches) % 2 == 0:
        for start, end in zip(*[iter(matches)]*2):
            start = Timecode(1000, start_seconds=float(start))
            end = Timecode(1000, start_seconds=float(end))
            silence_sequences.append(start)
            silence_sequences.append(end)
    else:
        raise Exception(
            'Unerwartete Anzahl von start/end-Silence-Paaren aus ffmpeg')
    logger.debug(f'output: {full_duration, silence_sequences}')
    return full_duration, silence_sequences

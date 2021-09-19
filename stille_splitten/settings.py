from pathlib import Path
import logging
import sys
import pkg_resources

app_root = Path.home() / 'Desktop' / 'stille_splitten'

#ffmpeg_file = 'ffmpeg'
#if 'win32' in sys.platform.lower():
#    ffmpeg_file = 'ffmpeg.exe'
#ffmpeg_file = pkg_resources.resource_filename('stille_splitten', f'bin/'+ffmpeg_file) 

#if not Path(ffmpeg_file).is_file():
#    raise Exception(f'Fehler: Benötigte ffmpeg-Datei nicht gefunden ({ffmpeg_file})')

ffmpeg_file = 'ffmpeg'

SETTINGS = dict(
    batch_processing=False,
    log_level=logging.INFO,
    log_file=app_root / 'stille_splitten.log',
    dir_results=app_root / 'ergebnisse',
    dir_batch_processing=app_root / 'stapelverarbeitung',
    write_results_to_dir=True,
    print_full_sequences=False,
    # (Stille-Schwellwert: dBFS, Stille-Mindestdauer: Sekunden)
    ffmpeg_options=[(-60, 2), (-50, 1), (-70, 2), (-50, 2),
                    (-70, 1.5), (-60, 1.5), (-60, 3), (-60, 1)],
    cli_input = None,
    run_id = None,
    ffmpeg_binary=ffmpeg_file
)
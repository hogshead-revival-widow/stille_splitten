from pathlib import Path
import logging

app_root = Path.home() / 'Desktop' / 'stille_splitten'


SETTINGS = dict(
    batch_processing=False,
    log_level=logging.INFO,
    log_file=app_root / 'stille_splitten.log',
    dir_results=app_root / 'ergebnisse',
    dir_batch_processing=app_root / 'stapelverarbeitung',
    write_results_to_dir=True,
    print_full_sequences=False,
    # (Stille-Schwellwert: dBFS, Stille-Mindestdauer: Sekunden)
    ffmpeg_options=[(-60, 2), (-50, 1), (-70, 2), (-50, 2)],
    cli_input=None,
    run_id=None,
    ffmpeg_binary='ffmpeg'
)

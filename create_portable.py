from os import error
import sys
import traceback
import subprocess
import shutil
import pkg_resources
from pathlib import Path
from stille_splitten.consts import NAME, FFMPEG_FILE, PYINSTALL_PLANNED

if not PYINSTALL_PLANNED:
    sys.exit('Pyinstallation laut stille_splitten.consts nicht geplant. Bitte ggf. ändern.')

try:
    import pyinstaller
except ModuleNotFoundError:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', 'pyinstall'])


template = '''from stille_splitten.cli import cli
cli()'''

file_name = Path(NAME).stem + '.py'
if not Path(file_name).is_file():
    with open(file_name, 'w') as f:
        f.write(template)
else:
    sys.exit(f'Kann Datei nicht anlegen, {file_name} existiert bereites.')


try:
    name_dir = NAME
    if '.' in NAME:
        name_dir = NAME.split('.')[0]
    ffmpeg_bin = Path('stille_splitten') / FFMPEG_FILE

    subprocess.check_call(['pyinstaller', file_name])

    target_path = Path(Path('dist') / name_dir / ffmpeg_bin.parent)
    target_path.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ffmpeg_bin, target_path)

    print(f'Done: {NAME} sollte nun als unabhängig ausführbare Datei vorliegen.')
except Exception as error:
    print(error, traceback.format_exc())
    print('Fehler, abgebrochen.')
created_file = Path(file_name) 
if created_file.is_file():
    created_file.unlink()

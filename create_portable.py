import sys
import traceback
import subprocess
import shutil
from pathlib import Path
from stille_splitten.consts import NAME, FFMPEG_FILE, PYINSTALL_PLANNED

if not PYINSTALL_PLANNED:
    sys.exit('Erstellung einer portablen Version laut stille_splitten.consts nicht geplant. Bitte ggf. ändern.')


try:
    import pyinstaller
except ModuleNotFoundError:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', 'pyinstall'])


output_name = Path(NAME).stem
pyinstaller_input_file_content = '''from stille_splitten.cli import cli
cli()'''
pyinstaller_input_file = output_name + '.py'
pyinstaller_input_file = Path(pyinstaller_input_file)
if not pyinstaller_input_file.is_file():
    with open(pyinstaller_input_file, 'w') as f:
        f.write(pyinstaller_input_file_content)
else:
    sys.exit(f'''Kann Datei nicht anlegen,
{pyinstaller_input_file} existiert bereites.''')

try:
    ffmpeg_bin = Path('stille_splitten') / FFMPEG_FILE
    if not ffmpeg_bin.is_file():
        sys.exit('''Konnte ffmpeg-binary nicht finden. Bitte unter stille_splitten/bin ablegen
und `FFMPEG_FILE` in consts entsprechend benennen.''')

    subprocess.check_call(['pyinstaller', pyinstaller_input_file])

    dist_path = Path('dist') / output_name
    target_path = dist_path / ffmpeg_bin.parent
    target_path.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ffmpeg_bin, target_path)

    shutil.move(str(dist_path), output_name)

    print(f'''Das Verzeichnis `{Path(output_name).absolute()}`
enthält nun eine portable Version von `{NAME}`.''')

except Exception as error_was:
    print(error_was, traceback.format_exc())
    print('Fehler, abgebrochen.')

# clean up
to_be_removed = [
    Path('dist'),
    Path('build'),
    Path(output_name + '.spec'),
    pyinstaller_input_file
]

for item_to_remove in to_be_removed:
    if item_to_remove.is_file():
        item_to_remove.unlink()
    elif item_to_remove.is_dir():
        shutil.rmtree(item_to_remove)

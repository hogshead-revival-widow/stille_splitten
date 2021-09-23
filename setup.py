import sys
from pathlib import Path
from setuptools import setup, find_packages
from stille_splitten.consts import VERSION, NAME, FFMPEG_FILE, PYINSTALL_PLANNED

if PYINSTALL_PLANNED and not Path('stille_splitten' / Path(FFMPEG_FILE)).is_file():
    sys.exit('''Wenn `pyinstall`-Installation geplant ist, bitte in `consts.py`
    `FFMPEG_FILE` setzen''')

package_data = {'stille_splitten': []}
if PYINSTALL_PLANNED:
   package_data = {'stille_splitten': [FFMPEG_FILE]}

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

setup(
    name='stille_splitten',
    version=VERSION,
    description='Splittet Beiträge die durch Stille separiert sind',
    packages=find_packages(),
    python_requires='>=3.6.8',
    classifiers=['Development Status :: 3 - Alpha',
                 'Programming Language :: Python', 'Programming Language :: Python :: 3',
                 'Topic :: Multimedia :: Sound/Audio', 'Topic :: Multimedia :: Sound/Audio :: Analysis',
                 'Topic :: Utilities'],
    install_requires=install_requires,
    package_data=package_data,
    entry_points={
        "console_scripts": [f"{NAME} = stille_splitten.cli:cli"]
    }
)

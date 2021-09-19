#!/usr/bin/env python3


from setuptools import setup, find_packages
import sys


#ffmpeg_file = 'ffmpeg'
#if 'win32' in sys.platform.lower():
#    ffmpeg_file = 'ffmpeg.exe'

setup(
    name='stille_splitten',
    version='0.0.3',
    description='Splittet Beiträge die durch Stille separiert sind',
    packages=find_packages(),
    include_package_data=True,
    #package_data={'stille_splitten': ['bin/'+ffmpeg_file]},
    python_requires='>=3.8.2',
    classifiers=['Development Status :: 3 - Alpha',
                 'Programming Language :: Python', 'Programming Language :: Python :: 3',
                 'Topic :: Multimedia :: Sound/Audio', 'Topic :: Multimedia :: Sound/Audio :: Analysis',
                 'Topic :: Utilities'],
    install_requires=['click==8.0.1',
                      'et-xmlfile==1.1.0',
                      'ffmpeg-python==0.2.0',
                      'future==0.18.2',
                      'numpy==1.21.2',
                      'openpyxl==3.0.8',
                      'pandas==1.3.3',
                      'python-dateutil==2.8.2',
                      'pytz==2021.1',
                      'six==1.16.0',
                      'timecode==1.3.1'],
    entry_points={
        "console_scripts": ["stille_splitten = stille_splitten.cli:cli"]
    },
)

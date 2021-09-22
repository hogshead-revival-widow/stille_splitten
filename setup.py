from setuptools import setup, find_packages
from stille_splitten.consts import VERSION, NAME

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

setup(
    name=NAME,
    version=VERSION,
    description='Splittet Beiträge die durch Stille separiert sind',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6.8',
    classifiers=['Development Status :: 3 - Alpha',
                 'Programming Language :: Python', 'Programming Language :: Python :: 3',
                 'Topic :: Multimedia :: Sound/Audio', 'Topic :: Multimedia :: Sound/Audio :: Analysis',
                 'Topic :: Utilities'],
    install_requires=install_requires,
    entry_points={
        "console_scripts": [f"{NAME} = stille_splitten.cli:cli"]
    }
)

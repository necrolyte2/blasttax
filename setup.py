# Install setuptools automagically from the interwebz
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

from blasttax import __version__

setup(
    name = 'blasttax',
    version = __version__,
    py_modules = ['blasttax'],
    setup_requires = [
        'nose',
        'python-coveralls'
    ],
    tests_require = [
        'nose',
        'mock',
    ],
    install_requires = [],
    author = 'Tyghe Vallard',
    author_email = 'vallardt@gmail.com',
    description = 'Easily get taxonomy/phylogony information for a blast taxid',
    license = 'GPL v2',
    keywords = 'blast, taxid, taxonomy, phylogony, ncbi',
    url = 'https://github.com/necrolyte2/blasttax',
)

"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


# Read the API version from disk 
with open(path.join(here, 'pytaskmanager', 'VERSION')) as fp:
    __version__ = fp.read()


# Setup the package
setup(
    name='pytaskmanager',
    version=__version__,
    description='Package and utilities for distributed learning',
    long_description=long_description,
    url='https://github.com/mellesies/pytaskmanager',
    # author='Maastro/IKNL',
    # author_email='',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3',
    install_requires=[
        'appdirs',
        'bcrypt',
        'click',
        'flask',
        'flask-cors',
        'flask-jwt-extended',
        'flask-restful',
        'flask-sqlalchemy',
        'flask-marshmallow',
        'marshmallow',
        'marshmallow-sqlalchemy',
        'pyyaml',
        'requests',
        'termcolor',
        'sqlalchemy',
    ],
    package_data={  
        'pytaskmanager': [
            'server/server.wsgi', 
            'VERSION', 
            '_data/*.yaml',
            'server/resource/swagger/*.yaml'
        ],
    },
    entry_points={
        'console_scripts': [
            'ptm=pytaskmanager.cli.cli:cli',
        ],
    },
)
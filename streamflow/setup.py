"""Setup script for the pystreamflow python package.
"""

import os
from setuptools import setup, Extension

ext1 = Extension('ode', [os.path.join('pystreamflow', 'ode.c')])

setup(
    name='pystreamflow',
    description='Hydrology models in Python and PINTS',
    version='0.1',
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'pandas',
        'pints',
        ],
    extras_require={
        'dev': [
            'flake8>=3',
            ],
        'cvode': [
            'scikits.odes',
        ],
    },
    ext_modules=[ext1],
)

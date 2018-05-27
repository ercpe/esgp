#!/usr/bin/env python3

from setuptools import setup

VERSION = "0.1"

setup(name="esgp",
      version=VERSION,
      description="Enhanced SuperGenPass",
      author="Johann Schmitz",
      url="https://git.ercpe.de/ercpe/esgp",
      license="GPLv3",
      packages=['esgp'],
      install_requires=[
          'daiquiri',
          'PyQt5',
      ],
)

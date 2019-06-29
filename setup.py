# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='src',
    version='0.0.1',
    description='bcn-energy',
    long_description=readme,
    url='https://noumena.io/downloads',
    license=license,
    packages=find_packages(exclude=('src', 'tests', 'docs', 'BCNEnergy'))
)

from distribute_setup import use_setuptools
use_setuptools()

from distutils.core import Command
from setuptools import setup, find_packages


setup(
    name='orchestra',
    version='0.1',
    packages=find_packages(),

    tests_require=['pytest', 'mock'],

    author='Jason Michalski',
    author_email='armooo@armooo.net',
    description='Orchestra instrments your python code to try and create coverage reports',
)



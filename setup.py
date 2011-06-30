"""                                                                                                                                                                                                         
setup.py for nosedbreport
 
 
"""
__author__ = "Ali-Akber Saifee"
__email__ = "ali@indydevs.org"
 
from setuptools import setup, find_packages

setup(
    name='NoseDBResult',
    version='0.1',
    entry_points = {
        'nose.plugins.0.10': [
            'nosedbreport = nosedbreport:NoseDBReporter']
        },
    packages = ['nosedbreport'],
)


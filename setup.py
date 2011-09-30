"""                                                                                                                                                                                                         
setup.py for nosedbreport
 
 
"""
__author__ = "Ali-Akber Saifee"
__email__ = "ali@mig33global.com"
__copyright__ = "Copyright 2011, ProjectGoth"

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


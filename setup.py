"""
setup.py for nosedbreport


"""
__author__ = "Ali-Akber Saifee"
__email__ = "ali@indydevs.org"
__copyright__ = "Copyright 2014, Ali-Akber Saifee"

from setuptools import setup, find_packages
import nosedbreport
setup(
    name='nosedbreport',
    author = __author__,
    author_email = __email__,
    license = "MIT",
    version=nosedbreport.__version__,
    url='https://nosedbreport.readthedocs.org/en/latest/',
    include_package_data = True,
    package_data = {
            '':[ 'README.rst' ],
         },
    description='Nose plugin for recording test results to a database',
    long_description=open('README.rst').read(),
    entry_points = {
        'nose.plugins.0.10': [
            'nosedbreport = nosedbreport:NoseDBReporter']
        },
    packages = ['nosedbreport'],
)


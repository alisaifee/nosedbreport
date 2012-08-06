"""                                                                                                                                                                                                         
setup.py for nosedbreport
 
 
"""
__author__ = "Ali-Akber Saifee"
__email__ = "ali@mig33global.com"
__copyright__ = "Copyright 2011, ProjectGoth"

from setuptools import setup, find_packages

setup(
    name='NoseDBReport',
    author = __author__,
    author_email = __email__,
    license = "MIT",
    version='0.1',
    url='http://hg.indydevs.org/nosedbreport',
    include_package_data = True,
    package_data = {
            '':[ 'README' ],
         },
    description='Nose plugin for recording test results to a database',
    long_description=open('README').read(),
    entry_points = {
        'nose.plugins.0.10': [
            'nosedbreport = nosedbreport:NoseDBReporter']
        },
    packages = ['nosedbreport'],
)


.. _git repository: http://github.com/mig33/nosedbreport
.. _read the docs: http://nosedbreport.readthedocs.org/en/latest/

Introduction
============
nosedbreport exposes a single plugin that can front various backend databases to store
the result of a nose test execution. Having the results of your tests, whether they are part
of a continuous integration system or not, allows you to ask interesting questions about
your project such as

* What were the test suites that ran in the last five minutes
* What is the average time to run test case 'x' 
* What is the standard time to failure for test suite 'y'
* and so on...
 
These questions also allow you to build reporting, and monitoring tools based on automated
functional tests that you may be running against your development, staging or production
systems, such as heartbeat or availability pages.

Installation
============
* with easy_install ::
   
    sudo easy_install nosedbreport

* with pip ::
    
    sudo pip install nosedbreport

* from source (`git repository`_)::

    hg clone http://github.com/mig33/nosedbreport
    cd nosedbreport
    python setup.py build
    sudo python setup.py install

.. image:: https://secure.travis-ci.org/mig33/nosedbreport.png?branch=master
    :target: https://travis-ci.org/#!/mig33/nosedbreport

Usage
=====
* The most basic use case is to report the results of a test run into a mysql database,
   which can be achieved by adding the following options to your nose execution::

	nosetests --dbreport-dbtype=mysql --dbreport-host=your.mysql.com\
	 --dbreport-username=ali --dbreport-password=some-pass --dbreport-db=nosereport
 
* To create the appropriate schema in your mysql database::

    nosetests --dbreport-dbtype=mysql --dbreport-host=your.mysql.com\
     --dbreport-username=root  --dbreport-password=your-root-pass\
     --dbreport-db=nosereport --dbreport-create-schema

* For detailed usage refer to `read the docs`_


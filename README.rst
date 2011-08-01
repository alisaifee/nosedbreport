Introduction
============
nosedbreport exposes a single plugin that can front various backend databases to store
the result of a nose test execution.

Installation
------------ 
 * with easy_install ::
   
    sudo easy_install nosedbreport
 * with pip ::
    
    sudo pip install nosedbreport
 * from source ::

    hg clone http://hg.indydevs.org/ali/nosedbreport
    cd nosedbreport
    python setup.py build
    sudo python setup.py install


Usage
-----
 # The most basic use case is to report the results of a test run into a mysql database,
   which can be achieved by adding the following options to your nose execution::

	nosetests --dbreport_dbtype=mysql --dbreport_host=your.mysql.com --dbreport_user=ali --dbreport_password=some-pass --dbreport_db=nosereport
 
 # To create the appropriate schema in your mysql database::

    nosetests --dbreport_dbtype=mysql --dbreport_host=your.mysql.com --dbreport_user=root --dbreport_password=your-root-pass --dbreport_db=nosereport --dbreport_create_schema




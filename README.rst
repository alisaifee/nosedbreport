Introduction
============
nosedbreport exposes a single plugin that can front various backend dbs to store
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
 # The most basic use case is to report the results of a test run into a mysql database, which can be achieved by adding the following options::

	nosetests --dbreport_dbtype=mysql --dbreport_host=your.mysql.com --dbreport_user=ali --dbreport_password=some-pass --dbreport_db=nosetests






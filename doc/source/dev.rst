Development
===========
Contributing
------------
.. _bitbucket repository: http://hg.indydevs.org/nosedbreport

The source is maintained in a `bitbucket repository`_. Feel free to fork it to modify/extend the plugin.
Currently, the plugin is only backed by a MySQL connector, but it can be easily extended to support other databases.

To add a new database connector, you will need to:
 
 * add a new class that extends :class:`nosedbreport.base.NoseDBReporterBase`
 * implement the :meth:`configure`, :meth:`startTest` and :meth:`report` methods. (For an example see the MySQL implementation in
   :class:`nosedbreport.mysql.NoseMySQLReporter`)
 * add your new class to the :attr:`nosedbreport.plugin.NoseDBReporter.connectors` in :mod:`nosedbreport.plugin` in the following way::
   
    import newconnector
    connectors = { 
                  "newconnectorn" : newconnector.NoseNewConnectorReporter,
                  "mysql" : mysql.NoseMySQLReporter 
                }
 * this will make the newconnector available with the command line option --dbreport_dbtype=newconnector

Source Documentation
--------------------
.. automodule :: nosedbreport.plugin
    :members:
.. automodule :: nosedbreport.base
    :members:
.. automodule :: nosedbreport.mysql
    :members:



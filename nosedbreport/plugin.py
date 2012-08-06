import logging
from nose.plugins.base import Plugin
from base import NoseDBReporterBase
import mysql
import sqlite

__author__ = "Ali-Akber Saifee"
__email__ = "ali@mig33global.com"
__copyright__ = "Copyright 2011, ProjectGoth"


class NoseDBReporter(Plugin):
    """
    The main plugin that is loaded by :class:`nose.plugin.PluginManager`
    """
    #: list of db connectors available for use
    #: when specifying db_type.
    connectors = {
        "mysql":mysql.NoseMySQLReporter,
        "sqlite" : sqlite.NoseSQLiteReporter,
        }

    
    def __init__(self):
        Plugin.__init__(self)
        #: reference to an object that implements NoseDBReporterBase
        #: this object is chosen based on the command line option --dbreport_db_type
        self._other = None
        self.logger = logging.getLogger("nose.plugins.nosedbreport")
        
        
    def options(self, parser, env):
        """
        Register commandline options
        """
        parser.add_option("", "--dbreport-dbtype", dest="db_type", type="choice", choices=self.connectors.keys())
        parser.add_option("", "--dbreport-host", default="localhost", dest="dbreport_host")
        parser.add_option("", "--dbreport-port", dest="dbreport_port")
        parser.add_option("", "--dbreport-username", default="nose", dest="dbreport_username")
        parser.add_option("", "--dbreport-password", default="", dest="dbreport_password")
        parser.add_option("", "--dbreport-db", default="nosereport", dest="dbreport_db")
        parser.add_option("", "--dbreport-create-schema", action="store_true", dest="dbreport_create_schema")
    
    def __become(self, other):
        """
        store a reference to a new NodeDBReporter object. Future
        invocations of methods on the plugin will be proxied to this
        object. Identity crisis!
        
        :param other:an object of type :class:`~nosedbreport.base.NoseDBReporterBase`
        """
        self._other = other()
    
    def configure(self, options, conf):
        """
        Configure plugin. Plugin is disabled by default.
        """
        if options.db_type:
            self.enabled = options.db_type != None
            if self.enabled:
                if not issubclass(self.connectors[options.db_type], NoseDBReporterBase):
                    self.enabled = False
                    self.logger.error("dbreport_dbtype: %s is not a valid" % options.db_type)
                    return 
                self.__become(self.connectors[options.db_type])
                self._other.configure(options, conf)
                if options.dbreport_create_schema:
                    message=""
                    if self._other.construct_schema():
                        message = "schema created"
                    raise SystemExit(message)
                

    
    def __getattr__(self, attr):
        """
        overloaded getattr to be used for proxying method
        invocations to :data:`NoseDBReporter._other`
        """
        target = self._other
        if target:
            f = getattr(target, attr)
            return f
        else:
            return self.__dict__[attr]

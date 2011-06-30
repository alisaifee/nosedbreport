from nose.plugins.base import Plugin
import mysql



class NoseDBReporter(Plugin):
    """
    The main plugin that is loaded by :class:`nose.plugin.PluginManager`
    """
    
    connectors = {
        "mysql":mysql.NoseMySQLReporter
        }
    
    def __init__(self):
        Plugin.__init__(self)
        self._other = None
        
        
    def options(self, parser, env):
        """Register commandline options
        """
        parser.add_option("", "--dbreport_dbtype", dest="db_type", type="choice", choices=self.connector.keys())
        parser.add_option("", "--dbreport_host", default="localhost", dest="dbreport_host")
        parser.add_option("", "--dbreport_port", dest="dbreport_port")
        parser.add_option("", "--dbreport_username", default="nose", dest="dbreport_username")
        parser.add_option("", "--dbreport_password", default="", dest="dbreport_password")
        parser.add_option("", "--dbreport_db", default="noseresults", dest="dbreport_db")
        parser.add_option("", "--dbreport_create_schema", action="store_true", dest="dbreport_create_schema")
    def __become(self, other):
        self._other = other()
    
    def configure(self, options, conf):
        """Configure plugin. Plugin is enabled by default.
        """
        if options.db_type:
            self.enabled = options.db_type != None
            if self.enabled:
                self.__become(self.connectors[options.db_type])
                self._other.configure(options, conf)
                if options.dbreport_create_schema:
                    self._other.construct_schema()

    def __getattr__(self, attr):
        target = self._other
        if target:
            f = getattr(target, attr)
            return f
        else:
            return self.__dict__[attr]

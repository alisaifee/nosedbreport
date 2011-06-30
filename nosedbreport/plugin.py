from nose.plugins.base import Plugin
from base import NoseDBResultBase
import mysql



class NoseDBResult(Plugin):
    """
    """
    factory = {
        "mysql":mysql.NoseMySQLResult
        }
    
    def __init__(self):
        Plugin.__init__(self)
        self._other = None
        
        
    def options(self, parser, env):
        """Register commandline options
        """
        parser.add_option("", "--dbresult_dbtype", dest="db_type", type="choice", choices=["mysql"])
        parser.add_option("", "--dbresult_host", default="localhost", dest="dbresult_host")
        parser.add_option("", "--dbresult_port", dest="dbresult_port")
        parser.add_option("", "--dbresult_username", default="nose", dest="dbresult_username")
        parser.add_option("", "--dbresult_password", default="", dest="dbresult_password")
        parser.add_option("", "--dbresult_db", default="noseresults", dest="dbresult_db")
        parser.add_option("", "--dbresult_create_schema", action="store_true", dest="dbresult_create_schema")
    def __become(self, other):
        self._other = other()
    
    def configure(self, options, conf):
        """Configure plugin. Plugin is enabled by default.
        """
        if options.db_type:
            self.enabled = options.db_type != None
            if self.enabled:
                self.__become(self.factory[options.db_type])
                self._other.configure(options, conf)
                if options.dbresult_create_schema:
                    self._other.construct_schema()

    def __getattr__(self, attr):
        target = self._other
        if target:
            f = getattr(target, attr)
            return f
        else:
            return self.__dict__[attr]

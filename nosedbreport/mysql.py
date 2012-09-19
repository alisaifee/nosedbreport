import optparse
from datetime import datetime, timedelta
from base import NoseDBReporterBase

__author__ = "Ali-Akber Saifee"
__email__ = "ali@mig33global.com"
__copyright__ = "Copyright 2011, ProjectGoth"


class NoseMySQLReporter(NoseDBReporterBase):
    """
    MySQL Connector. Reports the results of each test run into the tables
    ``testcase``, ``testsuite``, ``testcaseexecution`` and ``testsuiteexecution``
    """
    name = "nosedbreport"

                                    
    run_insert_query = """
    insert into testcaseexecution (testcase, startTime, timeTaken, status, traceback, suiteexecution)
    values ('%(testcase)s', '%(startTime)s', '%(timeTaken)s', '%(status)s', '%(traceback)s', %(suiteexecution)d);
    """
    case_start_query = """
    insert into testcase values('%(id)s', '%(name)s', '%(description)s', '%(suite)s', '%(lastStarted)s', 0)
    on duplicate key update lastStarted='%(lastStarted)s', description='%(description)s';
    """
    suite_start_query = """
    insert into testsuite (name, lastStarted) values('%(suite)s', '%(lastStarted)s')
    on duplicate key update lastStarted='%(lastStarted)s';
    """
    suite_complete_query = """
    insert into testsuite (name, lastCompleted) values('%(suite)s', '%(lastCompleted)s')
    on duplicate key update lastCompleted='%(lastCompleted)s';
    """
    suiteexecution_complete_query = """
    insert into testsuiteexecution (suite, startTime, endTime)
    values ('%(suite)s', '%(startTime)s', '%(lastCompleted)s');
    """
    
    case_complete_query = """
    update testcase set lastCompleted = '%(lastCompleted)s';
    """

    
    
    def __init__(self):
        NoseDBReporterBase.__init__(self)
    
    
    def __execute_query(self, query, args):
        """
        helper method to execute a MySQL query and commit
        the result.
        
        :param query: the query to execute
        :param args: variable arguments to use when formatting the query

        """
        # santize quotes.
        for k,v in args.items():
            if type(v) == type("string"):
                args[k] = v.replace("'","\\'")
        ret = 0
        try:
            import MySQLdb
            cursor = self.connection.cursor()
            ret = cursor.execute( query % args )
            self.connection.commit()
        except MySQLdb.ProgrammingError, e:
            self.logger.error ( "failed to execute query with error: %s" % str(e[1]))
        except Exception, e:
            self.logger.error ("unknown error executing query: %s" % str(e))
        return ret
    
    def configure(self, options, conf):
        """
        sets up the MySQL database connection based on the options
        provided on the command line.
        """
        import MySQLdb
        try:
            self.connection = MySQLdb.connect(
                                              options.dbreport_host, 
                                              options.dbreport_username, 
                                              options.dbreport_password, 
                                              options.dbreport_db, 
                                              connect_timeout=5
                                              )
        except ImportError, e:
            self.enabled = False
            self.logger.error ("The MySQLdb module is required for nosedbreporter to work with mysql")
        except MySQLdb.OperationalError, e:
            self.enabled = False
            self.logger.error (e[1])

    def report(self, stream):
        """
        After successful completion of a nose run, perform the final reporting
        of the test results to the MySQL database.
        """
        if self.connection:
            results = self.test_case_results
            suiteexecids={}
            for suite in self.test_suites:
                suite_update = { "suite" : suite,
                                "startTime" : self.start_time,
                                "lastCompleted" : self.test_suites[suite]["lastCompleted"]
                                }
                self.__execute_query(self.suite_complete_query, suite_update)
                self.__execute_query(self.suiteexecution_complete_query, suite_update)

                # get the suiteexecution id now.
                self.connection.query ("""
                select id from testsuiteexecution where suite='%(suite)s' and
                startTime='%(startTime)s' and 
                endTime='%(lastCompleted)s' 
                """ % suite_update)
                result = self.connection.store_result()
                suiteexecids[suite] = result.fetch_row()[0][0]
                
            for case in results:
                case_update = { "id":case,
                                "name":results[case]["name"],
                                "description":results[case]["description"],
                                "suite":results[case]["suite"],
                                "lastStarted":results[case]["lastStarted"],
                                "lastCompleted":(
                                                datetime.strptime(results[case]["lastStarted"], self.time_fmt) + 
                                                timedelta(seconds=results[case]["timeTaken"])
                                                ).strftime(self.time_fmt)
                                                              
                            }

                run_update = { "testcase":case,
                                "suite":results[case]["suite"],
                                "suiteexecution":suiteexecids[results[case]["suite"]],
                                "startTime":results[case]["lastStarted"],
                                "timeTaken":results[case]["timeTaken"],
                                "status":results[case]["status"],
                                "traceback":results[case]["traceback"]
                                }
                self.__execute_query(self.case_complete_query, case_update)
                self.__execute_query(self.run_insert_query, run_update)
  
    def startTest(self, test):
        """
        record initiation of a test case. Update the last start time 
        of the test suite &  test case.
        """
        if self.connection:
            description = self.get_full_doc(test)
            test_id = test.id()
            file_path, suite, case = test.address()
            case_update = { "id":test_id,
                           "name":case,
                           "description":description,
                           "suite":suite,
                           "lastStarted":NoseDBReporterBase.time_now()
                           }
            suite_update = { "suite":suite,
                            "lastStarted":NoseDBReporterBase.time_now()
                            }
        
            self.__execute_query(self.suite_start_query, suite_update)
            self.__execute_query(self.case_start_query, case_update)

            
            
        super(NoseMySQLReporter, self).startTest(test)
        
        
    def construct_schema(self):
        """
        called when the `--dbreport_create_schema` command option 
        is passed to the plugin to create the mysql table schema.
        """
        testcase_schema = """ 
        CREATE TABLE `testcase` (
          `id` varchar(255) NOT NULL,
          `name` varchar(255) NOT NULL,
          `description` varchar(255) NOT NULL,
          `suite` varchar(255) NOT NULL,
          `lastStarted` datetime DEFAULT NULL,
          `lastCompleted` datetime DEFAULT NULL,
          PRIMARY KEY (`id`),
          KEY `idx_name` (`name`),
          KEY `idx_suite` (`suite`),
          CONSTRAINT `fk_suite_name` FOREIGN KEY (`suite`) REFERENCES `testsuite` (`name`)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1
        """
        testsuite_schema = """
        CREATE TABLE `testsuite` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `name` varchar(255) NOT NULL,
          `lastStarted` datetime DEFAULT NULL,
          `lastCompleted` datetime DEFAULT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `idx_name` (`name`) USING BTREE
        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1
        """
        testcaseexecution_schema = """
        CREATE TABLE `testcaseexecution` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `testcase` varchar(255) NOT NULL,
          `suiteexecution` int(11) NOT NULL,
          `startTime` datetime NOT NULL,
          `timeTaken` float NOT NULL,
          `status` enum('success','fail','error','skipped','') NOT NULL,
          `traceback` text NOT NULL,
          PRIMARY KEY (`id`),
          KEY `idx_status` (`status`),
          KEY `idx_testcase` (`testcase`) USING BTREE,
          KEY `idx_suiteexecution` (`suiteexecution`),
          CONSTRAINT `fk_testcase_id` FOREIGN KEY (`testcase`) REFERENCES `testcase` (`id`),
          CONSTRAINT `fk_suiteexec_id` FOREIGN KEY (`suiteexecution`) REFERENCES `testsuiteexecution` (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1
        """ 
        
        testsuiteexecution_schema = """
        CREATE TABLE `testsuiteexecution` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `suite` varchar(255) NOT NULL,
            `startTime` datetime NOT NULL,
            `endTime` datetime NOT NULL,
            PRIMARY KEY (`id`),
            KEY `idx_start` (`startTime`),
            KEY `idx_end` (`endTime`),
            CONSTRAINT `fk_testsuite_name` FOREIGN KEY (`suite`) REFERENCES `testsuite` (`name`)
        ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1
        """ 
        if self.connection:
            cursor = self.connection.cursor()
        
            if not cursor.execute("show tables like 'test%%'") == 4:
                cursor.execute ( testsuite_schema )
                cursor.execute ( testcase_schema )
                cursor.execute ( testsuiteexecution_schema )
                cursor.execute ( testcaseexecution_schema )
            return True
        else:
            self.logger.error("Unable to setup scheme due to mysql configuration error")
            return False

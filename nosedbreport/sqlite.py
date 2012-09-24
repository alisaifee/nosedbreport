import optparse
from datetime import datetime, timedelta
from base import NoseDBReporterBase

__author__ = "Ali-Akber Saifee"
__email__ = "ali@mig33global.com"
__copyright__ = "Copyright 2011, ProjectGoth"


class NoseSQLiteReporter(NoseDBReporterBase):
    """
    SQLLite Connector. Reports the results of each test run into the tables
    ``testcase``, ``testsuite``,``testcaseexecution`` and ``testsuiteexecution``
    """
    name = "nosedbreport"


    run_insert_query = """
    insert into testcaseexecution (testcase, startTime, timeTaken, status, traceback, suiteexecution)
    values ('%(testcase)s', '%(startTime)s', '%(timeTaken)s', '%(status)s', '%(traceback)s', %(suiteexecution)d);
    """
    case_start_query = """
    replace into testcase values('%(id)s', '%(name)s', '%(description)s', '%(suite)s', '%(lastStarted)s', 0)
    """
    suite_start_query = """
    replace into testsuite (name, lastStarted) values('%(suite)s', '%(lastStarted)s')
    """
    suite_complete_query = """
    replace into testsuite (name, lastCompleted) values('%(suite)s', '%(lastCompleted)s');
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
        helper method to execute a sqlite query and commit
        the result.

        :param query: the query to execute
        :param args: variable length argument list used to format ``query``
        """
        # santize quotes.
        for k,v in args.items():
            if type(v) == type("string"):
                args[k] = v.replace("'","''")
        ret = 0
        try:
            import sqlite3
            cursor = self.connection.cursor()
            ret = cursor.execute( query % args )
            self.connection.commit()
        except sqlite3.ProgrammingError, e:
            self.logger.error ( "failed to execute query with error: %s" % str(e[1]))
        except Exception, e:
            self.logger.error ("unknown error executing query %s: %s" % (query % args , str(e)))
        return ret

    def configure(self, options, conf):
        """
        sets up the sqlite database connection
        """
        import sqlite3
        try:
            self.connection = sqlite3.connect(
                                              options.dbreport_db
                                              )
        except ImportError, e:
            self.enabled = False
            self.logger.error ("The sqlite3 module is required for nosedbreporter to work with sqlite")
        except sqlite3.OperationalError, e:
            self.enabled = False
            self.logger.error (e)

    def report(self, stream):
        """
        After successful completion of a nose run, perform the final reporting
        of the test results to the sqlite database.
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
                cur = self.connection.cursor()

                cur.execute ("""
                    select id from testsuiteexecution where suite='%(suite)s' and
                    startTime='%(startTime)s' and
                    endTime='%(lastCompleted)s'
                    """ % suite_update)
                suiteexecids[suite] = cur.fetchone()[0]

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
        record initiation of a test case (``test``). Update the last start time
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



        super(NoseSQLiteReporter, self).startTest(test)


    def construct_schema(self):
        """
        called when the `--dbreport_create_schema` command option
        is passed to the plugin to create the sqlite table schema.
        """
        testcase_schema = """
        CREATE TABLE testcase(
            id    TEXT PRIMARY KEY,
            name  TEXT,
            description TEXT,
            suite TEXT,
            lastStarted TEXT,
            lastCompleted TEXT,
            FOREIGN KEY(suite) REFERENCES testsuite(name)
        )"""

        testsuite_schema = """
        CREATE TABLE testsuite(
          id INTEGER PRIMARY KEY,
          name TEXT UNIQUE,
          lastStarted TEXT,
          lastCompleted TEXT
        )
        """

        testcaseexecution_schema = """
        CREATE TABLE testcaseexecution (
          id INTEGER PRIMARY KEY,
          testcase TEXT,
          suiteexecution INTEGER,
          startTime TEXT,
          timeTaken REAL,
          status TEXT,
          traceback TEXT,
          FOREIGN KEY(testcase) REFERENCES testcase(id),
          FOREIGN KEY(suiteexecution) REFERENCES testsuiteexecution(id)
        )
        """

        testsuiteexecution_schema = """
        CREATE TABLE `testsuiteexecution` (
           id INTEGER PRIMARY KEY,
           suite TEXT,
           startTime TEXT,
           endTime TEXT,
           FOREIGN KEY(suite) REFERENCES testsuite(name)
        )
        """
        indices  = ["CREATE INDEX idx_name on testcase(name)",
        "CREATE INDEX tc_idx_suite on testcase(suite)",
        "CREATE INDEX ts_idx_name on testsuite(name)",
        "CREATE INDEX tce_idx_status on testcaseexecution(status)",
        "CREATE INDEX tce_idx_testcase on testcaseexecution(testcase)",
        "CREATE INDEX tce_idx_suiteexecution on testcaseexecution(suiteexecution)",
        "CREATE INDEX tse_idx_start on testsuiteexecution(startTime)",
        "CREATE INDEX tse_idx_end on testsuiteexecution(endTime)"]
        if self.connection:
            cursor = self.connection.cursor()

            cursor.execute ( testsuite_schema )
            cursor.execute ( testcase_schema )
            cursor.execute ( testsuiteexecution_schema )
            cursor.execute ( testcaseexecution_schema )
            for index in indices:
                cursor.execute ( index )

            return True
        else:
            self.logger.error("Unable to setup scheme due to mysql configuration error")
            return False

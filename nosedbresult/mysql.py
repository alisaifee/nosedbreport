"""
"""

import optparse
from datetime import datetime, timedelta
from base import NoseDBResultBase

class NoseMySQLResult(NoseDBResultBase):
    """
    """
                                    
    run_insert_query = """
    insert into testcaseexecution (testcase, startTime, timeTaken, status, traceback)
    values ('%(testcase)s', '%(startTime)s', '%(timeTaken)s', '%(status)s', '%(traceback)s');
    """
    case_start_query = """
    insert into testcase values('%(identifier)s', '%(name)s', '%(description)s', '%(suite)s', '%(lastStarted)s', 0)
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
    case_complete_query = """
    update testcase set lastCompleted = '%(lastCompleted)s';
    """

    
    
    def __init__(self):
        NoseDBResultBase.__init__(self)
        
    def configure(self, options, conf):
        import MySQLdb
        try:
            self.connection = MySQLdb.connect(
                                              options.dbresult_host, 
                                              options.dbresult_username, 
                                              options.dbresult_password, 
                                              options.dbresult_db, 
                                              connect_timeout=5
                                              )
        except Exception, e:
            print "not connected", str(e)
            self.enabled = False

    def report(self, stream):
        if self.connection:
            results = self.test_case_results
            for suite in self.test_suites:
                suite_update = { "suite" : suite,
                                "lastCompleted" : self.test_suites[suite]["lastCompleted"]
                                }
                if self.connection:
                    cursor = self.connection.cursor()
                    cursor.execute(self.suite_complete_query % suite_update )
            for case in results:
                case_update = { "identifier":case,
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
                                "startTime":results[case]["lastStarted"],
                                "timeTaken":results[case]["timeTaken"],
                                "status":results[case]["status"],
                                "traceback":results[case]["traceback"]
                                }
                if self.connection:
                    cursor = self.connection.cursor()
                    try:
                        cursor.execute(self.case_complete_query, case_update)
                        cursor.execute(self.run_insert_query, run_update)
                        self.connection.commit()
                    except Exception, e:
                        print e
  
    def startTest(self, test):
        if self.connection:
            description = self.get_full_doc(test)
            test_id = test.id()
            file_path, suite, case = test.address()
            case_update = { "identifier":test_id,
                           "name":case,
                           "description":description,
                           "suite":suite,
                           "lastStarted":NoseDBResultBase.time_now()
                           }
            suite_update = { "suite":suite,
                            "lastStarted":NoseDBResultBase.time_now()
                            }
        
            cursor = self.connection.cursor()
            try:
                print self.suite_start_query % suite_update
                print self.case_start_query % case_update
                cursor.execute(self.suite_start_query, suite_update)
                cursor.execute(self.case_start_query, case_update)
                self.connection.commit()

            except Exception, e:
                print "start",str(e)
            
            
        super(NoseMySQLResult, self).startTest(test)
        
        
    def construct_schema(self):
        testcase_schema = """ CREATE TABLE `testcase` (
      `identifier` varchar(255) NOT NULL,
      `name` varchar(255) NOT NULL,
      `description` varchar(255) NOT NULL,
      `suite` varchar(255) NOT NULL,
      `lastStarted` datetime DEFAULT NULL,
      `lastCompleted` datetime DEFAULT NULL,
      PRIMARY KEY (`identifier`),
      KEY `idx_identifier` (`identifier`),
      KEY `idx_name` (`name`),
      KEY `idx_suite` (`suite`),
      CONSTRAINT `fk_suite` FOREIGN KEY (`suite`) REFERENCES `testsuite` (`name`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    """
        testsuite_schema = """CREATE TABLE `testsuite` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `name` varchar(255) NOT NULL,
      `lastStarted` datetime DEFAULT NULL,
      `lastCompleted` datetime DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `idx_name` (`name`) USING BTREE
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1
    """
        testcaseexecution_schema = """CREATE TABLE `testcaseexecution` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `testcase` varchar(255) NOT NULL,
      `startTime` datetime NOT NULL,
      `timeTaken` float NOT NULL,
      `status` enum('success','fail','error','skipped','') NOT NULL,
      `traceback` text NOT NULL,
      PRIMARY KEY (`id`),
      KEY `idx_status` (`status`),
      KEY `idx_testcase` (`testcase`) USING BTREE,
      CONSTRAINT `fk_testcase_identifier` FOREIGN KEY (`testcase`) REFERENCES `testcase` (`identifier`)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1
    """ 
        cursor = self.connection.cursor()
        
        if not cursor.execute("show tables like 'test%%'") == 3:
            cursor.execute ( testsuite_schema )
            cursor.execute ( testcase_schema )
            cursor.execute ( testcaseexecution_schema )
        


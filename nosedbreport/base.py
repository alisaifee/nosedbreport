import logging
import os
import traceback
import sys
import pprint
from time import time
from datetime import datetime, timedelta
from nose.plugins.base import Plugin

class NoseDBReporterBase(Plugin):
    """
    Base class for Nose plugins that stash test results
    into a database.
    """
    name = "nosedbreport"
    enabled = False

    def __init__(self):
        self.connection = None
        self.test_suites = {}
        self.test_case_results = {}
        self._timer = 0
        self.logger = logging.getLogger("nose.plugins.nosedbreport")

    time_fmt = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def time_now():
        return datetime.now().strftime(NoseDBReporterBase.time_fmt)

    def get_full_doc(self, test):
        full_doc = ""
        try:
            func_doc = test.test._descriptors()[0].__doc__
            if func_doc:
                full_doc = func_doc
        except AttributeError:
            try:
                full_doc = test.test._testMethodDoc
            except AttributeError:
                full_doc = test.test._TestCase__testMethodDoc
        if full_doc:
            return "\n".join(k.strip() for k in full_doc.split("\n"))
        else:
            return ""
 
  
    def startTest(self, test):
        """
        collect information about a test before it begins,
        and initialize a timer to record time taken.
        """
        self._timer = time()
        description = self.get_full_doc(test)
        test_id = test.id()
        file_path, suite, case = test.address()
        
        self.test_case_results[test_id] = {
                                           "file_path":file_path,
                                           "suite":suite,
                                           "name":case,
                                           "description":description,
                                           "status":"skipped",
                                           "lastStarted":NoseDBReporterBase.time_now(),
                                           "traceback":""
                                           }
        self.test_suites.setdefault(suite, {})
        
    
    def addError(self, test, err, capt=None):
        """
        sets the status of the test to either 'skipped' or 'error',
        collects the trace and time taken to execute.
        """
        file_path, suite, case = test.address()
        if issubclass(err[0], SkipTest):
            self.test_case_results[id]["status"] = "skipped"
            self.test_case_results[id]["timeTaken"] = 0
        else:
            taken = time() - self._timer
            tb = ''.join(traceback.format_exception(*err))
            id = test.id()
            if self.test_case_results.has_key(id):
                self.test_case_results[id]["traceback"] = tb
                self.test_case_results[id]["timeTaken"] = taken
                self.test_case_results[id]["status"] = "error"
                self.test_suites[suite]["lastCompleted"] = NoseDBReporterBase.time_now()

    
    def addFailure(self, test, err, capt=None, tb_info=None):
        """
        sets the status of the test to 'fail',
        collects the trace and time taken to execute.
        """
        file_path, suite, case = test.address()
        taken = time() - self._timer
        tb = ''.join(traceback.format_exception(*err))        
        id = test.id()
        if self.test_case_results.has_key(id):
            self.test_case_results[id]["traceback"] = tb
            self.test_case_results[id]["timeTaken"] = taken
            self.test_case_results[id]["status"] = "fail"      
            self.test_suites[suite]["lastCompleted"] = NoseDBReporterBase.time_now()
        
    def addSuccess(self, test, capt=None):
        """
        sets the status of the test to 'pass',
        and sets the time taken to execute.
        """
        file_path, suite, case = test.address()
        taken = time() - self._timer
        id = test.id()
        self.test_case_results[id]["status"] = "success"
        self.test_case_results[id]["timeTaken"] = taken
        self.test_suites[suite]["lastCompleted"] = NoseDBReporterBase.time_now()
        


Data Structures
---------------

Overview
========
By extending :class:`nosedbreport.base.NoseDBReporterBase` you essentially have access to two relevant
dictionaries, :attr:`nosedbreport.base.NoseDBReporterBase.test_suites` and :attr:`nodedbreport.base.NoseDBReporterBase.test_case_results`.

MySQL Example
=============
The :class:`nosedbreport.mysql.NoseMySQLReporter` backend translates the data structures of the plugin into mysql tables using 4 tables:

* testsuite
* testsuiteexecution
* testcase
* testcaseexecution

The MySQL tables are roughly related as follows:

.. digraph:: MySQLDb

	graph [
		rankdir="LR",
		fontname="Courier"
	];
	"testsuite" [
		label="<f0>testsuite|<f1>name",
		shape="record"
		];
	"testcase" [
		label="<f0>testcase|<f1>id|<f2>suite",
		shape="record"
		];
	"testsuiteexecution" [
		label="<f0>testsuiteexecution|<f1>id|<f2>suite",
		shape="record"
		];
	"testcaseexecution" [
		label="<f0>testcaseexecution|<f1>id|<f2>testcase",
		shape="record"
		];
	"testcase":f2->"testsuite":f1;
	"testcaseexecution":f2->"testcase":f1;
	"testsuiteexecution":f2->"testsuite":f1;
	
	
	
	


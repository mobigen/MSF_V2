import unittest
import os
import sys
import datetime
import ConfigParser
import cx_Oracle

from OracleHandler import OracleHandler
import Mobigen.Common.Log as Log

Log.Init()

class TestOracleHandler(unittest.TestCase):
    """
        @brief test case usnig unittest.TestCase
    """
    def setUp(self):
        """
            @brief this method is called before every test methods
        """
        conf = ConfigParser.ConfigParser()
        conf.read("conf/Oracle.conf")
        section = 'TEST'
        self.db_obj = OracleHandler(section, conf)

        sql_create_table = """
           CREATE TABLE EMP
               (EMPNO NUMBER(4) NOT NULL,
                ENAME VARCHAR2(10),
                JOB VARCHAR2(9),
                MGR NUMBER(4),
                HIREDATE DATE,
                SAL NUMBER(7, 2),
                COMM NUMBER(7, 2),
                DEPTNO NUMBER(2))"""
        self.db_obj.executeQuery(sql_create_table)

        sql_insert = """
            INSERT INTO EMP VALUES
                (7369, 'SMITH',  'CLERK',     7902,
                TO_DATE('17-DEC-1980', 'DD-MON-YYYY'),  800, NULL, 20)"""
        self.db_obj.executeQuery(sql_insert)

    def tearDown(self):
        """
            @brief this method is called after every test methods
        """
        self.db_obj.executeQuery("DROP TABLE EMP")
        self.db_obj.disconnect()
        self.db_obj = None
        pass

    def test_connect_try(self):
        self.db_obj.connect()
        self.assertTrue(self.db_obj.Curs)

    def test_disconnect(self):
        self.db_obj.disconnect()
        result = False
        try:
            self.db_obj.Curs.execute("select * from HI")
        except cx_Oracle.InterfaceError as exc:
            result = True
        self.assertTrue(result)

    def test_executeGetData_try(self):
        sql_select = "select * from EMP"
        expected_result = (7369, 'SMITH', 'CLERK', 7902, \
                datetime.datetime(1980, 12, 17, 0, 0), 800.0, None, 20)

        self.assertEqual(self.db_obj.executeGetData(sql_select)[0],
                         expected_result)

    def test_executeGetData_DatabaseError(self):
        sql_select = "select * from nonexist"
        self.assertFalse(self.db_obj.executeGetData(sql_select))

    def test_executeGetData_InterfaceError(self):
        self.db_obj.disconnect()
        sql_select = "select * from EMP"

        expected_result = (7369, 'SMITH', 'CLERK', 7902, \
                datetime.datetime(1980, 12, 17, 0, 0), 800.0, None, 20)
        self.assertEqual(self.db_obj.executeGetData(sql_select)[0],
                         expected_result)

    def test_executeQuery_try(self):
        sql_create_table = """
            INSERT INTO EMP VALUES
                (7499, 'ALLEN',  'SALESMAN',  7698,
                TO_DATE('20-FEB-1981', 'DD-MON-YYYY'), 1600,  300, 30)"""
        self.assertTrue(self.db_obj.executeQuery(sql_create_table))

    def test_executeQuery_DatabaseError(self):
        sql_create_table = """
           CREATE TBLE EMP
                DEPTNO NUMBER(2))"""
        self.assertFalse(self.db_obj.executeQuery(sql_create_table))

    def test_executeQuery_InterfaceError(self):
        self.db_obj.disconnect()
        sql_select = "select * from EMP"
        self.assertTrue(self.db_obj.executeQuery(sql_select))

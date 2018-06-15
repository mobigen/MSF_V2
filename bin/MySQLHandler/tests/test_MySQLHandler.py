import unittest
import os
import sys
import datetime
import ConfigParser
import MySQLdb

from MySQLHandler import MySQLHandler
import Mobigen.Common.Log as Log

Log.Init()

class TestMySQLHandler(unittest.TestCase):
    """
        @brief test case usnig unittest.TestCase
    """
    def setUp(self):
        """
            @brief this method is called before every test methods
        """
        conf = ConfigParser.ConfigParser()
        conf.read("conf/MySQL.conf")
        section = 'TEST'
        self.db_obj = MySQLHandler(section, conf)

        sql_create_table = """
        create table member(
            id varchar(12) not null primary key,
            passwd varchar(12) not null,
            name varchar(10) not null,
            reg_date datetime not null
        )
        """
        self.db_obj.executeQuery(sql_create_table)

        sql_insert = """
           insert into member(id, passwd, name, reg_date)
             values('cook', '1234' , 'John', 20180607060350)"""
        self.db_obj.executeQuery(sql_insert)


    def tearDown(self):
        """
            @brief this method is called after every test methods
        """
        self.db_obj.executeQuery("DROP TABLE member")
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
        except MySQLdb.ProgrammingError as exc:
            result = True
        self.assertTrue(result)

    def test_executeGetData_try(self):
        sql_select = "select * from member"
        expected_result = ('cook', '1234', 'John', \
                           datetime.datetime(2018, 6, 7, 6, 3, 50))

        self.assertEqual(self.db_obj.executeGetData(sql_select)[0],
                         expected_result)

    def test_executeGetData_except(self):
        sql_select = "select * from nonexist"
        self.assertFalse(self.db_obj.executeGetData(sql_select))

    def test_executeQuery_try(self):
        sql_create_table = """
                insert into member(id, passwd, name, reg_date)
                values('exercise', '4321' , 'Tom', now())"""
        self.assertTrue(self.db_obj.executeQuery(sql_create_table))

    def test_executeQuery_except(self):
        sql_create_table = """
           CREATE TBLE EMP
                DEPTNO NUMBER(2))"""
        self.assertFalse(self.db_obj.executeQuery(sql_create_table))


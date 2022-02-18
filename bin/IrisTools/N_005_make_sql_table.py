#!/usr/bin/env python3

# 2022-02-07 
# make no_partition LOCAL table & index from  csv data file(header exist) 
# 2022-02-15  : db_insert_time  option 으로 처리하기

import API.M6_IRIS2_PY3 as M6
import os, sys
import time
import numpy as np
import glob
import subprocess
import re
import argparse

######
class IRIS_CONNECT :

    def __init__(self, addr, id, passwd, port, db_name) :

        self.addr = addr
        self.id = id
        self.passwd = passwd
        self.port = int(port) 
        self.db_name = db_name
	
        self.conn = None
        self.curs = None

        self.load_property = M6.LoadProperty()


    def CONNECT(self, fsep="|^|", rsep="|^-^|") :
        if self.conn != None : 
            self.curs.Close()
            self.conn.close()

        
        self.fsep = fsep
        self.rsep = rsep

        self.conn = M6.Connection(self.addr, self.id, self.passwd, Database=self.db_name)
        self.curs = self.conn.Cursor()

        self.curs.SetFieldSep(fsep)
        self.curs.SetRecordSep(rsep)
        self.curs.SetTimeout(100)

        return(self.conn, self.curs)


    def DIS_CONNECT(self) :
        try :
            self.curs.Close()
            self.conn.close()
        except :
            self.curs = None
            self.conn = None
        
       

######

if __name__ == "__main__" :

    addr = 'xxx.xx.xx.xx' 
    id = 'id' 
    
    passwd = 'pwd'
    port = 5050 
    db = 'mydb' 


    fld_sep = '|^|'
    row_sep = '\n'
    

    # ----------------------------------------------------------------
    # ARGV  : tablename, data_file, column_seperator, [-addcolumn]
    # ----------------------------------------------------------------

    tablename      = ""
    data_file = '/Users/seory/Documents/Docu2022/IRIS_2022/TEST/no_par/LOCAL_TEST_NO_PARTITION_HOST.dat'
    col_sep = '|^|'
    db_insert_time_flag = False

    parser = argparse.ArgumentParser(description='This is TABLE CREATE SQL printing script. ')
    parser.add_argument('tablename')
    parser.add_argument('data_file')
    parser.add_argument('col_sep')
    parser.add_argument('-a', '--a', dest='a', action='store_true',  help='DB_INS_DATE2 column exist')

    args = parser.parse_args()
    tablename = args.tablename
    data_file = args.data_file
    col_sep = args.col_sep
    db_insert_time_flag = args.__dict__['a']

    #print("TABLE = [%s], data_dir = [%s]\ncolumns_seperator = %s ,  DB_INS_DATE2 = [%s]" % (tablename,data_file,col_sep,db_insert_time_flag))

    # -------------------------------------------------------
    # read data file , get columns
    # -------------------------------------------------------

    if not os.path.exists(data_file) :
        print(">>>> file %s not found" % data_file)
        sys.exit()

    header_list = []
    header_str = ''
    fh = open(data_file, 'r')
    for line in fh :
        if len(header_list) == 0 :
            line = line.strip()
            lineList = line.split(col_sep)
            for col in lineList :
                tmp = re.sub('\s+', '_', col.strip())
                header_list.append(tmp)
                if header_str == '' : header_str = "%s TEXT|REAL|INTEGER" % tmp 
                else :                header_str = "%s, \n%s TEXT|REAL|INTEGER" % (header_str, tmp)
            break
    fh.close()


    # ----------------------------------------------
    # no partition LOCAL table schema
    # ----------------------------------------------
    
    if db_insert_time_flag  :   # True
        create_table_sql = """
CREATE TABLE {} (
{},
DB_INS_DATE TEXT  
)

DATASCOPE LOCAL 
RAMEXPIRE 0
DISKEXPIRE 1
PARTITIONKEY a
PARTITIONDATE b
PARTITIONRANGE 1 ; 

.table option {} DISK OFF

CREATE INDEX {}_IDX1 ON {} (DB_INS_DATE );
CREATE INDEX {}_IDX2 ON {} (    ); """.format( tablename, header_str, tablename, tablename, tablename, tablename, tablename)
    else :
        create_table_sql = """
CREATE TABLE {} (
{}
)

DATASCOPE LOCAL 
RAMEXPIRE 0
DISKEXPIRE 1
PARTITIONKEY a
PARTITIONDATE b
PARTITIONRANGE 1 ; 

.table option {} DISK OFF

CREATE INDEX {}_IDX1 ON {} (    ); """.format( tablename, header_str, tablename, tablename, tablename, tablename, tablename)

    
    print(create_table_sql)
    sys.exit()

"""
    # ----------------------------------------------------
    # IRIS DB connect
    # ----------------------------------------------------

    myiris = IRIS_CONNECT(addr, id, passwd, port, db)
    try :
        (conn, curs) = myiris.CONNECT()
    except Exception as e :
        print(str(e))
        print(">>>> IRIS DB connect fail")
        sys.exit()

    curs.SetFieldSep(fld_sep)
    curs.SetRecordSep(row_sep)


    # ----------------------------------------------------
    # IRISDB : CREATE TABLE
    # ----------------------------------------------------


    try :
        curs.Execute2(str(create_table_sql))
        for row in curs :
            print(row)
    except Exception as e_str :
        print(str(e_str))
        sys.exit()


    myiris.DIS_CONNECT()
"""

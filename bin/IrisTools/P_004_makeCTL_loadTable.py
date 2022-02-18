#!/usr/bin/env python3

# 2022-01-26 add YEAR partition 

import API.M6_IRIS2_PY3 as M6
import pandas as pd
import os, sys
import time
import numpy as np
import glob

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

    addr = 'xxx.xxx.xxx.xx' 
    id = 'id' 
   
    passwd = 'passwd'
    port = 5050 
    db = 'mydb' 


    column_sep = '|^|'
    row_sep = '\n'
    

    # ------------------------------------------------------
    # CONFIG  : tablename, data_dir
    # ------------------------------------------------------

    tablename      = ""
    partition_key = '1' 
    data_dir = '/Users/seory/Documents/Docu2022/IRIS_2022/TEST/merge'
    if len(sys.argv) == 3 :
        tablename = sys.argv[1]
        data_dir = sys.argv[2]
    elif len(sys.argv) == 4 :
        tablename = sys.argv[1]
        data_dir = sys.argv[2]
        partition_key = sys.argv[3]
    else :
        print(">>>> %s tablename data_directory")
        print(">>>> %s tablename data_directory [partition_key]")
        print("ex) %s LOCAL_TEST_HOST /Users/seory/Documents/Docu2022/IRIS_2022/TEST/merge" % sys.argv[0])
        print("ex) %s LOCAL_TEST_HOST /Users/seory/Documents/Docu2022/IRIS_2022/TEST/merge 1" % sys.argv[0])
        sys.exit()


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

    curs.SetFieldSep(column_sep)
    curs.SetRecordSep(row_sep)


    # ----------------------------------------------------------
    # get COLUMN LIST  -> make CTL file
    # ----------------------------------------------------------
    """
    TABLE_CAT    TABLE_SCHEM    TABLE_NAME         COLUMN_NAME       DATA_TYPE    TYPE_NAME    COLUMN_SIZE    BUFFER_SIZE
 BUFFER_LENGTH    DECIMAL_DIGITS    NULLABLE    REMARKS    COLUMN_DEF    SQL_DATA_TYPE    SQL_DATETIME_SUB    CHAR_OCTET_LEN
GTH    ORDINAL_POSITION    IS_NULLABLE    SCOPE_CATLOG    SCOPE_SCHEMA    SCOPE_TABLE    SOURCE_DATA_TYPE    IS_AUTOINCREMEN
T    NOTINDEXED
    """

    control_file_path = "%s/%s.new.ctl"  % (data_dir, tablename)
    wfh = open(control_file_path, 'w')
    collist = []
    get_col_sql = "table columns %s" % tablename
    try :
        curs.Execute2(str(get_col_sql))
        tmp_num = 0
        for row in curs :
            tmp_num += 1
            colname = str(row[3])
            collist.append(colname)
            wfh.write(colname + str(row_sep))
    except Exception as e_str :
        print(str(e_str))
        sys.exit()
    wfh.close()

    # ------------------------------------------------
    # LOAD DATA FILE  : tablename_YYYYMMDDHHmmss.dat
    # ------------------------------------------------

    filelist = glob.glob("%s/%s_??????????????.???" % (data_dir, tablename))
    filelist.sort()
    for data_file in filelist :
        partition = data_file[-18:-4]
        
        try :
            result = curs.Load(tablename, partition_key, partition, control_file_path, data_file)
            print("%s %s %s %s %s" % (tablename, partition_key, partition, control_file_path, data_file))
            print("LOAD : ", result)
        except Exception as e :
            print(str(e))
            sys.exit() 

    myiris.DIS_CONNECT()

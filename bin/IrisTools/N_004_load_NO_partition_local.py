#!/usr/bin/env python3

# 2022-02-03 no_partition table loading
# 2022-02-16 data file header exist ->  -header

import API.M6_IRIS2_PY3 as M6
import pandas as pd
import os, sys
import time
import numpy as np
import glob
import subprocess
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

    addr = 'xxx.xxx.xxx.xx' 
    id = 'id' 
   
    passwd = 'passwd'
    port = 5050 
    db = 'mydb' 


    column_sep = '|^|'
    row_sep = '\n'
    

    # ------------------------------------------------------
    # ARGV  : tablename, data_dir, [-header] 
    # ------------------------------------------------------

    tablename      = ""
    data_dir = ''
    header_flag = False   # not exist

    parser = argparse.ArgumentParser(description='This is load script for NO_PARTITION_TABLE ')
    parser.add_argument('tablename')
    parser.add_argument('data_dir')
    parser.add_argument('-header', '--header', dest='header', action='store_true', help='header line exist')
    args = parser.parse_args()

    tablename = args.tablename
    data_dir = args.data_dir
    header_flag =  args.__dict__['header']

    print("TABLE NAME = [%s], data_dir = [%s]\ndata file header line = [%s]  " % (tablename, data_dir, header_flag))

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

    control_file_path = "%s/%s.new.ctl"  % (data_dir, tablename)
    wfh = open(control_file_path, 'w')
    collist = []
    get_col_sql = "table columns %s" % tablename

    try :
        curs.Execute2(str(get_col_sql))
        for row in curs :
            colname = str(row[3])
            collist.append(colname)
            wfh.write(colname + str(row_sep))
    except Exception as e_str :
        print(str(e_str))
        sys.exit()
    wfh.close()


    # ------------------------------------------------
    # LOAD DATA FILE  : tablename.dat
    # ------------------------------------------------

    filelist = glob.glob("%s/%s.dat" % (data_dir, tablename))
    filelist.sort()

    for data_file in filelist :

        print(data_file)
        new_file = "%s.new" % data_file
        st = time.time()
        try :
            if header_flag : 
                my_cmd = "/usr/bin/awk -F '\\\\|\\\\^\\\\|' -v OFS='\|\^\|' " +  "'NR >= 2 { print }' " + " > %s %s" % ( new_file, data_file) 
                print(my_cmd)
                sp = subprocess.Popen(my_cmd , stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (stdout, stderr) = sp.communicate()
                result = curs.Load(tablename, '1', '19000101000000', control_file_path, new_file)
  
            else : 
    
                result = curs.Load(tablename, '1', '19000101000000', control_file_path, data_file)
            print(result)

            if os.path.exists(new_file) : 
                os.remove(new_file)
                print("DEL %s" % new_file)
            print(time.time() - st)
        except Exception as e :
            print(str(e))
            sys.exit() 

    myiris.DIS_CONNECT()

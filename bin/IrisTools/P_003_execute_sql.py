#!/usr/bin/env python3

# 2022-02-03 no_partition table case 
# dot command process ( .table ....)

import API.M6_IRIS2_PY3 as M6
import pandas as pd
import os, sys, re
import time
import numpy as np
import glob
import subprocess


# make ctl, awk cmd -> backup file -> merge new data -> backupfile delete

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

    addr = '192.168.107.22' 
    id = 'test' 
    #passwd = '!hello.iris0'
    passwd = 'test'
    port = 5050 
    db = 'test' 

    sql_file = ''
    if len(sys.argv) == 2 :
        sql_file = sys.argv[1]
    else :
        print("%s sql_file" % sys.argv[0])
        sys.exit()


    myiris = IRIS_CONNECT(addr, id, passwd, port, db)
    (conn, curs) = myiris.CONNECT()


    
    curs.SetFieldSep('|^|')
    curs.SetRecordSep('\n')

    # ----------------------------------------------------------
    # READ SQL from sql_file 
    # ----------------------------------------------------------

    if os.path.isfile(sql_file) != True :
        print(">>>> %s not exists" % sql_file)
        sys.exit()
        
    exec_sql = ''
    dot_cmd = ''
    fh = open(sql_file, 'r')
    for line in fh :
        if re.search('^\s*\.table ', line) :
            dot_cmd = re.sub('^\s*\.table', 'table', line) 
            res = curs.Execute2(dot_cmd)
            print(res)
            continue 
            
        if re.search('\s*;\s*$', line) :
            exec_sql = exec_sql + str(line) 
            try :
                curs.Execute2(exec_sql)
            except Exception as e :
                print(str(e))
                pass
            exec_sql = ''
        else :
            exec_sql = exec_sql + str(line)

        
    fh.close()

    myiris.DIS_CONNECT()
    sys.exit()
 

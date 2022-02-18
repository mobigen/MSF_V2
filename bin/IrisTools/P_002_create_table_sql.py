#!/usr/bin/env python3


# 2022-01-26 add year partition table SQL

import API.M6_IRIS2_PY3 as M6
import os, sys, re
import time
import glob
import subprocess



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

    tablename      = "LOCAL_TEST_HOST_MON"
    p_k            = 'P_K'

    new_partitionrange = 43200

    if len(sys.argv) == 3 :
        tablename = sys.argv[1]
        if ( sys.argv[2] == 'hour' ) :  
            new_partitionrange = 60
        elif ( sys.argv[2] == 'day' ) :  
            new_partitionrange = 1440
        elif ( sys.argv[2] == 'month' ) :  
            new_partitionrange = 43200
        elif ( sys.argv[2] == 'year' ) :  
            new_partitionrange = 525600
        else : 
            print(">>> ERR :  partition not available ( partition ex: hour, day, month, year)")
            sys.exit()
 
    else :
        print("%s tablename partition(hour|day|month|year)" % sys.argv[0])
        print("example) %s tablename month" % sys.argv[0])
        sys.exit()


    myiris = IRIS_CONNECT(addr, id, passwd, port, db)
    (conn, curs) = myiris.CONNECT()


    
    curs.SetFieldSep('|^|')
    curs.SetRecordSep('\n')

    # ----------------------------------------------------------
    # get TABLE SCHEMA  from "table schema tablename"
    # ----------------------------------------------------------
    get_tab_schema = ''
    get_sql = "table schema %s" % tablename
    curs.Execute2(str(get_sql))
    for row in curs :
        get_tab_schema = str(row[2])
    
    tab_schema = re.sub('\;\s*$', '', get_tab_schema)

    datascope = 'LOCAL'
    ramexpire = 10                     # default
    diskexpire = 5256000               # default
    partitionkey = 'P_K'               # default
    partitiondate = 'PARTITION_DATE'   # default
    partitionrange = new_partitionrange 
    
    
    # -------------------------------------------------
    # make CREATE Query from "table info tablename"
    # -------------------------------------------------
    get_cfg_sql = 'table info %s' % tablename
    curs.Execute2(str(get_cfg_sql))
    for row in curs :
        datascope = row[2]  

        if new_partitionrange == 525600 :   # year partition
            ramexpire = 0
            diskexpire = 52560000
        else :
            ramexpire = int(row[3])  
            diskexpire = int(row[4])  

        partitionkey = str(row[5])  
        partitiondate = str(row[6])  

        sql_new_template = """DROP TABLE IF EXISTS {};
        {}
        DATASCOPE {}
        RAMEXPIRE {}
        DISKEXPIRE {}
        PARTITIONKEY {} 
        PARTITIONDATE {}
        PARTITIONRANGE {}; """.format( tablename, tab_schema, datascope, ramexpire, diskexpire, partitionkey, partitiondate, partitionrange)


        print(sql_new_template + '\n')         
        
    
    get_index_sql = 'table index %s' % tablename

    idx_sql = ''
    curs.Execute2(str(get_index_sql))
    for row in curs :
        idx_sql = row[3]
        print(idx_sql)
        
    myiris.DIS_CONNECT()
    sys.exit()
   
 

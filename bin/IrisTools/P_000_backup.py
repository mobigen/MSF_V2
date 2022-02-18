#!/usr/bin/env python3


# 2022-02-07 no partition table backup 

import API.M6_IRIS2_PY3 as M6
import pandas as pd
import os, sys
import time
import numpy as np
import glob
import subprocess


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
            try :
                self.curs.Close()
                self.conn.close()
            except :
                pass   

        
        self.fsep = fsep
        self.rsep = rsep

        try :
            self.conn = M6.Connection(self.addr, self.id, self.passwd, Database=self.db_name)
            self.curs = self.conn.Cursor()
    
            self.curs.SetFieldSep(fsep)
            self.curs.SetRecordSep(rsep)
            self.curs.SetTimeout(100)
    
            return(self.conn, self.curs)
        except Exception as e :
            return False


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
    passwd = 'test'
    port = 5050 
    db = 'test' 


    column_sep = '|^|'
    row_sep = '\n'

    # ------------------------------------------------------
    # CONFIG  : tablename, backup_dir 
    # ------------------------------------------------------

    tablename      = "LOCAL_TEST_NO_PARTITION_HOST"
    backup_dir = '/Users/seory/Documents/Docu2022/IRIS_2022/TEST/backup'

    if len(sys.argv) == 3 :
        tablename = sys.argv[1]
        backup_dir = sys.argv[2]
    else :
        print(">>>> %s tablename backup_directory " % sys.argv[0])
        sys.exit()
    
    if os.path.isdir(backup_dir) == False : os.makedirs(backup_dir)

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


    # ----------------------------------------------------
    # global / LOCAL 
    # ----------------------------------------------------

    """
iplus> .table list GLOBAL_TEST_TABLE
Ret : +OK Success


 DB_NAME    TABLE_NAME           SCOPE     RAM_EXP_TIME    DSK_EXP_TIME    KEY_STRING    PARTITION_STRING    PARTITION_RANGE
===============================================================================================================================
 TEST       GLOBAL_TEST_TABLE    GLOBAL    0               0               None          None                0
===============================================================================================================================

    """
    SCOPE = 'LOCAL'
    RAM_EXP_TIME = ''
    DSK_EXP_TIME = ''

    get_sql = "table list %s " % tablename
    try :
        curs.Execute2(str(get_sql))
        for row in curs :
            SCOPE = str(row[2])
            RAM_EXP_TIME = str(row[3])
            DSK_EXP_TIME = str(row[4])
    except Exception as e_str :
        print(str(e_str))
        sys.exit()
    


    if SCOPE == 'GLOBAL'  or ( SCOPE == 'LOCAL' and RAM_EXP_TIME == '0' and DSK_EXP_TIME == '1' ) :  # GLOBAL OR NO_PARTITION TABLE
        backup_file = "%s/%s.dat" % (backup_dir, tablename)
        select_sql = "select * from %s ;" % (tablename)
        wfh = open(backup_file, 'w')
    
        try :
            curs.Execute2(str(select_sql))
            for row in curs :
                prn = column_sep.join(row)
                wfh.write(prn + row_sep)
            wfh.close() 
            print("END ", backup_file)
        except Exception as e_str :
            print(str(e_str)) 
            sys.exit()

    else : 

        # ----------------------------------------------------
        # get PARTITION LIST : par_list  -> table partition_info
        # ----------------------------------------------------
        
        get_sql = "table partition_info %s --ignore-path LOCATION(PARTITION > '00000000000000')" % tablename
        try :
            curs.SetTimeout(200)
            curs.Execute2(str(get_sql))
            par_list = []
            for row in curs :
                par_list.append(row[1])
        except Exception as e_str :
            print(str(e_str))
            sys.exit()
        
        my_list = list(set(par_list))   # get unique partition
        my_list.sort()
    
    
        # ----------------------------------------------------
        # BACKUP per PARTITION : 파티션 별로 파일 백업 
        # ----------------------------------------------------
    
        for partition in my_list :
    
            backup_file = "%s/%s_%s.dat" % (backup_dir, tablename, partition)
    
            hint_localtion = "/*+ BYPASS, LOCATION (PARTITION = '" + partition + "') */\n"
            select_sql = "%s select * from %s ;" % (hint_localtion, tablename)
    
            wfh = open(backup_file, 'w')
    
            try :
                curs.Execute2(str(select_sql))
                for row in curs :
                    prn = column_sep.join(row)
                    wfh.write(prn + row_sep)
                wfh.close() 
                print("END ", backup_file)
            except Exception as e_str :
                print(str(e_str)) 
                sys.exit()
    

    
    myiris.DIS_CONNECT()

    sys.exit()

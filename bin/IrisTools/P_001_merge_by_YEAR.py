#!/usr/bin/env python3


# 2022-01-21 ver01
# 2022-01-25 YEAR merge 

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

    tablename      = "LOCAL_TEST_HOST"
    backup_dir = '/Users/seory/Documents/Docu2022/IRIS_2022/TEST/backup'
    merge_dir = '/Users/seory/Documents/Docu2022/IRIS_2022/TEST/merge_YY'

    if len(sys.argv) == 4 :
        tablename = sys.argv[1]
        backup_dir = sys.argv[2]
        merge_dir = sys.argv[3] 
    else :
        print(">>>> %s tablename backup_directory mergefile_directory" % sys.argv[0])
        print(">>>> %s LOCAL_TEST_HOST /Users/seory/Documents/Docu2022/IRIS_2022/TEST/backup  /Users/seory/Documents/Docu2022/IRIS_2022/TEST/merge_YY" % sys.argv[0])
        sys.exit()
    
    if os.path.isdir(backup_dir) == False : os.makedirs(backup_dir)
    if os.path.isdir(merge_dir) == False : os.makedirs(merge_dir)

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

    # ---------------------------------------------------
    # get PARTITION COLUMN NAME
    # ---------------------------------------------------
    """
     DB_NAME    TABLE_NAME         SCOPE    RAM_EXP_TIME    DSK_EXP_TIME    KEY_STRING    PARTITION_STRING    PARTITION_RANGE    ZIP_OPTION    USING_FTS
    """
    my_partition_colname = ''

    get_par_col_sql = "table info %s" % tablename
    try :
        curs.Execute2(str(get_par_col_sql))
        for row in curs :
            my_partition_colname = str(row[6]) 
            #print("PARITION COLUMN : ", my_partition_colname)
    except Exception as e_str :
        print(str(e_str)) 
        sys.exit()

    # ----------------------------------------------------------
    # get COLUMN LIST  && PARTITION COLUMN location_index
    # ----------------------------------------------------------
    """
    TABLE_CAT    TABLE_SCHEM    TABLE_NAME         COLUMN_NAME       DATA_TYPE    TYPE_NAME    COLUMN_SIZE    BUFFER_SIZE    BUFFER_LENGTH    DECIMAL_DIGITS    NULLABLE    REMARKS    COLUMN_DEF    SQL_DATA_TYPE    SQL_DATETIME_SUB    CHAR_OCTET_LENGTH    ORDINAL_POSITION    IS_NULLABLE    SCOPE_CATLOG    SCOPE_SCHEMA    SCOPE_TABLE    SOURCE_DATA_TYPE    IS_AUTOINCREMENT    NOTINDEXED
    """

    my_partition_colname_index = 1 

    collist = []
    get_col_sql = "table columns %s" % tablename
    try :
        curs.Execute2(str(get_col_sql))
        tmp_num = 0
        for row in curs :
            tmp_num += 1
            colname = str(row[3])
            collist.append(colname)
            #print(row)
    
            if colname == my_partition_colname : 
                my_partition_colname_index = tmp_num
    except Exception as e_str :
        print(str(e_str)) 
        sys.exit()
    


    backup_file_list = glob.glob("%s/%s_??????????????.dat" % (backup_dir, tablename))
    backup_file_list.sort()
    for backup_file in backup_file_list :

        # ------------------------------------------------------------------------------
        # partition column modify / append YEAR partition file 
        # ------------------------------------------------------------------------------
        YYYY_pattern = backup_file[-18:-14]
        new_file = "%s/%s_%s0101000000.dat" % (merge_dir, tablename, YYYY_pattern)

        my_cmd = "/usr/bin/awk -F '\\\\|\\\\^\\\\|' -v OFS='\|\^\|'  '{ sub(" + '"[0-9]{10}$", "0101000000", $%s) ; print }' % (my_partition_colname_index)  + "' >> %s %s" % (new_file, backup_file)

        sp = subprocess.Popen(my_cmd , stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (stdout, stderr) = sp.communicate()


    myiris.DIS_CONNECT()

    sys.exit()

LOCAL_TEST_HOST.MON.sql                                                                             000644  000765  000024  00000000745 14172443314 015072  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         DROP TABLE IF EXISTS LOCAL_TEST_HOST;
        CREATE TABLE LOCAL_TEST_HOST ( PARTITION_DATE TEXT , CTIME TEXT , P_K TEXT , HH TEXT , HOST TEXT , ERR_CNT INTEGER , LOG_CNT INTEGER )
        DATASCOPE LOCAL
        RAMEXPIRE 10
        DISKEXPIRE 5256000
        PARTITIONKEY P_K 
        PARTITIONDATE PARTITION_DATE
        PARTITIONRANGE 44640; 

CREATE INDEX LOCAL_TEST_HOST_IDX1 ON LOCAL_TEST_HOST ( CTIME DESC );
CREATE INDEX LOCAL_TEST_HOST_IDX2 ON LOCAL_TEST_HOST ( HOST DESC );
                           LOCAL_TEST_NO_PARTITION_HOST.sql                                                                    000644  000765  000024  00000000547 14203074710 016462  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         
CREATE TABLE LOCAL_TEST_NO_PARTITION_HOST (
CTIME TEXT, 
HH TEXT, 
HOST TEXT, 
LOG_CNT INTEGER, 
TOTAL_CNT INTEGER
)

DATASCOPE LOCAL 
RAMEXPIRE 0
DISKEXPIRE 1
PARTITIONKEY a
PARTITIONDATE b
PARTITIONRANGE 1 ; 

.table option LOCAL_TEST_NO_PARTITION_HOST DISK OFF

CREATE INDEX LOCAL_TEST_NO_PARTITION_HOST_IDX1 ON LOCAL_TEST_NO_PARTITION_HOST ( CTIME   ); 
                                                                                                                                                         ._N_004_load_NO_partition_local.py                                                                  000755  000765  000024  00000000322 14203060044 017560  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                             Mac OS X            	   2   �      �                                      ATTR       �   �   *                  �   *  $com.apple.metadata:_kMDItemUserTags  bplist00�                            	                                                                                                                                                                                                                                                                                                              PaxHeader/N_004_load_NO_partition_local.py                                                          000755  000765  000024  00000000357 14203060044 021324  x                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         30 mtime=1644978212.853756715
114 LIBARCHIVE.xattr.com.apple.metadata:_kMDItemUserTags=YnBsaXN0MDCgCAAAAAAAAAEBAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAJ
95 SCHILY.xattr.com.apple.metadata:_kMDItemUserTags=bplist00�                            	
                                                                                                                                                                                                                                                                                 N_004_load_NO_partition_local.py                                                                    000755  000765  000024  00000010720 14203060044 017346  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         #!/usr/bin/env python3

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

    addr = '192.168.107.22' 
    id = 'test' 
    #passwd = '!hello.iris0'
    passwd = 'test'
    port = 5050 
    db = 'test' 


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
                                                ._N_005_make_sql_table.py                                                                           000755  000765  000024  00000000322 14203074571 015760  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                             Mac OS X            	   2   �      �                                      ATTR       �   �   *                  �   *  $com.apple.metadata:_kMDItemUserTags  bplist00�                            	                                                                                                                                                                                                                                                                                                              PaxHeader/N_005_make_sql_table.py                                                                   000755  000765  000024  00000000356 14203074571 017523  x                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         29 mtime=1644984697.38843526
114 LIBARCHIVE.xattr.com.apple.metadata:_kMDItemUserTags=YnBsaXN0MDCgCAAAAAAAAAEBAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAJ
95 SCHILY.xattr.com.apple.metadata:_kMDItemUserTags=bplist00�                            	
                                                                                                                                                                                                                                                                                  N_005_make_sql_table.py                                                                             000755  000765  000024  00000011667 14203074571 015561  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         #!/usr/bin/env python3

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

    addr = '192.168.107.22' 
    id = 'test' 
    #passwd = '!hello.iris0'
    passwd = 'test'
    port = 5050 
    db = 'test' 


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
                                                                         ._P_000_backup.py                                                                                   000755  000765  000024  00000000322 14200101543 014242  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                             Mac OS X            	   2   �      �                                      ATTR       �   �   *                  �   *  $com.apple.metadata:_kMDItemUserTags  bplist00�                            	                                                                                                                                                                                                                                                                                                              PaxHeader/P_000_backup.py                                                                           000755  000765  000024  00000000357 14200101543 016006  x                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         30 mtime=1644200803.797008137
114 LIBARCHIVE.xattr.com.apple.metadata:_kMDItemUserTags=YnBsaXN0MDCgCAAAAAAAAAEBAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAJ
95 SCHILY.xattr.com.apple.metadata:_kMDItemUserTags=bplist00�                            	
                                                                                                                                                                                                                                                                                 P_000_backup.py                                                                                     000755  000765  000024  00000013312 14200101543 014030  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         #!/usr/bin/env python3


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
                                                                                                                                                                                                                                                                                                                      ._P_002_create_table_sql.py                                                                         000755  000765  000024  00000000322 14201141654 016300  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                             Mac OS X            	   2   �      �                                      ATTR       �   �   *                  �   *  $com.apple.metadata:_kMDItemUserTags  bplist00�                            	                                                                                                                                                                                                                                                                                                              PaxHeader/P_002_create_table_sql.py                                                                 000755  000765  000024  00000000357 14201141654 020044  x                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         30 mtime=1644479404.332051584
114 LIBARCHIVE.xattr.com.apple.metadata:_kMDItemUserTags=YnBsaXN0MDCgCAAAAAAAAAEBAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAJ
95 SCHILY.xattr.com.apple.metadata:_kMDItemUserTags=bplist00�                            	
                                                                                                                                                                                                                                                                                 P_002_create_table_sql.py                                                                           000755  000765  000024  00000010007 14201141654 016064  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         #!/usr/bin/env python3


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

    addr = '192.168.107.22' 
    id = 'test' 
    #passwd = '!hello.iris0'
    passwd = 'test'
    port = 5050 
    db = 'test' 

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
   
 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         ._P_003_execute_sql.py                                                                              000755  000765  000024  00000000322 14176673630 015350  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                             Mac OS X            	   2   �      �                                      ATTR       �   �   *                  �   *  $com.apple.metadata:_kMDItemUserTags  bplist00�                            	                                                                                                                                                                                                                                                                                                              PaxHeader/P_003_execute_sql.py                                                                      000755  000765  000024  00000000357 14176673630 017114  x                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         30 mtime=1643870104.415607751
114 LIBARCHIVE.xattr.com.apple.metadata:_kMDItemUserTags=YnBsaXN0MDCgCAAAAAAAAAEBAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAJ
95 SCHILY.xattr.com.apple.metadata:_kMDItemUserTags=bplist00�                            	
                                                                                                                                                                                                                                                                                 P_003_execute_sql.py                                                                                000755  000765  000024  00000005175 14176673630 015146  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         #!/usr/bin/env python3

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
 
                                                                                                                                                                                                                                                                                                                                                                                                   ._P_004_makeCTL_loadTable.py                                                                        000755  000765  000024  00000000322 14174126600 016243  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                             Mac OS X            	   2   �      �                                      ATTR       �   �   *                  �   *  $com.apple.metadata:_kMDItemUserTags  bplist00�                            	                                                                                                                                                                                                                                                                                                              PaxHeader/P_004_makeCTL_loadTable.py                                                                000755  000765  000024  00000000357 14174126600 020007  x                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         30 mtime=1643163008.801123468
114 LIBARCHIVE.xattr.com.apple.metadata:_kMDItemUserTags=YnBsaXN0MDCgCAAAAAAAAAEBAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAJ
95 SCHILY.xattr.com.apple.metadata:_kMDItemUserTags=bplist00�                            	
                                                                                                                                                                                                                                                                                 P_004_makeCTL_loadTable.py                                                                          000755  000765  000024  00000010462 14174126600 016034  0                                                                                                    ustar 00seory                           staff                           000000  000000                                                                                                                                                                         #!/usr/bin/env python3

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

    addr = '192.168.107.22' 
    id = 'test' 
    #passwd = '!hello.iris0'
    passwd = 'test'
    port = 5050 
    db = 'test' 


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
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
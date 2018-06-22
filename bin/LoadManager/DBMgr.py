# -*- coding: utf-8 -*-
import os
import math
import time
import ConfigParser
import Mobigen.Common.Log as Log; Log.Init()
import unicodedata
import codecs

class DBMgr:
    # DIRECTION
    DIR_SRC = 0
    DIR_DST = 1
    DIR_TYPE = (DIR_SRC, DIR_DST)

    # MAXINUM FILE DESCRIPTOR
    FD_NUM = 100

    # DEFAULT IRIS TERM
    DEFAULT_IRIS_TERM = 10

    def __init__(self, dbConf, dir):
        self.csvFd = {}
        self.fdQueue = []

        self.DB_CONF = {}
        self.DB_CONF = self.loadConfig(dbConf)

        if not dir in self.DIR_TYPE:
            raise ValueError("Invalid direction:%s" % dir)
        else :
            self.dir = dir

        self.initConfig()

        self.keyIndex = 0

    def initConfig(self):
        self.initDBMS_IP()
        self.initDBMS_PORT()
        self.initDBMS_DB()
        self.initDBMS_ID()
        self.initDBMS_PWD()
        self.initEncoding()
        self.initETC()
        self.initIRIS()

    def initDBMS_IP(self):
        key = "SRC_IP"
        if self.dir == self.DIR_DST:
            key = "DST_IP"

        if not key in self.DB_CONF["GENERAL"]:
            raise ValueError("No %s value." % key)
        if self.DB_CONF["GENERAL"][key].strip() == "":
            raise ValueError("Invalid %s value." % key)

        self.DBMS_IP = self.DB_CONF["GENERAL"][key]

    def initDBMS_PORT(self):
        key = "SRC_PORT"
        if self.dir == self.DIR_DST:
            key = "DST_PORT"

        try :
            self.DBMS_PORT = int(self.DB_CONF["GENERAL"][key])
        except :
            self.DBMS_PORT = self.getDefaultPort()

    def initDBMS_DB(self):
        key = "SRC_DB"
        if self.dir == self.DIR_DST:
            key = "DST_DB"

        try:
            self.DBMS_DB = self.DB_CONF["GENERAL"][key]
        except:
            self.DBMS_DB = ""

    def initDBMS_ID(self):
        key = "SRC_ID"
        if self.dir == self.DIR_DST:
            key = "DST_ID"

        if not key in self.DB_CONF["GENERAL"]:
            raise ValueError("No %s value." % key)
        if self.DB_CONF["GENERAL"][key].strip() == "":
            raise ValueError("Invalid %s value." % key)

        self.ID = self.DB_CONF["GENERAL"][key]

    def initDBMS_PWD(self):
        key = "SRC_PWD"
        if self.dir == self.DIR_DST:
            key = "DST_PWD"

        if not key in self.DB_CONF["GENERAL"]:
            raise ValueError("No %s value." % key)

        self.PWD = self.DB_CONF["GENERAL"][key]

    def initEncoding(self):
        try:
            self.SRC_ENC = self.DB_CONF["GENERAL"]["SRC_ENC"]
        except:
            self.SRC_ENC = "utf-8"

        try:
            self.DST_ENC = self.DB_CONF["GENERAL"]["DST_ENC"]
        except:
            self.DST_ENC = "utf-8"

    def initETC(self):
        try:
            self.DATA_DIR    = self.DB_CONF["GENERAL"]["DATA_DIR"]
        except:
            self.DATA_DIR    = "."

        self.LOAD_DIR        = "%s/%s" % (self.DATA_DIR, "LOAD")
        self.LOAD_DONE_DIR    = "%s/%s" % (self.DATA_DIR, "LOAD_DONE")
        self.ERR_LOAD_DIR    = "%s/%s" % (self.DATA_DIR, "ERR_LOAD")
        self.ERR_ETC_DIR    = "%s/%s" % (self.DATA_DIR, "ERR_ETC")

        # DATA_DIR의 서브 디렉토리가 존재하지 않는다면 생성한다. 
        if not os.path.exists(self.LOAD_DIR):
            os.mkdir(self.LOAD_DIR)

        if not os.path.exists(self.LOAD_DONE_DIR):
            os.mkdir(self.LOAD_DONE_DIR)

        if not os.path.exists(self.ERR_LOAD_DIR):
            os.mkdir(self.ERR_LOAD_DIR)

        if not os.path.exists(self.ERR_ETC_DIR):
            os.mkdir(self.ERR_ETC_DIR)

        try:
            self.ROWSEP = self.DB_CONF["GENERAL"]["ROWSEP"].replace("\\n", "\n").replace("\\r", "\r")
        except:
            self.ROWSEP = "\n"

        try:
            self.COLSEP     = self.DB_CONF["GENERAL"]["COLSEP"]
        except:
            self.COLSEP = ","

        if not "DST_TABLE" in self.DB_CONF["GENERAL"]:
            raise ValueError("No DST_TABLE value.")
        if self.DB_CONF["GENERAL"]["DST_TABLE"].strip() == "":
            raise ValueError("Invalid DST_TABLE value.")

        self.TABLE = self.DB_CONF["GENERAL"]["DST_TABLE"]

    def initIRIS(self):
        try:
            self.IRIS_KEY_PARSE = int(self.DB_CONF["IRIS"]["KEY_PARSE"])
        except:
            self.IRIS_KEY_PARSE = 1

        if self.IRIS_KEY_PARSE == 3:
            if not "KEY_LEN" in self.DB_CONF["IRIS"]:
                raise ValueError("No KEY_LEN value in IRIS section.")
            else:
                try:
                    self.IRIS_KEY_LEN = int(self.DB_CONF["IRIS"]["KEY_LEN"])
                except:
                    raise ValueError("Invalid KEY_LEN value in IRIS section.")

                if self.IRIS_KEY_LEN <= 0:
                    raise ValueError("Invalid KEY_LEN value in IRIS section.")

        try:
            self.IRIS_KEY = int(self.DB_CONF["IRIS"]["KEY_INDEX"])
        except:
            self.IRIS_KEY = -1

        if self.IRIS_KEY == 0:
            raise ValueError("Invalid KEY_INDEX value(%s) in IRIS section." % self.IRIS_KEY)

        try:
            self.IRIS_KEY_COUNT = int(self.DB_CONF["IRIS"]["KEY_COUNT"])
        except:
            self.IRIS_KEY_COUNT = 1

        try:
            self.IRIS_PAT = int(self.DB_CONF["IRIS"]["DATE_TIME_INDEX"])
        except:
            self.IRIS_PAT = -1

        if self.IRIS_PAT == 0:
            raise ValueError("Invalid DATE_TIME_INDEX value(%s) in IRIS section." % self.IRIS_PAT)

        try:
            self.IRIS_TERM = int(self.DB_CONF["IRIS"]["PARTITION_TERM"])
        except:
            self.IRIS_TERM = DEFAULT_IRIS_TERM

    # load 구현은 자식 클래스에 위임한다.
    def load(self):
        raise NotImplementedError("Should have implemented this")

    # execute 구현은 자식 클래스에 위임한다.
    def execute(self, sql):
        raise NotImplementedError("Should have implemented this")

    # None은 ''으로 변환하고, encoding된 것은 decoding한다
    def translate(self, row):
        #print row

        newRow = []
        #print row
        for i in range(len(row)):
            if row[i] == None :
                newRow.append("")
            else:
                newVal = ""
                if type(row[i]).__name__ == "str":
                    try:
                        newVal = unicode(row[i], self.SRC_ENC)
                    except:
                        try:
                            newVal = "%s" % row[i].decode("euc-kr")
                        except:
                            newVal = "%s" % row[i]
#                        __LOG__.Exception()
                        #print "(%s)" % (row[i])
                else:
                    newVal = "%s" % row[i]

                newRow.append(newVal)

        return newRow

    def unload(self, sql, splitFlag):
        conn = None
        cur = None

        csvFile = None

        # KEY_PARSE가 2인 경우 사용. 초기화 한다. 
        self.keyIndex = 0

        sTime = time.time()

        try:
            '''
            SQL_CONF = {}
            SQL_CONF = self.loadConfig(sqlFile)

            sql = SQL_CONF["GENERAL"]["SQL"]
            '''

            (conn, cur) = self.execute(sql)

            for row in cur:
                #__LOG__.Trace("THIS : %s" % row)
                row = self.translate(row)

                # encoding/decoding한 row string을 받는다
                rowStr = "%s%s" % (self.COLSEP.join(row), self.ROWSEP)

                # SPLIT을 해야 하는 경우
                if splitFlag:
                    pat = "00000000000000"
                    key = "0"

                    if self.IRIS_PAT >= 1 and len(row) >= self.IRIS_PAT:
                        pat = self.getPat(row[self.IRIS_PAT-1], self.IRIS_TERM)

                    if self.IRIS_KEY >= 1 and len(row) >= self.IRIS_KEY:
                        key = self.getKey(row[self.IRIS_KEY-1])
                    #print "%s,%s,%s,%s,%s,%s\n" % (self.TABLE, pat, key, row, self.ROWSEP, self.COLSEP)

                    self.writeCsv(self.TABLE, pat, key, rowStr)
                # SPLIT을 할 필요가 없는 경우
                else:
                    if csvFile == None:
                        fileName = "%s/%s.csv" % (self.LOAD_DIR, self.TABLE)
                        __LOG__.Trace("unload file open : %s" % fileName)
                        csvFile = codecs.open(fileName, encoding=self.DST_ENC, mode="w")

                    csvFile.write(rowStr)
        finally:
            if splitFlag:
                self.closeCsv()
            else:
                if csvFile != None:
                    csvFile.close()

            if cur != None:
                try:
                    # IRIS Close
                    cur.Close()
                except:
                    try:
                        # RDBMS Close
                        cur.close()
                    except:
                        pass


            if conn != None:
                conn.close()

            processingTime = time.time() - sTime
            __LOG__.Trace("%s Unloading time : %0.3f\n" % (self.__class__.__name__, processingTime))
            

    # unload시 파일을 나눌지에 대한 flag. default는 false.
    def isSplit(self) :
        return False

    # 각 DBMS별 default port를 리턴한다.
    def getDefaultPort(self) :
        raise NotImplementedError("Should have implemented this")

    def getPat(self, dtValue, patTerm) :
        if len(dtValue) < 14 :
            #raise ValueError("Datetime length should be 14.(yyyyMMddHHMMss)")
            dt = 1
            val = 20130101000000

            return "%s" % (val)
        else :
            dt = int(dtValue)
            val = dt - (dt % (patTerm * 100))

            return "%s" % (val)

    def getKey(self, keyValue) :
        value = "None"

        # KEY_PARSE가 1인 경우, KEY_INDEX의 값이 그대로 사용
        if self.IRIS_KEY_PARSE == 1 :
            if len(keyValue) > 0 :
                value = keyValue
        # KEY_PARSE가 2인 경우, KEY_COUNT에 의해 Key 생성
        elif self.IRIS_KEY_PARSE == 2 :
            self.keyIndex += 1
            value = str(self.keyIndex % self.IRIS_KEY_COUNT)
        # KEY_PARSE가 3인 경우, KEY_LEN에 의해 Key컬럼의 뒷자리 갯수만큼을 Key로 본다
        elif self.IRIS_KEY_PARSE == 3 :
            keyLen = self.IRIS_KEY_LEN
            keyValueLen = len(keyValue)
            value = keyValue[keyValueLen-keyLen:keyValueLen]

        return value

    def createFd(self, fileName) :
        queueSize = len(self.fdQueue)

        if queueSize >= self.FD_NUM :
            oldFileName = self.fdQueue.pop(0)
            self.csvFd[oldFileName].close()
            del self.csvFd[oldFileName]

        newFd = None
        if os.path.exists(fileName) :
            newFd = codecs.open(fileName, encoding=self.DST_ENC, mode="a")
        else :
            newFd = codecs.open(fileName, encoding=self.DST_ENC, mode="w")

        self.fdQueue.append(fileName)
        self.csvFd[fileName] = newFd

        return newFd

    def writeCsv(self, table, pat, key, rowStr):
        try :
            fileName = "%s/%s_%s_%s.csv" % (self.LOAD_DIR, table, pat, key)
        except :
            print "fileName error"
            sys.exit(1)

        fd = ""

        if fileName in self.csvFd:
            fd = self.csvFd[fileName]
        else:
            fd = self.createFd(fileName)

        fd.write(rowStr);
    
    def closeCsv(self):
        for oneFileName in self.csvFd:
            self.csvFd[oneFileName].close()

        del self.csvFd
        del self.fdQueue

        self.csvFd = {}
        self.fdQueue = []

    def loadConfig(self, conf):
        confObj = ConfigParser.ConfigParser()
        confObj.read(conf)
        retHash = {}
        for section in confObj.sections():
            retHash[section] = {}
            for (key, value) in confObj.items(section):
                retHash[section][key.upper()] = value

        return retHash

import os.path
import base64
import time
import sys
import signal
import json

from .M6_Exception import ConnectionFailException, LoginFailException, LoadTypeException
from .LoadProperty import LoadProperty
try:
    from Mobigen.Common import Log
    from Mobigen.Common.Log import __LOG__
    Log.Init()
except:
    pass


class Cursor(object):
    def __init__(self, sock, Debug=False, LogModule='STDOUT'):
        object.__init__(self)
        self.firstExecute = False
        self.sock = sock
        self.isDebug = Debug
        if Debug:
            signal.signal(signal.SIGINT, self._signal_handler)

        self.buffer = []
        self.LogModule = LogModule;

        self.record_sep = '' #^^ : record sep
        self.field_sep = '' #^_ : unit sep

        self.statusInfo = ""
        self.bufSize = 1024
        self.has_next = False

    def __iter__(self):        
        return self    

    def next(self):        
        return self.__next__()

    def __next__(self):
        if len(self.buffer) == 0: self.ReadData()
        record = self.buffer.pop(0)
        return record

    def hasNext(self):
        return self.has_next

    def _signal_handler(self, signum, frame):
        if self.isDebug:
            if self.LogModule == "STDOUT":
                sys.stdout.Watch(self.statusInfo)
                sys.stdout.flush()
            elif self.LogModule == "MOBIGEN":
                __LOG__.Watch(self.statusInfo)
            sys.exit(0)

    def SetTimeout(self, time):
        self.sock.SetTimeout(time)
        
    def SetInfo(self, id, password, host, libinfo) :
        if self.isDebug:
            debugStartTime = time.time()

        param = "%s,%s,%s,%s" % (id, password, host, libinfo)
        sendMsg = "SETINFO %s\r\n" % base64.b64encode(param.encode('utf-8')).decode('utf-8')

        # send SETINFO command
        self.sock.SendMessage(sendMsg)

        # result message from UDM
        msg = self.sock.Readline()
        if msg[0] != "+" : raise ConnectionFailException(msg)

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print("[DEBUG_TIME] SetInfo() %f" % (debugEndTime - debugStartTime))
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] SetInfo() %f" % (debugEndTime - debugStartTime))

    def SetBufSize(self, size):
        self.bufSize = size

    def Login(self, id, password, libinfo) :
        if self.isDebug:
            debugStartTime = time.time()

        param = "%s,%s,%s" % (id, password, libinfo)
        sendMsg = 'LOGIN %s\r\n' % base64.b64encode(param.encode('utf-8')).decode('utf-8')

        # send LOGIN command
        self.sock.SendMessage(sendMsg)

        # welcome message from PGD
        msg = self.sock.Readline()
        if msg[0] != "+" : raise LoginFailException(msg)

        # welcome message from UDM
        msg = self.sock.Readline()
        if msg[0] != "+" : raise ConnectionFailException(msg)

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print("[DEBUG_TIME] Login() %f" % (debugEndTime - debugStartTime))
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] Login() %f" % (debugEndTime - debugStartTime))

    def SetFieldSep(self, sep) :
        if self.isDebug:
            debugStartTime = time.time()

        sendMsg = 'SET_FIELD_SEP %s\r\n' % base64.b64encode(sep.encode('utf-8')).decode('utf-8')
        self.sock.SendMessage(sendMsg)
        msg = self.sock.Readline()
        if msg[0] != "+" : return False
        self.field_sep = sep

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print("[DEBUG_TIME] SetFieldSep() %f" % (debugEndTime - debugStartTime))
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] SetFieldSep() %f" % (debugEndTime - debugStartTime))

        return True

    def SetRecordSep(self, sep) :
        if self.isDebug:
            debugStartTime = time.time()

        sendMsg = 'SET_RECORD_SEP %s\r\n' % base64.b64encode(sep.encode('utf-8')).decode('utf-8')
        self.sock.SendMessage(sendMsg)
        msg = self.sock.Readline()
        if msg[0] != "+" : return False
        self.record_sep = sep

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print("[DEBUG_TIME] SetRecordSep() %f" % (debugEndTime - debugStartTime))
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] SetRecordSep() %f" % (debugEndTime - debugStartTime))

        return True

    def Metadata(self):
        sendMsg = "METADATA\r\n"
        self.sock.SendMessage(sendMsg)
        msg = self.sock.Readline()
        if msg[0] != "+" : raise Exception(msg)
        (tag, size) = msg.strip().split(" ", 1)
        iSize = int(size)
        metaDataDict = {}
        if iSize:
            metaData = self.sock.Read(iSize)
            (columnNameList, columnTypeList) = json.loads(metaData)
            metaDataDict['ColumnCount'] = len(columnNameList)
            metaDataDict['ColumnName'] = columnNameList
            metaDataDict['ColumnType'] = columnTypeList
        return metaDataDict

    def check_semi(self, sql):
        chk_sql = sql.upper().strip()
        if chk_sql.startswith("SELECT") \
                or chk_sql.startswith("UPDATE") \
                or chk_sql.startswith("INSERT") \
                or chk_sql.startswith("DELETE") \
                or chk_sql.startswith("CREATE") \
                or chk_sql.startswith("DROP") \
                or chk_sql.startswith("ALTER") \
                or chk_sql.startswith("/*+"):
            if not chk_sql.endswith(";"):
                return sql + ";"
        return sql

    def Execute2(self, sql):
        self.has_next = False
        if self.isDebug:
            debugStartTime = time.time()

        # sql = self.check_semi(sql)

        sendMsg = "EXECUTE2 %s\r\n%s" % (len(sql.encode('utf-8')), sql)
        self.sock.SendMessage(sendMsg)
        msg = self.sock.Readline()
        if msg[0] != "+" : raise Exception(msg)
        self.firstExecute = False

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print("[DEBUG_TIME] Execute2() %f" % (debugEndTime - debugStartTime))
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] Execute2() %f" % (debugEndTime - debugStartTime))

        return msg

    def Execute(self, sql):
        self.has_next = False
        if self.isDebug:
            debugStartTime = time.time()

        sql = self.check_semi(sql)
        sql_length = len(sql)

        sendMsg = "EXECUTE %s\r\n%s" % (sql_length, sql)
        #print sendMsg;
        self.firstExecute = False
        self.sock.SendMessage(sendMsg)
        self.firstExecute = True

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print("[DEBUG_TIME] Execute() %f" % (debugEndTime - debugStartTime))
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] Execute() %f" % (debugEndTime - debugStartTime))

    def ReadData(self) :
        if self.isDebug:
            debugStartTime = time.time()

        if not self.firstExecute : self.sock.SendMessage("CONT\r\n")
        else: self.firstExecute = False

        msg = self.sock.Readline()
        try: (tag, param) = msg.strip().split(" ", 1) 
        except: tag = msg.strip()

        if "+OK" == tag : 
            self.has_next = True
            raise StopIteration()
        if "-" == tag[0] : raise Exception(param)

        data = self.sock.Read(int(param))
        self.buffer = json.loads(data)

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print("[DEBUG_TIME] ReadData() %f" % (debugEndTime - debugStartTime))
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] ReadData() %f" % (debugEndTime - debugStartTime))

    def Fetch(self): 
        pass

    def Fetchall(self): 
        if self.isDebug:
            debugStartTime = time.time()

        if not self.firstExecute : self.sock.SendMessage("CONT ALL\r\n")
        else: self.firstExecute = False

        tmp_str = ""
        tmp_list = []
        while True:
            msg = self.sock.Readline()
            try: (tag, param) = msg.strip().split(" ", 1) 
            except: tag = msg.strip()

            if "+OK" == tag:
                break
            if "-" == tag[0]:
                raise Exception(param)

            tmp_list += json.loads(self.sock.Read(int(param)))

            self.sock.SendMessage("CONT ALL\r\n")

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print("[DEBUG_TIME] Fetchall() %f" % (debugEndTime - debugStartTime))
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] Fetchall() %f" % (debugEndTime - debugStartTime))

        return tmp_list

    def Fetchone(self):
        return self.next()

    def _checkValidity(self, table, key, partition):
        if key == "" :
            raise LoadTypeException("-ERR Empty Key in %s(partition: %s)" % (table, partition))
        try :
            time.strptime(partition, "%Y%m%d%H%M%S")
        except ValueError:
            raise LoadTypeException("-ERR Invalid Partition Time [%s] in %s" % (partition, table))

    def LoadGlobal(self, table, control_file_path, dat_file_path, load_property=None):
        try :
            self.LoadCore(table, "", "", control_file_path, dat_file_path, load_property=load_property)
        except LoadTypeException as e:
            return str(e)
        return self.sock.Readline()

    def Load(self, table, key, partition, control_file_path, dat_file_path, load_property=None):
        self._checkValidity(table, key, partition)

        try :
            self.LoadCore(table, key, partition, control_file_path, dat_file_path, load_property=load_property)
        except LoadTypeException as e:
            return str(e)
        return self.sock.Readline()
    
    def LoadStringGlobal(self, table, control_string, dat_string, load_property=None):
        try :
            self.LoadCore(table, "", "", None, None, control_string=control_string, dat_string=dat_string, load_property=load_property)
        except LoadTypeException as e:
            return str(e)
        return self.sock.Readline()

    def LoadString(self, table, key, partition, control_string, dat_string, load_property=None):
        self._checkValidity(table, key, partition)
        try :
            self.LoadCore(table, key, partition, None, None, control_string=control_string, dat_string=dat_string, load_property=load_property)
        except LoadTypeException as e:
            return str(e)
        return self.sock.Readline()

    def _logger(self, msg):
        if self.isDebug:
            if self.LogModule == "STDOUT":
                print(msg)
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace(msg)

    def LoadCore(self, table, key, partition, control_file_path=None, dat_file_path=None, CMD='IMPORT', control_string=None, dat_string=None, load_property=None):
        self._logger("[DEBUG] GetSizeStart (%s)" % control_file_path)

        if load_property is None:
            load_property = LoadProperty()

        if dat_file_path is None and dat_string is None:
            raise LoadTypeExcetion("-ERR dat is invalid.\r\n")

        # check record_sep is valid when csv loading.
        if load_property.is_csv_dat() and not self.record_sep in ('\r', '\n'):
            raise LoadTypeException("-ERR Record Separator is invalid. [%s]\r\n" % repr(self.record_sep))

        # check control file is exists when normal loading.
        if not load_property.is_csv_dat() and control_file_path is None and control_string is None:
            raise LoadTypeException("-ERR ctl file doesn't exist.\r\n")

        if control_file_path:
            ctl_size = os.path.getsize(control_file_path)
        elif control_string:
            ctl_size = len(control_string)
        else:
            ctl_size = 4
            control_string = 'NULL'

        self._logger("[DEBUG] GetSizeEnd")

        if dat_file_path is None:
            data_size = len(dat_string)
        else:
            self._logger("[DEBUG] GetSizeStart (%s)" % dat_file_path)
            data_size = os.path.getsize(dat_file_path)
            self._logger("[DEBUG] GetSizeEnd")

        if CMD == 'IMPORT':
            sendMsg = "%s %s,%s,%s,%s,%s,%s\r\n" % (CMD, table, key, partition, ctl_size, data_size, load_property.to_str())
        else:
            sendMsg = "%s %s,%s,%s,%s,%s\r\n" % (CMD, table, key, partition, ctl_size, data_size)

        self.sock.SendMessage(sendMsg)

        fileList = []
        if control_file_path is not None:
            fileList.append(control_file_path)
        else:
            self.sock.SendMessage(control_string)

        if dat_file_path is not None:
            fileList.append(dat_file_path)

        for f in fileList :
            fobj = open(f,encoding='utf-8')
            self._logger("[DEBUG] OpenFile (%s)" % f)

            while True :
                if self.isDebug:
                    self.statusInfo = "Befor FileRead"
                buf = fobj.read(self.bufSize)
                if self.isDebug:
                    self.statusInfo = "After FileRead"

                if not buf:
                    break #EOF

                if self.isDebug:
                    self.statusInfo = "Befor SendMessage"
                self.sock.SendMessage(buf)
                if self.isDebug:
                    self.statusInfo = "After SendMessage"

            self._logger("[DEBUG] End (%s)" % f)
            fobj.close()

        if dat_file_path is None:
            self.sock.SendMessage(dat_string)

    def Close(self):
        pass

if __name__ == "__main__" :
    import time
    c = Cursor(None)

    for i in c :
        print(i)
        time.sleep(1)

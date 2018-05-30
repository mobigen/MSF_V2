import os.path
import base64
import time
import sys
import signal

try:
    from Mobigen.Common import Log
    from Mobigen.Common.Log import __LOG__
    Log.Init()
except:
    pass

class LoginFailException(Exception) : pass
class ConnectionFailException(Exception) : pass
class LoadTypeException(Exception) : pass

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

    def __iter__(self):        
        return self    

    def next(self):        
        if len(self.buffer) == 0 : self.ReadData()
        record = self.buffer.pop(0)
        return record.split(self.field_sep)

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
        sendMsg = "SETINFO %s\r\n" % (base64.b64encode(param))

        # send SETINFO command
        self.sock.SendMessage(sendMsg)

        # result message from UDM
        msg = self.sock.Readline()
        if msg[0] != "+" : raise ConnectionFailException, msg

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print "[DEBUG_TIME] SetInfo() %f" % (debugEndTime - debugStartTime)
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] SetInfo() %f" % (debugEndTime - debugStartTime))

    def SetBufSize(self, size):
        self.bufSize = size

    def Login(self, id, password, libinfo) :
        if self.isDebug:
            debugStartTime = time.time()

        param = "%s,%s,%s" % (id, password, libinfo)
        sendMsg = "LOGIN %s\r\n" % (base64.b64encode(param))

        # send LOGIN command
        self.sock.SendMessage(sendMsg)

        # welcome message from PGD
        msg = self.sock.Readline()
        if msg[0] != "+" : raise LoginFailException, msg

        # welcome message from UDM
        msg = self.sock.Readline()
        if msg[0] != "+" : raise ConnectionFailException, msg

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print "[DEBUG_TIME] Login() %f" % (debugEndTime - debugStartTime)
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] Login() %f" % (debugEndTime - debugStartTime))

    def SetFieldSep(self, sep) :
        if self.isDebug:
            debugStartTime = time.time()

        sendMsg = "SET_FIELD_SEP %s\r\n" % (base64.b64encode(sep))
        self.sock.SendMessage(sendMsg)
        msg = self.sock.Readline()
        if msg[0] != "+" : return False
        self.field_sep = sep

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print "[DEBUG_TIME] SetFieldSep() %f" % (debugEndTime - debugStartTime)
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] SetFieldSep() %f" % (debugEndTime - debugStartTime))

        return True

    def SetRecordSep(self, sep) :
        if self.isDebug:
            debugStartTime = time.time()

        sendMsg = "SET_RECORD_SEP %s\r\n" % (base64.b64encode(sep))
        self.sock.SendMessage(sendMsg)
        msg = self.sock.Readline()
        if msg[0] != "+" : return False
        self.record_sep = sep

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print "[DEBUG_TIME] SetRecordSep() %f" % (debugEndTime - debugStartTime)
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] SetRecordSep() %f" % (debugEndTime - debugStartTime))

        return True

    def Metadata(self):
        sendMsg = "METADATA\r\n"
        self.sock.SendMessage(sendMsg)
        msg = self.sock.Readline()
        if msg[0] != "+" : raise Exception, msg
        (tag, size) = msg.strip().split(" ", 1)
        iSize = int(size)
        metaDataDict = {}
        if iSize:
            metaData = self.sock.Read(iSize)
            (columnName, columnType) = metaData.split(self.record_sep)
            columnNameList = columnName.split(self.field_sep)
            columnTypeList = columnType.split(self.field_sep)
            metaDataDict['ColumnCount'] = len(columnNameList)
            metaDataDict['ColumnName'] = columnNameList
            metaDataDict['ColumnType'] = columnTypeList
        return metaDataDict

    def Execute2(self, sql):
        if self.isDebug:
            debugStartTime = time.time()

        sendMsg = "EXECUTE2 %s\r\n%s" % (len(sql), sql)
        self.sock.SendMessage(sendMsg)
        msg = self.sock.Readline()
        if msg[0] != "+" : raise Exception, msg
        self.firstExecute = False

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print "[DEBUG_TIME] Execute2() %f" % (debugEndTime - debugStartTime)
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] Execute2() %f" % (debugEndTime - debugStartTime))

        return msg

    def Execute(self, sql):
        if self.isDebug:
            debugStartTime = time.time()

        sql_length = len(sql)

        sendMsg = "EXECUTE %s\r\n%s" % (sql_length, sql)
        #print sendMsg;
        self.firstExecute = False
        self.sock.SendMessage(sendMsg)
        self.firstExecute = True

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print "[DEBUG_TIME] Execute() %f" % (debugEndTime - debugStartTime)
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

        if "+OK" == tag : raise StopIteration
        if "-" == tag[0] : raise Exception, param

        data = self.sock.Read(int(param))
        self.buffer = data.split(self.record_sep)

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print "[DEBUG_TIME] ReadData() %f" % (debugEndTime - debugStartTime)
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
        while True:
            msg = self.sock.Readline()
            try: (tag, param) = msg.strip().split(" ", 1) 
            except: tag = msg.strip()

            if "+OK" == tag:
                break
            if "-" == tag[0]:
                raise Exception, param

            if tmp_str == "":
                tmp_str = self.sock.Read(int(param))
            else:
                tmp_str += self.record_sep + self.sock.Read(int(param))

            self.sock.SendMessage("CONT ALL\r\n")
        st = time.time()
        tmp_list = tmp_str.split(self.record_sep)
        tmp_list = map(lambda x: x.split(self.field_sep), tmp_list)
        et = time.time()
        #print "string to list : %f" % (et-st)

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == "STDOUT":
                print "[DEBUG_TIME] Fetchall() %f" % (debugEndTime - debugStartTime)
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG_TIME] Fetchall() %f" % (debugEndTime - debugStartTime))

        return tmp_list

    def Fetchone(self):
        return self.next()

    def LoadProc(self, proc_file_path):
        data_size = os.path.getsize(proc_file_path)
        f = open(proc_file_path)
        data = f.read()
        f.close()
        sendMsg = "LOAD_PROC %s\r\n%s" % (data_size, data)
        self.sock.SendMessage(sendMsg)
        return self.sock.Readline()

    def Load_Rename(self, table, key, partition, control_file_path, data_file) :
        return  self.Load(table, key, partition, control_file_path, \
            data_file, "IMPORT_RENAME")

    def Load_BFILE(self, table, key, partition, control_file_path, data_file, load_ready_check=False) :
        if load_ready_check:
            retMsg = self.LoadReady(table, key, partition)
            if retMsg[0] == '-': return retMsg
        try :
            self.LoadCore(table, key, partition, control_file_path, data_file, "IMPORT_BFILE")
        except LoadTypeException, e:
            return str(e)

        retMessage = None

        while True :
            retMessage = self.sock.Readline()
            if retMessage[:3] == "+OK" : break

            fileInfo = retMessage[6:].strip()

            try :
                self.sock.SendMessage("%s %d\r\n" % (fileInfo, os.path.getsize(fileInfo) ) )

                tmpFile = open(fileInfo)
                while True :
                    data = tmpFile.read(self.bufSize)
                    if not data: break #EOF
                    self.sock.SendMessage(data)
                tmpFile.close()
            except : 
                self.sock.SendMessage("%s %d\r\n" % (fileInfo, 0 ) )

        return retMessage

    def LoadGlobal(self, table, control_file_path, \
            data_file, CMD="IMPORT", reload=False) :
    
        try :
            self.LoadCore(table, "", "", control_file_path, data_file, CMD, load_ready_check=False, reload=reload)
        except LoadTypeException, e:
            return str(e)
        return self.sock.Readline()

    def Load(self, table, key, partition, control_file_path,\
            data_file, CMD="IMPORT", load_ready_check=False, reload=False) :

        self.checkValidity(table, key, partition)

        try :
            self.LoadCore(table, key, partition, control_file_path, data_file, CMD, load_ready_check=load_ready_check, reload=reload)
        except LoadTypeException, e:
            return str(e)
        return self.sock.Readline()
    
    def LoadEx(self, table, key, partition, control_file_path,\
            data, CMD="IMPORT", load_ready_check=False) :

        self.checkValidity(table, key, partition)

        try :
            self.LoadCore(table, key, partition, control_file_path, "", CMD, data=data, load_ready_check=load_ready_check)
        except LoadTypeException, e:
            return str(e)
        return self.sock.Readline()

    def checkValidity(self, table, key, partition):
        if key == "" :
            raise LoadTypeException, "-ERR Empty Key in %s(partition: %s)" % (table, partition)
        try :
            time.strptime(partition, "%Y%m%d%H%M%S")
        except ValueError:
            raise LoadTypeException, "-ERR Invalid Partition Time [%s] in %s" % (partition, table)


    def LoadCore(self, table, key, partition, control_file_path, data_file, CMD, data="", load_ready_check=False, reload=False) :

        if load_ready_check:
            retMsg = self.LoadReady(table, key, partition)
            if retMsg[0] == '-': return retMsg
    
        if self.isDebug:
            if self.LogModule == "STDOUT":
                print "[DEBUG] GetSizeStart (%s)" % control_file_path,
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG] GetSizeStart (%s)" % control_file_path)

        ctl_size = os.path.getsize(control_file_path)

        if self.isDebug:
            if self.LogModule == "STDOUT":
                print "[DEBUG] GetSizeEnd"
            elif self.LogModule == "MOBIGEN":
                __LOG__.Trace("[DEBUG] GetSizeEnd")

        if data_file == "":
            data_size = len(data)
        else:
            if self.isDebug:
                if self.LogModule == "STDOUT":
                    print "[DEBUG] GetSizeStart (%s)" % data_file,
                elif self.LogModule == "MOBIGEN":
                    __LOG__.Trace("[DEBUG] GetSizeStart (%s)" % data_file)

            data_size = os.path.getsize(data_file)

            if self.isDebug:
                if self.LogModule == "STDOUT":
                    print "[DEBUG] GetSizeEnd"
                elif self.LogModule == "MOBIGEN":
                    __LOG__.Trace("[DEBUG] GetSizeEnd")

        sendMsg = None
        if CMD == 'IMPORT':
            sendMsg = "%s %s,%s,%s,%s,%s,%s\r\n" % (CMD, table, key, partition, ctl_size, data_size, str(reload).upper())
        else:
            sendMsg = "%s %s,%s,%s,%s,%s\r\n" % (CMD, table, key, partition, ctl_size, data_size)

        self.sock.SendMessage(sendMsg)

        if data_file == "":
            fobj = open(control_file_path)
            if self.isDebug:
                if self.LogModule == "STDOUT":
                    print "[DEBUG] OpenControlFile %s" % control_file_path
                elif self.LogModule == "MOBIGEN":
                    __LOG__.Trace("[DEBUG] OpenControlFile %s" % control_file_path)

            while True:
                if self.isDebug:
                    self.statusInfo = "Befor FileRead"
                buf = fobj.read(self.bufSize)
                if self.isDebug:
                    self.statusInfo = "Afefor FileRead"

                if not buf: break #EOF

                if self.isDebug:
                    self.statusInfo = "Befor SendMessage"
                self.sock.SendMessage(buf)
                if self.isDebug:
                    self.statusInfo = "After SendMessage"

            if self.isDebug:
                if self.LogModule == "STDOUT":
                    print "[DEBUG] End (%s)" % control_file_path
                elif self.LogModule == "MOBIGEN":
                    __LOG__.Trace("[DEBUG] End (%s)" % control_file_path )

            fobj.close()
            self.sock.SendMessage(data)
        else:
            fileList = [control_file_path, data_file]
            for f in fileList :
                fobj = open(f)
                if self.isDebug:
                    if self.LogModule == "STDOUT":
                        print "[DEBUG] OpenFile (%s)" % f
                    elif self.LogModule == "MOBIGEN":
                        __LOG__.Trace("[DEBUG] OpenFile (%s)" % f )
                while True :
                    if self.isDebug:
                        self.statusInfo = "Befor FileRead"
                    buf = fobj.read(self.bufSize)
                    if self.isDebug:
                        self.statusInfo = "After FileRead"

                    if not buf: break #EOF

                    if self.isDebug:
                        self.statusInfo = "Befor SendMessage"
                    self.sock.SendMessage(buf)
                    if self.isDebug:
                        self.statusInfo = "After SendMessage"

                if self.isDebug:
                    if self.LogModule == "STDOUT":
                        print "[DEBUG] End (%s)" % f 
                    elif self.LogModule == "MOBIGEN":
                        __LOG__.Trace("[DEBUG] End (%s)" % f )
                fobj.close()

    def LoadReady(self, table, key, partition):
        self.checkValidity(table, key, partition)

        sendMsg = "IMPORT_READY %s,%s,%s\r\n" % (table, key, partition)
        self.sock.SendMessage(sendMsg)
        return self.sock.Readline()
    
    def To_Disk(self, table, key, partition):
        self.checkValidity(table, key, partition)
        sendMsg = "TO_DISK %s,%s,%s\r\n" % (table, key, partition)
        self.sock.SendMessage(sendMsg)
        return self.sock.Readline()

    def To_Ram(self, table, key, partition, expire_time):
        self.checkValidity(table, key, partition)
        sendMsg = "TO_RAM %s,%s,%s,%s\r\n" % (table, key, partition, expire_time)
        self.sock.SendMessage(sendMsg)
        return self.sock.Readline()

    def GetFile(self, remote_file, local_file) :
        cmd = "GETFILE %s\r\n" % remote_file
        self.sock.SendMessage(cmd)

        retMsg = self.sock.Readline()

        #print "*", retMsg

        filesize = int(retMsg.strip())

        bufferSize = self.bufSize
        remained = filesize

        f = open(local_file+".temp", "w")

        if filesize > 0 :

            data = self.sock.Read( filesize )
            f.write(data)

            #while remained > 0  :
            #    data = self.sock.Read( bufferSize )
            #    remained = remained - len(data)
            #    f.write(data)
    
        f.close()
    
        os.rename(local_file+".temp", local_file)

        resultMsg = self.sock.Readline()
        
        return resultMsg

    def GetInfo(self, param) :
        cmd = "GET_INFO %s\r\n" % param
        self.sock.SendMessage(cmd)
        
        retMsg = self.sock.Readline()

        if "+" == retMsg[0]:
            while True :
                msg = self.sock.Readline()
                if msg[0] == '.' : break
                retMsg += msg
        return retMsg    
        
    def Close(self):
        pass

if __name__ == "__main__" :
    import time
    c = Cursor(None)

    for i in c :
        print i
        time.sleep(1)

# coding: utf-8

import sys, time
from M6_Cursor import Cursor
from Socket import Socket

from M6_Exception import ConnectionFailException

try:
    from Mobigen.Common import Log
    from Mobigen.Common.Log import __LOG__
    Log.Init()
except:
    pass

VERSION = "Python-M6-API-1.1"
LISTENER_PORT = 7050


class Connection(object) :

    """
    - Logmodule
        : STDOUT - stdout
        : MOBIGEN - mobigen log module
    """
    def __init__(self, addr_info, id, password, Direct=False, Debug=False, LogModule='STDOUT', Timeout=0, Database='DEFAULT'):
        object.__init__(self)

        self.addr_info = addr_info.strip().split(":")
        self.id = id
        self.password = password
        self.isDirect = Direct
        self.isDebug = Debug
        self.LogModule = LogModule
        self.timeout = Timeout
        self.Database = Database

        self.cursor_ = None
        self.sock_ = Socket()
        if self.timeout > 0:
            self.sock_.SetTimeout(self.timeout)

        # connect
        self.Connect()

    def Connect(self):
        if self.isDebug:
            debugStartTime = time.time()

        # ip
        ip = self.addr_info[0]

        # port
        if len(self.addr_info) > 1:
            port = self.addr_info[1]
        else:
            port = LISTENER_PORT

        self.__connect(ip, port)

        if self.isDirect :
            (udm_ip, udm_port) = self.nsdConnect()
            self.__connect(udm_ip, udm_port)

        if self.isDebug:
            debugEndTime = time.time()
            if self.LogModule == 'STDOUT':
                print "[DEBUG_TIME] Connect() %f" % (debugEndTime - debugStartTime)
            elif self.LogModule == 'MOBIGEN':
                __LOG__.Trace("[DEBUG_TIME] Connect() %f" % (debugEndTime - debugStartTime))

    def __connect(self, ip, port):
        if not self.sock_ : self.sock_ = Socket()
        if self.timeout > 0:
            self.sock_.SetTimeout(self.timeout)

        # try to connect
        try:
            #if __debug__: print "Trying %s ..." % ":".join(self.addr_info)
            self.sock_.Connect(ip, port)
            #if __debug__: print "Connected to %s." % ":".join(self.addr_info)
        except Exception, e:
            self.close()
            raise ConnectionFailException, "Unable to connect to server.[%s]" % str(e)

        # read welcome message
        (result, msg) = self.sock_.ReadMessage()
        if not result:
            self.close()
            raise ConnectionFailException, "Unable to readMessage. sock"


    def nsdConnect(self):
        self.sock_.SendMessage("GET\r\n")
        (result, msg) = self.sock_.ReadMessage()
        if not result :
            if msg.strip() == "Invalid Command":
                raise ConnectionFailException, "For DIRECT Connection, IRIS NSD PORT is required, but invalid port is given."
            raise ConnectionFailException, msg

        (ip, port) = msg.strip().split(":")

        self.sock_.SendMessage("QUIT\r\n")
        try: self.sock_.Readline() # NSD : OK BYE
        except : pass
        try: self.sock_.close()
        except: pass
        self.sock_ = None
        return (ip, port)

    def Cursor(self) :
        return self.cursor()

    def cursor(self) :
        self.cursor_ = Cursor(self.sock_, Debug=self.isDebug, LogModule=self.LogModule)

        if self.isDirect:
            host = self.sock_.sock.getsockname()[0]
            self.cursor_.SetInfo(self.id, self.password, host, VERSION)
        else:
            self.cursor_.Login(self.id, self.password, VERSION)

        if self.Database != "DEFAULT":
            print self.Database
            self.cursor_.Execute2("use %s;" % self.Database)

        return self.cursor_

    def toPrint(self):
        print "addr_info: ", self.addr_info
        print "id: ", self.id
        print "passwd: ", self.password
        print "cursor: ", self.cursor_

    def commit(self) :
        pass

    def close(self) :
        self.commit()
        if self.cursor_:
            self.cursor_.Close()

        try: self.sock_.SendMessage("QUIT\r\n", timeOut=1)
        except: pass
        try: self.sock_.Readline(timeOut=1)
        except: pass
        try: self.sock_.close()
        except: pass
        self.sock_ = None

def main():

    # listenr
    conn = Connection("58.181.37.135:5050", "id", "passwd")

    # udm
    #conn = Connection("10.0.0.1:5100", "id", "passwd", Direct=True)

    c = conn.Cursor()
    c.SetRecordSep("|^|")

    sql = "show tables"

    c.Execute(sql)

    for a in c:
        print ",".join(a)

    #conn.toPrint()
    conn.close()

def testDirectConnect():
    conn = Connection("58.181.37.135:5000", "test", "test", Direct=True)

    c = conn.Cursor()
    c.SetRecordSep("|^|")

    sql = "show tables"

    c.Execute(sql)

    for a in c:
        print ",".join(a)

    #conn.toPrint()
    conn.close()

def testInvalidPort():
    conn = Connection("58.181.37.135:5050", "test", "test", Direct=True)

    c = conn.Cursor()
    c.SetRecordSep("|^|")

    sql = "show tables"

    c.Execute(sql)

    for a in c:
        print ",".join(a)

    #conn.toPrint()
    conn.close()

def testInvalidPw():
    conn = Connection("58.181.37.135:5050", "test", "tesdt")

    c = conn.Cursor()
    c.SetRecordSep("|^|")

    sql = "show tables"

    c.Execute(sql)

    for a in c:
        print ",".join(a)

    #conn.toPrint()
    conn.close()


if __name__ == "__main__":
    try :
        #main()
        #testDirectConnect()
        #testInvalidPort()
        testInvalidPw()

    except Exception, e:
        print "ERROR :", str(e)

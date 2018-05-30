#!/bin/env python
# coding: utf-8

import socket, struct, errno


class Socket(object) :
    class SocketDisconnectException(Exception) : pass
    class SocketDataSendException(Exception) : pass
    class SocketTimeoutException(Exception) : pass

    def __init__(self) :
        object.__init__(self)
        self.sock = None

        self.remain = 0
        self.tmpList = []
        self.addr = ""
        self.inbuf = ""

        self.timeout = None

    def Connect(self, ip, port) :
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        linger = struct.pack( "ii", 1, 0 )
        self.sock.setsockopt( socket.SOL_SOCKET, socket.SO_LINGER, linger )
        self.sock.connect((ip, int(port)))
        #self.setSock(self.sock)

    def Bind(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind( ("", int(port)) )
        self.sock.listen(10)

        #self.setSock(self.sock)

    def Accept(self):
        (cSock, addr) =  self.sock.accept()
        c = Socket()
        c.setSock(cSock)
        c.addr = addr
        return c

    def setSock(self, sock):
        self.sock = sock

    def SetTimeout(self, time):
        self.timeout = time
        self.sock.settimeout(time)

    def Readline(self, modeBlock=True, timeOut=0) :
        if timeOut > 0: self.sock.settimeout(timeOut)
        else: self.sock.settimeout(self.timeout)

        data = self.readline(modeBlock)

        self.sock.settimeout(self.timeout)
        return data

    def Read(self, size, modeBlock=True, timeOut=0) :
        if timeOut > 0: self.sock.settimeout(timeOut)
        else: self.sock.settimeout(self.timeout)

        data = self.read(size, modeBlock)

        self.sock.settimeout(self.timeout)
        return data

    def SendMessage(self, cmd, timeOut=0) :
        if timeOut > 0: self.sock.settimeout(timeOut)
        else: self.sock.settimeout(self.timeout)

        self.sendMessage(cmd)

        self.sock.settimeout(self.timeout)

    #######################################################
    #
    # 한줄 단위로 Return
    #
    def readline(self, modeBlock=True) :
        #__LOG__.Trace("ReadLine S")
        data = ""
        local_sock  = self.sock
        local_inbuf = self.inbuf

        lf = local_inbuf.find('\n')
        if lf >= 0:
            data = local_inbuf[:lf+1]
            local_inbuf = local_inbuf[lf+1:]
            self.inbuf = local_inbuf
            self.sock  = local_sock
            return data


        while True:
            #__LOG__.Trace("Recv S")
            try : r = local_sock.recv(1024*2000)
            except socket.timeout:
                self.inbuf = local_inbuf
                self.sock  = local_sock
                raise Socket.SocketTimeoutException
            except socket.error, e:
                if e.args[0] == errno.ECONNRESET:
                    self.inbuf = local_inbuf
                    self.sock  = local_sock
                    raise Socket.SocketDisconnectException
            #__LOG__.Trace("Recv E")
            if not r:
                self.inbuf = local_inbuf
                self.sock  = local_sock
                # connection broken
                # disconnect
                raise Socket.SocketDisconnectException
        
            local_inbuf = local_inbuf + r
    
            lf = r.find('\n')
            if lf >= 0:
                lf = local_inbuf.find('\n')
                data = local_inbuf[:lf + 1]
                local_inbuf = local_inbuf[lf + 1:]
                break

            # 함수가 Non-Block Mode 로 동작하는 경우 리턴
            if not modeBlock : break

        self.inbuf = local_inbuf
        self.sock  = local_sock

        return data

    def read(self, size, modeBlock=True) :
        #__LOG__.Watch((size, len(self.inbuf)))

        local_sock    = self.sock
        local_remain  = self.remain
        local_inbuf   = self.inbuf
        local_tmpList = self.tmpList

        local_remain = size

        tmpData = ""
        local_tmpList = []

        if len(local_inbuf) > 0:
            #__LOG__.Watch((self.remain, len(self.inbuf)))
            if local_remain > len(local_inbuf):
                local_remain -= len(local_inbuf)
                local_tmpList.append(local_inbuf)
                local_inbuf = ""
            else :  #  <=
                # remain 을 감소시켜줘야되지 않나???
                tmpData = local_inbuf[:local_remain]
                local_inbuf = local_inbuf[local_remain:]
                self.inbuf = local_inbuf
                return tmpData

        #print dir(self.sock)

        while 1 : 
            tmpData = ''
            try: tmpData = local_sock.recv(local_remain)
            except socket.timeout:
                self.sock    = local_sock
                self.remain  = local_remain
                self.inbuf   = local_inbuf
                self.tmpList = local_tmpList
                raise Socket.SocketTimeoutException
            except socket.error, e:
                if e.args[0] == errno.ECONNRESET:
                    self.sock    = local_sock
                    self.remain  = local_remain
                    self.inbuf   = local_inbuf
                    self.tmpList = local_tmpList
                    raise Socket.SocketDisconnectException
            #__LOG__.Watch((len(tmpData), self.remain))

            if tmpData == "":
                # connection broken
                # disconnect
                self.sock    = local_sock
                self.remain  = local_remain
                self.inbuf   = local_inbuf
                self.tmpList = local_tmpList
                raise Socket.SocketDisconnectException

            local_tmpList.append(tmpData)
            local_remain -= len(tmpData)

            # 정상적인 경우
            if local_remain <= 0: break

        local_remain = 0
        str = ''.join(local_tmpList)
        local_tmpList = []

        self.sock    = local_sock
        self.remain  = local_remain
        self.inbuf   = local_inbuf
        self.tmpList = local_tmpList

        return str

    def ReadMessage(self) :
        line = self.Readline()
        (code, msg) = line.split(" ", 1)

        if   code[0] == "+":
            return (True, msg)
        else:
            return (False, msg)

    def sendMessage(self, cmd) :
        while True:
            n =  self.sock.send(cmd)
            if n == len(cmd):
                break;
            elif n <= 0:
                self.sock.settimeout(None)
                raise Socket.SocketDataSendException

            cmd = cmd[n:]

    def close(self):
        if self.sock:
            #self.sock.shutdown(2)
            self.sock.close()
            self.sock = None

def server():
    s = Socket()
    s.Bind(9999)

    client_sock = s.Accept()

    client_sock.SendMessage("+OK Hello World!!!!\r\n")

    while True:
        msg = client_sock.Readline()
        client_sock.SendMessage("+OK %s" %msg )
        if msg.strip().upper() == "QUIT":
            break

    client_sock.close()
    s.close()


def client():
    s = Socket()
    s.Connect("localhost", 9999)
    print s.ReadMessage()
    s.SendMessage("GET\r\n")
    print s.ReadMessage()
    s.close()


if __name__ == "__main__":
    #client()
    server()

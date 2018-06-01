#!/bin/env python
#!-*- coding:utf-8 -*-

import sys
import signal
import ConfigParser
import time
import datetime
import os

import Mobigen.Common.Log as Log
import API.M6 as M6

G_SHUTDOWN = True

def Shutdown(sigNum = 0, frame = 0) :
    global G_SHUTDOWN
    __LOG__.Trace("Recv Signal (%s)" % sigNum)
    G_SHUTDOWN = False

signal.signal(signal.SIGTERM, Shutdown)  # Sig Terminate : 15
signal.signal(signal.SIGINT, Shutdown)   # Sig Inturrupt : 2
signal.signal(signal.SIGHUP, Shutdown)  # Sig HangUp : 1
signal.signal(signal.SIGPIPE, Shutdown) # Sig Broken Pipe : 13

class IrisLoader() :
    def __init__(self) :

        self.SECTION = sys.argv[1]

        self.GetParser()
        self.SetLog()
        self.GetConfig()

    def GetParser(self) :
        try:
            self.PARSER = ConfigParser.ConfigParser()
            if os.path.exists(sys.argv[2]): self.PARSER.read(sys.argv[2])
            else: self.PARSER = None
        except:
            print 'GetParser Error'
            self.PARSER = None

        if self.PARSER is None:
            print 'GetParser Error \n usage : %s ConfigFile' % ( sys.argv[0] )
            sys.exit()

    def SetLog(self) :

        #default Log
        self.logFilePath = 'Log'
        self.logFileSize = 1000000
        self.logFileCount = 10

        if (self.PARSER != None) :
            if self.PARSER.get('Log','LogFilePath') != '' :
                self.logFilePath = self.PARSER.get('Log','LogFilePath')

            self.logFileSize = self.PARSER.get('Log','LogFileSize')
            self.logFileCount = self.PARSER.get('Log','LogFileCount')

            if not os.path.exists(self.logFilePath) :
                os.makedirs(self.logFilePath)

            LOG_NAME = '%s/%s_%s.log' % (self.logFilePath, os.path.basename(sys.argv[0])[:-3], self.SECTION)
            Log.Init(Log.CRotatingLog(os.path.expanduser(LOG_NAME), int(self.logFileSize), int(self.logFileCount)))
						
    def GetConfig(self) :
        try :
            self.IRIS_IP = self.PARSER.get('IRIS','IRIS_IP')
            self.IRIS_ID = self.PARSER.get('IRIS','IRIS_ID')
            self.IRIS_PWD = self.PARSER.get('IRIS','IRIS_PWD')

            self.CTL_PATH = self.PARSER.get('IRIS', 'CTL_PATH')
            self.TABLE = self.PARSER.get('IRIS', 'TABLE')
            self.FILE_REMOVE = self.PARSER.get('IRIS', 'FILE_REMOVE')
            self.KEY_FILTER = self.PARSER.get('IRIS', 'KEY_FILTER')
            self.TIMEOUT = self.PARSER.getint('IRIS', 'TIMEOUT')
            try : self.SEPARATE = self.PARSER.get('IRIS', 'SEPARATE')
            except : self.SEPARATE = ','

            try : self.STDOUT = self.PARSER.get('IRIS', 'STDOUT') #Y or N
            except : self.STDOUT = 'N'

            #Section 별 셋팅
            try : self.TABLE = self.PARSER.get(self.SECTION, 'TABLE')
            except : pass

            try : self.KEY_FILTER = self.PARSER.get(self.SECTION, 'KEY_FILTER')
            except : pass

            try : self.FILE_REMOVE = self.PARSER.get(self.SECTION, 'FILE_REMOVE')
            except : pass

            try : self.STDOUT = self.PARSER.get(self.SECTION, 'STDOUT') #Y or N
            except : pass

            if self.KEY_FILTER == '' : self.KEY_FILTER = None
            else : self.KEY_FILTER = self.KEY_FILTER.split(',')

            __LOG__.Trace(self.KEY_FILTER)
            self.CONFIG_MOD_TIME = os.path.getmtime(sys.argv[2])


        except :
            __LOG__.Exception()
            sys.exit()

    def run(self) :

        __LOG__.Trace('Start IrisLoaer!!!!!')

        global G_SHUTDOWN

        while G_SHUTDOWN :
            try :

                #time.sleep(1)
                strFilePath = sys.stdin.readline().strip()

                __LOG__.Trace('stdin - %s' % strFilePath)

                if strFilePath[:7] != 'file://' :
                    __LOG__.Trace('stdin Error [%s]' % strFilePath)
                    sys.stderr.write("\n")
                    sys.stderr.flush()
                    continue

                strFilePath = strFilePath[7:]
                __LOG__.Trace(strFilePath)

				#ex -> KEY_PARTITION.dat
				Key = os.path.basename(strFilePath).split('.')[0].split('_')[0]
                Partition = os.path.basename(strFilePath).split('.')[0].split('_')[1]
                CtlPath = self.CTL_PATH

				#키 필터
                if self.KEY_FILTER != None :
                    if not Key in self.KEY_FILTER :
                        #__LOG__.Trace('KeyFilter[%s] / RecvKey[%s]' % (self.KEY_FILTER, Key))
                        sys.stderr.write("\n")
                        sys.stderr.flush()
                        continue

				#파일 존재 확인
                if not os.path.exists(strFilePath) :
                    __LOG__.Trace('Error Path [%s]' % strFilePath)
                    sys.stderr.write("\n")
                    sys.stderr.flush()
                    continue

				#파일 사이즈 확인
                if  os.path.getsize(strFilePath) == 0 :
                    __LOG__.Trace('File Size Error [%s]' % strFilePath)

                    if self.FILE_REMOVE == 'Y' :
                        os.unlink(strFilePath) #파일 삭제함

                    if self.STDOUT == 'Y' :
                        __LOG__.Trace('stdOUT - file://%s-%s.%s\n' % (strFilePath.split('.')[0],Partition,strFilePath.split('.')[1]))
                        sys.stdout.write('file://%s-%s.%s\n' % (strFilePath.split('.')[0],Partition,strFilePath.split('.')[1]))
                        sys.stdout.flush()

                    sys.stderr.write("\n")
                    sys.stderr.flush()
                    continue

                #IRIS 접속
                conn = M6.Connection(self.IRIS_IP,self.IRIS_ID,self.IRIS_PWD, Direct = True)
				c = conn.Cursor()
                c.SetFieldSep(self.SEPARATE)
                c.SetRecordSep('\n')
                c.SetTimeout(self.TIMEOUT) #60초 TimeOut시간 줌

                __LOG__.Trace('%s %s %s %s %s' % (self.TABLE, Key, Partition, CtlPath, strFilePath))

                strResult = c.Load(self.TABLE, Key, Partition, CtlPath, strFilePath)
                if strResult[0:3] == '+OK':
                    __LOG__.Trace(strResult)

                    if self.FILE_REMOVE == 'Y' :
                        os.unlink(strFilePath)

                    if self.STDOUT == 'Y' :
                        __LOG__.Trace('stdOUT - file://%s-%s.%s\n' % (strFilePath.split('.')[0],Partition,strFilePath.split('.')[1]))
                        sys.stdout.write('file://%s-%s.%s\n' % (strFilePath.split('.')[0],Partition,strFilePath.split('.')[1]))
                        sys.stdout.flush()

                else :
                    if len(strResult) > 1000 : strResult = strResult[:1000]
                    __LOG__.Trace(strResult)

                c.Close()
                conn.close()
				
				sys.stderr.write('\n')
                sys.stderr.flush()


            except :
                __LOG__.Exception()

            sys.stderr.write("\n")
            sys.stderr.flush()
            #time.sleep(1)

if __name__ == "__main__" :

    if len(sys.argv) != 3 :
        print '%s Section ConfigPath' % sys.argv[0]
        sys.exit()

    obj = IrisLoader()
    obj.run()

    __LOG__.Trace("PROCESS END...\n")

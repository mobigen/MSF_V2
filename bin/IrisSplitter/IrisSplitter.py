#!/bin/env python
#!-*- coding:utf-8 -*-

import sys
import signal
import ConfigParser
import time
import datetime
import os

import Mobigen.Common.Log as Log

G_SHUTDOWN = True

def Shutdown(sigNum = 0, frame = 0) :
        global G_SHUTDOWN
        __LOG__.Trace("Recv Signal (%s)" % sigNum)
        G_SHUTDOWN = False

signal.signal(signal.SIGTERM, Shutdown)  # Sig Terminate : 15
signal.signal(signal.SIGINT, Shutdown)   # Sig Inturrupt : 2
signal.signal(signal.SIGHUP, Shutdown)  # Sig HangUp : 1
signal.signal(signal.SIGPIPE, Shutdown) # Sig Broken Pipe : 13

class IrisSplitter() :
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
                        #Default 설정
                        self.SAVE_PATH = self.PARSER.get('COMMON', 'SAVE_PATH')
                        self.SAVE_SEPARATE = self.PARSER.get('COMMON', 'SAVE_SEPARATE')
                        self.FILE_SEPARATE = self.PARSER.get('COMMON', 'FILE_SEPARATE')
                        self.STDIN_STRING = self.PARSER.get('COMMON', 'STDIN_STRING')

                        #키 인덱스
                        self.KEY_INDEX = self.PARSER.getint('COMMON', 'KEY_INDEX')
                        try : ksidx = self.PARSER.getint('COMMON', 'KEY_START_INDEX')
                        except : ksidx = None
                        try : keidx = self.PARSER.getint('COMMON', 'KEY_END_INDEX')
                        except : keidx = None

                        self.PARTITION_RANGE = self.PARSER.getint('COMMON', 'PARTITION_RANGE')
                        self.PARTITION_INDEX = self.PARSER.getint('COMMON', 'PARTITION_INDEX')

                        #개별 설정
                        try : self.SAVE_PATH = self.PARSER.get(self.SECTION, 'SAVE_PATH')
                        except : pass
                        try : self.SAVE_SEPARATE = self.PARSER.get(self.SECTION, 'SAVE_SEPARATE')
                        except : pass
                        try : self.FILE_SEPARATE = self.PARSER.get(self.SECTION, 'FILE_SEPARATE')
                        except : pass
                        try : self.STDIN_STRING = self.PARSER.get(self.SECTION, 'STDIN_STRING')
                        except : pass

                        #키 인덱스
                        try : self.KEY_INDEX = self.PARSER.getint(self.SECTION, 'KEY_INDEX')
                        except : pass
                        try : ksidx = self.PARSER.getint(self.SECTION, 'KEY_START_INDEX')
                        except : pass
                        try : keidx = self.PARSER.getint(self.SECTION, 'KEY_END_INDEX')
                        except : pass

                        self.KEY_SLICE = slice(ksidx,keidx)

                        if not os.path.exists(self.SAVE_PATH) :
                                os.makedirs(self.SAVE_PATH)

                except :
                        __LOG__.Exception()
                        sys.exit()

        def run(self) :

                __LOG__.Trace('Start Make Iris Loader File!!')

                while G_SHUTDOWN :
                        try :

                                stdin = sys.stdin.readline()
                                __LOG__.Trace('stdin : %s' % stdin)
                                try :
                                        if stdin[:len(self.STDIN_STRING)] != self.STDIN_STRING :
                                                __LOG__.Trace('Error Stdin Data ==> %s' % stdin)
                                                sys.stderr.write(stdin)
                                                sys.stderr.flush()
                                                continue
                                except :
                                        __LOG__.Exception()
                                        sys.stderr.write(stdin)
                                        sys.stderr.flush()
                                        continue

                                FilePath = stdin[len(self.STDIN_STRING):-1]

                                if not os.path.exists(FilePath) :
                                        __LOG__.Trace('Error File Path Exists [%s]' % FilePath)
                                        sys.stderr.write(stdin)
                                        sys.stderr.flush()
                                        continue

                                diFile = {}
                                with open(FilePath, 'r') as fd :

                                        for line in fd :

                                                row = line[:-1].split(self.FILE_SEPARATE)

                                                Key = row[self.KEY_INDEX][self.KEY_SLICE]
                                                Partition = row[self.PARTITION_INDEX] #YYYYMMDDHHMMSS

                                                #Partition 설정
                                                Partition = Partition.translate(None,' -:/') #-:/ 제거함

                                                if self.PARTITION_RANGE == 1 :
                                                        Partition = Partition[:12] + '00'
                                                elif self.PARTITION_RANGE == 5 :
                                                        Partition[12] = str(int(Partition[12]) - int(Partition[12]) % 5)
                                                elif self.PARTITION_RANGE == 10 :
                                                        Partition = Partition[:11] + '000'
                                                elif self.PARTITION_RANGE == 60 :
                                                        Partition = Partition[:10] + '0000'
                                                elif self.PARTITION_RANGE == 1440 :
                                                        Partition = Partition[:8] + '000000'

                                                #제외 인덱스? - 이건 추후에 적용

                                                FileName = '%s_%s_%s' % (Key, Partition, os.path.basename(FilePath))
                                                SaveFilePath = os.path.join(self.SAVE_PATH,FileName)

                                                try :
                                                        diFile[SaveFilePath].write(self.SAVE_SEPARATE.join(str(v) for v in row) + '\n')
                                                except :
                                                        diFile[SaveFilePath] = open(SaveFilePath, 'w')
                                                        diFile[SaveFilePath].write(self.SAVE_SEPARATE.join(str(v) for v in row) + '\n')

                                        for fp in diFile.keys() :
                                                diFile[fp].close()
                                                __LOG__.Trace('file://%s\n' % diFile[fp].name)
                                                sys.stdout.write('file://%s\n' % diFile[fp].name)
                                                sys.stdout.flush()
                                                diFile[fp] = None
                                                del diFile[fp]

                                        diFile = {}

                                        sys.stderr.write('\n')
                                        sys.stderr.flush()
                        except :
                                __LOG__.Exception()
                                break

if __name__ == "__main__" :

        if len(sys.argv) != 3 :
                print '%s Section ConfigPath' % sys.argv[0]
                sys.exit()

        obj = IrisSplitter()
        obj.run()

        __LOG__.Trace("PROCESS END...\n")

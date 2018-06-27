#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import re
import os
import time
import socket  # socket
import signal
import ConfigParser

import paramiko
import threading
import datetime

#import Mobigen.Common.Log as Log; Log.Init()
import Mobigen.Common.Log as Log

SHUTDOWN = False

class IndxHandler :

        def __init__(self, sRdir, sBase, sRidx) :

                self.sRdir = sRdir      # for default filename
                self.sBase = sBase
                self.sRidx = sRidx

                if not os.path.exists(os.path.dirname(self.sRidx)) :
                        os.makedirs(os.path.dirname(self.sRidx))

        def read(self) :

                try :

                        oIndx = open( self.sRidx, 'r')
                        sName, sLnum = oIndx.readline().strip().split(',')
                        oIndx.close()

                except Exception, ex :

                        sName, sLnum = self.make()

                return ( sName, int(sLnum) )

        def save(self, sName, sLnum) :

                try :

                        oIndx = open( self.sRidx, 'w' )
                        oIndx.write( sName + "," + str(sLnum) + "\n")
                        oIndx.close()

                except Exception, ex :

                        __LOG__.Exception("Oops: %s" % (str(ex)))
                        pass

        def make(self) :

                #self.sBase = self.sBase.replace('%', '%%')
                __LOG__.Trace(self.sBase)
                sTemp = time.strftime( self.sBase ) if  self.sBase.find('%') >= 0 else self.sBase
                sRdnm = os.path.join( self.sRdir, sTemp ); sRnum = "0"
                __LOG__.Trace(sRdnm)

                return ( sRdnm, sRnum )

class SSHTailer :

        def __init__(self, sHost, sPort, sUser, sPass, sRdir, sPatn, sBase, sLdir, sRidx,sSect) :#, sIdir, sInam) :


                self.bLoop = True

                self.sHost = sHost
                self.sPort = sPort
                self.sUser = sUser
                self.sPass = sPass

                self.sRdir = sRdir
                self.sPatn = sPatn
                self.sBase = sBase
                self.sLdir = sLdir
                self.sRidx = sRidx

                self.sSect = sSect

                if not os.path.exists(self.sLdir) :
                        os.makedirs(self.sLdir)

                # for find command
                self.sTdir = os.path.dirname ( os.path.join( sRdir, sPatn ) )
                self.sTnam = os.path.basename( os.path.join( sRdir, sPatn ) )

                self.oIndx = IndxHandler( self.sRdir, self.sBase, self.sRidx )
                self.sName, self.iLine = self.oIndx.read()
                __LOG__.Trace("Read: Indx ( %s, %d )" % ( self.sName, self.iLine ))

                self.hSSH = {}
                self.hSSH["C"]  = [ self.connect(), None, None, None ]
                self.hSSH["T"]  = [ self.connect(), None, None, None ]

                stdin, stdout, stderr = self.hSSH["C"][0].exec_command("uname")
                sdata = ''.join( stdout.readlines() )
                sdata = sdata.replace('\n', '').strip()
                sdata = sdata.upper()

                self.sOsnm = ''
                self.sPpid = ''

                self.encode= ''

                if       "LINUX" in sdata :
                        self.hSSH["C"][1] = 'find %s -maxdepth 1 -name "%s" -print'
                        self.hSSH["T"][1] = 'echo $$; tail -n +%d -f %s'
                        self.encode = 'utf8'
                elif "SUNOS" in sdata :
                        self.hSSH["C"][1] = 'find %s -name "%s" -print'
                        self.hSSH["T"][1] = 'echo $$; tail +%df %s'
                        self.encode = 'cp949'
                else :
                        self.hSSH["C"][1] = 'find %s -name "%s" -print'
                        self.hSSH["T"][1] = 'echo $$; tail -n +%d -f %s'

                self.sOsnm = sdata

        def __del__(self) :

                self.clear()

        def stop(self) :

                self.bLoop = False

                self.clear()

        def clear(self) :

                try :   self.cleanup()
                except : pass

        def check(self) :

                if      not self.isexistname() :

                        sName = self.getnextname()

                        if      not sName :
                                return False

                        self.sName = sName; self.iLine = 1

                self.execute(); return True

        def connect(self) :

                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=self.sHost, port=int(self.sPort), username=self.sUser, password=self.sPass, timeout = 10)

                __LOG__.Trace("Conn: %s/%s %s/%s" % (self.sHost, self.sPort, self.sUser, self.sPass))

                return ssh

        def reconnect(self) :

                self.disconnect()

                self.hSSH["C"][0] = self.connect()
                self.hSSH["T"][0] = self.connect()

                __LOG__.Trace("Reco: %s/%s" % (self.sHost, self.sPort))

        def disconnect(self) :

                try     : self.hSSH["C"][0].close()
                except : pass
                try     : self.hSSH["T"][0].close()
                except : pass

                __LOG__.Trace("Disc: %s/%s" % (self.sHost, self.sPort))

        def getnames(self) :

                Names = []

#               self.hSSH["C"][2] = self.hSSH["C"][1] % ( self.sRdir, self.sPatn )
                self.hSSH["C"][2] = self.hSSH["C"][1] % ( self.sTdir, self.sTnam )


                stdin, stdout, stderr= self.hSSH["C"][0].exec_command( self.hSSH["C"][2] )

                for sName in stdout.readlines() :

                        sName = sName.strip()
                        Names.append( sName )

                Names.sort()

                __LOG__.Trace("Comd: %s" % ( self.hSSH["C"][2] ))
                __LOG__.Trace("Chck: Curr:%s, Last:%s" % ( self.sName, Names[-1:] ))

                return Names

        def execute(self) :

                Sess = self.hSSH["T"][0].get_transport().open_session()
                Sess.settimeout(10)
                self.hSSH["T"][3] = Sess.makefile()

                self.hSSH["T"][2] = self.hSSH["T"][1] % ( self.iLine, self.sName )
                Sess.exec_command( self.hSSH["T"][2] ) #"cd %s; %s" % ( self.sRdir, sComd ) )

                __LOG__.Trace("Comd: %s" % ( self.hSSH["T"][2] ))

        def cleanup(self) :


                sComd = 'ps -ef|grep %s|grep -v grep' %(self.sPpid)

                Sess = self.hSSH["T"][0].get_transport().open_session()
                Temp = Sess.makefile()
                Sess.exec_command( sComd )

                for sPros in Temp.xreadlines() :

                        lWord = sPros.split()
                        if len(lWord) < 2 :

                                continue

                        elif lWord[2] == self.sPpid :

                                sComd = 'kill -9 %s' %(lWord[1])
                                break

                        else :

                                # ps -fu eva | grep 'tail -f SRQA03-omc_log-20150501.log' | grep -v grep | awk '{print $2}'
                                sComd = "kill -9 `ps -fu %s | grep '%s' | grep -v grep | awk '{print $2}'`" % ( self.sUser, self.hSSH["T"][2] )
                                #sComd = "kill -9 %s"%(self.sPpid)

                self.hSSH["T"][0].get_transport().open_session().exec_command( sComd )

                __LOG__.Trace("Comd: %s" % ( sComd ))

        def getnextnames(self) :

                Nexts = []

                for sName in self.getnames() :

                        if  sName > self.sName :

                                Nexts.append( sName )

                return Nexts

        def isexistname(self) :

                for sName in self.getnames() :

                        if  sName == self.sName :
                                return True

                else :
                        return False


        def getnextname(self) :

                Nexts = self.getnextnames()

                if  Nexts : return Nexts.pop(0)
                else      : return None

        def collect(self) :

                iRcnt = 0

                while self.bLoop :

                        data = ''

                        try :

                                #data = self.hSSH["T"][3].readline()
                                #data = self.hSSH["T"][3].readlines()
                                if self.sSect =='PM_ADDNET1' or self.sSect =='PM_ADDNET2':
                                        sBnam = time.strftime("STATUS_%Y%m%d.csv")  #SAVE FILE NAME PATTERN
                                else:
                                        sBnam = self.sName
                                sLdnm = os.path.join( self.sLdir, os.path.basename( sBnam  ) )
                                self.oFile = open( sLdnm, "a" )
                                tmp = self.hSSH["T"][3].readline().strip()

                                if tmp != '' :

                                        self.sPpid = tmp
                                        iRcnt = 0
                                        __LOG__.Watch( self.sPpid )

                                else  :

                                        iRcnt += 1
                                        if iRcnt >= 10 : raise Exception("Get Line Abnormal State.")
                                        else : continue

                                sTemp = ''
                                if self.encode != 'cp949':
                                        sTemp = self.hSSH["T"][3].readline()
                                else:
                                        sTemp = self.hSSH["T"][3].readline().decode('cp949')

                                if not  sTemp.strip() == '' :

                                        self.oFile.write( sTemp ); self.oFile.flush()
                                        yield  sTemp


                                for line in self.hSSH["T"][3].xreadlines() :

                                        self.oFile.write( line ); self.oFile.flush()
                                        yield line

                        except socket.timeout :

                                __LOG__.Trace("timeout!")

                                if  not self.bLoop :

                                        break

                                sNext = self.getnextname()

                                # for simulation
                                if  sNext :

                                        self.cleanup(); time.sleep(10)

                                        self.sName = sNext; self.iLine = 1
                                        self.execute()

                                        continue

                                self.cleanup(); time.sleep(10)
                                #self.sName = self.sName; self.iLine = 1
                                self.reconnect()
                                self.execute()
                                continue

                        except Exception, ex :

                                __LOG__.Exception()
                                sNext = self.getnextname()

                                if  sNext :

                                        self.cleanup(); time.sleep(10)
                                        self.sName = sNext; self.iLine = 1
                                        self.execute()
                                        continue

                                self.cleanup(); time.sleep(10)
                                #self.sName = self.sName; self.iLine = 1
                                self.reconnect()
                                self.execute()

        def fileinfo(self) :

                return ( self.sName, self.iLine )

        def filename(self) :

                return self.sName

        def fileindx(self) :

                return self.iLine

class ProcessManager(threading.Thread) :

        def __init__(self) :

                threading.Thread.__init__(self)
                self.process_dict = dict()
                self.th_list = list()

                self.th_dict = dict()

                self.shutdown = False

        def __del__(self) :

                pass

        def set_process(self, porcess, *args) :

                self.process_dict[porcess] = args

        def start_process(self) :

                for obj in self.process_dict :

                        th = obj(*self.process_dict[obj])
                        __LOG__.Trace("Start - %s"%th.__class__.__name__)
                        th.deamon = True
                        th.start()
                        self.th_list.append(th)

        def close_porcess(self) :


                for th in self.th_list :

                        th.shutdown()

                for th in self.th_list :

                        th.join()

                for i in range(len(self.th_list)) :

                        self.th_list.pop()

        def chk_process(self) :

                for th in self.th_list :

                        if not th.isAlive() :

                                self.close_porcess()
                                self.start_process()


        def stop(self) :

                self.shutdown = True


        def run(self) :

                self.start_process()
                base = ''

                while not self.shutdown :

                        self.chk_process()
                        """
                        curr = time.strftime("%Y%m%d%H%M")
                                        if base == '' :
                                base = curr

                        elif base != curr :


                                Base  = curr
                                self.chk_process()

                        else :

                                time.sleep(1)
                        """
                        time.sleep(1)
                self.close_porcess()

class Worker :

        def __init__(self, sSect, sConf) :

                self.bLoop = True

                self.sSect = sSect
                self.sConf = sConf

                Conf = ConfigParser.SafeConfigParser()
                Conf.read(sConf)

                self.Conf = Conf

                self.sHost = Conf.get( sSect, "HOST" )
                self.sPort = Conf.get( sSect, "PORT" )
                self.sUser = Conf.get( sSect, "USER" )
                self.pwd_list = Conf.get( sSect, "PASS" ).split(',')
                self.sPass = self.pwd_list[0]

                self.sUids = Conf.get( sSect, "UIDS" )
                self.sEndp = Conf.get( sSect, "EPTN" )

                self.sRdir = Conf.get( sSect, "RDIR" )
                self.sPatn = Conf.get( sSect, "PATN" )
                self.sBase = Conf.get( sSect, "BASE" )
                self.sLdir = Conf.get( sSect, "LDIR" )
                self.sRidx = Conf.get( sSect, "RIDX" )

                self.PROC_TYPE = Conf.get( sSect, "PROC_TYPE" ) #F or O or FO(File or StdOut or File+StdOut)
                self.SAVE_PATH = Conf.get( sSect, "SAVE_PATH" ) #PROC_TYPE에 F가 존재하는 경우 파일 저장 위치
                self.SAVE_RANGE = Conf.get( sSect, "SAVE_RANGE" ) #PROC_TYPE에 F가 존재하는 경우 파일 DATE 범위 (D or H or M or S)

                if len(self.SAVE_PATH) != 0 and not os.path.exists(self.SAVE_PATH) :
                        try : os.makedirs(self.SAVE_PATH)
                        except : pass

                # for simulation
                try     : self.sIntv = Conf.get( sSect, "INTV" )
                except : self.sIntv = "1"

                self.oData = None
                self.oSndr = None
                self.oPasr = None
                self.oDict = None

                __LOG__.Trace( "Conf: %s" % ( [ self.sUids, self.sEndp] ))

                signal.signal(signal.SIGTERM, self.sign)
                signal.signal(signal.SIGINT , self.sign)
                try : signal.signal(signal.SIGHUP , self.sign)
                except : pass
                try : signal.signal(signal.SIGPIPE, self.sign)
                except : pass

                def get_pwd():

                        while True:
                                for pwd in self.pwd_list:
                                        yield pwd

                self.pwd_iter = get_pwd()


        # 15:Terminate, 2:Interrupt, 1:Hangup, 13:BrokenPipe
        def sign(self, iNum=0, iFrm=0) :

                __LOG__.Trace("Sign: %d" % (iNum))

                self.bLoop = False

                if      self.oData :

                        self.oData.stop()


        def work(self) :

                __LOG__.Trace("Work: strt")

                sBase = time.strftime("%Y%m%d%H%M")

                while self.bLoop :

                        # check dictionary
                        try :
                                self.oData = SSHTailer( self.sHost, self.sPort, self.sUser, self.sPass, self.sRdir, self.sPatn, self.sBase, self.sLdir, self.sRidx,self.sSect)
                                break
                        except paramiko.ssh_exception.AuthenticationException:          self.sPass = next(self.pwd_iter)
                        except :
                                __LOG__.Exception()
                                try : self.oData.stop()
                                except : pass

                                __LOG__.Exception()
                                time.sleep(60)

                while self.bLoop :

                        try :

                                while self.bLoop :

                                        if      self.oData.check() :

                                                break

                                        __LOG__.Trace("None: not found '%s'" % ( self.oData.filename() ))

                                        time.sleep(10)

                        except Exception :

                                __LOG__.Exception()

                                self.oData.stop()
                                time.sleep(1)
                                try : self.oData = SSHTailer( self.sHost, self.sPort, self.sUser, self.sPass, self.sRdir, self.sPatn, self.sBase, self.sLdir, self.sRidx,self.sSect)
                                except paramiko.ssh_exception.AuthenticationException:          self.sPass = next(self.pwd_iter)
                                except : self.oData.stop(); __LOG__.Exception(); time.sleep(10)

                        while self.bLoop :

                                try :

                                        oLine = self.oData.collect() # taiㅣ 수집 데이터
                                        if      oLine  :
                                                for sline in oLine :
                                                        __LOG__.Trace("SLINE : %s" % sline)

                                                        if not self.bLoop : break
                                                        self.oData.iLine += 1

                                                        if sline == '' : time.sleep(0); continue

                                                        #sline = re.sub('\r|\x8c|\x00', '', sline)
                                                        sline = re.sub('\r', '', sline)

                                                        if sline :

                                                                if sline[-1] != '\n' : sline += '\n'

                                                                #StdOut 할지 파일 저장할지 여기서 처리
                                                                if self.PROC_TYPE.find('O') >= 0 :
                                                                        __LOG__.Trace('data://%s' % sline)
                                                                        sys.stdout.write('data://%s' % sline)
                                                                        sys.stdout.flush()

                                                                if self.PROC_TYPE.find('F') >= 0 :

                                                                        FileName = ''

                                                                        if self.SAVE_RANGE == 'D' : FileName = '%s_%s.dat' % (self.sSect, datetime.datetime.now().strftime('%Y%m%d') + '000000')
                                                                        elif self.SAVE_RANGE == 'H' : FileName = '%s_%s.dat' % (self.sSect, datetime.datetime.now().strftime('%Y%m%d%H') + '0000')
                                                                        elif self.SAVE_RANGE == 'M' : FileName = '%s_%s.dat' % (self.sSect, datetime.datetime.now().strftime('%Y%m%d%H%M') + '00')
                                                                        elif self.SAVE_RANGE == 'S' : FileName = '%s_%s.dat' % (self.sSect, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))

                                                                        if len(FileName) :
                                                                                with open(os.path.join(self.SAVE_PATH, FileName), 'a') as fd :
                                                                                        fd.write(sline)

                                                                #index 저장
                                                                self.oData.oIndx.save( self.oData.sName, self.oData.iLine )
                                                                __LOG__.Trace("Save: Indx ( %s, %d )" % ( self.oData.fileinfo() ))

                                                self.oData.oIndx.save( self.oData.sName, self.oData.iLine )
                                                __LOG__.Trace("Save: Indx ( %s, %d )" % ( self.oData.fileinfo() ))

                                        time.sleep(0)

                                except Exception, ex :

                                        __LOG__.Exception()
                                        try: self.oData = SSHTailer( self.sHost, self.sPort, self.sUser, self.sPass, self.sRdir, self.sPatn, self.sBase, self.sLdir, self.sRidx,self.sSect)
                                        except paramiko.ssh_exception.AuthenticationException:          self.sPass = next(self.pwd_iter)
                                        time.sleep(1)

                __LOG__.Trace("Work: stop")


def main() :

        if  len(sys.argv) < 3 :
                sys.stderr.write("Usage: %s SECTION CONFIG\n" % (sys.argv[0]))
                sys.stderr.flush()
                sys.exit()

        sSect = sys.argv[1]
        sConf = sys.argv[2]

        Conf = ConfigParser.SafeConfigParser()
        Conf.read(sConf)

        sLogd = os.path.expanduser(Conf.get('COMMON', 'LOG'))
        sLogm = os.path.splitext(os.path.basename(sys.argv[0]))[0] + "." + sSect + ".log"
        sLogs = os.path.join(sLogd, sLogm)

        if not '-d' in sys.argv :
                Log.Init(Log.CRotatingLog(sLogs, 30000000, 10))
        else : Log.Init()

        __LOG__.Trace("process strt: ( pid:%d ) >>>" % (os.getpid()))

        try :

                oWork = Worker(sSect, sConf)
                oWork.work()

        except Exception, ex :

                __LOG__.Exception()

        time.sleep(5)

        __LOG__.Trace("process stop: ( pid:%d ) <<<" % (os.getpid()))

if __name__ == '__main__' :

        main()

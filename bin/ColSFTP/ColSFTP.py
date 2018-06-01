#!/usr/env python
#coding:utf8

import stat
import re
import fnmatch
import signal
import sys
import os
import ConfigParser
import time
import datetime
import pdb
import getopt

import paramiko
import Mobigen.Common.Log as Log

SHUTDOWN = False

def usage():
        print >> sys.stderr,"""usage : python [file][SECTION][conffile] [--help][--stime|--etime] (year/month/day/hour/minute)
        exam : python ColSftp.py SFTPCONF ColSftp.conf --stime 201504240600 --etime 201504270600
        exam : python ColSftp.py SFTPCONF ColSftp.conf --stime 201504240600
        exam : python ColSftp.py SFTPCONF ColSftp.conf

        stime = start time
        etime = end time
        """

def signalShutdownHandler(sigNum,handler):
        global SHUTDOWN
        SHUTDOWN = True
        sys.stderr.write('Catch Signal : %s\n\n' % sigNum)
        sys.stderr.flush()

signal.signal(signal.SIGTERM, signalShutdownHandler) #sigNum 15 : Terminate
signal.signal(signal.SIGINT, signalShutdownHandler)  # sigNum  2 : Interrupt

class FileNotFountException(Exception) : pass

class ColSftp(object):
        def __init__(self,options,args):
                self.options = options
                self.args = args
                self.starttime = 0
                self.endtime = 0
                self.optionparsing()

                try:
                        #Config 파일 불러들임.
                        self.config = ConfigParser.ConfigParser()
                        self.config.read(sys.argv[2])

                        #log설정
                        module = os.path.basename(sys.argv[0])
                        section = sys.argv[1]
                        logpath = self.config.get('Log','LOG_PATH')
                        logsize = self.config.get('Log','LOG_SIZE')
                        logcount = self.config.get('Log','LOG_COUNT')
                        logname = os.path.expanduser('%s/%s_%s.log' % (logpath, module,section))
                        Log.Init(Log.CRotatingLog(logname,logsize ,logcount))
                        #Log.Init()
                except:
                        __LOG__.Exception()
                        os._exit(1)

                try :
                        #ssh connection
                        self.ip = self.config.get(section,'ftp_ip')
                        self.remote_host = self.config.get(section,'ftp_id')
                        self.remote_password1 = self.config.get(section,'ftp_pwd1')
                        self.remote_password2 = self.config.get(section,'ftp_pwd2')
                        self.remote_dir = self.config.get(section,'REMOTE_DIR')
                        self.remote_patt = self.config.get(section,'REMOTE_PATT')
                        self.pathsidx = self.config.get(section,'PATHSIDX') #로컬의 저장하고자 하는 파일위치를 원격지의 패스에서 일부 가져다 씀 시작(basename 제외)
                        self.patheidx = self.config.get(section,'PATHEIDX') #로컬의 저장하고자 하는 파일위치를 원격지의 패스에서 일부 가져다 씀 끝
                except:
                        __LOG__.Exception()
                        os._exit(1)
                try : self.port = self.config.get(section, 'ftp_port')
                except : self.port = 22

                try : self.header_info = self.config.get(section,'HEADER_INFO')
                except : self.header_info = ''

                try : self.sleep_time = self.config.get(section,'SLEEP_TIME')
                except : self.sleep_time = 5

                try : self.local_dir = self.config.get(section,'LOCAL_DIR')
                except : self.local_dir = os.getcwd()

                try : self.index_path = self.config.get(section, 'INDEX_PATH')
                except : self.index_path = os.getcwd()

                try : self.index_name = self.config.get(section, 'INDEX_NAME')
                except : self.index_name = sys.argv[0]+'_'+section

		try : os.makedirs(self.local_dir)
		except : pass
	
		try : os.makedirs(self.index_path)
		except : pass

                self.RUN_TIME = datetime.datetime.now()
                self.run()

        def optionparsing(self):
                try:
                        for op,p in self.options:
                                if op in ('-h','--help'):
                                        usage()
                                        os._exit(1)
                                elif op in ('-s','--stime'):
                                        self.starttime = time.mktime(datetime.datetime.strptime(p,"%Y%m%d%H%M").timetuple())
                                elif op in ('-e','--etime'):
                                        self.endtime = time.mktime(datetime.datetime.strptime(p,"%Y%m%d%H%M").timetuple())
                except:
                        __LOG__.Exception()

        def connectSFTP(self):
                try:
                        transport = paramiko.Transport((self.ip, int(self.port)))
                        transport.connect(username=self.remote_host, password=self.remote_password1)
                        sftp = paramiko.SFTPClient.from_transport(transport)

                        __LOG__.Trace('SFTP Connected Success!!')
                        return sftp, transport
                except:
                        __LOG__.Exception()
                        try :
                                transport = paramiko.Transport((self.ip, int(self.port)))
                                transport.connect(username=self.remote_host, password=self.remote_password2)
                                sftp = paramiko.SFTPClient.from_transport(transport)
                                return sftp, transport
                        except :
                                __LOG__.Exception()
                                os._exit(1)

        def get_remote_filenames(self, sftp_connector):
                #pdb.set_trace()
                fnames=list()
                crash_check = list()

                try :
                        self.remote_date = os.path.join( self.remote_dir,time.strftime ( self.remote_dir, time.localtime(time.time()-30) ) )
                        __LOG__.Trace(self.remote_date)
                        fnames = sftp_connector.listdir(self.remote_date)
                        crash_check = sftp_connector.listdir(self.remote_date)

                        if fnames != crash_check :
                                __LOG__.Trace("No Matching File :: Crash!!")
                                return []

                        fnames.sort(key = lambda x: (sftp_connector.stat(os.path.join(self.remote_date,x)).st_mtime, 0))

                except :
                        #sorting시 잘못된 파일이 있으면 뜨는 에러임.
                        __LOG__.Trace("No Such files!!")
                        return []

                #start and end option check - none of both
                if int(self.starttime) == 0 and int(self.endtime) == 0 :
                        return fnames

                with_list = list()
                for fname in fnames:
                        try :
                                file_mktime = sftp_connector.stat(os.path.join(self.remote_date,fname)).st_mtime

                                #starttime only
                                if int(self.endtime)==0 and int(self.starttime) < file_mktime :
                                        return fnames[fnames.index(fname):]

                                #endtime only
                                if int(self.starttime)==0 and int(self.endtime) < file_mktime :
                                        return fnames[:fnames.index(fname)]

                                #starttime and endtime
                                if int(self.starttime) < file_mktime and int(self.endtime) > file_mktime :
                                        with_list.append(fname)
                                        if int(self.endtime) <= file_mktime :
                                                return with_list
                        except :
                                __LOG__.Exception()
                                return []
                return with_list

        def get_new_filenames(self, sftp_connector, curr_time) :

                #get sorted filelist
                fnames = self.get_remote_filenames(sftp_connector)
                #find index
                for fname in fnames :
                        try :
                                #compare index : sort by time
                                if int(curr_time) < sftp_connector.stat(os.path.join(self.remote_date,fname)).st_mtime :
                                        return fnames[fnames.index(fname):]
                        except :
                                __LOG__.Trace("No New File!")
                                return []
                return []

        def load_index(self):

                try:
                        f = open(os.path.join(self.index_path,self.index_name),'r')
                        index_info = f.readline()
                        return index_info
                except:
                        __LOG__.Exception()
                        return []

        def dump_index(self,file_name,file_time,file_size):
                try:
                        f = open(os.path.join(self.index_path,self.index_name),'w')
                        f.write(file_name+'|^|'+str(file_time)+'|^|'+str(file_size)+'\n')
                        __LOG__.Trace("Dump Index : %s"%(file_name+'|^|'+str(file_time)+'|^|'+str(file_size)))
                        f.close()
                except:
                        __LOG__.Exception()

        def fileTransport(self, sftp_connector, fname):
                try:
                        file_name = os.path.basename(fname)
                        _from = os.path.join(fname).strip()

                        __LOG__.Trace(fname)
                        #년/월/일/시
                        #SavePath = '%s/%s/%s/%s/%s' % (self.local_dir,file_name[-12:-8],file_name[-8:-6],file_name[-6:-4],file_name[-4:-2])
                        #if self.pathsidx == self.patheidx :
                        #       SavePath = os.path.join(self.local_dir, '/'.join(str(v) for v in [os.path.dirname(_from).split('/')[int(self.pathsidx)]]))
                        #else :
                        #       SavePath = os.path.join(self.local_dir, '/'.join(str(v) for v in os.path.dirname(_from).split('/')[int(self.pathsidx):int(self.patheidx)]))

                        SavePath = os.path.join(os.path.join(self.local_dir,  '/'.join(str(v) for v in os.path.dirname(_from).split('/')[int(self.pathsidx):int(self.patheidx)])) , file_name.split('.')[1][:10])

                        __LOG__.Trace(SavePath)
			
                        if not os.path.exists(SavePath):
                                os.makedirs(SavePath)

                        _to = os.path.join(SavePath, file_name+'.tmp').strip()
                        sftp_connector.get(_from,_to)
                        os.rename(os.path.join(SavePath, file_name+'.tmp'),os.path.join(SavePath,file_name))

                        #__LOG__.Trace("Std out : %s " % os.path.join('%s' % os.path.join(self.local_dir, file_name)))
                        #sys.stdout.write(os.path.join('file://%s\n' % os.path.join(self.local_dir, file_name)))
                        str_out = os.path.join('file://%s\n' % os.path.join(SavePath,file_name))
                        __LOG__.Trace("Std out : %s " % str_out)
                        sys.stdout.write(str_out)
                        sys.stdout.flush()
                        return True
                except:
                        __LOG__.Exception()
                        #if not os.path.exists(self.local_dir):
                        #       __LOG__.Trace("automatically make local dir: %s" % self.local_dir)
                        #       os.makedirs(self.local_dir)
                        try :
                                if not sftp_connector.stat(os.path.join(self.remote_date,fname)):
                                        __LOG__.Trace("no such file : %s" % fname)
                        except :
                                pass
                                return False
                        return False

        def run(self):

                try :
                        curr_info = self.load_index().split('|^|')
                        curr_file = curr_info[0].strip()
                        curr_time = curr_info[1].strip()
                        try : curr_size = int(curr_info[2].strip())
                        except : curr_size = 0
                except :
                        curr_file = None
                        curr_time = None
                        curr_size = 0
                        __LOG__.Trace("No Have Index")
                        pass

                index_write_list = list()

                while True:
                        __LOG__.Trace("================================ while start =====================================")
                        if SHUTDOWN:
                                __LOG__.Trace("SHUTDOWN : %s" %SHUTDOWN)
                                break

                        sftp, transport = self.connectSFTP()

                        curr_file_list = search(sftp, self.remote_dir, self.remote_patt,curr_time,curr_size)
                        #break
                        curr_file_list.sort()

                        #for i in curr_file_list :
                        #       __LOG__.Trace(i)

                        #sftp.close()
                        #transport.close()

                        #break

                        #size can be changed when vi is updated!
                        #no index = first execute
                        #if curr_file == None :
                        #       curr_file_list = self.get_remote_filenames(sftp)
                        #exist index = not first execute
                        #else :
                        #       curr_file_list = self.get_new_filenames(sftp, curr_time)

                        __LOG__.Trace("Be down Number of files : %s " % len(curr_file_list))

                        #file transport
                        error_flag = True
                        for fname in curr_file_list :
                                if SHUTDOWN :
                                        __LOG__.Trace("SHUTDOWN : %s" % SHUTDOWN)
                                        break

                                #if not fnmatch.fnmatch(fname, self.remote_patt) :
                                #       continue

                                error_flag = self.fileTransport(sftp,fname)
                                if not error_flag :
                                        break

                                curr_file = fname
                                try :
                                        curr_time = sftp.stat(fname).st_mtime
                                        curr_size = sftp.stat(fname).st_size
                                except : __LOG__.Trace("No Such File!")

                        if error_flag and curr_file != None and len(curr_file_list) > 0 :
                                self.dump_index(curr_file, curr_time, curr_size)

                        sftp.close()
                        transport.close()

                        __LOG__.Trace("============================= while end sleep %s =============================" % int(self.sleep_time))
                        time.sleep(int(self.sleep_time))

                self.dump_index(curr_file, curr_time, curr_size)

def find_dir(obj, current_dir, dir_list) :
        __LOG__.Trace(dir_list)
        if len(dir_list) == 0 :
                yield current_dir
        else :
                try :
                        for dir in obj.listdir(current_dir + '/') :
                                if fnmatch.fnmatch(os.path.basename(dir), dir_list[0]) :
                                        for file_name in find_dir(obj, os.path.join(current_dir, dir), dir_list[1:]) :
                                                __LOG__.Trace(file_name)
                                                yield file_name
                except : yield None

def get_file_list(sftp_obj, path, patt) :
        dir_list = filter(None, re.split('/+', os.path.normpath(os.path.join(path, patt))))
        return [ p for p in find_dir(sftp_obj, '/', dir_list) if p ]

def search(sftp_obj, path, patt,curr_time, curr_size) :
        try :
                li = []
                #p = re.compile(patt)
		
		__LOG__.Trace(path)
                filenames = sftp_obj.listdir(path)
                for filename in filenames:
                        full_filename = os.path.join(path, filename)
                        #if os.path.isdir(full_filename):
                        lstatout = str(sftp_obj.lstat(full_filename)).split()[0]
                        if 'd' in lstatout:
                                li += search(sftp_obj, full_filename, patt,curr_time, curr_size)
                        else:
                                #if p.match(filename) :a
				if filename.find(patt) > 0 : 
                                        if curr_time == None or int(curr_time) < sftp_obj.stat(full_filename).st_mtime :
                                                #__LOG__.Trace('%s/%s' % (full_filename, sftp_obj.stat(full_filename).st_mtime))
                                                li.append(full_filename)
                                        elif int(curr_time) == sftp_obj.stat(full_filename).st_mtime and sftp_obj.stat(full_filename).st_size != curr_size :
                                                li.append(full_filename)
        except :
                __LOG__.Exception()

        return li
if __name__=='__main__':
        try:
                if len(sys.argv) < 3 or len(sys.argv) > 7:
                        usage()
                        os._exit(1)

                options, args = getopt.getopt(sys.argv[3:],"s:e:",["stime=","etime=","help"])
                es = ColSftp(options, args)
                es.setDaemon(True)
                es.start()

                while G_SHUTDOWN :
                        if not es or not es.isAlive() :
                                es = ColSftp(options, args)
                                es.setDaemon(True)
                                es.start()

                        #30분동안 동작하지 않았다면?????
                        if es.RUN_TIME < datetime.datetime.now() - datetime.timedelta(minutes = 30) :
                                __LOG__.Trace('Process Hangs......ReStart')
                                es = Collector_FTP()
                                es.setdaemon(True)
                                es.start()

                        time.sleep(60)


        except:
                usage()
                __LOG__.Exception()


#!/usr/env python
#coding:utf8

import stat
import signal
import sys
import os
import ConfigParser
import time
import datetime as dt
import getopt

import paramiko
import Mobigen.Common.Log as Log

Log.Init()

SHUTDOWN = False

def usage():
    print >> sys.stderr,"""usage : python [File] [Section] [Config path] [--help] [--stime|--etime] (year/month/day/hour/minute)
    exam : python SFTPCollector.py SFTPCONF SFTPCollector.conf --stime 201504240600 --etime 201504270600
    exam : python SFTPCollector.py SFTPCONF SFTPCollector.conf --stime 201504240600
    exam : python SFTPCollector.py SFTPCONF SFTPCollector.conf

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


class SFTPCollector(object):
    def __init__(self, section, conf_path, options, args):
        self.options = options
        self.args = args
        self.starttime = 0
        self.endtime = 0
        self.port = 22
        self.sleep_time = 5
        self.local_dir = os.getcwd()
        self.index_path = os.getcwd()
        self.index_name = sys.argv[0] + '_' + section
        self.optionparsing()

        try:
            #Config 파일 불러들임.
            self.config = ConfigParser.ConfigParser()
            self.config.read(conf_path)

            #log설정
            module = os.path.basename(sys.argv[0])
            logpath = self.config.get('Log','LOG_PATH')
            logsize = self.config.get('Log','LOG_SIZE')
            logcount = self.config.get('Log','LOG_COUNT')
            logname = os.path.expanduser('%s/%s_%s.log' % (logpath, module, section))
            Log.Init(Log.CRotatingLog(logname, logsize, logcount))
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
            self.pathsidx = self.config.getint(section,'PATHSIDX') #로컬의 저장하고자 하는 파일위치를 원격지의 패스에서 일부 가져다 씀 시작(basename 제외)
            self.patheidx = self.config.getint(section,'PATHEIDX') #로컬의 저장하고자 하는 파일위치를 원격지의 패스에서 일부 가져다 씀 끝
        except:
            __LOG__.Exception()
            os._exit(1)

        if self.config.has_option(section, 'ftp_port'):
            self.port = self.config.getint(section, 'ftp_port')
        if self.config.has_option(section, 'SLEEP_TIME'):
            self.sleep_time = self.config.getint(section, 'SLEEP_TIME')
        if self.config.has_option(section, 'LOCAL_DIR'):
            self.local_dir = self.config.get(section, 'LOCAL_DIR')
        if self.config.has_option(section, 'INDEX_PATH'):
            self.index_path = self.config.get(section, 'INDEX_PATH')
        if self.config.has_option(section, 'INDEX_NAME'):
            self.index_name = self.config.get(section, 'INDEX_NAME')

        if not os.path.exists(self.local_dir):
            os.makedirs(self.local_dir)
        if not os.path.exists(self.index_path):
            os.makedirs(self.index_path)

        self.RUN_TIME = dt.datetime.now()
        self.run()

    def optionparsing(self):
        try:
            for op, p in self.options:
                time_tuple = dt.datetime.strptime(p,"%Y%m%d%H%M").timetuple()
                if op in ('-h','--help'):
                    usage()
                    os._exit(1)
                elif op in ('-s','--stime'):
                    self.starttime = time.mktime(time_tuple)
                elif op in ('-e','--etime'):
                    self.endtime = time.mktime(time_tuple)
        except:
            __LOG__.Exception()

    def connectSFTP(self, n=2):
        # 설정된 두개의 비밀번호를 사용하여 접속시도
        attempts = 0
        pwd = self.remote_password1
        while attempts < n:
            try:
                transport = paramiko.Transport((self.ip, int(self.port)))
                transport.connect(username=self.remote_host,
                                  password=pwd)
                sftp = paramiko.SFTPClient.from_transport(transport)
                __LOG__.Trace('SFTP Connected Success!!')
                break
            except:
                attempts += 1
                pwd = self.remote_password2
                __LOG__.Exception()
        if attempts == n:
            os._exit(1)
        return sftp, transport

    def load_index(self):
        try:
            f = open(os.path.join(self.index_path,self.index_name),'r')
            index_info = f.readline()
            f.close()
            return index_info
        except:
            __LOG__.Exception()
            return False

    def dump_index(self,file_name,file_time,file_size):
        try:
            content = file_name + '|^|' + str(file_time) + '|^|' + str(file_size)
            with open(os.path.join(self.index_path, self.index_name), 'w') as f:
                f.write(content + '\n')
            __LOG__.Trace("Dump Index : %s" % content)
        except:
            __LOG__.Exception()

    def fileTransport(self, sftp_connector, fname):
        try:
            file_name = os.path.basename(fname)
            _from = os.path.join(fname).strip()
            __LOG__.Trace(fname)

            included_path = '/'.join(str(v) for v in
                    os.path.dirname(_from).split('/')[self.pathsidx:self.patheidx])

            SavePath = os.path.join(os.path.join(self.local_dir, included_path),
                                    file_name.split('.')[1][:10])
            __LOG__.Trace(SavePath)

            if not os.path.exists(SavePath):
                os.makedirs(SavePath)

            _to = os.path.join(SavePath, file_name+'.tmp').strip()
            sftp_connector.get(_from, _to)
            os.rename(os.path.join(SavePath, file_name+'.tmp'),
                      os.path.join(SavePath, file_name))

            str_out = os.path.join('file://%s\n' % os.path.join(SavePath, file_name))
            __LOG__.Trace("Std out : %s " % str_out)
            sys.stdout.write(str_out)
            sys.stdout.flush()
            return True
        except:
            __LOG__.Exception()
            try:
                if not sftp_connector.stat(os.path.join(self.remote_date,fname)):
                    __LOG__.Trace("no such file : %s" % fname)
            except:
                pass
            return False

    def run(self):
        idx = self.load_index()
        curr_file, curr_time, curr_size = None, None, 0
        if idx:
            curr_info = idx.split('|^|')
            if len(curr_info) == 3:
                curr_file, curr_time, curr_size = curr_info
            elif len(curr_info) == 2:
                curr_file, curr_time = curr_info
            else:
                __LOG__.Trace("Unknown index logic")
        else:
            __LOG__.Trace("Have no index")
            pass

        index_write_list = list()

        while True:
            __LOG__.Trace("========================While start ========================")
            if SHUTDOWN:
                __LOG__.Trace("SHUTDOWN : %s" %SHUTDOWN)
                break

            sftp, transport = self.connectSFTP()

            curr_file_list = search(sftp, self.remote_dir,
                                    self.remote_patt, curr_time, curr_size)
            curr_file_list.sort()
            __LOG__.Trace("Be down Number of files : %s" % len(curr_file_list))

            #file transport
            error_flag = True
            for curr_file in curr_file_list:
                if SHUTDOWN:
                    __LOG__.Trace("SHUTDOWN : %s" % SHUTDOWN)
                    break

                error_flag = self.fileTransport(sftp, curr_file)
                if not error_flag:
                    break

                try:
                    curr_time = sftp.stat(curr_file).st_mtime
                    curr_size = sftp.stat(curr_file).st_size
                except:
                    __LOG__.Trace("No Such File!")

            if error_flag and curr_file and len(curr_file_list):
                self.dump_index(curr_file, curr_time, curr_size)

            sftp.close()
            transport.close()

            __LOG__.Trace("=================== while end sleep %d ====================" \
                    % self.sleep_time)
            time.sleep(self.sleep_time)

        self.dump_index(curr_file, curr_time, curr_size)

def search(sftp_obj, path, patt, curr_time, curr_size):
    # index에 시간이 표시되있지 않으면 전부 추가
    # sftp연결된 곳의 파일의 수정시간이 index에 표기된 시간보다 크면 추가
    # index에 표기된 시간이랑 같고 index에 있는 사이즈랑 다르면 추가
    try:
        li = []
        __LOG__.Trace(path)
        filenames = sftp_obj.listdir(path)
        for filename in filenames:
            full_filename = os.path.join(path, filename)
            lstatout = str(sftp_obj.lstat(full_filename)).split()[0]
            if 'd' in lstatout:
                li += search(sftp_obj, full_filename, patt, curr_time, curr_size)
            else:
                if filename.find(patt) > 0:
                    if curr_time == None or \
                        int(curr_time) < sftp_obj.stat(full_filename).st_mtime:
                        li.append(full_filename)
                    elif int(curr_time) == sftp_obj.stat(full_filename).st_mtime and \
                        sftp_obj.stat(full_filename).st_size != curr_size:
                        li.append(full_filename)
    except:
        __LOG__.Exception()

    return li

if __name__=='__main__':
    try:
        if len(sys.argv) < 3 or len(sys.argv) > 7:
            usage()
            os._exit(1)

        options, args = getopt.getopt(sys.argv[3:], "s:e:", ["stime=", "etime=", "help"])
        es = SFTPCollector(sys.argv[1], sys.argv[2], options, args)
        es.setDaemon(True)
        es.start()

        while G_SHUTDOWN :
            if not es or not es.isAlive() :
                es = SFTPCollector(options, args)
                es.setDaemon(True)
                es.start()

            #30분동안 동작하지 않았다면?????
            if es.RUN_TIME < datetime.datetime.now() - datetime.timedelta(minutes = 30) :
                __LOG__.Trace('Process Hangs......ReStart')
                es = Collector_FTP()
                es.setdaemon(True)
                es.start()

            time.sleep(60)
    except Exception, ex:
        usage()
        __LOG__.Exception()


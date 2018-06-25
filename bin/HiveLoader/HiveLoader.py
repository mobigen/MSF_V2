# -*- coding: utf-8 -*-
import signal
import sys
import os
import datetime as dt
import ConfigParser

from pyhive import hive

import Mobigen.Common.Log as Log

G_SHUTDOWN = True

def shutdown(sigNum=0, frame=0):
    global G_SHUTDOWN
    __LOG__.Trace("Recv Signal (%s)" % sigNum)
    G_SHUTDOWN = False

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGHUP, shutdown)
signal.signal(signal.SIGPIPE, shutdown)

class HIVEController:
    def __init__(self):
        self.module = sys.argv[0]
        self.section = sys.argv[1]
        self.cfg = ConfigParser.ConfigParser()
        self.cfg.read(sys.argv[2])
        self.connRetry = 3

        self.set_logger()
        self.set_config()

    def set_config(self):
        try:
            print "HI"
            self.conn_info = {
                "host": self.cfg.get("HIVE", "IP"),
                "port": self.cfg.get("HIVE", "PORT")
            }
            print self.conn_info
            self.cursor = hive.connect(**self.conn_info).cursor()
            self.table = self.cfg.get(self.section, "Table")
            print self.table
            self.partitions = self.cfg.get(self.section, "Partitions").split(',')
            print self.partitions
        except Exception, ex:
            __LOG__.Trace("Exception: %s" % ex)
            sys.exit()

    def set_logger(self):
        self.logFilePath = 'Log'
        self.logFileSize = 1000000
        self.logFileCount = 10

        if (self.cfg != None):
            if self.cfg.has_option('Log', 'LogFilePath'):
                self.logFilePath = self.cfg.get('Log', 'LogFilePath')
            if self.cfg.has_option('Log', 'LogFileSize'):
                self.logFileSize = self.cfg.getint('Log', 'LogFileSize')
            if self.cfg.has_option('Log', 'LogFileCount'):
                self.logFileCount = self.cfg.getint('Log', 'LogFileCount')

            if not os.path.exists(self.logFilePath):
                os.makedirs(self.logFilePath)

            LOG_NAME = '%s/%s.log' % (self.logFilePath,
                                      os.path.basename(self.module)[:-3])
            Log.Init(Log.CRotatingLog(os.path.expanduser(LOG_NAME),
                                      self.logFileSize,
                                      self.logFileCount))

    def load_data(self, path, partition_val):
        """
            Loads the file with the specified path in STDIN to Hive

            Parameters
            ----------
            path: <string>
                path specified in STDIN
            partition_val: <list>
                partition specified in STDIN

            Note
            ----
            The query to execute is carved in this code.
            Fix it a little as needed.
        """
        partition_lst = []
        for x in range(len(self.partitions)):
            partition_lst.append("%s='%s'" % (self.partitions[x], partition_val[x]))
        partition_str = ','.join(lst)

        query = "LOAD DATA INPATH '%s' \
                 OVERWRITE INTO TABLE %s \
                 PARTITION(%s)" % (path, self.table, partition_str)
        __LOG__.Trace(query)
        try:
            self.cursor = hive.connect(**self.conn_info).cursor()
            self.cursor.execute(query)
        except Exception, ex:
            __LOG__.Trace(ex)

    def run(self):
        while G_SHUTDOWN:
            stdin = sys.stdin.readline()
            __LOG__.Trace("STD IN : %s" % stdin)
            try:
                if stdin[:7] == 'file://':
                    data = stdin.split('://')[1].strip()
                    path, partition_val = data.split('||')[0], data.split('||')[1:]
                    # self.set_table(table)
                    self.load_data(path, partition_val)
                else:
                    __LOG__.Trace("STDIN with Invalid format")
            except:
                __LOG__.Exception()
            sys.stderr.write('\n')
            sys.stderr.flush()

def main():
    if len(sys.argv) != 3:
        print 'Usage : %s <Section> <ConfigFilePath>' % sys.argv[0]
        sys.exit()

    obj = HIVEController()
    __LOG__.Trace('---------------HIVEController Start!----------------')
    obj.run()

if __name__ == '__main__':
    main()


# -*- coding: utf-8 -*-
import ConfigParser
import os
import signal
import sys
import datetime as dt
from Consumer import Consumer

import Mobigen.Common.Log as Log;

Log.Init()

SHUTDOWN = False

def Handler(signum, frame):
    global SHUTDOWN
    SHUTDOWN = True
    __LOG__.Trace("Catch Signal= %s" % signum)

signal.signal(signal.SIGTERM, Handler)

class MessageMonitor():
    def __init__(self, module, section, cfgfile):
        self.module = module
        self.topic = section
        self.cfgfile = cfgfile
        self.idx_file = None
        self.dump_dir = None
        self.delimiter = None
        self.start_delimiter = "START"
        self.end_delimiter = "END"
        self.consumer_cfg = {
            "bootstrap.servers": "localhost:9092",
            "group.id": "group",
            "session.timeout.ms": 6000,
            "default.topic.config": {
                "auto.commit.enable": True,
                "auto.offset.reset": "smallest",
                "auto.commit.interval.ms": 1000
            }
        }

        self.get_parser(module, cfgfile)
        self.set_config()
        self.set_logger()
        self.Consumer = Consumer(self.topic, self.consumer_cfg)

    def get_parser(self, module, cfgfile):
        try:
            self.cfg = ConfigParser.ConfigParser()
            if os.path.exists(cfgfile): self.cfg.read(cfgfile)
            else: self.cfg = None
        except:
            print "get_parser Error"
            self.PARSER = None

        if self.cfg is None:
            print 'usage : %s <Topic> <ConfigFile>' % module

    def set_config(self):
        section = self.topic

        try:
            self.start_delimiter = self.cfg.get(section, "START_DELIMITER")
            self.end_delimiter = self.cfg.get(section, "END_DELIMITER")
            self.idx_file = self.cfg.get(section, "INDEX_FILE")
            self.dump_path = self.cfg.get(section, "DUMP_PATH")
        except Exception, ex:
            print "Exception : %s" % ex
            sys.exit()

        if self.cfg.has_option(section, "bootstrap.servers"):
            self.consumer_cfg["bootstrap.servers"] = \
                self.cfg.get(section, "bootstrap.servers")
        if self.cfg.has_option(section, "group.id"):
            self.consumer_cfg["group.id"] = \
                self.cfg.get(section, "group.id")
        if self.cfg.has_option(section, "session.timeout.ms"):
            self.consumer_cfg["session.timeout.ms"] = \
                self.cfg.getint(section, "session.timeout.ms")
        if self.cfg.has_option(section, "auto.commit_enable"):
            self.consumer_cfg["auto.commit_enable"] = \
                self.cfg.getboolean(section, "auto.commit_enable")
        if self.cfg.has_option(section, "auto.offset.reset"):
            self.consumer_cfg["auto.offset.reset"] = \
                self.cfg.get(section, "auto.offset.reset")
        if self.cfg.has_option(section, "auto.commit.interval.ms"):
            self.consumer_cfg["auto.commit.interval.ms"] = \
                self.cfg.getint(section, "auto.commit.interval.ms")

    def set_logger(self):
        self.logFilePath = 'Log'
        self.logFileSize = 1000000
        self.logFileCount = 10

        if (self.cfg != None):
            if self.cfg.get('Log', 'LogFilePath') != '':
                self.logFilePath = self.cfg.get('Log', 'LogFilePath')

            self.logFileSize = self.cfg.get('Log', 'LogFileSize')
            self.logFileCount = self.cfg.get('Log', 'LogFileCount')

            if not os.path.exists(self.logFilePath):
                os.makedirs(self.logFilePath)

            LOG_NAME = '%s/%s_%s.log' % (self.logFilePath,
                                         os.path.basename(self.module)[:-3],
                                         self.topic)
            Log.Init(Log.CRotatingLog(os.path.expanduser(LOG_NAME),
                                      int(self.logFileSize),
                                      int(self.logFileCount)))


    def save_index(self, file_name):
        idx_file = self.idx_file
        wfd = open(idx_file, 'w')
        wfd.write(file_name + '\n')
        wfd.close()
        __LOG__.Trace("Save Index : %s" % file_name)

    def load_index(self):
        print self.idx_file
        if os.path.exists(self.idx_file):
            with open(idx_file, "r") as rfd:
                curr = rfd.read().strip()
            if curr == '':
                curr = None
        else:
            __LOG__.Trace("IndexFile Not Exists: %s" % self.idx_file)
            curr = None
        return curr

    def get_filename(self, msg):
        # now = dt.datetime.now().strftime("%Y%m%d%H%M%S.txt")
        date, seq = msg.split('|^|')[1:]
        final_dir = os.path.join(self.dump_path, self.topic)
        filename = "%s_%s.csv" % (date.strip(), seq)
        if not os.path.exists(final_dir):
            os.makedirs(final_dir)

        return os.path.join(final_dir, filename)

    def run(self):
        #file_name = self.load_index()
        #wfd = False
        #if file_name:
        #    wfd = open(file_name, 'w')
        while not SHUTDOWN:
            msg = self.Consumer.polling(1)
            #print msg
            if msg == None or msg == '':
                continue
            if msg.startswith(self.start_delimiter):
                file_name = self.get_filename(msg)
                self.save_index(file_name)
                wfd = open(file_name, 'w')
            elif msg.strip() == self.end_delimiter:
                if wfd:
                    wfd.close()
                    #print "DUMP FILE : %s" % file_name
                    __LOG__.Trace("Dump File : %s" % file_name)
                    sys.stdout.write('%s://%s\n' % (self.topic,
                                                    os.path.abspath(file_name)))
                else:
                    __LOG__.Trace("be empty queue")
            else:
                try:
                    wfd.write(msg + '\n')
                except:
                    pass

def main():
    module = os.path.basename(sys.argv[0])

    if len(sys.argv) < 3:
        print >> sys.stderr, "Usage : %s Topic ConfigFile" % module
        return

    section = sys.argv[1]
    cfgfile = sys.argv[2]

    MessageMonitor(module, section, cfgfile).run()

if __name__ == "__main__":
    try:
        main()
    except:
        __LOG__.Exception()


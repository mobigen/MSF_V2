import sys
import os
import signal
import datetime
import ConfigParser

from MySQLHandler import MySQLHandler
from OracleHandler import OracleHandler
import confluent_kafka

import Mobigen.Common.Log as Log;

G_SHUTDOWN = True

def Shutdown(sigNum = 0, frame = 0) :
        global G_SHUTDOWN
        __LOG__.Trace("Recv Signal (%s)" % sigNum)
        G_SHUTDOWN = False

signal.signal(signal.SIGTERM, Shutdown)  # Sig Terminate : 15
signal.signal(signal.SIGINT, Shutdown)   # Sig Inturrupt : 2
signal.signal(signal.SIGHUP, Shutdown)  # Sig HangUp : 1
signal.signal(signal.SIGPIPE, Shutdown) # Sig Broken Pipe : 13

class Producer():
    def __init__(self):
        self.topic = sys.argv[1]
        self.cfgfile = sys.argv[2]

        self.volume = 10000
        self.start_delimiter = "START"
        self.end_delimiter = "END"
        self.producer_cfg = {
                "bootstrap.servers": "localhost:9092",
                "message.max.bytes": 1000000,
                "metadata.request.timeout.ms": 60000,
                "default.topic.config": {
                    "produce.offset.report": True,
                    "request.required.acks": 1,
                    "auto.commit.enable": True
                }
        }

        self.GetParser(sys.argv)
        self.SetLog(sys.argv)
        self.GetConfig()

        self.p = confluent_kafka.Producer(**self.producer_cfg)

    def delivery_callback(self, err, msg):
        if err:
            __LOG__.Trace('Message failed delivery: %s' % err)
        else:
            __LOG__.Trace('Message delivered to %s [%d] @ %o' %
                        (msg.topic(), msg.partition(), msg.offset()))


    def GetParser(self, argv):
        try:
            self.PARSER = ConfigParser.ConfigParser()
            if os.path.exists(argv[2]): self.PARSER.read(argv[2])
            else: self.PARSER = None
        except Exception, ex:
            sys.stdout.write('GetParser Error\n')
            self.PARSER = None

        if self.PARSER is None:
            sys.stdout.write('Usage : %s Section ConfigFile\n' % argv[0])
            sys.exit()

    def SetLog(self, argv) :
        #default Log
        self.logFilePath = 'Log'
        self.logFileSize = 100000
        self.logFileCount = 10

        if (self.PARSER != None) :
            if self.PARSER.get('Log','LogFilePath') != '' :
                self.logFilePath = self.PARSER.get('Log','LogFilePath')

            self.logFileSize = self.PARSER.get('Log','LogFileSize')
            self.logFileCount = self.PARSER.get('Log','LogFileCount')

            if not os.path.exists(self.logFilePath) :
                os.makedirs(self.logFilePath)

            LOG_NAME = '%s/%s_%s.log' % (self.logFilePath, 
                                         os.path.basename(argv[0])[:-3], 
                                         argv[1])

            Log.Init(Log.CRotatingLog(os.path.expanduser(LOG_NAME), 
                                      int(self.logFileSize), 
                                      int(self.logFileCount)))

    def GetConfig(self) :
        try :
            self.db_type = self.PARSER.get(self.topic, 'DB_TYPE')
            self.db_confpath = self.PARSER.get(self.topic, 'DB_CONFPATH')
            self.db_section = self.PARSER.get(self.topic, 'DB_SECTION')
            self.volume = self.PARSER.getint(self.topic, 'VOLUME')
            self.col_delimiter = self.PARSER.get(self.topic, 'COL_DELIMITER')
            self.PARSER_DB = ConfigParser.ConfigParser()
            if os.path.exists(self.db_confpath):
                self.PARSER_DB.read(self.db_confpath)
            else:
                self.PARSER_DB = None
            if self.db_type == "Oracle":
                self.db_obj = OracleHandler(self.db_section, self.PARSER_DB)
            elif self.db_type == "MySQL":
                self.db_obj = MySQLHandler(self.db_section, self.PARSER_DB)

            self.QUERY_STRING = self.PARSER.get(self.topic, 'QUERY')
            # self.INDEX_PATH = self.PARSER.get('COMMON','INDEX_PATH')
        except :
            __LOG__.Exception()
            sys.exit()

    def produce(self, line):
        try:
            self.p.produce(self.topic, line.rstrip(), callback=self.delivery_callback)
        except BufferError as e:
            __LOG__.Trace('Local producer queue is full \
                    (%d messages awaiting delivery): try again' % len(self.p))
        self.p.poll(0)

    def get_strrow(self, row):
        strrow = ''
        for x in row:
            if isinstance(x, datetime.datetime):
                strrow += x.strftime("%Y%m%d%H%M%S")
            else:
                strrow += str(x).strip()
            strrow += self.col_delimiter
        return strrow[:-1]

    def run(self):
        while G_SHUTDOWN:
            stdin = sys.stdin.readline()
            __LOG__.Trace("STD IN : %s" % stdin)
            try:
                prefix, date = stdin.split('://')
            except:
                __LOG__.Trace("Unmatched prefix")
                continue
            if prefix == 'DATE':
                # query = self.QUERY_STRING % date
                query = self.QUERY_STRING
                data = self.db_obj.executeGetData(query)
                #print data
                head = 0
                while data[head*self.volume:(head+1)*self.volume]:
                    self.produce("START|^|%s|^|%s" % (date, str(head)))
                    for row in data[head*self.volume:(head+1)*self.volume]:
                        line = self.get_strrow(row)
                        self.produce(line)
                        self.p.flush()
                    self.produce("END")
                    head += 1
                    self.p.flush()
            sys.stderr.write('\n')
            sys.stderr.flush()



def main():
    if len(sys.argv) != 3:
        print sys.argv
        print 'Usage : %s section ConfigFilePath' % sys.argv[0]
        sys.exit()

    obj = Producer()
    __LOG__.Trace('---------------%s Producer Start!-----------------' % sys.argv[1])

    obj.run()

if __name__ == '__main__':
    main()


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, signal, time, re
import ConfigParser
from DBMgr import DBMgr
from IrisMgr import IrisMgr
from OracleMgr import OracleMgr
#from MysqlMgr import MysqlMgr
import Mobigen.Common.Log as Log; Log.Init()

IRIS = "IRIS"
ORACLE = "ORACLE"
MYSQL = "MYSQL"

DB_TYPE = ( IRIS, ORACLE, MYSQL )

SHUTDOWN = True

def handler(sigNum, frame) :
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)

    global SHUTDOWN
    SHUTDOWN = False

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT,  handler)
signal.signal(signal.SIGHUP, signal.SIG_IGN)
signal.signal(signal.SIGPIPE, signal.SIG_IGN)

def loadConfig(conf) :
    confObj = ConfigParser.ConfigParser()
    confObj.read(conf)
    retHash = {}
    for section in confObj.sections() :
        retHash[section] = {}
        for (key, value) in confObj.items(section) :
            retHash[section][key.upper()] = value

    return retHash

def getDBMgr(dbConf, dir):
    global DB_TYPE
    global IRIS, ORACLE, MYSQL

    dbms = None
    dbMgr = None

    DB_CONF = {}
    DB_CONF = loadConfig(dbConf)

    if dir == DBMgr.DIR_SRC:
        # [GENERAL] section에 [SRC_DBMS]가 없다면 None을 return
        if not "SRC_DBMS" in DB_CONF["GENERAL"] or \
            DB_CONF["GENERAL"]["SRC_DBMS"].strip() == "":
            return None

        dbms = DB_CONF["GENERAL"]["SRC_DBMS"]
        if dbms in DB_TYPE:
            __LOG__.Trace("Selected source DBMS : %s" % dbms)
        else :
            raise ValueError("Invalid SRC_DBMS value. %s only the value of one will be allowed. Please check the value in %s\n" % (DB_TYPE, dbConf))

    elif dir == DBMgr.DIR_DST:
        # [GENERAL] section에 [DST_DBMS]가 없다면 None을 return
        if not "DST_DBMS" in DB_CONF["GENERAL"] or \
            DB_CONF["GENERAL"]["DST_DBMS"].strip() == "":
            return None

        dbms = DB_CONF["GENERAL"]["DST_DBMS"]
        if dbms in DB_TYPE:
            __LOG__.Trace("Selected destination DBMS : %s" % dbms)
        else:
            raise ValueError("Invalid DST_DBMS value. %s only the value of one will be allowed. Please check the value in %s\n" % (DB_TYPE, dbConf))
    else:
        raise ValueError("Invalid direction : %s" % dir)

    if dbms == IRIS:
        dbMgr = IrisMgr(dbConf, dir)
    elif dbms == ORACLE:
        dbMgr = OracleMgr(dbConf, dir)
    #elif dbms == MYSQL :
        #dbMgr = MysqlMgr(dbConf, dir)

    return dbMgr


def initLog(dbConf, logName):
    # LOG 관련 DEFAULT VALUE
    logDir = "."
    logLine = 1000000
    logDevide = 5

    DB_CONF = {}
    DB_CONF = loadConfig(dbConf)

    try:
        logDir = DB_CONF["GENERAL"]["LOG_DIR"]
        if not os.path.exists(logDir) :
            __LOG__.Trace("LOG_DIR(%s) doesn't exist. Current directory will be used.\n" % logDir)
            logDir = "."
    except:
        pass

    try:
        logLine = int(DB_CONF["GENERAL"]["LOG_LINE"])
    except:
        pass

    try:
        logDevide = int(DB_CONF["GENERAL"]["LOG_DEVIDE"])
    except:
        pass

    Log.Init(Log.CRotatingLog("%s/%s.%s.log" % (logDir, os.path.basename(sys.argv[0]), logName), logLine, logDevide))


def main():
    readFileStr = ''
    while SHUTDOWN:
        ephemeralMode = False
        try:
            sqlFile, stTime, enTime = sys.argv[3:6]
            ephemeralMode = True
            __LOG__.Trace( "Ephemeral Mode ON [ SQL : {0}  \
                    %stime : {1}  %etime : {2} ]".format( sqlFile, stTime, enTime ) )
        except:
            ephemeralMode = False

        if not ephemeralMode:
            readFileStr = sys.stdin.readline().strip()
        else:
            readFileStr = sqlFile

        sqlFile = re.sub('file:\/\/', '', readFileStr)

        logName = sys.argv[1]
        confPath = sqlFile

        if not os.path.exists(confPath):
            sys.stderr.write("conf_path(%S) does not exists.\n" % confPath)
            sys.exit()

        __LOG__.Trace("[STDIN] %s" % readFileStr)

        srcDBMgr = getDBMgr(confPath, DBMgr.DIR_SRC)
        destDBMgr = getDBMgr(confPath, DBMgr.DIR_DST)

        try:
            if os.path.exists(sqlFile):
                SQL_CONF = {}
                SQL_CONF = loadConfig(sqlFile)

                sql = SQL_CONF["GENERAL"]["SQL"]

                if ephemeralMode:
                    sql = sql.replace("%stime", stTime).replace("%etime", enTime)

                # SRC_DBMS가 지정되어 있다면 unload를 수행한다.
                if srcDBMgr:
                    if destDBMgr:
                        srcDBMgr.unload(sql, destDBMgr.isSplit())
                    else:
                        srcDBMgr.unload(sql, False)

                # DST_DBMS가 지정되어 있다면 load를 수행한다.
                if destDBMgr:
                    # 쓰레드 고려
                    destDBMgr.load()

                sys.stdout.write("%s\n" % readFileStr)
                sys.stdout.flush()

                __LOG__.Trace("[STDOUT] %s" % readFileStr)
            else:
                __LOG__.Trace("Not Exist SQL File : %s" % sqlFile)
        finally:
            sys.stderr.write("%s\n" % readFileStr)
            sys.stderr.flush()

            __LOG__.Trace("[STDERR] %s" % readFileStr)

        if ephemeralMode:
            break


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: %s    log_name db_conf\n" % sys.argv[0])
        sys.exit()

    logName    = sys.argv[1]
    confPath = sys.argv[2]

    # LOG 설정
    initLog(confPath, logName)
    __LOG__.Trace("%s Started..." % (sys.argv[0]))

    try:
        main()
    except Exception, err:
        __LOG__.Exception()
        sys.stderr.write('ERROR: %s\n' % str(err))

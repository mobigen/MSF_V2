# encoding: utf-8
"""
Process.py

Copyright (c) 2012 Mobigen. All rights reserved.
"""

import os
import sys

def chkPid(serverName) :

    pid = readPid(serverName)
    if (pid > 0):
        try:
            r = os.kill(int(pid), 0)
        except:
            # Process
            # OSError: [Errno 3] No such process
            #print "(%s:%s)" % (sys.exc_type, sys.exc_value)
            return False

        if (r == None):
            return True
    return False

def writePid(serverName) :

    if chkPid(serverName) == True:
        return False
    
    f = open(serverName + ".pid", "w")
    f.write(str(os.getpid()))
    f.close()

    return True
  

def readPid(serverName) :

    line = ""
    try:
        f = open(serverName + ".pid", "r")
        line = f.readline()
        f.close()
    except:
        line = ""

    if (line == ""):
        return -1

    return int(line)

def killPid(pid) :
    os.kill(pid, 9)


if __name__ == "__main__" :
    print writePid("Process")
    print readPid("Process")

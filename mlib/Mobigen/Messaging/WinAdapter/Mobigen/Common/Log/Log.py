#!/home/mobigen/bin/python

import sys
import time
import getopt
import Mobigen.Common.Log as Log; 

OUTPUT = None
bNewLine = False

try: opts, args = getopt.getopt(sys.argv[1:], "no:", ["newline", "output="])
except getopt.GetoptError: sys.exit()

if(len(args)==3) :
	Log.Init(Log.CRotatingLog(args[0], args[1], args[2]))
else :
	Log.Init()

for o, v in opts:
	if o in ("-o", "--output"):
		exec("OUTPUT = __LOG__.%s" % (v))

	if o in ("-n", "--newline"):
		bNewLine = True

while True :
	if(bNewLine) :
		line = sys.stdin.readline()
	else :
		line = sys.stdin.readline().strip()

	if(not line) : break

	OUTPUT(line)

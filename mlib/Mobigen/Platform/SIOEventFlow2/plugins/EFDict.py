#!/usr/bin/env pypy

import sys
import EFCommandServer
import EFDictCore
import re

SYNC_CMD_STR = "PUT APP MPT MAP DEL CLR SVF SVB LDF LDB"
SYNC_CMD_LIST = SYNC_CMD_STR.split(" ")

class EFDict:
	def __init__(self, ip, port, **opt) :
		dc = EFDictCore.EFDictCore()

		self.cs = EFCommandServer.EFCommandServer( dc, ip, port, **opt )
		self.mode = opt["mode"]

	def stdout(self):
		for line in self.cs.stdout() :
			if  self.mode == "sync":
#				if SYNC_CMD_STR.find(line[:3].upper()) >= 0:
				if line[:3].upper() in SYNC_CMD_LIST :
					yield line
			else :
				yield line


if __name__ == "__main__":
	if len(sys.argv) < 3 :
		print "usage : %s ip port mode" % (sys.argv[0])
		sys.exit()
	
	ip = sys.argv[1]
	port = int(sys.argv[2])
	try: modeVal = sys.argv[3]
	except: modeVal = "stdio"

	dict = EFDict(ip, port, mode=modeVal)
	for line in dict.stdout():
		sys.stdout.write(line)
		sys.stdout.flush()

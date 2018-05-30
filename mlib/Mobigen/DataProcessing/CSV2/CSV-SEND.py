#!/home/mobigen/bin/python
# -*- coding: cp949 -*-

import sys
from socket import *

import Mobigen.Archive.CSV as CSV
import Mobigen.Common.Log as Log; Log.Init()

def Main() :
	if (len(sys.argv)!=4) : 
		return

	ip   = sys.argv[1]
	port = int(sys.argv[2])
	strInputPath = sys.argv[3]

	Reader = CSV.Reader(strInputPath, CSV.PARTITION)
	Reader.EnableSplit(False)
	Reader.SetLast()

	sock = socket(AF_INET, SOCK_STREAM)
	sock.connect((ip, port))

	while True :
		line = Reader.next()
		sock.sendall(line+"\n")

if __name__ == "__main__" :
	Main()

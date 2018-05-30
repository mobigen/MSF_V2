#!/usr/bin/python

VERSION = '1.2'

import re, socket

def read(conn, dataLen) :
	remained = dataLen
	data = ''
	while True :
		# print 'debug : remained = %s' % (remained)
		try :
			tmpData = conn.recv(remained)
		except socket.timeout :
			continue

		if tmpData :
			data += tmpData
			if len(data) == dataLen :
				return data
			else :
				remained = dataLen - len(data)
		else :
			raise Exception, 'socket broken'

def read_until(conn, bufStr, pat) :
	while 1 :
		try :
			dataStr = conn.recv(1024)
		except socket.timeout :
			continue

		if dataStr :
			bufStr += dataStr
			# se = re.search('^(.+\$ )', bufStr, re.DOTALL)
			patStr = '^(.+%s)' % (pat)
			se = re.search(patStr, bufStr, re.DOTALL)
			if se :
				ans = se.group(1)
				bufStr = bufStr[len(ans):]
				return bufStr, ans
		else :
			return bufStr, ''

def main() :
	pass

if __name__ == '__main__' : main()

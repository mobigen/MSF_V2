#!/usr/bin/python

VERSION = '2.1'

import sys, telnetlib, time, re, struct, os

class Struct :
	def __init__(self, **args) :
		try : self.dataType = args['DataType']
		except : self.dataType = 'b'

	def pack(self, fileTime, msgTime, opt, key, val) :
		# yyyymmddhhmmss(14) yyyymmddhhmmss(14) opt(16) key(4) len(4) val
		return  struct.pack('!14s14s16sII' , str(fileTime), str(msgTime), '%16s'%opt, int(key), len(val)) + val
	
	def unpack(self, ovh) :
		# ovh = yyyymmddhhmmss(14) yyyymmddhhmmss(14) opt(16) key(4) len(4)
		return  struct.unpack('!14s14s16sII' , ovh)

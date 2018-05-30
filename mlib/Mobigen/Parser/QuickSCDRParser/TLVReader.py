#!/bin/env python

import cStringIO

class QTLVReader :
	FILE_MODE = False
	STRING_MODE = True

	def __init__(self, param, stringMode = STRING_MODE) :
		if stringMode :
			self.data = cStringIO.StringIO(param)
		else :
			self.data = open(param, "r")
		self.recCount = 0

	def __iter__(self) :
		return self

	def getRecCount(self) :
		return self.recCount

	def next(self) :
		tag = 0
		length = 0

		try :
			# STEP 1: read in tag field
			# read in first tag octet
			tag = ord(self.data.read(1))
			# check if this is an extension tag
			if (tag & 0x1f) == 0x1f :
				# yes, this is an extension tag
				while True :
					# read in next tag octet
					tmp_tag = ord(self.data.read(1))
					# update tag value
					tag = (tag << 8) | tmp_tag
					# check if this is the last extension octet
					if (tmp_tag & 0x80) != 0x80 :
						break

			# STEP 2: read in length field
			length = ord(self.data.read(1))
			if length >= 0x80 :
				# this is multi-octet length field
				lofl = 0x7F & length
				if lofl <= 0 :
					# critical error!!
					raise StopIteration
				else :
					length = 0
					lcnt = 0
					while (lcnt < lofl) :
						tmp_len = ord(self.data.read(1))
						length = (length << 8) | tmp_len
						lcnt += 1

			# STEP 3: read in values
			value = self.data.read(length)

			self.recCount += 1
			return tag, length, value

		except :
			self.data.close()
			raise StopIteration

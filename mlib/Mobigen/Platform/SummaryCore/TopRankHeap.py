#!/usr/bin/env python
# -*- coding: utf-8 -*-

import heapq, sys

class TopRankHeap :
	def __init__(self, topCnt) :
		self.heap = []
		self.topCnt = topCnt
		self.smallest = 9999999999

	def sfio(self, line) :
		words = line.strip().split(',')
		if len(words) < 2 :
			return None

		flag = words.pop(0)
		cmd = words.pop(0).upper()

		if cmd == "PUT" :
			keyStr = ",".join( words[:-1] )
			valInt = int( words[-1] )
			self.put( keyStr, valInt )
			return None

		elif cmd == "GET" :
			return "".join( [ line for line in self.get() ] )
			return "".join( [ line for line in self.get() ] )

		elif cmd == "CLR" :
			return self.clr()

	def put(self, keyStr, valInt) :
		valList = [valInt, keyStr]
		if len(self.heap) < self.topCnt :
			heapq.heappush(self.heap, valList)
			if self.smallest > valList[0] :
				self.smallest = valList[0]

		else :
			if self.smallest < valList[0] :
				heapq.heappop(self.heap)
				heapq.heappush(self.heap, valList)
				self.smallest = min(self.heap)[0]
		# print "debug : heap = %s" % self.heap
		# sys.stdin.readline()

		return None

	def get(self) :
		for tmpList in self.heap :
			# print "debug : get : tmpList = %s" % tmpList
			yield "%s,%s\n" % (tmpList[1], tmpList[0])

	def clr(self) :
		self.heap = []
		self.smallest = 9999999999
		return None

	def run(self) :
		while True :
			line = sys.stdin.readline().strip()
			res = self.sfio(line)
			if res != None :
				print res,


def main() :
	if len(sys.argv) != 2 :
		print "usage : %s topRankCount" % (sys.argv[0] )
		print "0,put,key1,key2,..,value"
		print "..."
		print "0,get"
		sys.exit()
	topCnt = int( sys.argv[1] )

	TopRankHeap(topCnt).run()

if __name__ == "__main__" : main()

#! /bin/env python
#coding:utf-8

"""
remove -t(alivetime) option. 
add -m(maxlensize) option
"""
import sys
import os
import re
import time
import getopt
import signal
import itertools
from collections import defaultdict
from collections import deque

SHUTDOWN = False

def shutdown(sigNum, frame):
	global SHUTDOWN
	SHUTDOWN = True
	sys.stderr.write('Catch Signal : %s \n\n' % sigNum)
	sys.stderr.flush()
signal.signal(signal.SIGTERM, shutdown) # sigNum 15 : Terminate
signal.signal(signal.SIGINT, shutdown)  # sigNum  2 : Interrupt

def usage():
	print >> sys.stderr, """Usage : python [file][option] .. 
	[-h | --help ] : help message
	[-g (word) | --grep (word) ] : grep (word) about STDIN
	[-n (number) | --number (number) ] : cashing n about STDIN
	[-r (regex) | --regular (regex) ] : grep (regex) about STDIN 
	[-m (number) | --maxlensize (number) ] : set deque max size
	"""

	print >> sys.stderr, """Exam : 
	1. python test.py -g .txt -n 3 
	2. python test.py -g .txt -r '\d'
	3. python test.py -t 20 -n 2 -r '\d' -g txt -g csv --grep jpg
	"""

class EFEventModule(object) :
	def __init__(self,options,args):
		object.__init__(self)
		self.options = options
		self.args = args
		self.stacksize = 1
		self.deq = deque(maxlen=1000)
		self.olist = defaultdict(lambda:[])
		self.option_onlyn_flag = True

	def processing(self, stdin):
		#for option e
		for eop in self.olist['-e']:
			if eop in stdin :
				return
		
		#for option g
		for patt in self.olist['-g'] :
			if patt in stdin :
				self.deq.append(stdin)
				#print 'g flag' , self.deq
				return
						
		#for option r
		for patt in self.olist['-r'] :
			if re.search(patt, stdin) :
				self.deq.append(stdin)
				#print 'r flag',self.deq
				return

		#for option only n
		if self.option_onlyn_flag:
			self.deq.append(stdin)

	def run(self):
		self.preprocessing()
		while not SHUTDOWN:
			stdin = sys.stdin.readline()
			stdin_strip = stdin.strip()
			#for optionprocessing
			self.processing(stdin_strip)
			#for afterprocessing	
			if self.deq.count(stdin_strip) == int(self.stacksize):
				sys.stdout.write("%s" % stdin)
				sys.stdout.flush()

				deqcopy = deque(itertools.islice(self.deq,0,len(self.deq)))
				for d in deqcopy:
					if stdin_rep == d:
						self.deq.remove(d)
			#stderr
			sys.stderr.write("%s" % stdin)
			sys.stderr.flush()

	def preprocessing(self):
		try:
			for op, p in self.options:
				if op in ('-h','--help'):
					#option h
					usage()
					os._exit(1)
				elif op in ('-n','--number'):
					self.stacksize = p
				elif op in ('-g','--grep'):
					self.olist['-g'].append(p)
					self.option_onlyn_flag = False
				elif op in ('-e','--except'):
					self.olist['-e'].append(p)
				elif op in ('-r','--regular'):
					self.olist['-r'].append(p)
					self.option_onlyn_flag = False
				elif op in ('-m','--maxlensize'):
					#option m
					self.deq = deque(maxlen=int(p))
				else:
					raise Exception("unhandled option")
		except ValueError:
			raise Exception("you need to check input type")

	def __del__(self):
		pass

def main():
	try:
		if len(sys.argv)==1 :
			usage()
			os._exit(1)
		options, args = getopt.getopt(sys.argv[1:],'g:hn:e:r:m:',['grep=','help','number=','except=','regular=', 'maxlensize='])
		obj = EFEventModule(options,args)
		obj.run()
	except getopt.GetoptError:
		raise Exception("unhandled option, please [filename][-h|--help]")

if __name__== "__main__":
	main()

#! /bin/python
#coding:utf-8
import subprocess
import datetime
import time
import os
import sys
import signal
import getopt
import calendar
import threading
import select

SHUTDOWN = False

def shutdown(sigNum, frame):
	global SHUTDOWN
	SHUTDOWN = True
	sys.stderr.write('Catch Signal : %s \n\n' % sigNum)
	sys.stderr.flush()
signal.signal(signal.SIGTERM, shutdown) #sigNum 15 : Terminate
signal.signal(signal.SIGINT, shutdown) #sigNum 2 : Interrupt

def usage():
	print >> sys.stderr, """Usage : python [this_filename][file][,timeoption(default: -m * -h * -d * -o * -w *)]

	[this_filename] : EFScheduler.py

	[file] : -p ( file://%Y/%m/%d-%H:%M:%S ) formatting
		 -e (filepath) exec file
	
	[timeoption] : -m ( number[0-59] | (number)-(number) | 0,2,3,...,59 ) minute 
	-h ( number[0-24] | (number)-(number) | 0,2,3,...,24 ) hour
	-d ( number[1-31] | (number)-(number) | 1,2,3,...,31 ) day
	-o ( number[1-12] | (number)-(number) | 1,2,3,...,12 ) month
	-w ( number[0-6] | (number)-(number) | 0(mon),2,3,...,6(sun)) weekend 

Condition : 1.this file wait only 10second, when [file] don't print stdout or stderr
			2.nevertheless stdout or stderr is nothing, this file stdout '' and stderr ''
"""

	print >> sys.stderr, """
Exam : 1. python EFScheduler.py -e "test.sh" -m */2
       2. python EFScheduler.py -e "test.sh" -p "test.sh://%Y/%m/%d-%H:%M:%S -m 10-20" -h 0 """

class EFScheduler(object):
	def __init__(self, options,args):
		super(EFScheduler, self).__init__()
		self.options = options
		self.args = args
		ft = datetime.datetime.today()
		self.delta_input = [ft.minute,ft.hour,ft.day,ft.month,ft.weekday(),ft.second]
		self.console_input = ['*','*','*','*','*']
		self.slashlist =[[],[],[],[],[]]
		self.fdinput=[]
		self.formatinput=[]
		self.token=0
	
	def preprocessing(self):
		epflag =True
		for op, p in self.options:
			if p == sys.argv[0]:
				p='*'
			if op in '-m':
				self.console_input[0]=p
			elif op in '-h':
				self.console_input[1]=p
			elif op in '-d':
				self.console_input[2]=p
			elif op in '-o':
				self.console_input[3]=p
			elif op in '-w':
				self.console_input[4]=p
			elif op in '-e':
				epflag = False
				if p.lower() == 'python':
					raise Exception(" mark '' is needed. exam : 'python xxx.py' ")
				else:
					self.fdinput.append(p.split())
			elif op in '-p':
				epflag =False
				self.formatinput.append(p)
			elif op in '--help':
				usage()
				os._exit(1)
			else:
				raise Exception("Unhandled Option, option --help")
				os._exit(1)
		if epflag:
			raise Exception("You must use -p or -e option")
			os._exit(1)

	def optionprocessing(self, consoleIndex, limittime, rangestart=0):
		if '/' in self.console_input[consoleIndex]:
			sp = self.console_input[consoleIndex].split('/')
			args = sp[0]
		else:
			args = self.console_input[consoleIndex]

		numlist=[]	
		if '*' in args:
			numlist = [i for i in range(rangestart,limittime)]

		if ',' in args:
			token = args.split(',')
			numlist = [int(i) for i in token]

		if '-' in args:
			token = args.split('-')
			for i in range(int(token[0]),int(token[1])+1):
				numlist.append(int(i))
		
		if '/' in self.console_input[consoleIndex]:
			token = int(sp[1])
			self.slashlist[consoleIndex] =[i for i in range(0,60) if i%token ==0]
		
		if args.isdigit():
			numlist=[int(args)]

		return numlist

	def processing(self,nt,minute,hour,day,month,weekday):
		if nt.second in [0,1]:
			if self.token ==1:
				return
			self.token =1
		else:
			self.token =0
			return
		if not nt.minute in minute:
			return
		if not nt.hour in hour:
			return
		if not nt.day in day:
			return
		if not nt.month in month:
			return
		if not nt.weekday() in weekday:
			return
	
		for cmd in self.fdinput:
			try:
				pipe = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				read_stdout = [pipe.stdout]
				read_stderr = [pipe.stderr]
			
				if pipe.poll() is not None:
					read_stdout.pop(pipe.stdout)
					read_stderr.pop(pipe.stderr)

				rolist,wolist,xolist = select.select(read_stdout,[],[],10)
				relist,welist,xelist = select.select(read_stderr,[],[],10)
			
				for f_out in rolist:
					output = f_out.readlines()
					if output ==[]:
						out = ''
						sys.stdout.write("%s\n"%out)
						sys.stdout.flush()

					for out in output:
						out = out.strip()
						sys.stdout.write("%s\n"%out)
						sys.stdout.flush()	
				
				for f_err in relist :
					output = f_err.readlines()
					if output==[]:
						out =''
						sys.stdout.write("%s\n"%out)
						sys.stdout.flush()

					for out in output:
						out = out.strip()
						sys.stderr.write("%s\n"%out)
						sys.stderr.flush()	

			except OSError: #unvalid input about option -e
				sys.stderr.write("Option -e is invaild : %s \n" % cmd)
				sys.stderr.flush()
				pass
			except UnboundLocalError: #about OSError 
				pass

		for fm in self.formatinput:
			try:
				tmp = fm.split('://')
				t = time.strftime(tmp[1], time.localtime())
				t1 = tmp[0].strip()
				f = t1+" "+t	
				sys.stdout.write("%s\n" %f)
				sys.stdout.flush()
				sys.stderr.write("%s\n" %f)
				sys.stderr.flush()

			except IndexError:
				sys.stderr.write("Option -p is invaild : %s \n" % fm)
				sys.stderr.flush()
				pass

	def run(self):
		self.preprocessing()
		minutelist = self.optionprocessing(0,60)
		hourlist = self.optionprocessing(1,24)
		daylist = self.optionprocessing(2,32,1)
		monthlist = self.optionprocessing(3,13,1)
		weekdaylist = self.optionprocessing(4,7)
		slashlist = self.slashlist
			
		totallist = [minutelist, hourlist, daylist, monthlist, weekdaylist]
		tmplist=[]
		for i in range(len(slashlist)):
			if len(slashlist[i])>0:
				for n in totallist[i]:
					if n in slashlist[i]:
						tmplist.append(n)
				totallist[i] = tmplist

		while not SHUTDOWN:
			nt = datetime.datetime.today()
		#	print "NOW TIME",nt
			self.processing(nt, totallist[0], totallist[1], totallist[2], totallist[3], totallist[4])
			time.sleep(1)

def main():
	try:
		if len(sys.argv)==1:
			raise Exception("you must write option -e or -p")
			os._exit(1)
		options, args = getopt.getopt(sys.argv[1:], 'm:h:d:o:w:e:p:',['help'])
		obj = EFScheduler(options,args)
		obj.run()
	except getopt.GetoptError:
		raise Exception("unhandled option")

if __name__=="__main__":
	main()

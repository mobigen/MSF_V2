# -*- coding: cp949 -*-
import os
import sys
import types
import time
import string
from traceback import *

from DummyLog import CDummyLog

traceOutput = sys.stdout
watchOutput = sys.stdout
writeOutput = sys.stdout
exceptOutput = sys.stdout
errorOutput = sys.stderr

# __main__���� Init()�� ȣ���ϴ� ��� �⺻ �����ϴ� Mobigen Log
class CPipeLog(CDummyLog):
	def __init__(self, pipe, level=1000000) :
		self.SetLevel(level)
		self.pid = str(os.getpid())

		pipepath = "/tmp/mobigen/%s" % pipe
		try: os.mkfifo(pipepath,0655)
		except: pass
		self.pipe = os.open(pipepath,os.O_WRONLY);
		self.fo = os.fdopen(self.pipe, "w")

	def SetLevel(self, level) :
		self.level = level

	def WatchEx (self, variableName, level=0):
		"""variableName�� �ڼ��� ������ ����ϱ� ���� Debug �Լ�"""
		if(level > self.level) : return 

		paramDict = { }

		try :
			stack = extract_stack ( )[-2:][0]
			actualCall = stack[3]
			if ( actualCall is None ):
				actualCall = "watch ( [unknown] )"
			left = string.find ( actualCall, '(' )
			right = string.rfind ( actualCall, ')' )
			paramDict["varName"]    = string.strip ( actualCall[left+1:right] )  # everything between '(' and ')'
			paramDict["varType"]    = str ( type ( variableName ) )[7:-2]
			paramDict["value"]      = repr ( variableName )
			paramDict["methodName"] = stack[2]
			paramDict["lineNumber"] = stack[1]
			paramDict["fileName"]   = stack[0]
		except :
			import psyco
			frame = psyco._getemulframe(1)
			actualCall = frame.f_code.co_names[-3]
			paramDict["varName"]    = string.strip ( actualCall )  
			paramDict["varType"]    = str ( type ( variableName ) )[7:-2]
			paramDict["value"]      = repr ( variableName )
			paramDict["methodName"] = frame.f_code.co_name
			paramDict["lineNumber"] = frame.f_lineno
			paramDict["fileName"]   = frame.f_code.co_filename

		paramDict["pid"]  = self.pid
		paramDict["time"]   = time.strftime("%Y/%m/%d %H:%M:%S")
		outStr = '[%(time)s] PID %(pid)s, File "%(fileName)s", line %(lineNumber)d, in %(methodName)s\n  %(varName)s <%(varType)s> = %(value)s\n\n'
		os.write ( self.pipe, outStr % paramDict )

	def Watch (self, variableName, level=0):
		"""variableName�� ������ ������ ����ϱ� ���� Debug �Լ�"""
		if(level > self.level) : return 

		paramDict = { }

		try :
			stack = extract_stack ( )[-2:][0]
			actualCall = stack[3]
			if ( actualCall is None ):
				actualCall = "watch ( [unknown] )"
			left = string.find ( actualCall, '(' )
			right = string.rfind ( actualCall, ')' )
	
			paramDict["varName"]    = string.strip ( actualCall[left+1:right] )  # everything between '(' and ')'
			paramDict["varType"]    = str ( type ( variableName ) )[7:-2]
			paramDict["value"]      = repr ( variableName )
			paramDict["lineNumber"] = stack[1]
			paramDict["methodName"] = stack[2]
			paramDict["fileName"]   = os.path.basename(stack[0])
		except :
			import psyco
			frame = psyco._getemulframe(1)
			actualCall = frame.f_code.co_names[-3]
			paramDict["varName"]    = string.strip ( actualCall )  
			paramDict["varType"]    = str ( type ( variableName ) )[7:-2]
			paramDict["value"]      = repr ( variableName )
			paramDict["methodName"] = frame.f_code.co_name
			paramDict["lineNumber"] = frame.f_lineno
			paramDict["fileName"]   = os.path.basename(frame.f_code.co_filename)
			
		paramDict["pid"]  = self.pid
		paramDict["time"]   = time.strftime("%Y/%m/%d %H:%M:%S")
		outStr = '[%(time)s] %(pid)s, "%(fileName)s", %(lineNumber)d, %(methodName)s : %(varName)s <%(varType)s> = %(value)s\n'
		os.write ( self.pipe, outStr % paramDict )

	def TraceEx (self, text, level=0):
		"""text�� ������ �ڼ��� ����ϱ� ���� Debug �Լ�"""
		if(level > self.level) : return 

		paramDict = { }

		try :
			stack = extract_stack ( )[-2:][0]
			paramDict["methodName"] = stack[2]
			paramDict["lineNumber"] = stack[1]
			paramDict["fileName"]   = stack[0]
		except :
			import psyco
			frame = psyco._getemulframe(1)
			paramDict["methodName"] = frame.f_code.co_name
			paramDict["lineNumber"] = frame.f_lineno
			paramDict["fileName"]   = frame.f_code.co_filename

		paramDict["text"]       = text
		paramDict["time"]   = time.strftime("%Y/%m/%d %H:%M:%S")
		paramDict["pid"]  = self.pid
		outStr = '[%(time)s] PID %(pid)s, File "%(fileName)s", line %(lineNumber)d, in %(methodName)s\n  %(text)s\n\n'
		os.write (self.pipe, outStr % paramDict )

	def Trace (self, text, level=0):
		"""text�� ������ ������ ����ϱ� ���� Debug �Լ�"""
		if(level > self.level) : return 

		paramDict = { }
		try :
			stack = extract_stack ( )[-2:][0]
			paramDict["methodName"] = stack[2]
			paramDict["lineNumber"] = stack[1]
			paramDict["fileName"]   = os.path.basename(stack[0])
		except:
			import psyco
			frame = psyco._getemulframe(1)
			paramDict["methodName"] = frame.f_code.co_name
			paramDict["lineNumber"] = frame.f_lineno
			paramDict["fileName"]   = os.path.basename(frame.f_code.co_filename)

		paramDict["text"]       = text
		paramDict["time"]   = time.strftime("%Y/%m/%d %H:%M:%S")
		paramDict["pid"]  = self.pid
		outStr = '[%(time)s] %(pid)s, "%(fileName)s", %(lineNumber)d, %(methodName)s : %(text)s\n'
		os.write (self.pipe, outStr % paramDict )
			

	def Write (self, text, level=0):
		"""text�� ����ϱ� ���� Debug �Լ�"""
		if(level > self.level) : return 
		os.write(self.pipe, text )

	def Error (self, text, level=0) :
		"""text�� errorOutput(stderr)���� ����ϴ� �Լ�"""
	#	if(level > self.level) : return 
		os.write(self.pipe,  text )

	def Exception (self, level=0) :
		if(level > self.level) : return 
		etype, value, tb = sys.exc_info()
		self.PrintException(etype, value, tb)

	def PrintException(self, type, value, tb) :
		os.write(self.pipe, "[%s] !!! Exception !!!\n" % (time.strftime("%Y/%m/%d %H:%M:%S")))
	#	print_exception(type, value, tb.tb_next, None, exceptOutput)
		print_exception(type, value, tb, None, self)

	def write(self, data) :
		os.write(self.pipe, data)
# -*- coding: cp949 -*-
import os
import sys
import types
import time
import string
from traceback import *

from DummyLog import CDummyLog

traceOutput = sys.stderr
watchOutput = sys.stderr
writeOutput = sys.stderr
exceptOutput = sys.stderr
errorOutput = sys.stderr

# __main__에서 Init()을 호출하는 경우 기본 동작하는 Mobigen Log
class CStandardErrorLog(CDummyLog):
	def __init__(self, level=1000000) :
		self.SetLevel(level)
		self.pid = str(os.getpid())

	def SetLevel(self, level) :
		self.level = level

	def WatchEx (self, variableName, level=0):
		"""variableName의 자세한 정보를 출력하기 위한 Debug 함수"""
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
		watchOutput.write ( outStr % paramDict )
		watchOutput.flush()

	def Watch (self, variableName, level=0):
		"""variableName의 간략한 정보를 출력하기 위한 Debug 함수"""
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
		watchOutput.write ( outStr % paramDict )
		watchOutput.flush()

	def TraceEx (self, text, level=0):
		"""text의 내용을 자세히 출력하기 위한 Debug 함수"""
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
		traceOutput.write ( outStr % paramDict )
		watchOutput.flush()

	def Trace (self, text, level=0):
		"""text의 내용을 간략히 출력하기 위한 Debug 함수"""
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
		traceOutput.write ( outStr % paramDict )
		watchOutput.flush()
			

	def Write (self, text, level=0):
		"""text를 출력하기 위한 Debug 함수"""
		if(level > self.level) : return 
		writeOutput.write ( text )
		watchOutput.flush()

	def Error (self, text, level=0) :
		"""text를 errorOutput(stderr)으로 출력하는 함수"""
	#	if(level > self.level) : return 
		errorOutput.write ( text )
		watchOutput.flush()

	def Exception (self, level=0) :
		if(level > self.level) : return 
		etype, value, tb = sys.exc_info()
		self.PrintException(etype, value, tb)

	def PrintException(self, type, value, tb) :
		exceptOutput.write("[%s] !!! Exception !!!\n" % (time.strftime("%Y/%m/%d %H:%M:%S")))
	#	print_exception(type, value, tb.tb_next, None, exceptOutput)
		print_exception(type, value, tb, None, exceptOutput)

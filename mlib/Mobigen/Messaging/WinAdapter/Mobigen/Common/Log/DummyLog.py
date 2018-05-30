# -*- coding: cp949 -*-

# __LOG__ 가 정의되어 있지 않을때 하위모듈의 올바른 동작을 지원하기 위한 Dummy Log 
class CDummyLog : 
	def SetPID(self, pid) : pass
	def WatchEx (self, variableName, level=0):		pass
	def Watch (self, variableName, level=0):		pass
	def TraceEx (self, variableName, level=0):		pass
	def Trace (self, variableName, level=0):		pass
	def Write (self, variableName, level=0):		pass
	def Exception (self, level=0):					pass
	def SetLevel(self, level) :						pass
	def PrintException(self, type, value, tb) :     pass

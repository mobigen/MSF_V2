# -*- coding: cp949 -*-
import sys 
import types
from traceback   import *

from DummyLog    import CDummyLog
from StandardLog import CStandardLog
from StandardErrorLog import CStandardErrorLog
from RotatingLog import CRotatingLog
from PipeLog     import CPipeLog
from UDPLog      import CUDPLog

__VERSION__ = "Release 2 (2005/10/21)"
# pysco.full() 모드에서 동작 가능하도록 수정.
#__VERSION__ = "Release 1 (2005/10/11)"
# pysco 충돌문제 해결
__LOG__ = None

#def Init(**args) :
def Init(userDefine = None) :
	# 모듈 Import 정보를 조사한다.

	impStepList = extract_stack()
	if(len(impStepList)==0) :
		# psyco.full()이 동작하는걸로 본다.
		import psyco
		frame = psyco._getemulframe()
		impStepList = frame.f_code.co_names

	# __main__ 이 아닌 곳에서 import 되는경우 __LOG__ 사용을 위해 
	# 임시로 Dummy Log 를 생성한다.

	if(len(impStepList)!=2) :
		curModule = __GetParentModule__()
		if(curModule==None) :
			sys.modules['__main__'].__dict__["__LOG__"] = CDummyLog()
			return

		if(curModule.__name__ != "__main__" and not curModule.__dict__.has_key("__LOG__")) :
			curModule.__dict__["__LOG__"] = CDummyLog()
			return 

	# __LOG__ 를 생성한다.
	global __LOG__

	if(userDefine != None) : __LOG__ = userDefine
	else : 	__LOG__ = __InitMain__()


	sys.modules["__main__"].__LOG__ = __LOG__

	for subModuleName in  sys.modules :
		subModule = sys.modules[subModuleName]

		if(type(subModule) == types.NoneType) : continue
		if(not "Log" in subModule.__dict__) : continue
		if(subModuleName == "__main__") : continue

		# 하위 모듈에서 사용 가능하도록 __LOG__ 등록한다.
		subModule.__LOG__ = __LOG__

def __Exception__(type, value, tb):
	if hasattr(sys, 'ps1') or not sys.stderr.isatty() or type == SyntaxError: 
		sys.__excepthook__(type, value, tb)
	else:
		if(__LOG__) :
			 __LOG__.PrintException(type, value, tb)

def AutoException() :
	if __debug__:
		sys.excepthook = __Exception__

def SetLevel(level) :
	global __LOG__
	if(__LOG__) : __LOG__.SetLevel(level)

def __InitMain__() :
	return CStandardLog()

def __GetParentModule__(Test = 0) :

	# impStepList[0] : __GetParentModlue__ 을 호출한 함수
	# impStepList[1] : Log.py 
	# impStepList[2] : Log.py를 Import 한 modlue
	try : 
		impStepList = extract_stack()
		impStepList.reverse()
		parentModulePath = impStepList[2][0]
	except :
		import psyco
		frame = psyco._getemulframe(2)
		parentModulePath = frame.f_code.co_filename

	parentModule = None
	for name in  sys.modules :
		moduleInfo = str(sys.modules[name])
		if (moduleInfo.find(parentModulePath) != -1) : 
			parentModule = sys.modules[name] # 상위 모듈 획득
			break
		elif (moduleInfo.find("__main__") != -1 and \
			moduleInfo.find("<frozen>") != -1) :
			# freeze로 컴파일한경우...
			parentModule = sys.modules[name] # 상위 모듈 획득
			break

	return parentModule

def Version() :
	return __VERSION__ 

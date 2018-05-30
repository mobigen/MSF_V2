
include ./MakeVars

all:
	(cd lib/src/xml; make)
	(cd lib/src/common; make)
	(cd lib/src/core; make)
	(cd lib/src/OpenThreads; make)
	(cd lib/MD5-0.5; make build; make install)
	(cd lib/StrUtil-2.4; make build; make install)
	(cd lib/PthX-2.0.3; make build; make install)
	(cd lib/SecureProxy-0.1; make build; make install)
	(cd src/common; make)
ifeq ($(ORA_ENABLE),-DORACLE_ENABLE)
	(cd src/ora; make)
endif
	(cd src/agent; make)

clean:
	(cd lib/src/xml; make clean)
	(cd lib/src/common; make clean)
	(cd lib/src/core; make clean)
	(cd lib/src/OpenThreads; make clean)
	(cd lib/MD5-0.5; make clean)
	(cd lib/StrUtil-2.4; make clean)
	(cd lib/PthX-2.0.3; make clean)
	(cd lib/SecureProxy-0.1; make clean)
	(cd src/common; make clean)
ifeq ($(ORA_ENABLE),-DORACLE_ENABLE)
	(cd src/ora; make clean)
endif
	(cd src/agent; make clean)
	(cd lib/lib; rm -f *.a)

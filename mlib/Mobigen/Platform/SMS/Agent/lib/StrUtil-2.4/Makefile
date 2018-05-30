PROFILE_FLAG = -pg
PROFILE_FLAG =

THREAD_FLAGS = -D_REENTRANT -D_PTHREADS

CXX = g++ -fPIC -g -W -Wall $(PROFILE_FLAG) $(THREAD_FLAGS)
CXXO = g++ -g -fPIC -O4 -DNDEBUG $(THREAD_FLAGS)

AR = ar

all:
	@echo "Usage: make build"
	@echo "       make clean"
	@echo "       make install      <== ../include ../lib"

build:
	@make StrUtil.o StrUtil.oo StrUtil_test.exe
	@make libStrUtil_debug.a libStrUtil.a
	@make libStrUtil.so

install:
	cp *.h ../include
	cp lib*.a ../lib

clean:
	\rm -f *.o *.oo *.exe *.so *.a core core.[0-9]* *.stackdump gmon.out


StrUtil_test.exe: StrUtil_test.o StrUtil_simpleMatch.o
	$(CXX) -o $@ StrUtil_test.o StrUtil_simpleMatch.o

StrUtil_test.o: StrUtil.cpp StrUtil.h
	$(CXX) -c -o $@ StrUtil.cpp -DSTR_UTIL_TEST

#{
StrUtil.o: StrUtil.cpp StrUtil.h
	$(CXX) -c -o $@ StrUtil.cpp

StrUtil.oo: StrUtil.cpp StrUtil.h
	$(CXXO) -c -o $@ StrUtil.cpp
#}

#{
StrUtil_simpleMatch.o: StrUtil_simpleMatch.cpp StrUtil.h
	$(CXX) -c -o $@ StrUtil_simpleMatch.cpp

StrUtil_simpleMatch.oo: StrUtil_simpleMatch.cpp StrUtil.h
	$(CXXO) -c -o $@ StrUtil_simpleMatch.cpp
#}

libStrUtil_debug.a: StrUtil.o StrUtil_simpleMatch.o
	$(AR) rcv $@ StrUtil.o StrUtil_simpleMatch.o

libStrUtil.a: StrUtil.oo StrUtil_simpleMatch.oo
	$(AR) rcv $@ StrUtil.oo StrUtil_simpleMatch.oo

libStrUtil.so: StrUtil.oo StrUtil_simpleMatch.oo
	$(CXX) -shared -Xlinker -Bsymbolic -o $@ \
		StrUtil.oo StrUtil_simpleMatch.oo

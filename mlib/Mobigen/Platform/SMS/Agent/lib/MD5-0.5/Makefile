THREAD_FLAGS = -D_REENTRANT -D_PTHREADS -D_POSIX_REENTRANT_FUNCTIONS -D_POSIX_THREADS -D_THREAD_SAFE 


CXX = g++ -g -fPIC -W -Wall $(THREAD_FLAGS)
CXXO = g++ -g -fPIC -O4 -DNDEBUG $(THREAD_FLAGS)
AR = ar

all:
	@echo "Usage: make clean"
	@echo "       make build"
	@echo "       make build-hp"
	@echo "       make install    <==== ../include ../lib"

clean: 
	@rm -f *.o *.oo *.exe core *.a

build:
	@make MD5LIB.o
	@make MD5.o MD5.oo MD5_test.o MD5_test.exe
	@make libMD5_debug.a libMD5.a

build-hp:
	make build LIBNET="-lpthread"

install:
	@cp -f *.h ../include
	@cp -f *.a ../lib

MD5_test.exe: MD5_test.o MD5LIB.o
	$(CXX) -o $@ MD5_test.o MD5LIB.o $(LIBNET) -lpthread

MD5_test.o: MD5.cpp MD5.h
	$(CXX) -c -o $@ MD5.cpp -DMD5_TEST

MD5LIB.o: MD5LIB.h MD5LIB.c
	$(CXX) -c -o $@ MD5LIB.c

MD5.o: MD5.cpp MD5.h
	$(CXX) -c -o $@ MD5.cpp

MD5.oo: MD5.cpp MD5.h
	$(CXXO) -c -o $@ MD5.cpp

libMD5.a: MD5.oo MD5LIB.o
	$(AR) rcv $@ MD5.oo MD5LIB.o

libMD5_debug.a: MD5.o MD5LIB.o
	$(AR) rcv $@ MD5.o MD5LIB.o

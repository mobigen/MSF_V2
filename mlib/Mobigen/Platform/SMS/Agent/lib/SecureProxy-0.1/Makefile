THREAD_FLAGS = -D_REENTRANT -D_PTHREADS -D_POSIX_REENTRANT_FUNCTIONS -D_POSIX_THREADS -D_THREAD_SAFE

CXX = g++ -g -fPIC -W -Wall $(THREAD_FLAGS)
CXXO = g++ -g -fPIC -O4 -DNDEBUG $(THREAD_FLAGS)
AR = ar

LIB = ../lib/libStrUtil.a ../lib/libMD5.a ../lib/libPthTask.a \
	 ../lib/libPthSocket.a -lpthread

INC = -I../include -I.

all:
	@echo "Usage: make clean"
	@echo "       make build"
	@echo "       make install    <==== ../include ../lib"

clean:
	@rm -f *.o *.oo *.exe core *.a

build:
	make SecureProxy.o
	make SecureProxy.oo
	make libSecureProxy.a

install:
	cp -f SecureProxy.h ../include
	cp -f libSecureProxy.a ../lib

TestServer.exe: TestServer.o SecureProxy.o $(LIB)
	$(CXX) -o $@ TestServer.o SecureProxy.o $(LIB)

TestClient.exe: TestClient.o SecureProxy.o $(LIB)
	$(CXX) -o $@ TestClient.o SecureProxy.o $(LIB)

TestServer.o: TestServer.o SecureProxy.h
	$(CXX) -c -o $@ TestServer.cpp $(INC)

TestClient.o: TestClient.o SecureProxy.h
	$(CXX) -c -o $@ TestClient.cpp $(INC)

SecureProxy.o: SecureProxy.h SecureProxy.cpp
	$(CXX) -c -o $@ SecureProxy.cpp $(INC)

SecureProxy.oo: SecureProxy.h SecureProxy.cpp
	$(CXXO) -c -o $@ SecureProxy.cpp $(INC)

libSecureProxy.a: SecureProxy.oo
	$(AR) rcv $@ SecureProxy.oo

libSecureProxy_debug.a: SecureProxy.o
	$(AR) rcv $@ SecureProxy.o

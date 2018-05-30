INC_PTH = -I./include
LIB_PTH = -L./lib -lpthread

# LIBNET = -lsocket -lnsl -lposix4 -lpthread

# LIB_CCMALLOC = ../ccmalloc-0.4.0/lib/libccmalloc.a -ldl
# LIBNET = -lsocket -lnsl

# 다음 명령어를 정확하게 지정해 줘야 함.
CXX = g++ -g -fPIC -W -Wall -D_REENTRANT -D_PTHREADS
CXXO = g++ -g -fPIC -O4 -DNDEBUG -D_REENTRANT -D_PTHREADS
AR = ar

Pth_dir = `pwd`

all:
	@echo "Usage: make clean"
	@echo "       make build"
	@echo "       make build-solaris     <== -lnsl -lsocket"
	@echo "       make build-msg         <=== using IPC Msg"
	@echo "       make install           <==== ../lib ../include"

install:
	cp -f include/*.h ../include
	cp -f lib/*.a ../lib

build:
	@make ./o/PthTask.o ./o/PthTask.oo
	@make ./o/PthMutex.o ./o/PthMutex.oo
	@make ./o/PthSocket.o ./o/PthSocket.oo
	@make ./o/PthServer.o ./o/PthServer.oo
	@cp -f *.h ./include
	@make ./lib/libPthSocket_debug.a ./lib/libPthSocket.a
	@make ./lib/libPthTask_debug.a ./lib/libPthTask.a
	@make ./lib/libPthMutex_debug.a ./lib/libPthMutex.a
	@make ./lib/libPthServer_debug.a ./lib/libPthServer.a
	@make ./lib/libPthFramework_debug.a ./lib/libPthFramework.a

build-solaris:
	make build LIBNET="-lnsl -lsocket" LIB_PTH="-lposix4 -lpthread"

build-msg:
	@make ./o/PthMsg.o ./o/PthMsg.oo
	@make PthMsg_test.exe
	@make ./lib/libPthMsg_debug.a ./lib/libPthMsg.a

PthServer.exe: ./o/PthServer_exe.o ./o/PthTask.o ./o/PthSocket.o
	$(CXX) -o $@ ./o/PthServer_exe.o \
		./o/PthTask.o ./o/PthSocket.o \
		$(LIB_PTH) $(LIBNET) \
		$(LIB_CCMALLOC)

./o/PthServer_exe.o: PthServer.cpp PthServer.h
	$(CXX) -c -o $@ PthServer.cpp $(INC_PTH) -DPTHSERVER_TEST

./o/PthServer.o: PthServer.cpp PthServer.h
	$(CXX) -c -o $@ PthServer.cpp $(INC_PTH)

./o/PthServer.oo: PthServer.cpp PthServer.h
	$(CXXO) -c -o $@ PthServer.cpp $(INC_PTH)

#{
PthSocket_Send.exe: ./o/PthSocket_Send.o ./o/PthTask.o ./o/PthSocket.o
	$(CXX) -o $@ ./o/PthSocket_Send.o \
		./o/PthTask.o ./o/PthSocket.o $(LIB_PTH) $(LIBNET)

./o/PthSocket_Send.o: PthSocket_Send.cpp
	$(CXX) -c -o $@ PthSocket_Send.cpp $(INC_PTH) -DPTH_TEST

#}

#{
PthSocket_test2.exe: ./o/PthSocket_test2.o ./o/PthTask.o ./o/PthSocket.o
	$(CXX) -o $@ ./o/PthSocket_test2.o \
		./o/PthTask.o ./o/PthSocket.o $(LIB_PTH) $(LIBNET)

./o/PthSocket_test2.o: PthSocket_test2.cpp
	$(CXX) -c -o $@ PthSocket_test2.cpp $(INC_PTH) -DPTH_TEST

#}
PthSocket_test1.exe: ./o/PthSocket_test1.o ./o/PthTask.o ./o/PthSocket.o
	$(CXX)  -o $@ ./o/PthSocket_test1.o \
		./o/PthTask.o ./o/PthSocket.o $(LIB_PTH) $(LIBNET)

./o/PthSocket_test1.o: PthSocket_test1.cpp
	$(CXX) -c -o $@ PthSocket_test1.cpp $(INC_PTH) -DPTH_TEST

#{
PthTask.exe: ./o/PthTask_exe.o
	$(CXX)  -o $@ ./o/PthTask_exe.o $(LIB_PTH) $(LIBNET) 

./o/PthTask_exe.o: PthTask.cpp PthTask.h
	$(CXX) -c -o $@ PthTask.cpp $(INC_PTH) -DPTH_TEST

./o/PthTask.o: PthTask.cpp PthTask.h
	$(CXX) -c -o $@ PthTask.cpp $(INC_PTH)

./o/PthTask.oo: PthTask.cpp PthTask.h
	$(CXXO) -c -o $@ PthTask.cpp $(INC_PTH)
#}

#{
PthMutex_test.exe: ./o/PthMutex_exe.o ./o/PthTask.o
	$(CXX)  -o $@ ./o/PthMutex_exe.o ./o/PthTask.o $(LIB_PTH) $(LIBNET) 

./o/PthMutex_exe.o: PthMutex.cpp PthMutex.h
	$(CXX) -c -o $@ PthMutex.cpp $(INC_PTH) -DPTHMUTEX_TEST

./o/PthMutex.o: PthMutex.cpp PthMutex.h
	$(CXX) -c -o $@ PthMutex.cpp $(INC_PTH)

./o/PthMutex.oo: PthMutex.cpp PthMutex.h
	$(CXXO) -c -o $@ PthMutex.cpp $(INC_PTH)
#}

PthSocket.exe: ./o/PthSocket_exe.o
	$(CXX) -o $@ ./o/PthSocket_exe.o $(LIB_PTH) $(LIBNET)

./o/PthSocket_exe.o: PthSocket.cpp PthSocket.h
	$(CXX) -c -o $@ PthSocket.cpp $(INC_PTH) -DPTHSOCKET_TEST

./o/PthSocket.o: PthSocket.cpp PthSocket.h
	$(CXX) -c -o $@ PthSocket.cpp $(INC_PTH)

./o/PthSocket.oo: PthSocket.cpp PthSocket.h
	$(CXXO) -c -o $@ PthSocket.cpp $(INC_PTH)

PthMsg_test.exe: ./o/PthMsg_test.o
	$(CXX) -o $@ ./o/PthMsg_test.o ./o/PthTask.o $(LIB_PTH)

./o/PthMsg_test.o: PthMsg.cpp PthMsg.h
	$(CXX) -c -o $@ PthMsg.cpp $(INC_PTH) -DPTH_MSG_TEST

./o/PthMsg.o: PthMsg.cpp PthMsg.h
	$(CXX) -c -o $@ PthMsg.cpp $(INC_PTH)

./o/PthMsg.oo: PthMsg.cpp PthMsg.h
	$(CXXO) -c -o $@ PthMsg.cpp $(INC_PTH)

PthFramework_test.exe: ./o/PthFramework_test.o ./o/PthServer.o \
		./o/PthSocket.o ./o/PthTask.o
	$(CXX) -o $@ ./o/PthFramework_test.o ./o/PthServer.o \
		./o/PthSocket.o ./o/PthTask.o $(LIBNET) $(LIB_PTH)

#-lsocket

./o/PthFramework_test.o: PthFramework.cpp
	$(CXX) -c -o $@ PthFramework.cpp $(INC_PTH) -DPTH_FRAMEWORK_TEST

./o/PthFramework.o: PthFramework.cpp
	$(CXX) -c -o $@ PthFramework.cpp $(INC_PTH)

./o/PthFramework.oo: PthFramework.cpp
	$(CXXO) -c -o $@ PthFramework.cpp $(INC_PTH)

PthServerTest1.exe: PthServerTest1.cpp \
		./o/PthServer.o ./o/PthTask.o ./o/PthSocket.o
	$(CXX) -o $@ PthServerTest1.cpp \
		./o/PthServer.o ./o/PthTask.o ./o/PthSocket.o \
		$(LIB_PTH)

PthServerTest2.exe: PthServerTest2.cpp \
		./o/PthServer.o ./o/PthTask.o ./o/PthSocket.o
	$(CXX) -o $@ PthServerTest2.cpp \
		./o/PthServer.o ./o/PthTask.o ./o/PthSocket.o \
		$(LIB_PTH)
#{
PthMutex_test2.exe: PthMutex_test2.o
	$(CXX) -o $@ PthMutex_test2.o ../lib/libStrUtil.a \
		./lib/libPthMutex.a ./lib/libPthTask.a $(LIB_PTH)
PthMutex_test2.o: PthMutex_test2.cpp
	$(CXX) -c -o $@ PthMutex_test2.cpp $(INC_PTH) -I../include
#}

#{
PthMutex_test3.exe: PthMutex_test3.o
	$(CXX) -o $@ PthMutex_test3.o ../lib/libStrUtil.a \
		./lib/libPthMutex.a ./lib/libPthTask.a $(LIB_PTH)

PthMutex_test3.o: PthMutex_test3.cpp
	$(CXX) -c -o $@ PthMutex_test3.cpp $(INC_PTH) -I../include
#}


#{
./lib/libPthTask_debug.a: ./o/PthTask.o
	$(AR) rcv $@ ./o/PthTask.o

./lib/libPthTask.a: ./o/PthTask.oo
	$(AR) rcv $@ ./o/PthTask.oo

./lib/libPthMutex_debug.a: ./o/PthMutex.o
	$(AR) rcv $@ ./o/PthMutex.o

./lib/libPthMutex.a: ./o/PthMutex.oo
	$(AR) rcv $@ ./o/PthMutex.oo

./lib/libPthSocket_debug.a: ./o/PthSocket.o
	$(AR) rcv $@ ./o/PthSocket.o

./lib/libPthSocket.a: ./o/PthSocket.oo
	$(AR) rcv $@ ./o/PthSocket.oo

./lib/libPthServer_debug.a: ./o/PthServer.o
	$(AR) rcv $@ ./o/PthServer.o

./lib/libPthServer.a: ./o/PthServer.oo
	$(AR) rcv $@ ./o/PthServer.oo

./lib/libPthMsg_debug.a: ./o/PthMsg.o
	$(AR) rcv $@ ./o/PthMsg.o

./lib/libPthMsg.a: ./o/PthMsg.oo
	$(AR) rcv $@ ./o/PthMsg.oo

./lib/libPthFramework_debug.a: ./o/PthFramework.o
	$(AR) rcv $@ ./o/PthFramework.o

./lib/libPthFramework.a: ./o/PthFramework.oo
	$(AR) rcv $@ ./o/PthFramework.oo
#}

clean:
	rm -f ./lib/*.so.*
	rm -f core core.[0-9]* ./lib/lib*.a ./lib/lib*.la ./lib/*.so ./o/*.o
	rm -f *.stackdump ./o/*.oo *.exe */*.o */*.lo */*.exe
	rm -f *.o *.oo

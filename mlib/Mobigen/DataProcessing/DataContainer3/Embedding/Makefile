CC=/usr/bin/g++ -D_REENTRANT -O2

SSCOPTS=-DMT -DCMFILE_REORG_1 -DSS_SOLARIS32 -DSSMT -DSS_TASK_UNAVL -DSS_STRICT -DDEBPRMCHK -D__EXTENSIONS__ -D__DTMF
CCOPTS=$(SSCOPTS)

PYVERSION=2.4
PYPREFIX=/home/mobigen/usr/Python
INCLUDES=-I$(PYPREFIX)/include/python$(PYVERSION) -I./include
LIBS=-L$(PYPREFIX)/lib/python$(PYVERSION)/config
LDFLAGS=-avoid-version -module -no-undefined -Xlinker -export-dynamic
SRC=./src

OBJS =	demo.o 

demo: $(OBJS) libDataContainer.a
	$(CC) -o demo $(LIBS) $(OBJS) $(INCLUDES) -lpython$(PYVERSION) -lpthread -lnsl libDataContainer.a -ldb -lpthread -lnsl -ldl -lm -lutil $(LDFLAGS)

demod: $(OBJS) libDataContainer.so
	$(CC) -o demo $(OBJS) $(INCLUDES) -lpython$(PYVERSION) -lpthread -lnsl libDataContainer.so

libDataContainer.a : DataContainer.o
	ar crv libDataContainer.a DataContainer.o
	ranlib libDataContainer.a

libDataContainer.so:
	gcc -fPIC -g -c -Wall src/DataContainer.c -lpython$(PYVERSION) $(INCLUDES)
	gcc -shared -Wl,-soname,libDataContainer.so -o libDataContainer.so DataContainer.o -lc

clean:
	@rm -f *.o *.db* demo

demo.o: $(SRC)/demo.c
	$(CC) $(CCOPTS) -c $(INCLUDES) $(SRC)/demo.c

DataContainer.o: $(SRC)/DataContainer.cpp
	$(CC) $(CCOPTS) -c $(INCLUDES) $(SRC)/DataContainer.cpp


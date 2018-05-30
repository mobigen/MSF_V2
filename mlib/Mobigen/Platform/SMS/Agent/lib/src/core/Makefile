#
# Descript : Make KernelView Libraries
# Platform : SunOS
#
# $ID
#

include ../../../MakeVars

#MISC	=	$(HOME)/ktfsm/lib/src/misc
#IFLAGS=-I$(MISC)

#
# compile options

ATARGET=$(TOP_DIR)/lib/libsccore.a

CORE_INC_DIR = \
	-I./ \
	-I../common

#
# object
OBJS	=	sc_core.o \
		sc_system.o  \
		sc_network.o \
		cygwin.o

#
# default
all: $(OBJS) $(ATARGET)

$(ATARGET): $(OBJS)
	$(AR) cr $@ $(OBJS)

test:
	$(CPP) -L../.. $(CORE_INC_DIR) -o coreview.exe scCoreView.c $(ATARGET) -lscmisc  -lperfstat

.c.o:
	$(CORULE)

.cpp.o:
	$(CPPORULE)

clean:
	rm -rf $(OBJS) $(ATARGET) coreview.exe


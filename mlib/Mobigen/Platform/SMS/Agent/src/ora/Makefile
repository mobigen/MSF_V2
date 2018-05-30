#

include ../../makedir/env_oracle.mk
include ../../MakeVars


DSRCS = 

HOBJS = \


COBJS = 

ORA_OBJS = \
    COraConfCollector.o\
    COraHitRatioCollector.o\
    COraTopSqlCollector.o\
    COraSessionCountCollector.o\
    COraDBLinkCollector.o\
    COraTableSpaceCollector.o\
    COraRollbackCollector.o\
    CDBPool.o\
    CDBSession.o

DSRCS = \
    COraConfCollector.cpp\
    COraHitRatioCollector.cpp\
    COraTopSqlCollector.cpp\
    COraSessionCountCollector.cpp\
    COraDBLinkCollector.cpp\
    COraTableSpaceCollector.cpp\
    COraRollbackCollector.cpp\
    CDBSession.cpp

# Macro define

ATARGETS = ../../lib/libscora.a


all : $(ATARGETS)

$(ATARGETS): $(ORA_OBJS)
	$(AR) cr $@ $(ORA_OBJS)

.h.o: $(SRC)
	$(HORULE)


%.o: %.pc
	$(PROC) iname=$< $(PROCFLAGS) $(PROCPPFLAGS)\
		THREADS=YES ireclen=128 include=/usr/include include=$(ORACLE_HOME)/precomp/public include=$(TOP_DIR)/include/$(SYSTEM_TYPE) include=$(TOP_DIR)/include/ora include=$(TOP_DIR)/lib/src/common include=$(TOP_DIR)/lib/src/core include=$(TOP_DIR)/include/common 
	$(CPP) -c $(CFLAGS) $(INC_DIR) $(ORA_INC_DIR) $*.cpp
#	$(RM) $*.cpp

.cpp.o:
	$(CPPORULE)

clean:
	$(RM) -f ./*.o ./*.lis core $(ATARGETS) $(DSRCS)

start:
	$(HOME)/bin/$(CTARGETS)

debug:
	gdb $(CTARGETS) core

strip:
	strip $(HOME)/bin/$(CTARGETS)

new:
	$(MAKE) clean
	$(MAKE)

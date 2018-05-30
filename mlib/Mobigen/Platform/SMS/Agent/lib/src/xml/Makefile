#

include ../../../MakeVars

DSRCS = 

COBJS = 

ORA_OBJS = \
    tinystr.o\
    tinyxml.o\
	tinyxmlerror.o\
	tinyxmlparser.o

# Macro define

ATARGETS = $(TOP_DIR)/lib/libtinyxml.a

all : $(ATARGETS)

$(ATARGETS): $(ORA_OBJS)
	$(AR) cr $@ $(ORA_OBJS)

.cpp.o:
	$(CPPORULE)

clean:
	$(RM) -f ./*.o core $(ATARGETS) $(DSRCS)

strip:
	strip $(HOME)/bin/$(CTARGETS)

new:
	$(MAKE) clean
	$(MAKE)

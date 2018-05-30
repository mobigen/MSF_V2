#

include ../../MakeVars

CPPTARGET = $(TOP_DIR)/bin/scagent.exe

DSRCS = 

COBJS = \
	main.o

# Macro define

all : $(CPPTARGET)

$(CPPTARGET):$(OBJS)
	$(CPP) -g $(CPPFLAGS) $(INC_DIR) $(LIB_DIR) $(ORA_LIB_DIR) -o $@ $(OBJS) $(LIBS) $(PROXY_OBJS) $(ORA_LIBS)
	@echo ' '
	@echo '                  [3m[7m SMS Agent compile complete !! [2m[0m'
	@echo ' '

.cpp.o:
	$(CPPORULE)

clean:
	$(RM) -f $(COBJS) core.* $(CPPTARGET) $(DSRCS)

start:
	$(RM) -f $(CPPTARGET)
	-make
	$(CPPTARGET)

debug:
	gdb $(CPPTARGET) core

strip:
	strip $(HOME)/bin/$(CPPTARGET)

new:
	$(RM) -f $(CPPTARGET)
	$(MAKE)

#
# Descript : Make KernelView Libraries
# Platform : SunOS
#
# $ID
#

include ../../../MakeVars


#
# compile options

ATARGET=$(TOP_DIR)/lib/libscmisc.a

#
# object
OBJS	= u_bfsearch.o \
	u_exit.o \
	u_signal.o \
	u_environ.o \
	u_debug.o \
	u_user.o \
	u_dlist.o \
	u_missing.o \
	u_file.o \
	u_operate.o \
	u_process.o \
	u_time.o \
	u_tokenize.o

#
# default
all: $(OBJS) $(ATARGET)

$(ATARGET):
	$(AR) cr $@ $(OBJS)

.c.o:
	$(CORULE)

clean:
	rm -rf $(OBJS) $(ATARGET)




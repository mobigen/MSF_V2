#

include ../../MakeVars

DSRCS = 

COBJS = 

OBJS = \
	CProcessHealthCollector.o \
	CAlarmProcessor.o \
	CAgentConfCollector.o \
	CSyslogMonitorThread.o \
	CLogCheckCollector.o \
	CShellCommandCollector.o \
	CNetworkSessionCollector.o \
	CPatchConfCollector.o \
	CSWConfCollector.o \
	CCPUConfCollector.o \
	CMemoryConfCollector.o \
	CDiskConfCollector.o \
	CHostConfCollector.o \
	CIFConfCollector.o \
	CCPUPerfCollector.o \
	CCPULoadPerfCollector.o \
	CMemoryPerfCollector.o \
	CDiskPerfCollector.o \
	CDiskIOPerfCollector.o \
	CIFPerfCollector.o \
	CProcessPerfCollector.o \
	CTopMemProcessPerfCollector.o \
	CTopCPUProcessPerfCollector.o \
	CCollector.o \
	CKernelCore.o \
	CItem.o \
	CItemInstance.o \
	CItemCondition.o \
	CAgentConfigVar.o \
	CSocketWorker.o \
	CSocketWorkerThread.o \
	CProtocolProcessor.o \
	SCThread.o \
	CSchedulerThread.o \
	ThreadObserver.o \
	ThreadReporter.o \
	CRegex.o \
	CMessageFormatter.o \
	CAlarmProcessor.o \
	CMisc.o \
    CQueue.o

# Macro define

ATARGETS = ../../lib/libsccommon.a


all : $(ATARGETS)

$(ATARGETS): $(OBJS)
	$(AR) cr $@ $(OBJS)

.cpp.o:
	$(CPPORULE)

clean:
	$(RM) -f $(OBJS) core $(ATARGETS) $(DSRCS)

new:
	$(MAKE) clean
	$(MAKE)

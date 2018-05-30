
/*
 *
 * (C) COPYRIGHT h9mm. 2005
 *
 */

#ifndef _SC_COMMON_H_
#define _SC_COMMON_H_ 1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>

#if defined(AIX)
#include <sys/systemcfg.h>
#endif

#if defined(SunOS)
#include <sys/types.h>
#include <sys/kstat.h>
#include <sys/ddi.h>
#include <sys/sunddi.h>
#include <kstat.h>
#endif

#if defined(HPUX)
#include <sys/param.h>
#include <sys/pstat.h>
#include <sys/mib.h>
#endif

#if defined(CYGWIN)
#include "cygwin.h"
#endif

#include "u_operate.h"
#include "u_dlist.h"
/* #include "u_user.h" */

typedef h_node_t v_list_t;

#define SC_OK   1
#define SC_ERR -1

#define SC_STRING_MIN_LEN 32
#define SC_BINFO_STR_LEN 36
#define SC_STRING_AVR_LEN 128
#define SC_STRING_MAX_LEN 256

/* MOBIGEN Secure Agent Argument */
#define SC_STRING_ARG_LEN 1024	/* struct _scPSInfo.args */


#define SC_MAX_CPU_NUM 32

#ifdef __cplusplus
extern "C" {
#endif

#define SC_CPUSTAT_SYS  0
#define SC_CPUSTAT_USR 1
#define SC_CPUSTAT_IDLE 2
#define SC_CPUSTAT_ETC 3
#define SC_CPUSTAT_NUM 4

#define SC_IF_TYPE_ETHERNET 6
#define SC_IF_TYPE_LOOPBACK	24

#define	SC_TCP_ESTABLISHED  0
#define	SC_TCP_SYN_SENT		1
#define	SC_TCP_SYN_RECV		2
#define	SC_TCP_FIN_WAIT1	3
#define	SC_TCP_FIN_WAIT2	4
#define	SC_TCP_TIME_WAIT	5
#define	SC_TCP_CLOSE		6
#define	SC_TCP_CLOSE_WAIT	7
#define	SC_TCP_LAST_ACK		8
#define	SC_TCP_LISTEN		9
#define	SC_TCP_CLOSING		10
#define	SC_TCP_UNKNOWN		11

#define	SC_PS_SLEEP    'S'
#define	SC_PS_STOPPED  'T'
#define	SC_PS_DEFUNC   'Z'
#define	SC_PS_RUNNING  'R'
#define	SC_PS_SWAPPED  'W'
#define	SC_PS_UNKNOWN  '?'

#define	SC_SUM_BY_DEFAULT	0
#define	SC_SUM_BY_PNAME		1
#define	SC_SUM_BY_PARGS		2
#define	SC_SUM_BY_UNAME		3

#define	SC_SORT_BY_DEFAULT	0
#define	SC_SORT_BY_PID		1
#define	SC_SORT_BY_PNAME	2
#define	SC_SORT_BY_PARGS	3
#define	SC_SORT_BY_UNAME	4
#define	SC_SORT_BY_PCPU 	5
#define	SC_SORT_BY_PMEM 	6
#define	SC_SORT_BY_NPROC	7


/* process cache info (to calculate the cpustat per process) */
#ifndef NR_TASKS
#define NR_TASKS 2560
#endif

#define HASH_SIZE (NR_TASKS * 3 / 2)
#define HASH(x) (((x) * 1686629713U) % HASH_SIZE)

#if defined(SunOS)
#ifndef FSCALE
#define FSHIFT  8               /* bits to right of fixed binary point */
#define FSCALE  (1<<FSHIFT)
#endif /* FSCALE */

#define loaddouble(la) ((double)(la) / FSCALE)
#define Calcla(la, tm) loaddouble(la)

#define KCTL(K) (K)->kctl
#endif /* SunOS */

#if defined(HPUX)  || defined(AIX)
#define Calcla(la, tm) la = la
#endif /* HPUX */

#if defined(Linux)
#define Calcla(la, tm) ((double)(la)/100)
#endif

#if defined(CYGWIN) 
#define Calcla(la, tm) ((double)(la)/100)
#endif

typedef struct _scPSCache
{
	int pid;
	double cputime; /* HZ (1/100 Sec) */
	int toggle;
} scPSCache;

/* scCore data struct */
typedef struct _scCore
{
#if defined(AIX) || defined(Linux) || defined (CYGWIN)
	scPSCache pscache[HASH_SIZE];
	struct timeval pstmvalue;
	int    toggle;
#else
# if defined(SunOS)
	kstat_ctl_t *kctl;
# else
#  if defined(HPUX)
	struct pst_static pstatic;
	int maxcpu;
	int pstatus_index;
	
	/* ttynamelist */
	v_list_t *ttynames;

	/* short cut */
#define __physical pstatic.physical_memory
#define __maxproc  pstatic.max_proc
#  endif
# endif
#endif

#if defined(CYGWIN)
	HQUERY h_Diskquery;
	vector<ITEM> disk_item;				// disk io stat
	HQUERY h_Networkquery;
	vector<ITEM> network_item;			// network packet stat
	LARGE_INTEGER curFreq;
	int cpuNum;
	map<int, ProcessInfo> processList;  // CPU 사용시간을 저장
#endif // CYGWIN

} scCore;

typedef struct _scSysInfo
{
	/* hardcoded one */
	char pseudoname[SC_STRING_MIN_LEN];
	char pseudoversion[SC_STRING_MIN_LEN];
	char vendor[SC_STRING_MIN_LEN];

	char osname[SC_STRING_MIN_LEN];
	char version[SC_STRING_MIN_LEN];
	char release[SC_STRING_MIN_LEN];
	char hostname[SC_STRING_MIN_LEN];
	char machine[SC_STRING_MIN_LEN];
	char platform[SC_STRING_MIN_LEN];
	char hwserial[SC_STRING_MIN_LEN];
	char cputype[SC_STRING_MIN_LEN];
	unsigned long  clockspeed;
	unsigned int  ncpu;
	char spare_1[SC_STRING_MIN_LEN];
	char spare_2[SC_STRING_MIN_LEN];
	char spare_3[SC_STRING_MIN_LEN];
} scSysInfo;

typedef struct _scCpuRawStatus
{
	int id;
	unsigned long ticks[SC_CPUSTAT_NUM];
} scCpuRawStatus;

typedef struct _scCpuStatus
{
	int id;
	double total; /* 100 - idle == user + system + ?? */
	double user;
	double system;
	double idle;
	double etc;
} scCpuStatus;

typedef struct _scMemStatus
{
	unsigned long m_total;
	unsigned long m_used;
	double  m_usage;
	unsigned long s_total;
	unsigned long s_used;
	double  s_usage;
	unsigned long m_proc;
	unsigned long m_cache;
	unsigned long spare_1;
	unsigned long spare_2;
	unsigned long spare_3;
} scMemStatus;

typedef struct _scVMRawStatus
{
	unsigned long runqueue;
	unsigned long pagein;
	unsigned long pageout;
	unsigned long swapin;
	unsigned long swapout;
	unsigned long pagefault;
	unsigned long scanrate;
	unsigned long spare_1; 
	unsigned long spare_2;
	unsigned long spare_3;

	/* load average */
	double la_1min;
	double la_5min;
	double la_15min;
} scVMRawStatus;

typedef struct _scVMStatus
{
	unsigned long runqueue;
	unsigned long pagein;
	unsigned long pageout;
	unsigned long swapin;
	unsigned long swapout;
	unsigned long pagefault;
	unsigned long scanrate;
	unsigned long spare_1;
	unsigned long spare_2;
	unsigned long spare_3;

	/* load average */
	double la_1min;
	double la_5min;
	double la_15min;
} scVMStatus;

typedef struct _scSysStatus
{
	scCpuStatus cpu;
	scMemStatus mem;
	scVMStatus  vm;
} scSysStatus;

typedef struct _scIORawStatus
{
	char device[64];
	unsigned long nread;    /* read byte   */
	unsigned long nwritten; /* write bute  */
	unsigned long reads;    /* read count  */
	unsigned long writes;   /* write count */
	unsigned long spare_1;
	unsigned long spare_2;
	unsigned long spare_3;
} scIORawStatus;

typedef struct _scIOStatus
{
	char device[64];
	double nread;    /* read byte */
	double nwritten; /* write byte */
	double nxfer;    /* nread + nwritten */
	double reads;    /* read count */
	double writes;   /* write count */
	double xfers;    /* reads + writes */
	double spare_1;
	double spare_2;
	double spare_3;
	double spare_4;
	double spare_5;
} scIOStatus;

typedef struct _scFSInfo
{
	char device[64];
	char mntpoint[128];
	unsigned long blocksize;
	unsigned long sizetotal;
	unsigned long sizeused;
	unsigned long sizefree;
	unsigned long sizeavail;
	double  sizeusage;
	unsigned long filetotal;
	unsigned long fileused;
	unsigned long filefree;
	unsigned long fileavail;
	double  fileusage;
} scFSInfo;

typedef struct _scInterfaceInfo
{
	/* config info */
	char   ifname[SC_STRING_MAX_LEN];
	int    index;
	int    type;
	short  mtu;
	short  flags;
	char   hwaddr[8];
	int    speed;
	struct in_addr addr;
	struct in_addr broadaddr;
	struct in_addr subnetmask;
	struct in_addr networkid;
} scInterfaceInfo;

typedef struct _scInterfaceStatus
{
	scInterfaceInfo ifinfo;
	unsigned long inoctets;
	unsigned long outoctets;
	unsigned long inpkts;
	unsigned long outpkts;
	unsigned long inerrors;
	unsigned long outerrors;
	unsigned long collisions;
	double inoctusage;
	double outoctusage;
} scInterfaceStatus;

typedef struct _scInterfaceRawStatus
{
	scInterfaceInfo ifinfo;
	unsigned long inoctets;
	unsigned long outoctets;
	unsigned long inpkts;
	unsigned long outpkts;
	unsigned long inerrors;
	unsigned long outerrors;
	unsigned long collisions;
} scInterfaceRawStatus;

typedef struct _scPSInfo
{
	int  pid;
	int  ppid;
	int  uid;
	char pname[SC_STRING_MIN_LEN];
	char args[SC_STRING_ARG_LEN];
	time_t started;
	unsigned long  cputime;
	unsigned long memused;
	double  cpuusage;
	double  memusage;
	unsigned long nproc;
	unsigned long nthrd;
	char      state;
	unsigned long spare_1;
	unsigned long spare_2;
	unsigned long spare_3;
	int processor;
	int		pcount;
} scPSInfo;

typedef struct _scTCPInfo
{
	struct in_addr localaddr;
	struct in_addr remoteaddr;
	unsigned short localport;
	unsigned short remoteport;
	unsigned sndque;
	unsigned rcvque;
	int state;
	int count;
	int islisten;
} scTCPInfo;

typedef struct _scSysPatchInfo
{
	char		name[SC_STRING_AVR_LEN];
	char		version[SC_STRING_MIN_LEN];
	char		description[SC_STRING_MAX_LEN];
}scSysPatchInfo;

typedef struct _scSysPkgInfo
{
	char		pkgtype[SC_STRING_AVR_LEN];
	char		name[SC_STRING_AVR_LEN];
	char		version[SC_STRING_MIN_LEN];
	char		description[SC_STRING_MAX_LEN];
}scSysPkgInfo;

#ifdef __cplusplus
}
#endif

#endif /* _SC_COMMON_H_ */



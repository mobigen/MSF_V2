
/*
 *
 * (C) COPYRIGHT h9mm. 2005
 *
 */

#ifndef _SC_SYSTEM_H_
#define _SC_SYSTEM_H_ 1

#include <stdio.h>
#include <stdlib.h>
#include <sys/utsname.h>
#include <sys/types.h>
#include <dirent.h>
#include <unistd.h>
#include <sys/statvfs.h>
#include "sc_common.h"

#if defined(AIX)
#include <libperfstat.h>
#include <procinfo.h>
#include <mntent.h>
#endif

#if defined(SunOS)
#include <sys/types.h>
#include <sys/kstat.h>
#include <sys/ddi.h>
#include <sys/sunddi.h>
#include <sys/mnttab.h>
#include <sys/statvfs.h>
#include <sys/vfs.h>
#include <kvm.h>
#include <sys/cpuvar.h>
#include <sys/swap.h>
#include <sys/ioctl.h>
#include <stropts.h>
#include <procfs.h>
#include <libdevinfo.h>
#endif

#if defined(HPUX)
#include <mntent.h>
#include <sys/param.h>
#include <sys/pstat.h>
#include <sys/utsname.h>
#include <sys/dk.h>
#endif

#if defined(Linux) || defined(CYGWIN)
#include <mntent.h>
#include <sys/vfs.h>
#include <dirent.h>
#include <sys/stat.h>
#endif /* Linux */

#ifdef CYGWIN
#include "cygwin.h"
#endif

#ifdef __cplusplus
extern "C" {
#endif

#define SPARESLOT 10

int scCoreSysBasicInfo(scCore *, scSysInfo *);
int scCoreSysCpuInfo(scCore *, scSysInfo *);
int scCoreSysCpuRawStatus(scCore *, scCpuRawStatus *);
int scCoreSysMultiCpuRawStatus(scCore *, scCpuRawStatus cpustat[SC_CPUSTAT_NUM], int *ncpu);
int scCoreSysMemStatus(scCore *, scMemStatus *);
int scCoreSysSwapStatus(scCore *, scMemStatus *);
int scCoreSysVMRawStatus(scCore *, scVMRawStatus *);


v_list_t *scCoreSysIORawStatus(scCore *);
v_list_t *scCoreSysFSInfo(scCore *);
v_list_t *scCoreSysPSInfo(scCore *, int);

v_list_t *scCoreSysPatchInfo(scCore *);
v_list_t *scCoreSysPkgInfo(scCore *);

#if !defined(Linux) && !defined(CYGWIN)
int psinfo_cputime2pct(scCore *, scPSInfo *, double elapsed);
#endif


#ifdef Linux
v_list_t *scCoreSysIORawStatus_2_6(scCore *);

int scCoreSysSetupEachIORawStatus(scIORawStatus *,char *);

#endif // Linux


#ifdef CYGWIN
int scCoreSysSetupEachIORawStatus(scIORawStatus *, ITEM);
#endif


int pscache_update(scCore *core);
int f_fsrch_pname(const void *v1, const void *v2);
int f_fsrch_pargs(const void *v1, const void *v2);
int f_fsrch_uname(const void *v1, const void *v2);
void psinfo_sumup_pname(v_list_t *list, scPSInfo *psinfo);
void psinfo_sumup_pargs(v_list_t *list, scPSInfo *psinfo);
void psinfo_sumup_uname(v_list_t *list, scPSInfo *psinfo);

#define percent_cpu(pp) (((double)pp)/0x8000*100)
#define percent_mem(pp) (((double)pp)/0x8000*100)

#if defined(AIX)
int scCoreSysSetupEachIORawStatus(scIORawStatus *, perfstat_disk_t *);
int scCoreSysSetupEachFSInfo(scFSInfo *fsinfo, struct mntent *ent);
int scCoreSysSetupEachPSInfo32(scCore *, scPSInfo *, struct procsinfo64 *, double );
int scCoreSysSetupEachPSInfo64(scCore *, scPSInfo *, struct procentry64 *, double );
/* for 32bit kernel */
extern int getprocs(struct procsinfo64 *, int , struct fdsinfo *, int , pid_t *, int );
/* for 64bit kernel */
extern int getprocs64(struct procentry64 *, int , struct fdsinfo64 *, int , pid_t *, int );
#endif /* AIX */


#if defined(SunOS)
int scCoreSysSetupEachFSInfo(scFSInfo *fsinfo, struct mnttab *ent);
int scCoreSysSetupEachPSInfo(scCore *core, scPSInfo *psinfo, char *dirname, double elapsed);
#else
int scCoreSysSetupEachFSInfo(scFSInfo *fsinfo, struct mntent *ent);
#endif /* SunOS */


#if defined(HPUX)
int scCoreSysSetupCpuType(char *type);

/* this is for cpuinfo */
#define HP_KA_HP200             "hp9000s200"
#define HP_KA_HP300             "hp9000s300"
#define HP_KA_HP400             "hp9000s400"
#define HP_KA_HP500             "hp9000s500"
#define HP_KA_HP700             "hp9000s700"
#define HP_KA_HP800             "hp9000s800"
#define HP_KA_HPCOMB            "hp9000"
#define HP_AA_PARISC            "PA-RISC"
#define HP_AA_MC68K             "MC680x0"

#define _PATH_SCHED_MODELS      "/usr/sam/lib/mo/sched.models"

#ifndef MNT_MNTTAB
#define MNT_MNTTAB "/etc/mnttab"
#endif

#endif /* HPUX */

#if defined(Linux) || defined(CYGWIN)

#define SC_PROC_CPUINFO 	 "/proc/cpuinfo"
#define SC_PROC_STAT 		 "/proc/stat"
#define SC_PROC_MEMINFO		 "/proc/meminfo"
#define SC_PROC_LOADAVG		 "/proc/loadavg"
#define SC_PROC_PARTITIONS	 "/proc/partitions"
#define SC_PROC_CPUINFO   	 "/proc/cpuinfo"
#define SC_PROC_NET_DEV   	 "/proc/net/dev"
#define SC_PROC_NET_TCP   	 "/proc/net/tcp"
#define SC_PROC_DISKSTATS  	 "/proc/diskstats"

int scCoreSysVMRawStatusLaStatus(scCore *core, scVMRawStatus *vmrawstat);

#ifndef CYGWIN
int scCoreSysSetupEachPSInfo(scCore *core, scPSInfo *psinfo, char *dirname, double elapsed);
#endif //

typedef struct proc_s {
	char
		user[10],       /* user name corresponding to owner of process */
		cmd[40],        /* basename of executable file in call to exec(2) */
		args[512],      /* cmdline */
		exec[128],      /* command line string vector (/proc/#/cmdline) */
		state,          /* single-char code for process state (S=sleeping) */
		ttyc[5],        /* string representation of controlling tty device */
		**environ;      /* environment string vector (/proc/#/environ) */
	int
		uid,            /* user id */
		pid,            /* process id */
		ppid,           /* pid of parent process */
		pgrp,           /* process group id */
		session,        /* session id */
		tty,            /* full device number of controlling terminal */
		tpgid,          /* terminal process group id */
		processor,      /* (ADDED) current (or most recent?) CPU */
		exit_signal,    /* (ADDED) might not be SIGCHLD */
		nlwp;           /* (ADDED) number of threads, or 0 if no clue */
	long
		priority,       /* kernel scheduling priority */
		nice,           /* standard unix nice level of process */
		size,           /* total # of pages of memory */
		resident,       /* number of resident set (non-swapped) pages (4k) */
		rss,            /* resident set size from /proc/#/stat */
		share,          /* number of pages of shared (mmap'd) memory */
		trs,            /* text resident set size */
		lrs,            /* shared-lib resident set size */
		drs,            /* data resident set size */
		dt,             /* dirty pages */
		alarm;          /* (ADDED) ? */
	unsigned long
		rtprio,         // stat            real-time priority
		sched,		// stat            scheduling class
		vsize,		// stat            number of pages of virtual memory ...
		rss_rlim,	// stat            resident set size limit?
		flags,		// stat            kernel flags for the process
		min_flt,	// stat            number of minor page faults since process start
		maj_flt,	// stat            number of major page faults since process start
		cmin_flt,	// stat            cumulative min_flt of process and child processes
		cmaj_flt;	// stat            cumulative maj_flt of process and child processes
	long long
		signal,         /* mask of pending signals */
		blocked,        /* mask of blocked signals */
		sigignore,      /* mask of ignored signals */
		sigcatch;       /* mask of caught  signals */
	unsigned long long
		utime,		// stat            user-mode CPU time accumulated by process
		stime,		// stat            kernel-mode CPU time accumulated by process
		cutime,		// stat            cumulative utime of process and reaped children
		cstime,		// stat            cumulative stime of process and reaped children
		start_time,	// stat            start time of process -- seconds since 1-1-70
		start_code,	// stat            address of beginning of code segment
		end_code,	// stat            address of end of code segment
		start_stack,	// stat            address of the bottom of stack for the process
		kstk_esp,	// stat            kernel stack pointer
		kstk_eip,	// stat            kernel instruction pointer
		wchan;		// stat (special)  address of kernel wait channel proc is sleeping in
	double
		pcpu;           /* %CPU usage (is not filled in by readproc!!!) */
} proc_t;

int psinfo_stat2proc(proc_t* P, char *dirname);
int psinfo_statm2proc(proc_t* P, char *dirname);
int psinfo_cmdline2proc(proc_t *P, char *dirname);
int psinfo_cputime2pct(scCore *core, proc_t *P, double elapsed);
#endif /* Linux */

/* system call to get program arguments */
extern int getargs(void *procinfo, int plen, char *args, int alen);
	/* procinfo:   pointer to array of procinfo struct */
	/* plen:       size of expected procinfo struct */
	/* args:       pointer to user array for arguments */
	/* alen:       size of expected argument array */

#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif /* _SC_SYSTEM_H_ */


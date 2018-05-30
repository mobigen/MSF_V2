
/*
 *
 * (C) COPYRIGHT h9mm. 2005
 *
 */

#ifndef _SC_CORE_H_
#define _SC_CORE_H_ 1


#include <stdio.h>
#include <stdlib.h>
#include <sys/utsname.h>
#include <sys/types.h>
#include <dirent.h>
#include <string.h>
#include <ctype.h>
#include <time.h>
#include <sys/time.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <netdb.h>
#include <sys/ioctl.h>


#if defined(AIX)
#include <mntent.h>
#endif
#include <sys/vfs.h>

#if defined(SunOS)
#include <kvm.h>
#include <kstat.h>
#include <sys/mntent.h>
#include <sys/cpuvar.h>
#include <sys/swap.h>
#include <sys/sockio.h>
#include <sys/ioctl.h>
#include <procfs.h>
#include <libdevinfo.h>
#include <sys/tihdr.h>
#include <inet/mib2.h>
#include <sys/dlpi.h>
#endif /* SunOS5X */

#if defined(HPUX)
#include <sys/param.h>
#include <sys/pstat.h>
#include <sys/dk.h>
#include <sys/mib.h>
#include <netinet/mib_kern.h>
#endif

#include <sys/param.h> 

#include "sc_common.h"
#include "sc_system.h"
#include "sc_network.h"

#if defined(AIX)
#include <procinfo.h>
#include <sys/procfs.h>
#include <libperfstat.h>
#include <sys/systemcfg.h>
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* create the scCore */
scCore *scCoreCreate();

/* destroy the scCore */
void scCoreDestroy(scCore *);

typedef struct _scCoreView
{
	scCore *core; /* kstat, kmem, etc */

	scCpuRawStatus u_cpurawstat;
	scCpuRawStatus m_cpurawstat[SC_MAX_CPU_NUM];

	scVMRawStatus  vmrawstat;
	struct timeval vmtmvalue;

	v_list_t *l_iorawstat;
	struct timeval iotmvalue;

	v_list_t *l_ifrawstat;
	struct timeval iftmvalue;
} scCoreView;

int scCoreViewInitalize();
scCoreView *scCoreViewCreate();
void scCoreViewDestroy(scCoreView *kvp);

int scCoreViewBasicInfo(scCoreView *, scSysInfo *);
int scCoreViewCpuStatus(scCoreView *, scCpuStatus *, scCpuStatus m_cpustat[SC_MAX_CPU_NUM], int *);
int scCoreViewOneCpuStatus(scCoreView *, scCpuStatus *);
int scCoreViewMultiCpuStatus(scCoreView *, scCpuStatus cpustat[SC_CPUSTAT_NUM], int *);

int scCoreViewMemStatus(scCoreView *, scMemStatus *);
int scCoreViewVMStatus(scCoreView *, scVMStatus *);
int scCoreViewSysStatus(scCoreView *, scSysStatus *);

v_list_t *scCoreViewIOStatus(scCoreView *);
v_list_t *scCoreViewFSInfo(scCoreView *);

v_list_t *scCoreViewPSInfo(scCoreView *, int , int );
char *scCoreViewPSStatus2Readable(char );

v_list_t *scCoreViewInterfaceInfo(scCoreView *);
v_list_t *scCoreViewInterfaceStatus(scCoreView *);
v_list_t *scCoreViewCPInfo(scCoreView *, int );
v_list_t *scCoreViewSysPatchInfo(scCoreView *);
v_list_t *scCoreViewSysPkgInfo(scCoreView *);
char *scCoreViewCPStatus2readable(int );

void scCoreViewRelease(v_list_t **list);

v_list_t *calcav_iostat(v_list_t *, v_list_t *, double );
v_list_t *calcav_ifstat(v_list_t *, v_list_t *, double );

int f_fsrch_device(const void *, const void *);
int f_fsrch_ifname(const void *, const void *);

int f_fsort_pid(const void *  , const void *);
int f_fsort_pname(const void *, const void *);
int f_fsort_pargs(const void *, const void *);
int f_fsort_uid(const void *  , const void *);
int f_fsort_pcpu(const void * , const void *);
int f_fsort_pmem(const void * , const void *);
int f_fsort_nproc(const void *, const void *);

#if defined(HPUX)

typedef struct _ttymap {
	dev_t dev;
	char name[9];
}ttymap_t;

char *scCoreLookupDevice(scCore *core, struct psdev *term);
void scCoreTTYNames(scCore *core, char *dir);
#endif

v_list_t *scCoreViewTCPInfo(scCoreView *cv, int listen_only);
char *scCoreViewTCPStatus2redable(int state);

#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif /* _SC_CORE_H_ */



/*
 *
 * (C) COPYRIGHT h9mm. 2..5
 *
 */
#if CYGWIN
#include <windows.h>
#endif //CYGWIN
#include "sc_core.h"


int scCoreViewInitalize()
{
	int err=SC_OK;
	return err;
}

#ifdef CYGWIN

int getCpuNum()
{
	SYSTEM_INFO SysInfo;
    memset(&SysInfo, '\0', sizeof (SYSTEM_INFO));
    GetSystemInfo (&SysInfo);

    return SysInfo.dwNumberOfProcessors;
}

#endif 

scCore *scCoreCreate()
{
#if defined(AIX)
	scCore *core;
	int i;

	if ((core = malloc(sizeof(scCore))) == NULL) {
		return NULL;
	}

	memset(core,0x00,sizeof(core));

	for (i = 0; i < HASH_SIZE; i++)
		(core->pscache)[i].pid = -1;

	return core;

#else
# if defined(SunOS)
	scCore *core;
	int iserror=1;

	if ((core = (scCore*)malloc(sizeof(scCore))) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] core create error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		return NULL;
	}
	else
		memset(core,0x00,sizeof(scCore));

	if ((core->kctl = kstat_open()) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] kstat_open error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		goto err_quit;
	}

	iserror = 0;
err_quit:
	if (iserror && core) 
		scCoreDestroy(core);

	return core;

# else
#  if defined(HPUX)

	scCore *core;
	struct pst_dynamic pdynamic;

	if ((core = (scCore *)malloc(sizeof(scCore))) == NULL) {
		return NULL;
	}

	if ((core->ttynames = ll_create_node(NULL,1)) == NULL) {
		/* release first */
		scCoreDestroy(core);

		return NULL;
	}

	scCoreTTYNames(core, "/dev");

	if (pstat_getstatic(&core->pstatic, sizeof(struct pst_static), 1, 0) == -1) {
		/* release first */
		scCoreDestroy(core);

		return NULL;
	}

	if (pstat_getdynamic(&pdynamic, sizeof(pdynamic), 1, 0) == -1) {
		/* release first */
		scCoreDestroy(core);

		return NULL;
	}

	/* setup maxcpu */
	core->maxcpu = pdynamic.psd_proc_cnt > SC_MAX_CPU_NUM ? SC_MAX_CPU_NUM : pdynamic.psd_proc_cnt;

	

	return core;

#  else /* HPUX */
#   if defined(Linux)  || defined(CYGWIN)

	scCore *core;
	int i;

	if ((core = (scCore *)malloc(sizeof(scCore))) == NULL) {
		return NULL;
	}

	/* initialize */
	memset(core,0x00,sizeof(scCore));

	for (i = 0; i < HASH_SIZE; i++)
		(core->pscache)[i].pid = -1;

#if defined(CYGWIN)
	core->h_Diskquery = NULL;
	core->disk_item = init_disk( & core->h_Diskquery);
	//PdhOpenQuery(NULL, 0, & core->h_Diskquery);
	core->h_Networkquery = NULL;
	core->network_item = init_network( & core->h_Networkquery);
	//PdhOpenQuery(NULL, 0, & core->h_Networkquery);
	QueryPerformanceFrequency(&core->curFreq);

	core->cpuNum = getCpuNum();
	core->processList.clear();
#endif // CYGWIN

	return core;
#   endif /* Linux or CYGWIN */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */

}

void scCoreDestroy(scCore *core)
{
#if defined(SunOS)
	if (core) {
		if (core->kctl) {
			kstat_close(core->kctl);
		}

		free(core); 
	}

	return ;
#else
#if defined(HPUX)
	if(core->ttynames)
		ll_destroy_node(&core->ttynames);
#endif
#if defined(CYGWIN)
	if (core->h_Diskquery) {
		close_handle(core->h_Diskquery);
	}
	if (core->h_Networkquery) {
		close_handle(core->h_Networkquery);
	}
#endif 
	if(core!=NULL) free(core);
#endif
}

scCoreView *scCoreViewCreate()
{
	int err = SC_OK;
	scCoreView *cv = (scCoreView *)malloc(sizeof(scCoreView));

	memset(cv,0x00,sizeof(scCoreView));
	
	if ((cv->l_iorawstat = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] node create error\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

	if ((cv->l_ifrawstat = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] node create error\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

	if ((cv->core = scCoreCreate()) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] scCore create error\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}
	
	err = 0;

err_quit:

	if (err) {
		scCoreViewDestroy(cv);
		cv = NULL;
	}

	return cv;
}

void scCoreViewDestroy(scCoreView *cv)
{
	if (cv) {
		if (cv->l_iorawstat)
			ll_destroy_node(&cv->l_iorawstat);
			
		if (cv->l_ifrawstat)
			ll_destroy_node(&cv->l_ifrawstat);

		if (cv && cv->core)
			scCoreDestroy(cv->core);

		free(cv);
	}

	return;
}

int scCoreViewBasicInfo(scCoreView *cv, scSysInfo *sysinfo)
{
	int err=SC_OK;

	if(!cv || !cv->core) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] core error!\n", __FUNCTION__, __LINE__);
#endif
		err=SC_ERR;
		goto err_quit;
	}

	if ((err = scCoreSysBasicInfo(cv->core,sysinfo)) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] can't get system basic information!\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

	if ((err = scCoreSysCpuInfo(cv->core,sysinfo)) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] can't get basic cpu information!\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

err_quit:

	return err;
}

int scCoreViewCpuStatus(scCoreView *cv, scCpuStatus *u_cpustat,
		scCpuStatus m_cpustat[SC_MAX_CPU_NUM], int *ncpu)
{
	int err=SC_OK;

	/* uni- */
	if ((err=scCoreViewOneCpuStatus(cv, u_cpustat)) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] fail to get cpu status\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

	/* multi- */
	if ((err=scCoreViewMultiCpuStatus(cv, m_cpustat, ncpu)) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] fail to get multi cpu status\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

err_quit:

	return err;
}

int scCoreViewOneCpuStatus(scCoreView *cv, scCpuStatus *cpustat)
{
	int err=SC_OK;
	long diff[SC_CPUSTAT_NUM], ticks[SC_CPUSTAT_NUM];

	scCpuRawStatus u_cpurawstat;

	if (!cv || !cv->core) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] core view is not null!\n", __FUNCTION__, __LINE__);
#endif
		err = SC_ERR;
		goto err_quit;
	}

	/* initialize first */
	memset(&u_cpurawstat,0x00,sizeof(scCpuRawStatus));

	if ((err = scCoreSysCpuRawStatus(cv->core,&u_cpurawstat)) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] get cpu raw status error!\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

	/* calculate the percentages */
	calcpc((long*)u_cpurawstat.ticks,
				(long*)cv->u_cpurawstat.ticks,
				ticks,
				diff,
				SC_CPUSTAT_NUM);

	cpustat->user   = (double)ticks[SC_CPUSTAT_USR]  / 10.0; 
	cpustat->system = (double)ticks[SC_CPUSTAT_SYS]  / 10.0;
	cpustat->etc    = (double)ticks[SC_CPUSTAT_ETC]  / 10.0; 
	cpustat->idle   = (double)ticks[SC_CPUSTAT_IDLE] / 10.0;

	/* calculate the total cpu */
	cpustat->total = 100.0 - cpustat->idle;
	cpustat->total = (0 > cpustat->total) ? 0.0 : cpustat->total;
	cpustat->id    = u_cpurawstat.id;

err_quit:
	return err;
}

int scCoreViewMultiCpuStatus(scCoreView *cv, scCpuStatus cpustat[SC_MAX_CPU_NUM], int *ncpu)
{
	long diff[SC_CPUSTAT_NUM], ticks[SC_CPUSTAT_NUM];
	int  err=SC_OK, i;

	scCpuRawStatus m_cpurawstat[SC_MAX_CPU_NUM];

	if (!cv || !cv->core) {
#ifdef DEBUG
		fprintf(stderr, "core view is null[%s,%d] !\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

	/* initialize first */
	memset(m_cpurawstat,0x00,SC_MAX_CPU_NUM*sizeof(scCpuRawStatus));

	if ((err=scCoreSysMultiCpuRawStatus(cv->core,m_cpurawstat,ncpu)) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] get multi cpu raw status error!\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

	/* scan all the cpus */
	for (i = 0; i < *ncpu; i++) {
		calcpc((long*)m_cpurawstat[i].ticks, (long*)cv->m_cpurawstat[i].ticks,
					ticks, diff, SC_CPUSTAT_NUM);

		cpustat[i].user   = (double)ticks[SC_CPUSTAT_USR]  / 10.0; 
		cpustat[i].system = (double)ticks[SC_CPUSTAT_SYS]  / 10.0;
		cpustat[i].etc    = (double)ticks[SC_CPUSTAT_ETC]  / 10.0; 
		cpustat[i].idle   = (double)ticks[SC_CPUSTAT_IDLE] / 10.0;

		/* calculate the total cpu */
		cpustat[i].total = 100.0 - cpustat[i].idle;
		cpustat[i].total = (0 > cpustat[i].total) ? 0.0 : cpustat[i].total;
		cpustat[i].id    = m_cpurawstat[i].id;
	}

err_quit:
	return err;
}

int scCoreViewMemStatus(scCoreView *cv, scMemStatus *memstat)
{
	int err=SC_OK;

	if (!cv || !cv->core) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] !\n", __FUNCTION__, __LINE__);
#endif
		err=SC_ERR;
		goto err_quit;
	}

	if ((err=scCoreSysMemStatus(cv->core, memstat)) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] can't get memory status!\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

	if ((err=scCoreSysSwapStatus(cv->core, memstat)) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "can't get swap memory status[%s,%d] !\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

	/* calculate the usage */
	memstat->m_usage = (double)memstat->m_used / (double)memstat->m_total * 100.0;
	memstat->s_usage = (double)memstat->s_used / (double)memstat->s_total * 100.0;

err_quit:

	return err;
}

int scCoreViewVMStatus(scCoreView *cv, scVMStatus *vmstat)
{
	int err=SC_OK;
	unsigned long out;
	double  elapsed;
	scVMRawStatus vmrawstat;

	if(!cv || !cv->core) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] core view is null!\n", __FUNCTION__, __LINE__);
#endif
		err = SC_ERR;
		goto err_quit;
	}

	/* initialize first */
	memset(&vmrawstat,0x00,sizeof(scVMRawStatus));

	if ((err=scCoreSysVMRawStatus(cv->core, &vmrawstat)) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "get virtual memory raw status error[%s,%d] !\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

	elapsed = getelapsed_r(&(cv->vmtmvalue), 1);

	vmstat->pagein    = calcav((long*)&(vmrawstat.pagein),
					(long*)&(cv->vmrawstat.pagein),
					(long*)&out,
					elapsed);

	vmstat->pageout   = calcav((long*)&(vmrawstat.pageout),
					(long*)&(cv->vmrawstat.pageout),
					(long*)&out,
					elapsed);

	vmstat->swapin    = calcav((long*)&(vmrawstat.swapin),
					(long*)&(cv->vmrawstat.swapin),
					(long*)&out,
					elapsed);

	vmstat->swapout   = calcav((long*)&(vmrawstat.swapout),
					(long*)&(cv->vmrawstat.swapout),
					(long*)&out,
					elapsed);

	vmstat->scanrate  = calcav((long*)&(vmrawstat.scanrate) ,
					(long*)&(cv->vmrawstat.scanrate),
					(long*)&out,
					elapsed);

	vmstat->pagefault = calcav((long*)&(vmrawstat.pagefault),
					(long*)&(cv->vmrawstat.pagefault),
					(long*)&out,
					elapsed);

	vmstat->runqueue  = calcav((long*)&(vmrawstat.runqueue),
					(long*)&(cv->vmrawstat.runqueue),
					(long*)&out,
					elapsed);

	/* for load average */
	vmstat->la_1min  = Calcla(vmrawstat.la_1min , elapsed);
	vmstat->la_5min  = Calcla(vmrawstat.la_5min , elapsed);
	vmstat->la_15min = Calcla(vmrawstat.la_15min, elapsed);

err_quit:
	return err;
}

int scCoreViewSysStatus(scCoreView *cv, scSysStatus *sysstat)
{
	int err=SC_OK;

	if ((err=scCoreViewOneCpuStatus(cv, &sysstat->cpu)) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] get cpu status error!\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

	if ((err=scCoreViewMemStatus(cv, &sysstat->mem)) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] get real memory status error!\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

	/* vm */
	if ((err=scCoreViewVMStatus(cv, &sysstat->vm)) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] can't get virtual memory status!\n", __FUNCTION__, __LINE__);
#endif
		goto err_quit;
	}

err_quit:
	return err;
}

v_list_t *scCoreViewIOStatus(scCoreView *cv)
{
	int err=SC_OK;
	v_list_t *l_iorawstat;
	v_list_t *l_iostat = NULL; /* this will be returned */

	if (!cv || !cv->core) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] !\n", __FUNCTION__, __LINE__);
#endif
		err=SC_ERR;
		goto err_quit;
	}

	if ((l_iorawstat = scCoreSysIORawStatus(cv->core)) != NULL) {
		/* calculate - elapsed time */
		double elapsed = getelapsed_r((struct timeval *)&(cv->iotmvalue), 1);

		if ((l_iostat = calcav_iostat(l_iorawstat, cv->l_iorawstat, elapsed)) == NULL) 
			fprintf(stderr, "[%s,%s,%d] iostat error!!\n", __FILE__, __FUNCTION__, __LINE__);

		/* release */
		ll_destroy_node(&l_iorawstat);
	}
	else
		fprintf(stderr, "[%s,%s,%d] iostat error!!\n", __FILE__, __FUNCTION__, __LINE__);

err_quit:
	return l_iostat;
}

v_list_t *calcav_iostat(v_list_t *l_nvalue, v_list_t *l_ovalue, double elapsed)
{
	int at;
	unsigned long   out;
	scIORawStatus *nvalue, *ovalue;
	scIOStatus iostat;
	v_list_t  *list;

	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] create node error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	at = 0;
	while ((nvalue = (scIORawStatus*)ll_element_at(l_nvalue,at++)) != NULL) {
		/* lookup */
		ovalue = (scIORawStatus *)ll_search_node_data(l_ovalue,nvalue,
					sizeof(scIORawStatus),f_fsrch_device);

		/* initialize first */
		memset(&iostat,0x00,sizeof(scIOStatus));

		if (ovalue) {
			/* found out */

#ifdef CYGWIN
			iostat.nread    = nvalue->nread;
			iostat.nwritten = nvalue->nwritten;
#else
			iostat.nread    = calcav((long*)&(nvalue->nread),
							(long*)&(ovalue->nread),
							(long*)&out,
							elapsed);
			iostat.nwritten = calcav((long*)&(nvalue->nwritten),
							(long*)&(ovalue->nwritten),
							(long*)&out,
							elapsed);
#endif // CYGWIN

			iostat.nxfer    = iostat.nread + iostat.nwritten;
	
			iostat.reads    = calcav((long*)&(nvalue->reads),
							(long*)&(ovalue->reads),
							(long*)&out,
							elapsed);

			iostat.writes   = calcav((long*)&(nvalue->writes),
							(long*)&(ovalue->writes),
							(long*)&out,
							elapsed);

			iostat.xfers    = iostat.reads + iostat.writes;

			iostat.spare_1  = calcav((long*)&(nvalue->spare_1),
							(long*)&(ovalue->spare_1),
							(long*)&out,
							elapsed);

			iostat.spare_2  = calcav((long*)&(nvalue->spare_2),
							(long*)&(ovalue->spare_2),
							(long*)&out,
							elapsed);

			iostat.spare_3  = calcav((long*)&(nvalue->spare_3),
							(long*)&(ovalue->spare_3),
							(long*)&out,
							elapsed);
		} else {
			ll_insert_node(l_ovalue,nvalue,sizeof(scIORawStatus), NULL);
#ifdef DEBUG
			fprintf(stderr, "[%s,%d] new item[%s]\n",
				 __FUNCTION__, __LINE__, nvalue->device);
#endif
		}

		//sprintf(iostat.device,"%s",nvalue->device);
		strcpy(iostat.device, nvalue->device);
		ll_insert_node(list,&iostat,sizeof(scIOStatus),NULL);
	}
	
	return list;
}

int f_fsrch_device(const void *v1, const void *v2)
{
	char *device1 = ((scIORawStatus *)v1)->device;
	char *device2 = ((scIORawStatus *)v2)->device;

	return (!strcmp(device1, device2)) ? NODE_FOUND : NODE_NOT_FOUND;
}

v_list_t *scCoreViewFSInfo(scCoreView *cv)
{
	return scCoreSysFSInfo(cv->core);
}

v_list_t *scCoreViewPSInfo(scCoreView *cv, int sumoption, int sortoption)
{
	v_list_t *l_psinfo;
	ll_compare_fn fcompare = NULL;

	if ((l_psinfo = scCoreSysPSInfo(cv->core, sumoption)) == NULL)
		return NULL;

	/* allocate the sort func */
	switch(sortoption)
	{
		case SC_SORT_BY_PID   :
			fcompare = f_fsort_pid;
			break;

		case SC_SORT_BY_PNAME :
			fcompare = f_fsort_pname;
			break;

		case SC_SORT_BY_PARGS :
			fcompare = f_fsort_pargs;
			break;

		case SC_SORT_BY_UNAME :
			fcompare = f_fsort_uid;
			break;

		case SC_SORT_BY_PCPU  :
			fcompare = f_fsort_pcpu;
			break;

		case SC_SORT_BY_PMEM  :
			fcompare = f_fsort_pmem;
			break;

		case SC_SORT_BY_NPROC  :
			fcompare = f_fsort_nproc;
			break;

		default:
			fcompare = NULL;
	}

	/* sort */
	if (fcompare)
		ll_sort_node(l_psinfo,NULL,sizeof(scPSInfo),fcompare);

	return l_psinfo;
}

char *scCoreViewPSStatus2Readable(char state)
{
	int at;

	static struct _ProcStateTable {
		char  state;
		char *readable;
	} 
	ProcStateTable[] = {
		{ SC_PS_SLEEP  , "sleeping" },
		{ SC_PS_STOPPED, "stopped"  },
		{ SC_PS_DEFUNC , "zombie"   },
		{ SC_PS_RUNNING, "running"  },
		{ SC_PS_SWAPPED, "swapped"  },
		{ -1          , "unknown"  }
	};

	/* lookup the proc state table */
	at = 0;
	while (ProcStateTable[at].state != (char)-1
			&& ProcStateTable[at].state != state) 
		at++;
	
	return ProcStateTable[at].readable;
}

int f_fsort_pid(const void *v1, const void *v2)
{
	int pid1 = ((scPSInfo *)v1)->pid;
	int pid2 = ((scPSInfo *)v2)->pid;

	return (pid1 > pid2) ? 1 : 0;
}

int f_fsort_pname(const void *v1, const void *v2)
{
	char *pname1 = ((scPSInfo *)v1)->pname;
	char *pname2 = ((scPSInfo *)v2)->pname;

	return (strcmp(pname1, pname2) > 0) ? 1 : 0;
}

int f_fsort_pargs(const void *v1, const void *v2)
{
	char *pargs1 = ((scPSInfo *)v1)->args;
	char *pargs2 = ((scPSInfo *)v2)->args;

	return (strcmp(pargs1, pargs2) > 0) ? 1 : 0;
}

int f_fsort_uid(const void *v1, const void *v2)
{
	int uid1 = ((scPSInfo *)v1)->uid;
	int uid2 = ((scPSInfo *)v2)->uid;

	return (uid1 > uid2) ? 1 : 0;
}

int f_fsort_pcpu(const void *v1, const void *v2)
{
	double pcpu1 = ((scPSInfo *)v1)->cpuusage;
	double pcpu2 = ((scPSInfo *)v2)->cpuusage;

	return (pcpu1 < pcpu2) ? 1 : 0;
}

int f_fsort_pmem(const void *v1, const void *v2)
{
	double pmem1 = ((scPSInfo *)v1)->memusage;
	double pmem2 = ((scPSInfo *)v2)->memusage;

	return (pmem1 < pmem2) ? 1 : 0;
}

int f_fsort_nproc(const void *v1, const void *v2)
{
	int pmem1 = ((scPSInfo *)v1)->nproc;
	int pmem2 = ((scPSInfo *)v2)->nproc;

	return (pmem1 < pmem2) ? 1 : 0;
}


v_list_t *scCoreViewInterfaceInfo(scCoreView *cv)
{
	v_list_t *l_ifstat = NULL;

	return l_ifstat;
}

v_list_t *scCoreViewInterfaceStatus(scCoreView *cv)
{
	v_list_t *l_ifrawstat;
	v_list_t *l_ifstat = NULL; /* this will be returned */

	if (!cv || !cv->core) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] core view is null!\n", __FUNCTION__, __LINE__);
#endif
		return NULL;
	}

	if ((l_ifrawstat = scCoreNetInterfaceRawStatus(cv->core)) != NULL) {
		double elapsed = getelapsed_r(&(cv->iftmvalue), 1);

		if ((l_ifstat = calcav_ifstat(l_ifrawstat, cv->l_ifrawstat, elapsed)) == NULL) 
			fprintf(stderr,"[%s,%d] network interface rawstatus error!\n", __FUNCTION__, __LINE__);

		/* release */
		ll_destroy_node(&l_ifrawstat);
	}
	else
		fprintf(stderr, "[%s,%d] error!!\n", __FUNCTION__, __LINE__);

	return l_ifstat;
}

v_list_t *calcav_ifstat(v_list_t *l_nvalue, v_list_t *l_ovalue, double elapsed)
{
	int at;
	unsigned long  out;
	scInterfaceRawStatus *nvalue, *ovalue;
	scInterfaceStatus ifstat;
	v_list_t  *list;

	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] create node error!\n", __FUNCTION__, __LINE__);
#endif
		return NULL;
	}

	at = 0;
	while ((nvalue = (scInterfaceRawStatus *)ll_element_at(l_nvalue,at++)) != NULL) {
		/* lookup */
		ovalue = (scInterfaceRawStatus *)ll_search_node_data(l_ovalue,nvalue,
					sizeof(scInterfaceRawStatus),f_fsrch_ifname);

		/* initialize first */
		memset(&ifstat,0x00,sizeof(scInterfaceStatus));

		if (ovalue) {
			/* found out */

#ifdef CYGWIN
			ifstat.inoctets   = nvalue->inoctets;

			ifstat.outoctets  = nvalue->outoctets;

			ifstat.inpkts     = nvalue->inpkts;

			ifstat.outpkts    = nvalue->outpkts;

			ifstat.collisions = 0;
#else // IS UNIX
			ifstat.inoctets   = calcav((long*)&(nvalue->inoctets),
							(long*)&(ovalue->inoctets),
							(long*)&out,
							elapsed);

			ifstat.outoctets  = calcav((long*)&(nvalue->outoctets),
							(long*)&(ovalue->outoctets),
							(long*)&out,
							elapsed);

			ifstat.inpkts     = calcav((long*)&(nvalue->inpkts),
							(long*)&(ovalue->inpkts),
							(long*)&out,
							elapsed);

			ifstat.outpkts    = calcav((long*)&(nvalue->outpkts),
							(long*)&(ovalue->outpkts),
							(long*)&out,
							elapsed);

		
			ifstat.collisions = calcav((long*)&(nvalue->collisions),
							(long*)&(ovalue->collisions),
							(long*)&out,
							elapsed);
#endif //
			
			ifstat.inerrors   = calcav((long*)&(nvalue->inerrors),
							(long*)&(ovalue->inerrors),
							(long*)&out,
							elapsed);

			ifstat.outerrors  = calcav((long*)&(nvalue->outerrors),
							(long*)&(ovalue->outerrors),
							(long*)&out,
							elapsed);


			if (nvalue->ifinfo.speed > 0) {
				// Mbps -> bps
				double speed = nvalue->ifinfo.speed / 1000000 * 1024 * 1024;
				ifstat.inoctusage  = ((ifstat.inoctets  * 8) / speed) * 100;
				ifstat.outoctusage = ((ifstat.outoctets * 8) / speed) * 100;
			} else {
				ifstat.inoctusage  = 0;
				ifstat.outoctusage = 0;
			}
		} else {
			ll_insert_node(l_ovalue,nvalue,sizeof(scInterfaceRawStatus), NULL);
		}

		memcpy(&(ifstat.ifinfo),&(nvalue->ifinfo),sizeof(scInterfaceInfo));

		ll_insert_node(list,&ifstat,sizeof(scInterfaceStatus),NULL);
	}
	
	return list;
}

int f_fsrch_ifname(const void *v1, const void *v2)
{
	char *ifname1 = ((scInterfaceRawStatus *)v1)->ifinfo.ifname;
	char *ifname2 = ((scInterfaceRawStatus *)v2)->ifinfo.ifname;

	return (!strcmp(ifname1, ifname2)) ? NODE_FOUND : NODE_NOT_FOUND;
}

v_list_t *scCoreViewTCPInfo(scCoreView *cv, int listen_only)
{
	return scCoreNetTCPInfo(cv->core, listen_only);
}

v_list_t *scCoreViewSysPatchInfo(scCoreView *cv)
{
	return scCoreSysPatchInfo(cv->core);
}

v_list_t *scCoreViewSysPkgInfo(scCoreView *cv)
{
	return scCoreSysPkgInfo(cv->core);
}


char *scCoreViewTCPStatus2redable(int state)
{
	int at;

	static struct _TcpStateTable {
		int   state;
		char *readable;
	} 
	TcpStateTable[] = {
		{ SC_TCP_ESTABLISHED, "ESTABLISHED" },
		{ SC_TCP_SYN_SENT   , "SYN_SENT"    },
		{ SC_TCP_SYN_RECV   , "SYN_RECV"    },
		{ SC_TCP_FIN_WAIT1  , "FIN_WAIT1"   },
		{ SC_TCP_FIN_WAIT2  , "FIN_WAIT2"   },
		{ SC_TCP_TIME_WAIT  , "TIME_WAIT"   },
		{ SC_TCP_CLOSE      , "CLOSE"       },
		{ SC_TCP_CLOSE_WAIT , "CLOSE_WAIT"  },
		{ SC_TCP_LAST_ACK   , "LAST_ACK"    },
		{ SC_TCP_LISTEN     , "LISTEN"      },
		{ SC_TCP_CLOSING    , "CLOSING"     },
		{ -1               , "UNKNOWN"     }
	};

	at = 0;
	while (TcpStateTable[at].state != -1
			&& TcpStateTable[at].state != state) 
		at++;
	
	return TcpStateTable[at].readable;
}

void scCoreViewRelease(v_list_t **list)
{

	ll_destroy_node(list);
	return ;
}

#if defined(HPUX)
void scCoreTTYNames(scCore *core, char *dir)
{
	char name [MAXPATHLEN+1];
	struct dirent **namelist;
	int i, n;

	if ((n = scandir(dir, &namelist, NULL, NULL)) < 0)
		return;

	for (i = 0; i < n; i++) {
		struct stat statbuf;
		char *str = namelist[i]->d_name;
		if (*str == '.') continue;

		sprintf (name, "%s/%s", dir, str);

		if (stat (name, &statbuf) < 0) continue;
		if (!isalpha ((int)*str)) str = name + sizeof ("/dev");
			ttymap_t ttyname;

			if (S_ISCHR (statbuf.st_mode)) {
				ttyname.dev = statbuf.st_rdev;
				strncpy(ttyname.name, str, 8);
				ttyname.name[9] = '\0';

				/* add up.. */
				ll_insert_node(core->ttynames,&ttyname,sizeof(ttymap_t),NULL);
			}
			else if (S_ISDIR (statbuf.st_mode))
				scCoreTTYNames(core, name);
	}

	free (namelist);
}


char *scCoreLookupDevice(scCore *core, struct psdev *term)
{
	dev_t dev;
	ttymap_t *ttyname;
	int at;

	if (term->psd_major == -1 && term->psd_minor == -1) return "?";

	dev = makedev(term->psd_major, term->psd_minor);

	at = 0;
	while ((ttyname =(ttymap_t *)ll_element_at(core->ttynames, at++)) != NULL) {
		if (dev == ttyname->dev)
			return ttyname->name;
	}

	return NULL;
}
#endif

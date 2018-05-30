
#include <stdio.h>
#include <stdlib.h>

#include "u_time.h"
#include "u_debug.h"
#include "u_dlist.h"
#include "u_process.h"
#include "u_operate.h"
#include "u_file.h"
#include "u_tokenize.h"
#include "u_bfsearch.h"
#include "u_user.h"

#include "sc_core.h"

static int verbose;
static int pollBasicinfoOn;
static int pollCpustatOn;
static int pollMemstatOn;
static int pollVmstatOn;
static int pollIostatOn;
static int pollIfstatOn;
static int pollFsinfoOn;
static int pollPsinfoOn;
static int pollTcpinfoOn;
static int pollInterval;
static int pollPatchOn;
static int pollPkgOn;

int tcpinfo_main(scCoreView *coreview)
{
	scTCPInfo *tcpinfo;
	v_list_t *list;
	int at;

	list = scCoreViewTCPInfo(coreview, 0);
	if (list) {
		at = 0;
		while ((tcpinfo = (scTCPInfo *)ll_element_at(list,at++)) != NULL) {
			if (verbose) {
				fprintf(stderr,"%5d | %5d - ", tcpinfo->rcvque, tcpinfo->sndque);
				fprintf(stderr,"%15s : %5d",
							inet_ntoa(tcpinfo->localaddr),
							ntohs(tcpinfo->localport));
				fprintf(stderr," -> %15s : %5d",
							inet_ntoa(tcpinfo->remoteaddr),
							ntohs(tcpinfo->remoteport));
				fprintf(stderr," %s", scCoreViewTCPStatus2redable(tcpinfo->state));
				fprintf(stderr,"\n");
			}
		}

		scCoreViewRelease(&list);
	}
	else
		perror("kernelview_tcpinfo");

	fprintf(stderr,"tcpinfo_main ..................... %f\n", getelapsed());

	return 1;
}

int cpustat_main(scCoreView *coreview)
{
	scSysInfo sysinfo;
	scCpuStatus u_cpu, m_cpu[SC_MAX_CPU_NUM];
	int ncpu, i;

	memset(&sysinfo,0x00,sizeof(scSysInfo));

	if (scCoreViewBasicInfo(coreview, &sysinfo) != SC_ERR) {
		if (verbose) {
			fprintf(stderr," osname    : %s\n", sysinfo.osname);
			fprintf(stderr," version   : %s\n", sysinfo.version);
			fprintf(stderr," release   : %s\n", sysinfo.release);
			fprintf(stderr," hostname  : %s\n", sysinfo.hostname);
			fprintf(stderr," machine   : %s\n", sysinfo.machine);
			fprintf(stderr," vendor    : %s\n", sysinfo.vendor);
			fprintf(stderr," cputype   : %s\n", sysinfo.cputype);
			fprintf(stderr," clockspeed: %d\n", sysinfo.clockspeed);
			fprintf(stderr," ncpu      : %d\n", sysinfo.ncpu);
		}
	}
	fprintf(stderr,"basic_main ....................... %f\n", getelapsed());

	/* cpu stat */
	if (scCoreViewCpuStatus(coreview, &u_cpu, m_cpu, &ncpu) != SC_ERR) {
		for (i = 0; i < ncpu; i++) {
			if (verbose) {
				fprintf(stderr,"cpu%d    - %5.1f, %5.1f, %5.1f, %5.1f, %5.1f\n",
						m_cpu[i].id, m_cpu[i].total,m_cpu[i].user,m_cpu[i].system,
						m_cpu[i].etc, m_cpu[i].idle);
			}
		}

		if (verbose) {
			fprintf(stderr,"average - %5.1f, %5.1f, %5.1f, %5.1f, %5.1f\n",
						u_cpu.total,u_cpu.user,u_cpu.system,
						u_cpu.etc, u_cpu.idle);
		}
	}
	fprintf(stderr,"cpustat_main ..................... %f\n", getelapsed());

	return 1;
}

int memstat_main(scCoreView *coreview)
{
	scMemStatus memstat;
	
	memset(&memstat,0x00,sizeof(scMemStatus));
	scCoreViewMemStatus(coreview, &memstat);
	if (verbose) {
		fprintf(stderr,"total mem : %lu\n", memstat.m_total);
		fprintf(stderr,"used  mem : %lu\n", memstat.m_used);
		fprintf(stderr,"proc  mem : %lu\n", memstat.m_proc);
		fprintf(stderr,"file  mem : %lu\n", memstat.m_cache);
		fprintf(stderr,"1     mem : %lu\n", memstat.spare_1);
		fprintf(stderr,"2     mem : %lu\n", memstat.spare_2);
		fprintf(stderr,"3     mem : %lu\n", memstat.spare_3);
		fprintf(stderr,"total swap: %lu\n", memstat.s_total);
		fprintf(stderr,"used  swap: %lu\n", memstat.s_used);
		fprintf(stderr,"mem  usage: %f\n", memstat.m_usage);
		fprintf(stderr,"swap usage: %f\n", memstat.s_usage);
	}
	fprintf(stderr,"memstat_main ..................... %f\n", getelapsed());

	return 1;
}

int vmstat_main(scCoreView *coreview)
{
	scVMStatus vmstat;

	/* vmstat */
	scCoreViewVMStatus(coreview,&vmstat);
	if (verbose) {
		fprintf(stderr,"pagein   : %f\n", vmstat.pagein);
		fprintf(stderr,"pageout  : %f\n", vmstat.pageout);
		fprintf(stderr,"swapin   : %f\n", vmstat.swapin);
		fprintf(stderr,"swapout  : %f\n", vmstat.swapout);
		fprintf(stderr,"pagefault: %f\n", vmstat.pagefault);
		fprintf(stderr,"scanrate : %f\n", vmstat.scanrate);
		fprintf(stderr,"runqueue : %f\n", vmstat.runqueue);
		fprintf(stderr,"ld min 1 : %f\n", vmstat.la_1min);
		fprintf(stderr,"ld min 5 : %f\n", vmstat.la_5min);
		fprintf(stderr,"ld min 15: %f\n", vmstat.la_15min);
	}
	
	fprintf(stderr,"vmstat_main ...................... %f\n", getelapsed());

	return 1;
}

int iostat_main(scCoreView *coreview)
{
	scIOStatus *iostat;
	v_list_t *list;
	int at;

	list = scCoreViewIOStatus(coreview);
	if (list) {
		at = 0;
		while ((iostat = (scIOStatus *)ll_element_at(list,at++)) != NULL) {
			if (verbose) {
				fprintf(stderr,"%s, %f, %f, %f, %f, %f\n", 
                       					iostat->device,
                       					iostat->nread,
                       					iostat->nwritten,
                       					iostat->nxfer,
                       					iostat->spare_4,
                       					iostat->spare_5
							);
			}
		}

		scCoreViewRelease(&list);
	}
	fprintf(stderr,"iostat_main ...................... %f\n", getelapsed());

	return 1;
}

int fsinfo_main(scCoreView *coreview)
{
	scFSInfo *fsinfo;
	v_list_t *list;
	int at;

	list = scCoreViewFSInfo(coreview);
	if (list) {
		at = 0;
		while ((fsinfo = (scFSInfo *)ll_element_at(list,at++)) != NULL) {
			if (verbose) {
				fprintf(stderr,"%10s, %10s - %lu, %lu, %lu, %f | %lu, %lu, %f\n",
									fsinfo->device,
									fsinfo->mntpoint,
									fsinfo->sizetotal,
									fsinfo->sizeused, 
									fsinfo->sizeavail, 
									fsinfo->sizeusage,
									fsinfo->filetotal,
									fsinfo->fileused,
									fsinfo->fileusage);
			}
		}

		scCoreViewRelease(&list);
	}
	else
		perror("scCoreViewRelease");

	fprintf(stderr,"fsinfo_main ...................... %f\n", getelapsed());

	return 1;
}

int psinfo_main(scCoreView *coreview)
{
	scPSInfo *psinfo;
	v_list_t *list;
	int at;
fprintf(stderr, "psinfo start..\n");
	list = scCoreViewPSInfo(coreview,SC_SUM_BY_DEFAULT,SC_SORT_BY_DEFAULT);
	if (list) {
		at = 0;
		while ((psinfo = (scPSInfo *)ll_element_at(list,at++)) != NULL) {
			if (verbose) {
				fprintf(stderr,"%15s - cpu%d, %d, %s, %d, cpu(%lu -> %f), mem(%lu -> %f) - (%c) %s\n", 
						psinfo->pname,
						psinfo->processor, 
						psinfo->pid,
						uid2name(psinfo->uid,0),
						psinfo->started,
						psinfo->cputime, psinfo->cpuusage,
						psinfo->memused, psinfo->memusage,
						psinfo->state,
						psinfo->args
				);
			}
		}

		scCoreViewRelease(&list);
	}
	else
		perror("scCoreViewRelease");

	fprintf(stderr,"psinfo_main ...................... %f\n", getelapsed());

	return 1;
}

int ifstat_main(scCoreView *coreview)
{
	scInterfaceStatus *ifstat;
	v_list_t *list;
	int at;

	list = scCoreViewInterfaceStatus(coreview);
	if (list) {
		at = 0;
		while ((ifstat = (scInterfaceStatus *)ll_element_at(list,at++)) != NULL) {
			char hwaddr[20];

			sprintf(hwaddr, "%02x:%02x:%02x:%02x:%02x:%02x",
					(ifstat->ifinfo.hwaddr[0] & 0377), (ifstat->ifinfo.hwaddr[1] & 0377),
					(ifstat->ifinfo.hwaddr[2] & 0377), (ifstat->ifinfo.hwaddr[3] & 0377),
					(ifstat->ifinfo.hwaddr[4] & 0377), (ifstat->ifinfo.hwaddr[5] & 0377)
			);

			if (verbose) {
				fprintf(stderr,"ifname  : %s\n", ifstat->ifinfo.ifname);
				fprintf(stderr,"-. addr : %s\n", inet_ntoa(ifstat->ifinfo.addr));
				fprintf(stderr,"-. broad: %s\n", inet_ntoa(ifstat->ifinfo.broadaddr));
				fprintf(stderr,"-. mask : %s\n", inet_ntoa(ifstat->ifinfo.subnetmask));
				fprintf(stderr,"-. netid: %s\n", inet_ntoa(ifstat->ifinfo.networkid));
				fprintf(stderr,"-. h/w  : %s\n", hwaddr);
				fprintf(stderr,"-. mtu  : %d\n", ifstat->ifinfo.mtu);
				fprintf(stderr,"-. speed: %d\n", ifstat->ifinfo.speed);
				fprintf(stderr,"-. stat : %f, %f | %f, %f\n",
								ifstat->inoctets, ifstat->outoctets,
								ifstat->inpkts, ifstat->outpkts);
				fprintf(stderr,"\n");
			}
		}

		scCoreViewRelease(&list);
	}
	else
		perror("scCoreViewRelease");

	fprintf(stderr,"ifstat_main ...................... %f\n", getelapsed());

	return 0;
}
#if 0
int utmp_main()
{
	utmplist_t *list;

	if ((list = utmp_create(1)) != NULL) {
		utmp_print(list);
		utmp_destroy(&list);
	}
	else
		perror("utmp_create");

	fprintf(stderr,"utmp_main ...................... %f\n", getelapsed());

	return 0;
}
#endif

int patch_main(scCoreView *cv)
{
	v_list_t *list;
	scSysPatchInfo *patch;
	int at=0;

	if((list = scCoreViewSysPatchInfo(cv))!=NULL) {
		while ((patch = (scSysPatchInfo *)ll_element_at(list,at++)) != NULL) {
			if(verbose) {
				printf("name[%s], version[%s], desc[%s]\n",
					patch->name, patch->version, patch->description);
			}
		}
		scCoreViewRelease(&list);
	}
	return 0;
}


int pkg_main(scCoreView *cv)
{
	v_list_t *list;
	scSysPkgInfo *pkg;
	int at=0;

	if((list = scCoreViewSysPkgInfo(cv))!=NULL) {
		while ((pkg = (scSysPkgInfo *)ll_element_at(list,at++)) != NULL) {
			if(verbose) {
				fprintf(stderr, "name[%s], version[%s], desc[%s]\n",
					pkg->name, pkg->version, pkg->description);
			}
		}
		scCoreViewRelease(&list);
	}
	return 0;
}

int usage(char *pname)
{
	fprintf(stderr,"usage: %s [-v] [-a] [-sN] [cpu|mem|vm|io|if|fs|ps]\n", pname);
	exit(1);
}

int main(int argc, char **argv)
{
	scCoreView *coreview;
	int i, count;

	if (argc == 1)
		usage(argv[0]);

	/* parse the args */
	for (i = 0; i < argc; i++) {
		if (!strncmp(argv[i], "-a", 2)) {
			pollBasicinfoOn = 1;
			pollCpustatOn = 1;
			pollMemstatOn = 1;
			pollVmstatOn = 1;
			pollIostatOn = 1;
			pollIfstatOn = 1;
			pollFsinfoOn = 1;
			pollPsinfoOn = 1;
			pollTcpinfoOn = 1;
			pollPatchOn = 1;
			pollPkgOn = 1;
		}
		else if (!strcmp(argv[i], "cpu")) {
			pollCpustatOn = 1;
		}
		else if (!strcmp(argv[i], "mem")) {
			pollMemstatOn = 1;
		}
		else if (!strcmp(argv[i], "vm")) {
			pollVmstatOn = 1;
		}
		else if (!strcmp(argv[i], "io")) {
			pollIostatOn = 1;
		}
		else if (!strcmp(argv[i], "if")) {
			pollIfstatOn = 1;
		}
		else if (!strcmp(argv[i], "fs")) {
			pollFsinfoOn = 1;
		}
		else if (!strcmp(argv[i], "ps")) {
			pollPsinfoOn = 1;
		}
		else if (!strcmp(argv[i], "patch")) {
			pollPatchOn = 1;
		}
		else if (!strcmp(argv[i], "pkg")) {
			pollPkgOn = 1;
		}
		else if (!strcmp(argv[i], "tcp")) {
			pollTcpinfoOn = 1;
		}
		else if (!strncmp(argv[i], "-s", 2) && strlen(argv[i]) > 2) {
			char *temp = &argv[i][2];
			pollInterval = atoi(temp);
		}
		else if (!strncmp(argv[i], "-v", 2)) {
			verbose = 1;
		}
		else if (!strncmp(argv[i], "-h", 2))
			usage(argv[0]);
	}

	/* setup the interval */
	pollInterval = pollInterval <= 0 ? 3 : pollInterval;
	setnmopt("coreview");
	setlvopt("WEM");

	/* enabling the kernel view */
	if ((coreview = scCoreViewCreate()) == NULL) {
		perror("scCoreViewCreate()");
		exit(1);
	}

	count = 1;
	while (1) {
		/* initialize the elapsed time */
		getelapsed();

		if (pollCpustatOn) cpustat_main(coreview);

		if (pollMemstatOn) memstat_main(coreview);

		if (pollVmstatOn) vmstat_main(coreview);

		if (pollFsinfoOn) fsinfo_main(coreview);

		if (pollIostatOn) iostat_main(coreview);

		if (pollPsinfoOn) psinfo_main(coreview);

		if (pollIfstatOn) ifstat_main(coreview);

		if (pollPatchOn) patch_main(coreview);

		if (pollPkgOn) pkg_main(coreview);

		if(pollTcpinfoOn) tcpinfo_main(coreview);

		exit(0);
//		utmp_main();

		/* print the basic info */
		fprintf(stderr,"\n");
		fprintf(stderr,"========================================\n");
		fprintf(stderr,"                SUMMARIES               \n");
		fprintf(stderr,"----------------------------------------\n");
		fprintf(stderr,"Count   : %d\n", count++);
		fprintf(stderr,"Interval: %d\n", pollInterval);
		fprintf(stderr,"========================================\n\n");

		sleep(pollInterval);
	}

	scCoreViewDestroy(coreview);
}





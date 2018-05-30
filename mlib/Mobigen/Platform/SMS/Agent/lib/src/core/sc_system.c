
/*
 *
 * (C) COPYRIGHT h9mm. 2005
 *
 */

#ifdef CYGWIN
#include <windows.h>
#include <tlhelp32.h.> //process
#include <psapi.h>
#include <sys/utsname.h>
typedef void (WINAPI *PGNSI)(LPSYSTEM_INFO);
#endif 

#include "sc_system.h"
#include "sc_core.h"

#if defined(HPUX) || defined(SunOS)
unsigned long PhysicalMemory = -1;
#else
# if defined(Linux) || defined(CYGWIN)
unsigned long PhysicalMemory = 0;
# endif
#endif

unsigned long g_physicalMemory = 0;



#if defined(AIX)
int scCoreSysSetupEachPSInfo32(scCore *core, scPSInfo *psinfo, struct procsinfo64 *procs, double elapsed)
{


	char args[256];
	int  cc;

	/* pid */
	psinfo->pid  = (int )procs->pi_pid;
	psinfo->ppid = (int )procs->pi_ppid;
	psinfo->uid  = (int )procs->pi_uid;

	/* setup the pname */
	if (procs->pi_pid == 0) {
		sprintf(psinfo->pname,"swapper");
	}
	else if (procs->pi_state != SZOMB) {
		if (procs->pi_flags & SKPROC) 
			sprintf(psinfo->pname,"Kernel (%s)", procs->pi_comm);
		else 
			sprintf(psinfo->pname,"%s", procs->pi_comm);
	}
	else 
		sprintf(psinfo->pname,"<defunct>");

	/* args */
	memset(args,0x00,sizeof(args));

	cc = getargs(procs,sizeof(struct procsinfo64),args,sizeof(args));
	if (cc != -1 && strlen(args)) {
		char ch, *cp = args;
		int  at;

		/* null to space */
		at = 0;
		while ((*cp || *(cp+1)) && at < 255) 
			psinfo->args[at++] = ((ch = *cp++) == '\0') ? ' ' : ch;

		trim(psinfo->args);
	}
	else
		sprintf(psinfo->args,"%s", psinfo->pname);

	/* memory & cputime */
	if (procs->pi_state != SZOMB && !(procs->pi_flags & SKPROC)) {
		/* memory */
		psinfo->memused  = page2k(procs->pi_drss + procs->pi_trss);

		/* cpu time */
		psinfo->cputime  = procs->pi_ru.ru_utime.tv_sec * 1.0;
		psinfo->cputime += procs->pi_ru.ru_stime.tv_sec * 1.0;
		psinfo->cputime += procs->pi_ru.ru_utime.tv_usec * 1e-9;
		psinfo->cputime += procs->pi_ru.ru_stime.tv_usec * 1e-9;
	}
	else {
		psinfo->memused = 0; psinfo->cputime = 0.0;
	}

	/* start time */
	psinfo->started = (procs->pi_state != SZOMB) ? procs->pi_start : 0;

	/* usage */
	psinfo->memusage = (psinfo->memused / (double)g_physicalMemory) * 100.0;
	psinfo_cputime2pct(core,psinfo,elapsed);

	/* state */
	psinfo->state = (procs->pi_state == SZOMB) ? SC_PS_DEFUNC :
				(procs->pi_state == SSTOP  ) ? SC_PS_STOPPED :
				(procs->pi_state == SIDL   ) ? SC_PS_SLEEP   :
				(procs->pi_state == SACTIVE) ? SC_PS_RUNNING :
				SC_PS_UNKNOWN;


	/* the rest */
	psinfo->processor = 0;
	psinfo->nproc = 1;
	psinfo->nthrd = procs->pi_thcount;

	return SC_OK;
}

int scCoreSysSetupEachPSInfo64(scCore *core, scPSInfo *psinfo, struct procentry64 *procs, double elapsed)
{
	char args[256];
	int  cc;
	
	/* pid */
	psinfo->pid  = procs->pi_pid;
	psinfo->ppid = procs->pi_ppid;
	psinfo->uid  = procs->pi_uid;

	/* setup the pname */
	if (procs->pi_pid == 0) {
		sprintf(psinfo->pname,"swapper");
	}
	else if (procs->pi_state != SZOMB) {
		if (procs->pi_flags & SKPROC) 
			sprintf(psinfo->pname,"Kernel (%s)", procs->pi_comm);
		else 
			sprintf(psinfo->pname,"%s", procs->pi_comm);
	}
	else 
		sprintf(psinfo->pname,"<defunct>");

	/* args */
	memset(args,0x00,sizeof(args));

	cc = getargs(procs,sizeof(struct procentry64),args,sizeof(args));
	if (cc != -1 && strlen(args)) {
		char ch, *cp = args;
		int  at;

		/* null to space */
		at = 0;
		while ((*cp || *(cp+1)) && at < 255) 
			psinfo->args[at++] = ((ch = *cp++) == '\0') ? ' ' : ch;

		trim(psinfo->args);
	}
	else
		sprintf(psinfo->args,"%s", psinfo->pname);

	/* memory & cputime */
	if (procs->pi_state != SZOMB && !(procs->pi_flags & SKPROC)) {
		/* memory */
		psinfo->memused  = page2k(procs->pi_drss + procs->pi_trss);

		/* cpu time */
		psinfo->cputime  = (procs->pi_ru.ru_utime.tv_sec + procs->pi_ru.ru_stime.tv_sec) * 1.0;
		psinfo->cputime += (procs->pi_ru.ru_utime.tv_usec + procs->pi_ru.ru_stime.tv_usec) * 1e-9;
	}
	else {
		psinfo->memused = 0;
		psinfo->cputime = 0.0;
	}

	/* start time */
	psinfo->started = (procs->pi_state != SZOMB) ? procs->pi_start : 0;

	/* usage */
	psinfo->memusage = (psinfo->memused / (double)g_physicalMemory) * 100.0;
	psinfo_cputime2pct(core,psinfo,elapsed);

	/* state */
	psinfo->state = (procs->pi_state == SZOMB) ? SC_PS_DEFUNC :
				(procs->pi_state == SSTOP  ) ? SC_PS_STOPPED :
				(procs->pi_state == SIDL   ) ? SC_PS_SLEEP   :
				(procs->pi_state == SACTIVE) ? SC_PS_RUNNING :
				SC_PS_UNKNOWN;


	/* the rest */
	psinfo->processor = 0;
	psinfo->nproc = 1;
	psinfo->nthrd = procs->pi_thcount;

	return SC_OK;
}
#endif /* AIX */

#if defined(SunOS)

int scCoreSysSetupEachPSInfo(scCore *core, scPSInfo *psinfo, char *dirname, double elapsed)
{
	int  fd;
	int  icheck; /* OK, ERR */
	char file[64];

	struct psinfo psi;

	sprintf(file,"/proc/%s/psinfo",dirname);

	/* open /proc/#/psinfo */
	if ((fd = open(file,O_RDONLY)) == -1)
		return SC_ERR;

	icheck = SC_OK;

	/* read.. */
	if (read(fd, &psi, sizeof(struct psinfo)) != -1) {
		/* check zombie,,, */
		if (psi.pr_nlwp == 0)
			sprintf(psi.pr_fname, "zombie");

		/* setup the painfo */
		psinfo->pid  = psi.pr_pid;
		psinfo->ppid = psi.pr_ppid;
		psinfo->uid  = psi.pr_uid;

		/* setup the names */
		sprintf(psinfo->pname,"%s",trim(psi.pr_fname));
		sprintf(psinfo->args ,"%s",trim(psi.pr_psargs));

		/* cpu time */
		psinfo->cputime  = psi.pr_time.tv_sec  * 1.0;
		psinfo->cputime += psi.pr_time.tv_nsec * 1e-9; /* second <- . -> nonosecond */
		
		psinfo->started = psi.pr_start.tv_sec;
		psinfo->memused = psi.pr_rssize;

		psinfo->cpuusage = percent_cpu(psi.pr_pctcpu);
		psinfo->memusage = percent_mem(psi.pr_pctmem);

		psinfo->state = (psi.pr_lwp.pr_state == SSLEEP) ? SC_PS_SLEEP :         
				(psi.pr_lwp.pr_state == SSTOP) ? SC_PS_STOPPED :
				(psi.pr_lwp.pr_state == SZOMB) ? SC_PS_DEFUNC  :
				(psi.pr_lwp.pr_state == SIDL ) ? SC_PS_SLEEP   :
				(psi.pr_lwp.pr_state == SRUN ) ? SC_PS_RUNNING : SC_PS_UNKNOWN;

		psinfo->processor = psi.pr_lwp.pr_onpro;
		psinfo->nthrd = psi.pr_nlwp;
		psinfo->nproc = 1;

		/* doesn't support below */
		psinfo->spare_1 = 0;
		psinfo->spare_2 = 0;
		psinfo->spare_3 = 0;
	}
	else
		icheck = SC_ERR;

	/* release.. */
	close(fd);

	return icheck;
}

#endif /* SunOS */

#if defined(HPUX)
int scCoreSysSetupEachPSInfo(scCore *core, scPSInfo *psinfo, double elapsed)
{
	struct pst_status pstatus;

	if (pstat_getproc(&pstatus,
			sizeof(struct pst_status), 1, core->pstatus_index) == 0
			|| pstatus.pst_pid == -1)
	{
		return 0;
	}

	psinfo->pid  = pstatus.pst_pid;
	psinfo->ppid = pstatus.pst_ppid;
	psinfo->uid  = pstatus.pst_uid;

	if (pstatus.pst_ucomm[0] == '\0') 
		sprintf(pstatus.pst_ucomm, "%s",
				pstatus.pst_pid == 0 ? "Swapper" :
				pstatus.pst_pid == 2 ? "Pager" : "[No name]");

	sprintf(psinfo->pname,"%s",trim(pstatus.pst_ucomm));
	sprintf(psinfo->args ,"%s",trim(pstatus.pst_cmd));

	psinfo->cputime = (pstatus.pst_stime + pstatus.pst_utime) * 1.0; 
		
	psinfo->started = pstatus.pst_start;
	psinfo->memused = page2k(pstatus.pst_rssize);

	psinfo->cpuusage  = pstatus.pst_pctcpu * 100.0;
	psinfo->memusage  = (double)psinfo->memused / PhysicalMemory;
	psinfo->memusage *= 100.0;

	psinfo->state = (pstatus.pst_stat == PS_SLEEP) ? SC_PS_SLEEP :         
			(pstatus.pst_stat == PS_STOP) ? SC_PS_STOPPED :
			(pstatus.pst_stat == PS_ZOMBIE) ? SC_PS_DEFUNC  :
			(pstatus.pst_stat == PS_IDLE) ? SC_PS_SLEEP   :
			(pstatus.pst_stat == PS_RUN) ? SC_PS_RUNNING : SC_PS_UNKNOWN;

	psinfo->processor = pstatus.pst_procnum;

#if (__OS__ >= 301100)
	psinfo->nthrd = pstatus.pst_nlwps;
#else
	psinfo->nthrd = 1;
#endif
	psinfo->nproc = 1;

	/* doesn't support below */
	psinfo->spare_1 = 0;
	psinfo->spare_2 = 0;
	psinfo->spare_3 = 0;

	/* update the index : don't forget this!! */
	core->pstatus_index = pstatus.pst_idx + 1;

	return 1;
}
#endif /* HPUX */


#if defined(Linux)

int scCoreSysSetupEachPSInfo(scCore *core, scPSInfo *psinfo, char *dirname, double elapsed)
{
	char file[64];
	proc_t ptable;
	struct stat sb;

	sprintf(file,"/proc/%s",dirname);
	memset(&ptable, 0x00, sizeof(proc_t));
	if (stat(file,&sb) == -1 || psinfo_stat2proc(&ptable,dirname) == SC_ERR){
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	ptable.uid = sb.st_uid;

	if (psinfo_cmdline2proc(&ptable, dirname) == SC_ERR)
		sprintf(ptable.args,"[%s]",ptable.cmd);

	psinfo_cputime2pct(core,&ptable,elapsed);

	/* setup the painfo */
	psinfo->pid  = ptable.pid;
	psinfo->ppid = ptable.ppid;
	psinfo->uid  = ptable.uid;

	sprintf(psinfo->pname,"%s",trim(ptable.cmd));
	sprintf(psinfo->args ,"%s",trim(ptable.args));

	psinfo->started = ptable.start_time; /* something wrong with start time */
	psinfo->cputime = (ptable.utime + ptable.stime) * 0.01; /* HZ (1/100) */
	psinfo->memused = page2k(ptable.rss);

	psinfo->cpuusage = ptable.pcpu;
	psinfo->memusage = (psinfo->memused / (double)PhysicalMemory) * 100.0;

	psinfo->state = (ptable.state == 'S') ? SC_PS_SLEEP :           /* for sleeping    */
				(ptable.state == 'D') ? SC_PS_SLEEP   : /* for uninterruptible sleep */
				(ptable.state == 'T') ? SC_PS_STOPPED : /* for stopped     */
				(ptable.state == 'Z') ? SC_PS_DEFUNC  : /* for zombies     */
				(ptable.state == 'W') ? SC_PS_SWAPPED : /* for swapped out */
				(ptable.state == 'R') ? SC_PS_RUNNING : /* for running     */
				SC_PS_UNKNOWN;

	psinfo->processor = ptable.processor;
	psinfo->nthrd = (!ptable.nlwp) ? 1 : ptable.nlwp;
	psinfo->nproc = 1;

	/* doesn't support below */
	psinfo->spare_1 = 0;
	psinfo->spare_2 = 0;
	psinfo->spare_3 = 0;

	return SC_OK;
}


int psinfo_cputime2pct(scCore *core, proc_t *P, double elapsed)
{
	scPSCache *tmp = &(core->pscache)[HASH(P->pid)];
	double cputime = (P->utime + P->stime) * 0.01;
	double delta;

	/* lookup all the entries */
	while (tmp->pid != P->pid && tmp->pid != -1) 
		tmp = (++tmp == core->pscache+HASH_SIZE) ? core->pscache : tmp;

	delta   = (tmp->pid == -1) ? cputime : cputime - tmp->cputime;
	P->pcpu = (delta / elapsed) * 100.0;

	/* backup.. */
	tmp->pid     = P->pid;
	tmp->cputime = cputime;
	tmp->toggle  = core->toggle;
	
	return SC_OK;
}

#elif CYGWIN

unsigned long FILEFileTimeToUnixTime( FILETIME FileTime )
{

	long long UnixTime;

	UnixTime = ((long long)FileTime.dwHighDateTime << 32) + FileTime.dwLowDateTime;

	/* convert to the Unix epoch */ 
	if (UnixTime >  (long long)(11644473600LL * 10000000LL) ) {
		UnixTime -= (long long)(11644473600LL * 10000000LL);
	}

	return (unsigned long)(UnixTime/10000000);
}

int psinfo_cputime2pct(scCore *core, proc_t *P, double elapsed)
{
	scPSCache *tmp = &(core->pscache)[HASH(P->pid)];
	double cputime = (P->utime + P->stime) * 0.01;
	double delta;

	/* lookup all the entries */
	while (tmp->pid != P->pid && tmp->pid != -1) 
		tmp = (++tmp == core->pscache+HASH_SIZE) ? core->pscache : tmp;

	delta   = (tmp->pid == -1) ? cputime : cputime - tmp->cputime;
	P->pcpu = (delta / elapsed) * 100.0;

	/* backup.. */
	tmp->pid     = P->pid;
	tmp->cputime = cputime;
	tmp->toggle  = core->toggle;
	
	return SC_OK;
}
 
double getProcessMemory(HANDLE hProcess, DWORD pid)
{
    PROCESS_MEMORY_COUNTERS pmc;

	double result = -1;

	if ( GetProcessMemoryInfo( hProcess, &pmc, sizeof(pmc)) )
	{
		result = pmc.PagefileUsage;
	}

	return result;
}

void getCpuUsage(scCore *core, scPSInfo *psinfo, HANDLE hProcess, DWORD pid)
{
	double cpuUsage = 0;
	unsigned long cputime = 0;
	FILETIME kernelTime, userTime, unuse;


	if (GetProcessTimes(hProcess, &unuse, &unuse, &kernelTime, &userTime)) {

		ProcessInfo processinfo;
		if ( core->processList.find(pid) != core->processList.end()) {
			LARGE_INTEGER curEnd, curStart;
			QueryPerformanceCounter( &curEnd );

			processinfo = core->processList[ pid ];
			curStart = processinfo.qpcount;


			long ProcTime = (kernelTime.dwLowDateTime - processinfo.ftKernel.dwLowDateTime) + (userTime.dwLowDateTime - processinfo.ftUser.dwLowDateTime);
			ProcTime = (ProcTime / core->cpuNum) / double((curEnd.QuadPart - curStart.QuadPart) / core->curFreq.QuadPart);
			cpuUsage = ProcTime / 100000;
		}
		
		
		processinfo.isAlive = true;
		processinfo.ftKernel = kernelTime;
		processinfo.ftUser = userTime;

		cputime = FILEFileTimeToUnixTime(userTime) + FILEFileTimeToUnixTime(kernelTime);

		QueryPerformanceCounter( &processinfo.qpcount );

		core->processList.insert(map<int,ProcessInfo>::value_type(pid, processinfo));
		//core->processList[ pid ] = processinfo;
	} else {
		cpuUsage = 0;
		cputime = 0;
	}

	psinfo->cputime = cputime;
	psinfo->cpuusage = cpuUsage;


	return ;
}

int scCoreSysSetupEachPSInfo(scCore *core, scPSInfo *psinfo,PROCESSENTRY32 *pe32)
{

	HANDLE hProcess;

	hProcess = OpenProcess( PROCESS_QUERY_INFORMATION | 
		PROCESS_VM_READ, FALSE, pe32->th32ProcessID );

	if (NULL == hProcess) {
        return SC_ERR;
	}
	
	/* setup the painfo */
	psinfo->pid  = pe32->th32ProcessID;
	psinfo->ppid = pe32->th32ParentProcessID;
	psinfo->uid  = 0;

	sprintf(psinfo->pname, "%s", trim(pe32->szExeFile));
	sprintf(psinfo->args , "%s", trim(pe32->szExeFile));

	//psinfo->started = ptable.start_time; /* something wrong with start time */
	//psinfo->cputime = (ptable.utime + ptable.stime) * 0.01; /* HZ (1/100) */


	getCpuUsage(core, psinfo, hProcess, pe32->th32ProcessID);

	psinfo->memused = getProcessMemory(hProcess, pe32->th32ProcessID);


	// PhysicalMemroy kbyte, psinfo->memused byte
	psinfo->memusage = ((psinfo->memused/1024) / (double)PhysicalMemory) * 100.0;

	psinfo->state = SC_PS_UNKNOWN;

#if 0
	psinfo->state = (ptable.state == 'S') ? SC_PS_SLEEP :           /* for sleeping    */
				(ptable.state == 'D') ? SC_PS_SLEEP   : /* for uninterruptible sleep */
				(ptable.state == 'T') ? SC_PS_STOPPED : /* for stopped     */
				(ptable.state == 'Z') ? SC_PS_DEFUNC  : /* for zombies     */
				(ptable.state == 'W') ? SC_PS_SWAPPED : /* for swapped out */
				(ptable.state == 'R') ? SC_PS_RUNNING : /* for running     */
				SC_PS_UNKNOWN;
#endif //0

	psinfo->processor = 0;
	psinfo->nthrd = pe32->cntThreads;
	psinfo->nproc = 1;

	/* doesn't support below */
	psinfo->spare_1 = 0;
	psinfo->spare_2 = 0;
	psinfo->spare_3 = 0;

	CloseHandle( hProcess );

	return SC_OK;
}

#else /* not linux */


int psinfo_cputime2pct(scCore *core, scPSInfo *ps, double elapsed)
{
#if !defined(SunOS) && !defined(HPUX)
	scPSCache *tmp = &(core->pscache)[HASH(ps->pid)];
	double cputime = ps->cputime;
	double delta;


	/* lookup all the entries */
	while (tmp->pid != ps->pid && tmp->pid != -1) 
		tmp = (++tmp == core->pscache+HASH_SIZE) ? core->pscache : tmp;

	delta        = (tmp->pid == -1) ? cputime : cputime - tmp->cputime;
	ps->cpuusage = (delta / elapsed) * 100.0;

	/* backup.. */
	tmp->pid     = ps->pid;
	tmp->cputime = cputime;
	tmp->toggle  = core->toggle;
#endif
	
	return SC_OK;
}

#endif /* Linux */

#ifdef CYGWIN
bool programInfo(char softwareKey[], char *programName,DWORD bufSize) {

	HKEY hKey;
	char key[BUFSIZ];


	memset(key, 0x00, BUFSIZ);
	snprintf(key, BUFSIZ, "%s\\%s",  UNINSTALL_KEY, softwareKey);

	if (RegOpenKeyEx( HKEY_LOCAL_MACHINE,
        key,
		0, KEY_READ, &hKey ) != ERROR_SUCCESS ) 
	{
        return false;
	}
	 
	bool result = false;
	if (RegQueryValueEx(hKey, "DisplayName", NULL, NULL, (LPBYTE)programName, &bufSize) == ERROR_SUCCESS ) {
		result = true;
	}

	RegCloseKey( hKey );

	return result;

}
#endif // CYGWIN

v_list_t *scCoreSysPatchInfo(scCore *core)
{
#if defined(HPUX)
	FILE *fp=NULL;
	v_list_t *list = NULL;
	scSysPatchInfo patch;
	char buf[512], *p=NULL, *q=NULL;
	int i=0;

	if((fp = popen("swlist -l product", "r"))==NULL) return NULL;

	if((list = ll_create_node(NULL, 1))==NULL){
		pclose(fp);
		return NULL;
	}
	memset(buf, 0x00, sizeof(buf));
	while(fgets(buf, sizeof(buf)-1, fp)){
		buf[strlen(buf)-1] = 0x00; p = buf;
		while(isspace(*p)) p++;
		if(*p == '#' || *p == 0x00) goto read_cont;
		if(strncmp(p, "PH", 2)!=0) goto read_cont;

		memset(&patch, 0x00, sizeof(patch));
		i=0;
		while(!isspace(*p) && *p != 0x00){
			if(i>=sizeof(patch.name)) break;
			patch.name[i++] = *p; p++;
		}

		while(isspace(*p)) p++; if(*p==0x00) goto read_cont;

		i=0;
		while(!isspace(*p) && *p != 0x00){
			if(i>=sizeof(patch.version)) break;
			patch.version[i++] = *p; p++;
		}

		while(isspace(*p)) p++; if(*p==0x00) goto read_cont;

		strcpy(patch.description, p);

		ll_insert_node(list, &patch, sizeof(scSysPatchInfo), NULL);
read_cont:
		memset(buf, 0x00, sizeof(buf));
	}

	pclose(fp);

	return list;
#endif /* HPUX */

#if defined(SunOS)
	FILE *fp=NULL;
	v_list_t *list = NULL;
	scSysPatchInfo patch;
	char buf[4096], *p=NULL, *q=NULL;
	int i=0;

	if((fp = popen("showrev -p", "r"))==NULL) return NULL;

	if((list = ll_create_node(NULL, 1))==NULL){
		pclose(fp);
		return NULL;
	}
	memset(buf, 0x00, sizeof(buf));
	while(fgets(buf, sizeof(buf)-1, fp)){
		buf[strlen(buf)-1] = 0x00; p = buf;
		while(isspace(*p)) p++;
		if(*p == '#' || *p == 0x00) goto read_cont;
		if(strncmp(p, "Patch: ", 7)!=0) goto read_cont;
		
		p+=7;
		memset(&patch, 0x00, sizeof(patch));
		i=0;
		while(!isspace(*p) && *p != 0x00){
			if(i>=sizeof(patch.name)) break;
			patch.name[i++] = *p; p++;
		}

		q = (char *)strstr(p, "Packages: ");
		if(q){
			q+=strlen("Packages: ");
			if(strlen(q)>=sizeof(patch.description))
				strncpy(patch.description, q, sizeof(patch.description)-1);
			else
				strcpy(patch.description, q);
		}

		ll_insert_node(list, &patch, sizeof(scSysPatchInfo), NULL);
read_cont:
		memset(buf, 0x00, sizeof(buf));
	}

	pclose(fp);

	return list;
#endif /* SunOS */

#if defined(AIX)
	FILE *fp=NULL;
	v_list_t *list = NULL;
	scSysPatchInfo patch;
	char buf[4096], *p=NULL, *q=NULL;
	int i=0;

	if((fp = popen("instfix -i", "r"))==NULL) return NULL;

	if((list = ll_create_node(NULL, 1))==NULL){
		pclose(fp);
		return NULL;
	}
	memset(buf, 0x00, sizeof(buf));
	while(fgets(buf, sizeof(buf)-1, fp)){
		buf[strlen(buf)-1] = 0x00; p = buf;
		while(isspace(*p)) p++;
		if(*p == '#' || *p == 0x00) goto read_cont;
		if((p = (char *)strstr(buf, " I"))==NULL) goto read_cont;
		
		p++;
		memset(&patch, 0x00, sizeof(patch));
		i=0;
		while(!isspace(*p) && *p != 0x00){
			if(i>=sizeof(patch.name)) break;
			patch.name[i++] = *p; p++;
		}

		ll_insert_node(list, &patch, sizeof(scSysPatchInfo), NULL);
read_cont:
		memset(buf, 0x00, sizeof(buf));
	}

	pclose(fp);

	return list;
#endif /* AIX */

#if defined(Linux)
	FILE *fp=NULL;
	v_list_t *list = NULL;
	scSysPatchInfo patch;
	char buf[4096], *p=NULL, *q=NULL;
	int i=0;

	if((fp = popen("rpm -q -a", "r"))==NULL) return NULL;

	if((list = ll_create_node(NULL, 1))==NULL){
		pclose(fp);
		return NULL;
	}
	memset(buf, 0x00, sizeof(buf));
	while(fgets(buf, sizeof(buf)-1, fp)){
		buf[strlen(buf)-1] = 0x00; p = buf;
		while(isspace(*p)) p++;
		if(*p == '#' || *p == 0x00) goto read_cont;
		if(strncmp(p, "kernel", 6)!=0) goto read_cont;
		
		memset(&patch, 0x00, sizeof(patch));
		if(strlen(p)>=sizeof(patch.name))
			strncpy(patch.name, p, sizeof(patch.name)-1);
		else
			strcpy(patch.name, p);

		ll_insert_node(list, &patch, sizeof(scSysPatchInfo), NULL);
read_cont:
		memset(buf, 0x00, sizeof(buf));
	}

	pclose(fp);

	return list;
#endif /* Linux */

#if CYGWIN
	HKEY hKey;
	v_list_t *list = NULL;
	scSysPatchInfo patch;
	char szProductType[BUFSIZ];

	if (RegOpenKeyEx( HKEY_LOCAL_MACHINE,
        UNINSTALL_KEY,
		0, KEY_READ, &hKey )  != ERROR_SUCCESS ) {
			return NULL;
	}

	if((list = ll_create_node(NULL, 1))==NULL){
		RegCloseKey( hKey );
		return NULL;
	}

	int i = 0;
	while(true) {
		char p[BUFSIZ];
		DWORD  dwBufLen = BUFSIZ;
		FILETIME ftLastWriteTime;      // last write time 

		memset(p, 0x00, BUFSIZ);
		memset(szProductType, 0x00, BUFSIZ);

		 if (RegEnumKeyEx(hKey, i++,
						 szProductType, 
						 &dwBufLen, 
						 NULL, 
						 NULL, 
						 NULL, 
						 &ftLastWriteTime) != ERROR_SUCCESS) 
		 {
			 break;
		 } 


		 if (strncmp(szProductType, "KB", 2) != 0) {
			 continue;
		 }

		 if (programInfo(szProductType, p, BUFSIZ) == false) {
			 continue;
		 }

		
		memset(&patch, 0x00, sizeof(patch));
		if(strlen(p)>=sizeof(patch.name))
			strncpy(patch.name, p, sizeof(patch.name)-1);
		else
			strcpy(patch.name, p);

		ll_insert_node(list, &patch, sizeof(scSysPatchInfo), NULL);
	}

	RegCloseKey( hKey );

	return list;
#endif /* cygwin */
}

v_list_t *scCoreSysPkgInfo(scCore *core)
{
#if defined(HPUX)
	FILE *fp=NULL;
	v_list_t *list = NULL;
	scSysPkgInfo pkg;
	char buf[512], *p=NULL, *q=NULL;
	int i=0;

	if((fp = popen("swlist -l product", "r"))==NULL) return NULL;

	if((list = ll_create_node(NULL, 1))==NULL){
		pclose(fp);
		return NULL;
	}
	memset(buf, 0x00, sizeof(buf));
	while(fgets(buf, sizeof(buf)-1, fp)){
		buf[strlen(buf)-1] = 0x00; p = buf;
		while(isspace(*p)) p++;
		if(*p == '#' || *p == 0x00) goto read_cont;
		if(strncmp(p, "PH", 2)==0) goto read_cont;

		memset(&pkg, 0x00, sizeof(pkg));
		i=0;
		while(!isspace(*p) || *p == 0x00){
			if(i>=sizeof(pkg.name)) break;
			pkg.name[i++] = *p; p++;
		}

		while(isspace(*p)) p++; if(*p==0x00) goto read_cont;

		i=0;
		while(!isspace(*p) || *p == 0x00){
			if(i>=sizeof(pkg.version)) break;
			pkg.version[i++] = *p; p++;
		}

		while(isspace(*p)) p++; if(*p==0x00) goto read_cont;

		strcpy(pkg.description, p);

		ll_insert_node(list, &pkg, sizeof(scSysPkgInfo), NULL);
read_cont:
		memset(buf, 0x00, sizeof(buf));
	}

	pclose(fp);

	return list;
#endif /* HPUX */

#if defined(SunOS)
	FILE *fp=NULL;
	v_list_t *list = NULL;
	scSysPkgInfo pkg;
	char buf[512], *p=NULL, *q=NULL;
	int i=0;

	if((fp = popen("pkginfo", "r"))==NULL) return NULL;

	if((list = ll_create_node(NULL, 1))==NULL){
		pclose(fp);
		return NULL;
	}

	memset(buf, 0x00, sizeof(buf));
	while(fgets(buf, sizeof(buf)-1, fp)){
		buf[strlen(buf)-1] = 0x00; p = buf;
		while(isspace(*p)) p++;
		if(*p == '#' || *p == 0x00) goto read_cont;

		memset(&pkg, 0x00, sizeof(pkg));
		i=0;
		while(!isspace(*p) || *p == 0x00){
			if(i>=sizeof(pkg.pkgtype)) break;
			pkg.pkgtype[i++] = *p; p++;
		}

		while(isspace(*p)) p++; if(*p==0x00) goto read_cont;

		i=0;
		while(!isspace(*p) || *p == 0x00){
			if(i>=sizeof(pkg.name)) break;
			pkg.name[i++] = *p; p++;
		}

		while(isspace(*p)) p++; if(*p==0x00) goto read_cont;

		strcpy(pkg.description, p);

		ll_insert_node(list, &pkg, sizeof(scSysPkgInfo), NULL);
read_cont:
		memset(buf, 0x00, sizeof(buf));
	}

	pclose(fp);

	return list;
#endif /* SunOS */

#if defined(AIX)
	FILE *fp=NULL;
	v_list_t *list = NULL;
	scSysPkgInfo pkg;
	char buf[512], line[2048], dummy[512], *p=NULL, *q=NULL;
	int i=0;

	if((fp = popen("lslpp -l", "r"))==NULL) return NULL;

	if((list = ll_create_node(NULL, 1))==NULL){
		pclose(fp);
		return NULL;
	}

	fgets(buf, sizeof(buf)-1, fp);
	fgets(buf, sizeof(buf)-1, fp);
	fgets(buf, sizeof(buf)-1, fp);
	memset(buf, 0x00, sizeof(buf));
	memset(line, 0x00, sizeof(line));
	while(fgets(buf, sizeof(buf)-1, fp)){
		if(buf[0] != ' ') goto read_cont;
		buf[strlen(buf)-1] = 0x20; p = buf;
		p+=2;
		if(*p!=0x20){
			if(line[0] != 0x00){
				memset(&pkg, 0x00, sizeof(pkg));
				p = line;
				while(isspace(*p)) p++;
				i=0;
				while(!isspace(*p) && *p != 0x00){
					if(i>=sizeof(pkg.name)) break;
					pkg.name[i++] = *p; p++;
				}
				while(isspace(*p)) p++;
				i=0;
				while(!isspace(*p) && *p != 0x00){
					if(i>=sizeof(pkg.version)) break;
					pkg.version[i++] = *p; p++;
				}
				while(isspace(*p)) p++;
				while(!isspace(*p)) p++;
				while(isspace(*p)) p++;

				strcpy(pkg.description, p);

				ll_insert_node(list, &pkg, sizeof(scSysPkgInfo), NULL);
			}
			memset(line, 0x00, sizeof(line));
			strcat(line, buf);
		}else{
			p = buf; while(isspace(*p)) p++;
			strcat(line, p);
		}

read_cont:
		memset(buf, 0x00, sizeof(buf));
	}

	pclose(fp);

	memset(&pkg, 0x00, sizeof(pkg));
	p = line;
	while(isspace(*p)) p++;
	i=0;
	while(!isspace(*p) && *p != 0x00){
		if(i>=sizeof(pkg.name)) break;
		pkg.name[i++] = *p; p++;
	}
	while(isspace(*p)) p++;
	i=0;
	while(!isspace(*p) && *p != 0x00){
		if(i>=sizeof(pkg.version)) break;
		pkg.version[i++] = *p; p++;
	}
	while(isspace(*p)) p++;
	while(!isspace(*p)) p++;
	while(isspace(*p)) p++;

	strcpy(pkg.description, p);

	ll_insert_node(list, &pkg, sizeof(scSysPkgInfo), NULL);

	return list;
#endif /* AIX */

#if defined(Linux)
	FILE *fp=NULL;
	v_list_t *list = NULL;
	scSysPkgInfo pkg;
	char buf[4096], *p=NULL, *q=NULL;
	int i=0;

	if((fp = popen("rpm -q -a", "r"))==NULL) return NULL;

	if((list = ll_create_node(NULL, 1))==NULL){
		pclose(fp);
		return NULL;
	}
	memset(buf, 0x00, sizeof(buf));
	while(fgets(buf, sizeof(buf)-1, fp)){
		buf[strlen(buf)-1] = 0x00; p = buf;
		while(isspace(*p)) p++;
		if(*p == '#' || *p == 0x00) goto read_cont;
		if(strncmp(p, "kernel", 6)==0) goto read_cont;
		
		memset(&pkg, 0x00, sizeof(pkg));
		if(strlen(p)>=sizeof(pkg.name))
			strncpy(pkg.name, p, sizeof(pkg.name)-1);
		else
			strcpy(pkg.name, p);

		ll_insert_node(list, &pkg, sizeof(scSysPkgInfo), NULL);
read_cont:
		memset(buf, 0x00, sizeof(buf));
	}

	pclose(fp);

	return list;
#endif /* Linux */

#ifdef CYGWIN

	HKEY hKey;
	v_list_t *list = NULL;
	scSysPkgInfo pkg;
	char szProductType[BUFSIZ];

	if (RegOpenKeyEx( HKEY_LOCAL_MACHINE,
        UNINSTALL_KEY,
		0, KEY_READ, &hKey )  != ERROR_SUCCESS ) {
			return NULL;
	}

	if((list = ll_create_node(NULL, 1))==NULL){
		RegCloseKey( hKey );
		return NULL;
	}

	int i = 0;
	while(true) {
		char p[BUFSIZ];
		DWORD  dwBufLen = BUFSIZ;
		FILETIME ftLastWriteTime;      // last write time 

		memset(p, 0x00, BUFSIZ);
		memset(szProductType, 0x00, BUFSIZ);

		 if (RegEnumKeyEx(hKey, i++,
						 szProductType, 
						 &dwBufLen, 
						 NULL, 
						 NULL, 
						 NULL, 
						 &ftLastWriteTime) != ERROR_SUCCESS) 
		 {
			 break;
		 } 


		 if (strncmp(szProductType, "KB", 2) == 0) {
			 continue;
		 }

		 if (programInfo(szProductType, p, BUFSIZ) == false) {
			 continue;
		 }

		
		memset(&pkg, 0x00, sizeof(pkg));
		if(strlen(p)>=sizeof(pkg.name))
			strncpy(pkg.name, p, sizeof(pkg.name)-1);
		else
			strcpy(pkg.name, p);

		ll_insert_node(list, &pkg, sizeof(scSysPatchInfo), NULL);
	}

	RegCloseKey( hKey );

	return list;
#endif /* cygwin */
}

int pscache_update(scCore *core)
{
	int i, count;

	count = 0;
#if !defined(SunOS) && !defined(HPUX) && !defined(CYGWIN)
	for (i = 0; i < HASH_SIZE; i++) {
		if ((core->pscache)[i].toggle != core->toggle) {
			(core->pscache)[i].pid = -1;
			count += 1;
		}
	}
#endif

	return count;
}


int f_fsrch_pname(const void *v1, const void *v2)
{
	char *pname1 = ((scPSInfo *)v1)->pname;
	char *pname2 = ((scPSInfo *)v2)->pname;

	return (!strcmp(pname1, pname2)) ? NODE_FOUND : NODE_NOT_FOUND;
}

void psinfo_sumup_pname(v_list_t *list, scPSInfo *psinfo)
{
	scPSInfo *tmp;
	int at;

	at = 0;
	if ((tmp = (scPSInfo *)ll_search_node_data(list,
					psinfo,
					sizeof(scPSInfo),
					f_fsrch_pname)) != NULL) 
	{
		tmp->started   = (tmp->started > psinfo->started)
					? psinfo->started : tmp->started;
		tmp->cputime  += psinfo->cputime;
		tmp->memused  += psinfo->memused;
		tmp->cpuusage += psinfo->cpuusage;
		tmp->memusage += psinfo->memusage;
		tmp->nthrd    += psinfo->nthrd;
		tmp->nproc    += psinfo->nproc;
		tmp->spare_1  += psinfo->spare_1;
		tmp->spare_2  += psinfo->spare_2;
		tmp->spare_3  += psinfo->spare_3;
	}
	else 
		ll_insert_node(list,psinfo,sizeof(scPSInfo),NULL);

	return;
}

int f_fsrch_pargs(const void *v1, const void *v2)
{
	char *pargs1 = ((scPSInfo *)v1)->args;
	char *pargs2 = ((scPSInfo *)v2)->args;

	return (!strcmp(pargs1, pargs2)) ? NODE_FOUND : NODE_NOT_FOUND;
}

void psinfo_sumup_pargs(v_list_t *list, scPSInfo *psinfo)
{
	scPSInfo *tmp;
	int at;

	at = 0;
	if ((tmp = (scPSInfo *)ll_search_node_data(list, psinfo, sizeof(scPSInfo), f_fsrch_pargs)) != NULL) {
		tmp->started   = (tmp->started > psinfo->started)
					? psinfo->started : tmp->started;
		tmp->cputime  += psinfo->cputime;
		tmp->memused  += psinfo->memused;
		tmp->cpuusage += psinfo->cpuusage;
		tmp->memusage += psinfo->memusage;
		tmp->nthrd    += psinfo->nthrd;
		tmp->nproc    += psinfo->nproc;
		tmp->spare_1  += psinfo->spare_1;
		tmp->spare_2  += psinfo->spare_2;
		tmp->spare_3  += psinfo->spare_3;
	}
	else 
		ll_insert_node(list,psinfo,sizeof(scPSInfo),NULL);

	return;
}

int f_fsrch_uname(const void *v1, const void *v2)
{
	int uid1 = ((scPSInfo *)v1)->uid;
	int uid2 = ((scPSInfo *)v2)->uid;

	return (uid1 == uid2) ? NODE_FOUND : NODE_NOT_FOUND;
}

void psinfo_sumup_uname(v_list_t *list, scPSInfo *psinfo)
{
	scPSInfo *tmp;
	int at;

	at = 0;
	if ((tmp = (scPSInfo *)ll_search_node_data(list, psinfo, sizeof(scPSInfo), f_fsrch_uname)) != NULL) {
		tmp->started   = (tmp->started > psinfo->started)
					? psinfo->started : tmp->started;
		tmp->cputime  += psinfo->cputime;
		tmp->memused  += psinfo->memused;
		tmp->cpuusage += psinfo->cpuusage;
		tmp->memusage += psinfo->memusage;
		tmp->nthrd    += psinfo->nthrd;
		tmp->nproc    += psinfo->nproc;
		tmp->spare_1  += psinfo->spare_1;
		tmp->spare_2  += psinfo->spare_2;
		tmp->spare_3  += psinfo->spare_3;
	}
	else 
		ll_insert_node(list,psinfo,sizeof(scPSInfo),NULL);

	return;
}

#if defined(Linux) || defined(CYGWIN)

int psinfo_stat2proc(proc_t* P, char *dirname)
{
	char  file[64], buf[U_MAXBUFSIZE];
	char *tmp;
	int   n;

	sprintf(file,"/proc/%s/stat",dirname);

	/* dump to memory*/
	if (f2b(file,buf,sizeof(buf)) == 0) 
		return SC_ERR;

	/* split into "PID (cmd" and "<rest>" */
	/* replace trailing ')' with NULL */
	if ((tmp = strrchr(buf, ')')) == NULL) 
		return SC_ERR;

	*tmp = '\0';                            

	/* parse these two strings separately, skipping the leading "(". */
	memset(P->cmd,0x00,sizeof(P->cmd));

	/* skip space after ')' too */
	if (sscanf(buf,"%d (%39c",&P->pid,P->cmd) != 2) 
		return SC_ERR;

	n = sscanf(tmp+2,
			"%c "
			"%d %d %d %d %d "
			"%lu %lu %lu %lu %lu "
			"%Lu %Lu %Lu %Lu "  /* utime stime cutime cstime */
			"%ld %ld "
			"%d "
			"%ld "
			"%Lu "  /* start_time */
			"%lu "
			"%ld "
			"%lu %Lu %Lu %Lu %Lu %Lu "
			"%*s %*s %*s %*s " /* discard, no RT signals & Linux 2.1 used hex */
			"%Lu %*s %*s "
			"%d %d "
			"%lu %lu",
			&P->state,
			&P->ppid, &P->pgrp, &P->session, &P->tty, &P->tpgid,
			&P->flags, &P->min_flt, &P->cmin_flt, &P->maj_flt, &P->cmaj_flt,
			&P->utime, &P->stime, &P->cutime, &P->cstime,
			&P->priority, &P->nice,
			&P->nlwp,
			&P->alarm,
			&P->start_time,
			&P->vsize,
			&P->rss,
			&P->rss_rlim, &P->start_code, &P->end_code, &P->start_stack, &P->kstk_esp, &P->kstk_eip,
			/*     P->signal, P->blocked, P->sigignore, P->sigcatch,   */ /* can't use */
			&P->wchan, /* &P->nswap, &P->cnswap, */  /* nswap and cnswap dead for 2.4.xx and up */
			/* -- Linux 2.0.35 ends here -- */
			&P->exit_signal, &P->processor,  /* 2.2.1 ends with "exit_signal" */
			/* -- Linux 2.2.8 to 2.5.17 end here -- */
			&P->rtprio, &P->sched  /* both added to 2.5.18 */
	); /* == 33 */

	/* the old notty val, update elsewhere bef. moving to 0 */
	if (P->tty == 0)
		P->tty = -1;

	/* when tty wasn't full devno */
	if (P->tty != -1 )
		P->tty = 4*0x100 + P->tty;

	return SC_OK;
}

int psinfo_statm2proc(proc_t* P, char *dirname)
{
	char file[64], buf[U_MAXBUFSIZE];

	/* set the path for /proc/#/statm */
	sprintf(file,"/proc/%s/statm",dirname);

	if (f2b(file,buf,sizeof(buf)) == 0)
		return SC_ERR;

	if (sscanf(buf,"%ld %ld %ld %ld %ld %ld %ld",
			&P->size, &P->resident, &P->share, &P->trs,
			&P->lrs, &P->drs, &P->dt) != 7)
		return SC_ERR;

	return SC_OK;
}

int psinfo_cmdline2proc(proc_t *P, char *dirname)
{
	char file[128], buf[U_MAXBUFSIZE];
	int  n;

	/* set the path for /proc/#/cmdline */
	memset(file, 0x00, sizeof(file));
	sprintf(file,"/proc/%s/cmdline",dirname);
	if ((n = f2b(file,buf,sizeof(buf))) == 0){
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s][%s]\n", __FILE__, __LINE__, file, strerror(errno));
#endif
		return SC_ERR;
	}

	/* calc size */
	n = (n > (int)sizeof(P->args)-1) ? sizeof(P->args)-1 : n; 
	/* alloc cmdline */
	P->args[n] = '\0';
	while (n-- > 0) 
		P->args[n] = (!isprint(buf[n])) ? ' ' : buf[n];
	return SC_OK;
}
#endif /* Linux */

#ifdef CYGWIN

void getName(char *vendor, char* version)
{
   OSVERSIONINFOEX osvi;
   SYSTEM_INFO si;
   PGNSI pGNSI;
   BOOL bOsVersionInfoEx;

   ZeroMemory(&si, sizeof(SYSTEM_INFO));
   ZeroMemory(&osvi, sizeof(OSVERSIONINFOEX));

   // Try calling GetVersionEx using the OSVERSIONINFOEX structure.
   // If that fails, try using the OSVERSIONINFO structure.

   osvi.dwOSVersionInfoSize = sizeof(OSVERSIONINFOEX);

   if( !(bOsVersionInfoEx = GetVersionEx ((OSVERSIONINFO *) &osvi)) )
   {
      osvi.dwOSVersionInfoSize = sizeof (OSVERSIONINFO);
      if (! GetVersionEx ( (OSVERSIONINFO *) &osvi) ) 
         return ;
   }

   // Call GetNativeSystemInfo if supported
   // or GetSystemInfo otherwise.

   pGNSI = (PGNSI) GetProcAddress(
      GetModuleHandle("kernel32.dll"), "GetNativeSystemInfo");
   if(NULL != pGNSI)
      pGNSI(&si);
   else GetSystemInfo(&si);

   switch (osvi.dwPlatformId)
   {
      // Test for the Windows NT product family.

      case VER_PLATFORM_WIN32_NT:

      // Test for the specific product.

      if ( osvi.dwMajorVersion == 6 && osvi.dwMinorVersion == 0 )
      {
         if( osvi.wProductType == VER_NT_WORKSTATION )
             strcpy(vendor, "Windows Vista ");
         else strcpy (vendor, "Windows Server \"Longhorn\" " );
      }

      if ( osvi.dwMajorVersion == 5 && osvi.dwMinorVersion == 2 )
      {
         if( GetSystemMetrics(SM_SERVERR2) )
            strcpy(vendor, "Microsoft Windows Server 2003 \"R2\" ");
         else if( osvi.wProductType == VER_NT_WORKSTATION &&
            si.wProcessorArchitecture==PROCESSOR_ARCHITECTURE_AMD64)
         {
            strcpy(vendor, "Microsoft Windows XP Professional x64 Edition ");
         }
         else strcpy(vendor, "Microsoft Windows Server 2003, ");
      }

      if ( osvi.dwMajorVersion == 5 && osvi.dwMinorVersion == 1 )
         strcpy(vendor, "Microsoft Windows XP ");

      if ( osvi.dwMajorVersion == 5 && osvi.dwMinorVersion == 0 )
         strcpy(vendor, "Microsoft Windows 2000 ");

      if ( osvi.dwMajorVersion <= 4 )
        strcpy(vendor, "Microsoft Windows NT ");

      // Test for specific product on Windows NT 4.0 SP6 and later.
      if( bOsVersionInfoEx )
      {
         // Test for the workstation type.
         if ( osvi.wProductType == VER_NT_WORKSTATION &&
              si.wProcessorArchitecture!=PROCESSOR_ARCHITECTURE_AMD64)
         {
            if( osvi.dwMajorVersion == 4 )
               strcat(vendor,  "Workstation 4.0 " );
            else if( osvi.wSuiteMask & VER_SUITE_PERSONAL )
               strcat(vendor, "Home Edition " );
            else strcat(vendor,  "Professional " );
         }
            
         // Test for the server type.
         else if ( osvi.wProductType == VER_NT_SERVER || 
                   osvi.wProductType == VER_NT_DOMAIN_CONTROLLER )
         {
            if(osvi.dwMajorVersion==5 && osvi.dwMinorVersion==2)
            {
               if ( si.wProcessorArchitecture ==
                    PROCESSOR_ARCHITECTURE_IA64 )
               {
                   if( osvi.wSuiteMask & VER_SUITE_DATACENTER )
                      strcat(vendor,  "Datacenter Edition "
                               "for Itanium-based Systems" );
                   else if( osvi.wSuiteMask & VER_SUITE_ENTERPRISE )
                      strcat(vendor, "Enterprise Edition "
                               "for Itanium-based Systems" );
               }

               else if ( si.wProcessorArchitecture ==
                         PROCESSOR_ARCHITECTURE_AMD64 )
               {
                   if( osvi.wSuiteMask & VER_SUITE_DATACENTER )
                      strcat(vendor,  "Datacenter x64 Edition " );
                   else if( osvi.wSuiteMask & VER_SUITE_ENTERPRISE )
                      strcat(vendor,  "Enterprise x64 Edition " );
                   else strcat(vendor,  "Standard x64 Edition " );
               }

               else
               {
                   if( osvi.wSuiteMask & VER_SUITE_DATACENTER )
                      strcat(vendor,  "Datacenter Edition " );
                   else if( osvi.wSuiteMask & VER_SUITE_ENTERPRISE )
                      strcat(vendor,  "Enterprise Edition " );
                   else if ( osvi.wSuiteMask & VER_SUITE_BLADE )
                      strcat(vendor,  "Web Edition " );
                   else strcat(vendor, "Standard Edition " );
               }
            }
            else if(osvi.dwMajorVersion==5 && osvi.dwMinorVersion==0)
            {
               if( osvi.wSuiteMask & VER_SUITE_DATACENTER )
                  strcat(vendor,  "Datacenter Server " );
               else if( osvi.wSuiteMask & VER_SUITE_ENTERPRISE )
                  strcat(vendor,  "Advanced Server " );
               else strcat(vendor,  "Server " );
            }
            else  // Windows NT 4.0 
            {
               if( osvi.wSuiteMask & VER_SUITE_ENTERPRISE )
                  strcat(vendor, "Server 4.0, Enterprise Edition " );
               else strcat(vendor,  "Server 4.0 " );
            }
         }
      }

      sprintf(version,"%s (Build %d)",
            osvi.szCSDVersion,
            osvi.dwBuildNumber & 0xFFFF);
      break;

      // Test for the Windows Me/98/95.
      case VER_PLATFORM_WIN32_WINDOWS:

      if (osvi.dwMajorVersion == 4 && osvi.dwMinorVersion == 0)
      {
          strcpy(vendor, "Microsoft Windows 95 ");
          if (osvi.szCSDVersion[1]=='C' || osvi.szCSDVersion[1]=='B')
             strcat(vendor,"OSR2 " );
      } 

      if (osvi.dwMajorVersion == 4 && osvi.dwMinorVersion == 10)
      {
          strcpy(vendor,"Microsoft Windows 98 ");
          if ( osvi.szCSDVersion[1]=='A' || osvi.szCSDVersion[1]=='B')
             strcat(vendor,"SE " );
      } 

      if (osvi.dwMajorVersion == 4 && osvi.dwMinorVersion == 90)
      {
          strcpy(vendor,"Microsoft Windows Millennium Edition");
      } 
      break;

      case VER_PLATFORM_WIN32s:

      strcpy(vendor,"Microsoft Win32s");
      break;
   }
   return ; 
}
#endif //CYGWIN



int scCoreSysBasicInfo(scCore *core, scSysInfo *sysinfo)
{
	int err=SC_OK;
	struct utsname u;

	if (uname(&u) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] uname error!\n", __FUNCTION__, __LINE__);
#endif
		return SC_ERR;
	}

	/* setup the hardcoded one */
	snprintf(sysinfo->pseudoname   ,SC_STRING_MIN_LEN,"%s%s.%s", u.sysname, u.version, u.release);
	snprintf(sysinfo->pseudoversion,SC_STRING_MIN_LEN,"%s.%s", u.version, u.release);
#if defined(AIX)
	snprintf(sysinfo->vendor       ,SC_STRING_MIN_LEN,"IBM");
#else
# if defined(SunOS)
	snprintf(sysinfo->vendor, SC_STRING_MIN_LEN, "SUN");
# else
#  if defined(HPUX)
	snprintf(sysinfo->vendor, SC_STRING_MIN_LEN, "HP");
#  else
#   if defined(Linux)
	snprintf(sysinfo->vendor, SC_STRING_MIN_LEN, "Linux");
# else
#	if defined(CYGWIN)
	char vendor[BUFSIZ], version[BUFSIZ];
	memset(vendor,'0x00', BUFSIZ);

	getName(vendor, version);

	snprintf(sysinfo->vendor, SC_STRING_MIN_LEN, "Windows");
#   else
	snprintf(sysinfo->vendor, SC_STRING_MIN_LEN, "Unknown");
#	endif
#   endif
#  endif
# endif
#endif /* AIX */

		/* setup the rest */

#ifdef CYGWIN
	snprintf(sysinfo->osname  ,SC_STRING_MIN_LEN,"%s",vendor);
	snprintf(sysinfo->version ,SC_STRING_MIN_LEN,"%s",version);
	snprintf(sysinfo->release ,SC_STRING_MIN_LEN,"%s",version);
#else 
	snprintf(sysinfo->osname  ,SC_STRING_MIN_LEN,"%s",u.sysname);
	snprintf(sysinfo->version ,SC_STRING_MIN_LEN,"%s",u.version);
	snprintf(sysinfo->release ,SC_STRING_MIN_LEN,"%s",u.release);
#endif // CYGWIN
	snprintf(sysinfo->hostname,SC_STRING_MIN_LEN,"%s",u.nodename);
	snprintf(sysinfo->machine ,SC_STRING_MIN_LEN,"%s",u.machine);

	return err;
}


int scCoreSysCpuInfo(scCore *core, scSysInfo *sysinfo)
{
	int err=SC_OK;
#if defined(AIX)
	perfstat_cpu_total_t pstat;

	if (perfstat_cpu_total(NULL,&pstat,sizeof(perfstat_cpu_total_t),1) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] perfstat cpu total error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	/* clock speed */
	sysinfo->ncpu = pstat.ncpus;

	/* clock speed */
	sysinfo->clockspeed = pstat.processorHZ >> U_LOG1024*2;

	/* cpu type */
	sprintf(sysinfo->cputype,"%s",pstat.description);
	return err;

#else
# if defined(SunOS)

	int count=0;

	kstat_t *ksp;
	kstat_named_t *kn;
	
	for (ksp = KCTL(core)->kc_chain; ksp != NULL; ksp = ksp->ks_next) {
		if (ksp->ks_type != KSTAT_TYPE_NAMED
				|| strcmp(ksp->ks_class ,"misc") != 0
				|| strcmp(ksp->ks_module,"cpu_info") != 0
				|| kstat_read(KCTL(core),ksp,NULL) == -1)
			continue;

		if (!count) {
			kn = (kstat_named_t*)kstat_data_lookup(ksp, "cpu_type");
			sprintf(sysinfo->cputype, "%s", (kn != NULL) ? kn->value.c : "unknown");
		
			kn = (kstat_named_t*)kstat_data_lookup(ksp, "clock_MHz");
			sysinfo->clockspeed = (kn != NULL) ? kn->value.i32 : 0;
		}

		count++;
	} 

	sysinfo->ncpu = count;

	return (!count) ? SC_ERR : SC_OK;
# else
#  if defined(HPUX)

	union  pstun pstatbuff;
	struct pst_processor pprocs;
	int clockspeed;

	sysinfo->ncpu = core->maxcpu;

	/* cpu speed */
	sysinfo->clockspeed = 0;
	pstatbuff.pst_processor = &pprocs;
	if (pstat(PSTAT_PROCESSOR, pstatbuff, sizeof(pprocs), (size_t)1, 0) > 0
				&& (clockspeed = pprocs.psp_iticksperclktick) > 0)
	{
		long hz = sysconf(_SC_CLK_TCK);
		sysinfo->clockspeed = clockspeed / hz / 100;
	}

	/* cpu type */
	if (scCoreSysSetupCpuType(sysinfo->cputype) == -1)
		sprintf(sysinfo->cputype, "unknown");

	return SC_OK;

#  else /* HPUX */
#   if defined(Linux) || defined(CYGWIN)

	char line[256], buf[8192];
	int  totlen, len, count, n;

	if ((len = f2b(SC_PROC_CPUINFO,buf,sizeof(buf))) == 0) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	totlen = 0, count = 0;

	while ((len = b2ln(buf+totlen,line,sizeof(line))) != 0) {
		char **tk;

		if (!strncmp(line,"processor",strlen("processor"))) count++;

		if (!strncmp(line,"model name",strlen("model name")) && count == 1) {
			if ((tk = tk_alloc(line,":",&n)) != NULL && n == 2) {
				snprintf(sysinfo->cputype,SC_BINFO_STR_LEN,"%s",tk[1]);
				trim(sysinfo->cputype);

				tk_release(&tk);
			}
		}

		if (!strncmp(line,"cpu MHz",strlen("cpu MHz")) && count == 1) {
			if ((tk = tk_alloc(line,":",&n)) != NULL && n == 2) {
				sysinfo->clockspeed = atoi(tk[1]);

				tk_release(&tk);
			}
		}

		totlen += len;
	}

	sysinfo->ncpu = count;

	return (!count) ? SC_ERR : SC_OK;

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */

}

#if defined(HPUX)
int scCoreSysSetupCpuType(char *type)
{
	FILE *f;
	char line[128], *cp, *model;
	struct utsname  un;

	/* uname() */
	if (uname(&un) != 0) return -1;

	if ((model = strrchr(un.machine, '/')) != NULL)
		++model;
	else
		model = un.machine;

	/* fopen() */
	if (!(f = fopen(_PATH_SCHED_MODELS, "r"))) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return -1;
	}
	while (fgets(line, sizeof(line), f)) {
		if (!strncmp(line, "/*", 2)) continue;
		if (strncmp(model, line, strlen(model))) continue;
		if ((cp = strchr(line, '\n')) != NULL) *cp = '\0';

		while(*cp != '\t') cp--;
		cp++;
		strcpy(type, cp);

		break;
	}

	fclose(f);

	return 1;
}

#endif

int scCoreSysCpuRawStatus(scCore *core, scCpuRawStatus *cpustat)
{

#if defined(AIX)
	int err=SC_OK;
	perfstat_cpu_total_t pstat;

	if (perfstat_cpu_total(NULL,&pstat,sizeof(perfstat_cpu_total_t),1) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] perfstat cpu total error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	cpustat->ticks[SC_CPUSTAT_USR]  = (unsigned long)pstat.user; /* user   */
	cpustat->ticks[SC_CPUSTAT_SYS]  = (unsigned long)pstat.sys;  /* system */
	cpustat->ticks[SC_CPUSTAT_ETC]  = (unsigned long)pstat.wait; /* wio    */
	cpustat->ticks[SC_CPUSTAT_IDLE] = (unsigned long)pstat.idle; /* idle   */
	cpustat->id = 0;

	return err;

#else
# if defined(SunOS)

	/* kernel specific */
	kstat_t *ksp;
	cpu_stat_t cpuvalue;

	/* you know how come.. */
	memset(cpustat,0x00,sizeof(scCpuRawStatus));

	/* lookup the cpustats */
	for (ksp = KCTL(core)->kc_chain; ksp != NULL; ksp = ksp->ks_next) {
		if (strncmp(ksp->ks_name, "cpu_stat", 8)
				|| kstat_read(KCTL(core),ksp,&cpuvalue) == -1)
			continue;

		/* cpu stats */
		cpustat->ticks[SC_CPUSTAT_USR]  += cpuvalue.cpu_sysinfo.cpu[1]; /* user */
		cpustat->ticks[SC_CPUSTAT_SYS]  += cpuvalue.cpu_sysinfo.cpu[2]; /* sys  */
		cpustat->ticks[SC_CPUSTAT_IDLE] += cpuvalue.cpu_sysinfo.cpu[0]; /* idle */

		/* wio */
		cpustat->ticks[SC_CPUSTAT_ETC] += (long) cpuvalue.cpu_sysinfo.wait[W_IO];
		cpustat->ticks[SC_CPUSTAT_ETC] += (long) cpuvalue.cpu_sysinfo.wait[W_PIO];
	}

	cpustat->id = 0;

	return SC_OK;

# else
#  if defined(HPUX)

	struct pst_dynamic pdynamic;

	memset(cpustat,0x00,sizeof(scCpuRawStatus));

	if (pstat_getdynamic(&pdynamic, sizeof(pdynamic), 1, 0) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	/* user */
	cpustat->ticks[SC_CPUSTAT_USR]  = pdynamic.psd_cpu_time[CP_USER];
	cpustat->ticks[SC_CPUSTAT_USR] +=pdynamic.psd_cpu_time[CP_NICE]; 

	/* sys */
	cpustat->ticks[SC_CPUSTAT_SYS]  = pdynamic.psd_cpu_time[CP_SYS];
	cpustat->ticks[SC_CPUSTAT_SYS] += pdynamic.psd_cpu_time[CP_SSYS];

	/* idle */
	cpustat->ticks[SC_CPUSTAT_IDLE] = pdynamic.psd_cpu_time[CP_IDLE];

	/* etc */
	cpustat->ticks[SC_CPUSTAT_ETC]  = pdynamic.psd_cpu_time[CP_WAIT]; 
	cpustat->ticks[SC_CPUSTAT_ETC] += pdynamic.psd_cpu_time[CP_SWAIT]; 
	cpustat->ticks[SC_CPUSTAT_ETC] += pdynamic.psd_cpu_time[CP_BLOCK];

	/* cpu Id */
	cpustat->id = 0;

	return SC_OK;

#  else /* HPUX */
#   if defined(Linux) || defined(CYGWIN)

	char buf[U_MAXBUFSIZE], line[256];
	int  totlen, len, n;

	if ((len = f2b(SC_PROC_STAT,buf,sizeof(buf))) == 0) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	/* cpustat */
	totlen = 0;
	while ((len = b2ln(buf+totlen,line,sizeof(line))) != 0) {
		if (!strncmp(line,"cpu ",4)) {
			n = sscanf(line,"cpu %lu %lu %lu %lu %*s\n",
						&(cpustat->ticks[SC_CPUSTAT_USR]), /* user   */
						&(cpustat->ticks[SC_CPUSTAT_ETC]), /* nice   */
						&(cpustat->ticks[SC_CPUSTAT_SYS]), /* system */
						&(cpustat->ticks[SC_CPUSTAT_IDLE]) /* idle */
			);

			if (n != 4) {
#ifdef DEBUG
				fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
				return SC_ERR;
			}
			else
				cpustat->id = 0;
		}

		totlen += len;
	}

	return SC_OK;

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */
}

int scCoreSysMultiCpuRawStatus(scCore *core, scCpuRawStatus cpustat[SC_CPUSTAT_NUM], int *ncpu)
{
#if defined(AIX)

	int err=SC_OK;

	int cpunum, cc, at;
	char *cp, ch, tmp[8];

	perfstat_id_t firstcpu;
	perfstat_cpu_t *pstat;


	/* calculate the number of cpus */
	cpunum = perfstat_cpu(NULL, NULL, sizeof(perfstat_cpu_t), 0);
	cpunum = (cpunum > SC_CPUSTAT_NUM) ? SC_CPUSTAT_NUM : cpunum;

	/* per cpu, cpu stat */
	if ((pstat = calloc(cpunum,sizeof(perfstat_cpu_t))) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] calloc error!\n", __FUNCTION__, __LINE__);
#endif
		err=SC_ERR;
		goto err_quit;
	}

	/* set logical cpu name */
	strcpy(firstcpu.name,"");

	if ((cc = perfstat_cpu(&firstcpu,pstat,sizeof(perfstat_cpu_t),cpunum)) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] perfstat cpu error[%s]!\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		err=SC_ERR;
		goto err_quit;
	}

	*ncpu = 0;
	while (*ncpu < cc) {
		cpustat[*ncpu].ticks[SC_CPUSTAT_USR]  = (unsigned long)pstat[*ncpu].user; /* user   */
		cpustat[*ncpu].ticks[SC_CPUSTAT_SYS]  = (unsigned long)pstat[*ncpu].sys;  /* system */
		cpustat[*ncpu].ticks[SC_CPUSTAT_ETC]  = (unsigned long)pstat[*ncpu].wait; /* wio    */
		cpustat[*ncpu].ticks[SC_CPUSTAT_IDLE] = (unsigned long)pstat[*ncpu].idle; /* idle   */

		/* derive cpu id from the logical name */
		cp = pstat[*ncpu].name;
		at = 0;
		while ((ch = *cp++) != '\0' && at < sizeof(tmp)-1) {
			if (isdigit((int)ch)) {
				tmp[at] = ch;
				at++;
			}
		}
		tmp[at] = '\0';

		cpustat[*ncpu].id = atoi(tmp);

		/* the next one */
		*ncpu = *ncpu + 1;
	}

err_quit:
	if (pstat)
		free(pstat);

	return err;

#else
# if defined(SunOS)

	kstat_t *ksp;
	cpu_stat_t cpuvalue;

	/* initialize */
	*ncpu = 0;

	/* lookup the cpustats */
	for (ksp = KCTL(core)->kc_chain; ksp != NULL; ksp = ksp->ks_next) {
		if (strncmp(ksp->ks_name, "cpu_stat", 8)
				|| kstat_read(KCTL(core),ksp,&cpuvalue) == -1)
			continue;

		/* in case */
		if (*ncpu >= SC_MAX_CPU_NUM) {
#ifdef DEBUG
			fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
			return SC_ERR;
		}

		/* cpu id */
		cpustat[*ncpu].id = atoi(ksp->ks_name + 8);

		/* cpu stats */
		cpustat[*ncpu].ticks[SC_CPUSTAT_USR]  = cpuvalue.cpu_sysinfo.cpu[1]; /* user */
		cpustat[*ncpu].ticks[SC_CPUSTAT_SYS]  = cpuvalue.cpu_sysinfo.cpu[2]; /* sys  */
		cpustat[*ncpu].ticks[SC_CPUSTAT_IDLE] = cpuvalue.cpu_sysinfo.cpu[0]; /* idle */

		/* wio */
		cpustat[*ncpu].ticks[SC_CPUSTAT_ETC]  = (long) cpuvalue.cpu_sysinfo.wait[W_IO];
		cpustat[*ncpu].ticks[SC_CPUSTAT_ETC] += (long) cpuvalue.cpu_sysinfo.wait[W_PIO];

		/* the next one */
		*ncpu = *ncpu + 1;
	}

	/* check out the number */
	if (!*ncpu) {
#ifdef DEBUG
			fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	return SC_OK;

# else
#  if defined(HPUX)

	int i;

	struct pst_dynamic pdynamic;

	if (pstat_getdynamic(&pdynamic, sizeof(pdynamic), 1, 0) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	/* setup the count */
	*ncpu = core->maxcpu;

	for (i = 0; i < *ncpu; i++) {
		/* cpu id */
		cpustat[i].id = i+1;

		/* user */
		cpustat[i].ticks[SC_CPUSTAT_USR]  = pdynamic.psd_mp_cpu_time[i][CP_USER];
		cpustat[i].ticks[SC_CPUSTAT_USR] +=pdynamic.psd_mp_cpu_time[i][CP_NICE]; 

		/* sys */
		cpustat[i].ticks[SC_CPUSTAT_SYS]  = pdynamic.psd_mp_cpu_time[i][CP_SYS];
		cpustat[i].ticks[SC_CPUSTAT_SYS] += pdynamic.psd_mp_cpu_time[i][CP_SSYS];

		/* idle */
		cpustat[i].ticks[SC_CPUSTAT_IDLE] = pdynamic.psd_mp_cpu_time[i][CP_IDLE];

		/* etc */
		cpustat[i].ticks[SC_CPUSTAT_ETC]  = pdynamic.psd_mp_cpu_time[i][CP_WAIT]; 
		cpustat[i].ticks[SC_CPUSTAT_ETC] += pdynamic.psd_mp_cpu_time[i][CP_SWAIT]; 
		cpustat[i].ticks[SC_CPUSTAT_ETC] += pdynamic.psd_mp_cpu_time[i][CP_BLOCK];
	}

	/* check out the number */
	if (!*ncpu) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	return SC_OK;

#  else /* HPUX */
#   if defined(Linux) || defined(CYGWIN)

	char buf[U_MAXBUFSIZE], line[256];
	int  totlen, len, n;

	if ((len = f2b(SC_PROC_STAT,buf,sizeof(buf))) == 0) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	*ncpu = 0, totlen = 0;

	while ((len = b2ln(buf+totlen,line,sizeof(line))) != 0) {
		if (!strncmp(line,"cpu",3) 
				&& isdigit((int)*(line+3))
				&& SC_MAX_CPU_NUM > *ncpu)
		{
			n = sscanf(line,"cpu%d %lu %lu %lu %lu %*s\n",
						&(cpustat[*ncpu].id),                   /* id    */
						&(cpustat[*ncpu].ticks[SC_CPUSTAT_USR]), /* user   */
						&(cpustat[*ncpu].ticks[SC_CPUSTAT_ETC]), /* nice   */
						&(cpustat[*ncpu].ticks[SC_CPUSTAT_SYS]), /* system */
						&(cpustat[*ncpu].ticks[SC_CPUSTAT_IDLE]) /* idle   */
			);

			if (n == 5) 
				*ncpu = *ncpu + 1;
		}

		totlen += len;
	}

	if (!*ncpu) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	return SC_OK;

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */
}
 

int scCoreSysMemStatus(scCore *core, scMemStatus *memstat)
{
#if defined(AIX)

	int err=SC_OK;

	unsigned long sizefree;

	perfstat_memory_total_t pstat;

	if (perfstat_memory_total(NULL, &pstat, sizeof(perfstat_memory_total_t), 1) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] perstat memory total error[%s]!\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	/* physical memory */
	sizefree         = page2k((unsigned long)pstat.real_free);
	memstat->m_total = page2k((unsigned long)pstat.real_total);
	memstat->m_used  = memstat->m_total - sizefree;

	/* swap */
	sizefree         = page2k((unsigned long)pstat.pgsp_free);
	memstat->s_total = page2k((unsigned long)pstat.pgsp_total);
	memstat->s_used  = memstat->s_total - sizefree;

	/* the rest */
	memstat->m_cache = page2k((unsigned long)pstat.numperm); /* file cache */
	memstat->m_proc  = 0;

	memstat->spare_1 = (unsigned long)pstat.pgsp_rsvd * 1024; /* reserved paging space */
	memstat->spare_2 = page2k((unsigned long)pstat.virt_total);   /* virtual memory total  */
	memstat->spare_3 = page2k((unsigned long)pstat.real_pinned);  /* pinned pages */

	return err;

#else
# if defined(SunOS)

	unsigned long m_free;

	kstat_t       *ksp;
	kstat_named_t *kn;

	if ((ksp = kstat_lookup(KCTL(core),"unix",0,"system_pages")) == NULL
					|| kstat_read(KCTL(core), ksp, 0) == -1
					|| (kn = (kstat_named_t*)kstat_data_lookup(ksp,"freemem")) == NULL)
	{
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	m_free = page2k(kn->value.ul);

	/* calculate the total & used */
	memstat->m_total = page2k(sysconf(_SC_PHYS_PAGES));
	memstat->m_used  = memstat->m_total - m_free;

	/* unless RMCTool is not supported. */
	memstat->m_proc  = 0;
	memstat->m_cache = 0;
	memstat->spare_1 = 0;
	memstat->spare_2 = 0;
	memstat->spare_3 = 0;

	return SC_OK;

# else
#  if defined(HPUX)

	unsigned long m_free;

	struct pst_static  pstatic;
	struct pst_dynamic pdynamic;


	if (pstat_getstatic(&pstatic, sizeof(pstatic), 1, 0) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	if (pstat_getdynamic(&pdynamic, sizeof(pdynamic), 1, 0) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	m_free = page2k(pdynamic.psd_free);
	memstat->m_total = page2k(pstatic.physical_memory);
	memstat->m_used  = memstat->m_total - m_free;

	memstat->m_proc  = 0;
	memstat->m_cache = 0;
	memstat->spare_1 = 0;
	memstat->spare_2 = 0;
	memstat->spare_3 = 0;

	return SC_OK;

#  else /* HPUX */
#   if defined(Linux) || defined(CYGWIN)

	char buf[U_MAXBUFSIZE], line[256], *p;
	int  totlen, len;

	if ((len = f2b(SC_PROC_MEMINFO,buf,sizeof(buf))) == 0) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n",
			__FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	totlen = 0;

	while ((len = b2ln(buf+totlen,line,sizeof(line))) != 0) {
		/* total:    used:    free:  shared: buffers:  cached: */
		if (!strncmp(line,"MemTotal:",9) && (p = skip_token(line)) != NULL) {
			memstat->m_total = (long)strtoull(p,&p,10);
		} else if(!strncmp(line,"MemFree:", 8) && (p = skip_token(line))!=NULL){
			memstat->m_used  = memstat->m_total - (long)strtoull(p,&p,10);
		} else if(!strncmp(line,"MemShared:", 10) &&
			(p = skip_token(line))!=NULL) {
			memstat->spare_1 = (long)strtoull(p,&p,10) ; /* shared  */
		} else if(!strncmp(line,"Buffers:", 8) && (p = skip_token(line))!=NULL){
			memstat->spare_2 = (long)strtoull(p,&p,10); /* buffers */
		} else if(!strncmp(line,"Cached:", 7) && (p = skip_token(line))!=NULL) {
			memstat->spare_3 = (long)strtoull(p,&p,10); /* cached  */
		} else if (!strncmp(line,"SwapTotal:",10) &&
			(p = skip_token(line)) != NULL) 
		{
			/* swapstat */
			memstat->s_total = (long)strtoull(p, &p, 10);
		} else if (!strncmp(line, "SwapFree:", 9) &&
			(p = skip_token(line)) != NULL) 
		{
			memstat->s_used  = memstat->s_total - ((long)strtoull(p, &p, 10) );
		}

		/* anon */
		if (!strncmp(line,"ActiveAnon:",11) && (p = skip_token(line)) != NULL) {
			memstat->m_proc = strtoul(p, &p, 10); /* kb unit */
		}

		/* cache */
		if (!strncmp(line,"ActiveCache:",12) && (p = skip_token(line)) != NULL){
			memstat->m_cache = strtoul(p, &p, 10); /* kb unit */
		}

		totlen += len;
	}

	// used = total - free - buffers - cached
	memstat->m_used  = memstat->m_used - memstat->spare_2 - memstat->spare_3 ;

	if (memstat->m_used <= 0) memstat->m_used =0;

	return SC_OK;

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */
}

int scCoreSysMemStatusPhysic(scCore *core, unsigned long *physic)
{
#if defined(AIX)
	int err=SC_OK;
	scMemStatus memstat;


	/* initialize first */
	memset(&memstat,0x00,sizeof(scMemStatus));

	/* calculate the physical memory */
	if ((err=scCoreSysMemStatus(core,&memstat)) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] can't get system memory status!\n", __FUNCTION__, __LINE__);
#endif
		return err;
	}

	*physic = (!memstat.m_total) ? 1 : memstat.m_total;

	return err;

#else
# if defined(SunOS)

	*physic = page2k(sysconf(_SC_PHYS_PAGES));
	*physic = (!*physic) ? 1 : *physic;

	return SC_OK;

# else
#  if defined(HPUX)

	*physic = page2k(core->__physical);
	*physic = (!*physic) ? 1 : *physic;

	return SC_OK;

#  else /* HPUX */
#   if defined(Linux) || defined(CYGWIN)

	scMemStatus memstat;

	memset(&memstat,0x00,sizeof(scMemStatus));

	if (scCoreSysMemStatus(core,&memstat) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	*physic = (!memstat.m_total) ? 1 : memstat.m_total;

	return SC_OK;

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */

}


int scCoreSysSwapStatus(scCore *core, scMemStatus *memstat)
{
	int err=SC_OK;

#if defined(AIX)
#else
# if defined(SunOS)

	register int cnt, i;
	register long t, f;
	struct swaptable *swt;
	struct swapent *ste;
	static char path[256];

	unsigned long s_free;

	cnt = swapctl(SC_GETNSWP, 0);

	/* allocate enough space to hold count + n swapents */
	if ((swt = (struct swaptable *)malloc(sizeof(int) + cnt
					* sizeof(struct swapent))) == NULL)
	{
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	swt->swt_n = cnt;

	/* fill in ste_path pointers: we don't care about the paths, so we point
	 * them all to the same buffer
	 */
	ste = &(swt->swt_ent[0]);
	i = cnt;
	while (--i >= 0) {
		ste++->ste_path = path;
	}

	/* grab all swap info */
	swapctl(SC_LIST, swt);

	/* walk thru the structs and sum up the fields */
	t = f = 0;
	ste = &(swt->swt_ent[0]);
	i = cnt;
	while (--i >= 0) {
		/* dont count slots being deleted */
		if (!(ste->ste_flags & ST_INDEL) && !(ste->ste_flags & ST_DOINGDEL)) {
			t += ste->ste_pages;
			f += ste->ste_free;
		}
		ste++;
	}

	/* set the proper swap values */
	s_free = page2k(f);
	memstat->s_total = page2k(t);
	memstat->s_used  = memstat->s_total - s_free;

	/* release the swaptable */
	free(swt);

	return SC_OK; 

# else
#  if defined(HPUX)

	register int cnt, i;
	register long t, f;
	unsigned long s_free;

	struct pst_swapinfo  *pswap;

	cnt = 1; t = f = 0;

	/* don't forget to free this */
	pswap = (struct pst_swapinfo *)malloc(1024 * sizeof(struct pst_swapinfo));
	if (pstat_getswap(pswap, sizeof(struct pst_swapinfo), cnt, 0) == -1) {
		/* release */
		free(pswap);
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	for (i = 0; i < cnt; i++) {
		if (pswap[i].pss_nblks <= 0) break;

		t += pswap[i].pss_nblks;
		f += pswap[i].pss_nfpgs;
	}

	s_free = page2k(f);
	memstat->s_total = page2k(t);
	memstat->s_used  = memstat->s_total - s_free;

	free(pswap);

	return SC_OK; 

#  else /* HPUX */
#   if defined(Linux) || defined(CYGWIN)

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */

	return err; 
}

int scCoreSysVMRawStatus(scCore *core, scVMRawStatus *vmrawstat)
{
#if defined(AIX)
	int err=SC_OK;
	perfstat_cpu_total_t cpstat;
	perfstat_memory_total_t mmstat;

	if (perfstat_cpu_total(NULL, &cpstat, sizeof(perfstat_cpu_total_t), 1) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] perfstat cpu total error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	if (perfstat_memory_total(NULL, &mmstat, sizeof(perfstat_memory_total_t), 1) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] perfstat memory total error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	/* setup the vmstat */
	vmrawstat->runqueue = (unsigned long)cpstat.runque;
	vmrawstat->pagein   = page2k((unsigned long)mmstat.pgins);
	vmrawstat->pageout  = page2k((unsigned long)mmstat.pgouts);
	vmrawstat->pagefault = (unsigned long)mmstat.pgexct;
	vmrawstat->scanrate  = (unsigned long)mmstat.scans;

	/* do not know how to */
	vmrawstat->swapin   = 0;
	vmrawstat->swapout  = 0;

	return err;
#else
# if defined(SunOS)

    kstat_t *ksp;
	kstat_named_t *kn;
    sysinfo_t  sysinfo;
    cpu_stat_t cpustats;

	/* runqueue */
	if ((ksp = kstat_lookup(KCTL(core),"unix",0,"sysinfo")) == NULL
					|| kstat_read(KCTL(core),ksp,&sysinfo) == -1)
	{
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	vmrawstat->runqueue = sysinfo.runque;

	/* the rest */
	for (ksp = KCTL(core)->kc_chain; ksp != NULL; ksp = ksp->ks_next) {
		if(strncmp(ksp->ks_name, "cpu_stat", 8)
				|| kstat_read(KCTL(core), ksp, &cpustats) == -1)
			continue;
	
		/* pageing */
		vmrawstat->pagein  += page2k((long)cpustats.cpu_vminfo.pgpgin);
		vmrawstat->pageout += page2k((long)cpustats.cpu_vminfo.pgpgout);
		vmrawstat->swapin  += page2k((long)cpustats.cpu_vminfo.pgswapin);
		vmrawstat->swapout += page2k((long)cpustats.cpu_vminfo.pgswapout);

		/* pagefault */
		vmrawstat->pagefault += (long)cpustats.cpu_vminfo.maj_fault;
		vmrawstat->pagefault += (long)cpustats.cpu_vminfo.hat_fault;
		vmrawstat->pagefault += (long)cpustats.cpu_vminfo.as_fault;

		/* scanrate */
		vmrawstat->scanrate += (long)cpustats.cpu_vminfo.scan;
	}

	/* lookup for load average */
	if ((ksp = kstat_lookup(KCTL(core),"unix",0,"system_misc")) == NULL
					|| kstat_read(KCTL(core), ksp, 0) == -1)
	{
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	/* 1 min */
	kn = (kstat_named_t*)kstat_data_lookup(ksp, "avenrun_1min");
	vmrawstat->la_1min = (kn != NULL) ? kn->value.ui32 : 0;

	/* 5 min */
	kn = (kstat_named_t*)kstat_data_lookup(ksp, "avenrun_5min");
	vmrawstat->la_5min = (kn != NULL) ? kn->value.ui32 : 0;

	/* 15 min */
	kn = (kstat_named_t*)kstat_data_lookup(ksp, "avenrun_15min");
	vmrawstat->la_15min = (kn != NULL) ? kn->value.ui32 : 0;

	return SC_OK;

# else
#  if defined(HPUX)

	int ncpus, i;

	struct pst_processor *pcpustat;
	struct pst_vminfo    pvminfo;

	ncpus = core->maxcpu;

	pcpustat = (struct pst_processor *)malloc(ncpus*sizeof(struct pst_processor));
	if (pstat_getprocessor(pcpustat,sizeof(struct pst_processor),ncpus,0) == -1) {
		free(pcpustat);

#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	for (i = 0; i < ncpus; i++){
		vmrawstat->la_1min += pcpustat[i].psp_avg_1_min;
		vmrawstat->la_5min += pcpustat[i].psp_avg_5_min;
		vmrawstat->la_15min += pcpustat[i].psp_avg_15_min;
		vmrawstat->runqueue += pcpustat[i].psp_runque;
	}
	vmrawstat->la_1min = vmrawstat->la_1min/ncpus;
	vmrawstat->la_5min = vmrawstat->la_5min/ncpus;
	vmrawstat->la_15min = vmrawstat->la_15min/ncpus;

	free(pcpustat);

	if (pstat_getvminfo(&pvminfo, sizeof(pvminfo), (size_t)1, 0) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	vmrawstat->pagein    = page2k(pvminfo.psv_spgpgin);
	vmrawstat->pageout   = page2k(pvminfo.psv_spgpgout);
	vmrawstat->swapin    = page2k(pvminfo.psv_spswpin);
	vmrawstat->swapout   = page2k(pvminfo.psv_spswpout);
	vmrawstat->pagefault = pvminfo.psv_spgfrec; /* not sure.. */
	vmrawstat->scanrate  = pvminfo.psv_sscan;
	
	return SC_OK;

#  else /* HPUX */
#   if defined(Linux) || defined(CYGWIN)

	char buf[U_MAXBUFSIZE], line[256], *p;
	int  totlen, len;

	if ((len = f2b(SC_PROC_STAT,buf,sizeof(buf))) == 0) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	totlen = 0;

	while ((len = b2ln(buf+totlen,line,sizeof(line))) != 0) {
		/* page */
		if (!strncmp(line,"page ",5) && (p = skip_token(line)) != NULL) {
			vmrawstat->pagein  = strtoul(p,&p,0);
			vmrawstat->pageout = strtoul(p,&p,0);
		}

		/* swap */
		if (!strncmp(line,"swap ",5) && (p = skip_token(line)) != NULL) {
			vmrawstat->swapin  = strtoul(p,&p,0);
			vmrawstat->swapout = strtoul(p,&p,0);
		}

		totlen += len;
	}

	if (scCoreSysVMRawStatusLaStatus(core, vmrawstat) != SC_OK) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	vmrawstat->pagefault = 0; //vmrawstat_pagefault();
	vmrawstat->scanrate  = 0; /* show me how to! */

	return SC_OK;

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */

}

#if defined(Linux) || defined(CYGWIN)
int scCoreSysVMRawStatusLaStatus(scCore *core, scVMRawStatus *vmrawstat)
{
	char buf[U_MAXBUFSIZE];
	int  runqueue, nthread, len;
	float la[3]; /* load average */

	if ((len = f2b(SC_PROC_LOADAVG,buf,sizeof(buf))) == 0) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	runqueue = 0;
	nthread = 0;

#ifdef Linux
	if ((len = sscanf(buf,"%f %f %f %d/%d %*d\n",
				&(la[0]), &(la[1]), &(la[2]), &runqueue, &nthread)) != 5)
#else //CYGWIN
	if ((len = sscanf(buf,"%f %f %f", &(la[0]), &(la[1]), &(la[2]))) != 3)
#endif
	{

#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	/* runqueue */
	vmrawstat->runqueue = (runqueue > 0) ? runqueue - 1 :
				(runqueue == 0) ? runqueue : 0;

	/* nprocs */
	/* vmrawstat->nprocs = nthread; */

	/* load average */
	vmrawstat->la_1min  = (unsigned long)(la[0] * 100);
	vmrawstat->la_5min  = (unsigned long)(la[1] * 100);
	vmrawstat->la_15min = (unsigned long)(la[2] * 100);

	return SC_OK;
}

#endif /* Linux */
        
v_list_t *scCoreSysIORawStatus(scCore *core)
{
#if defined(AIX)
	int err=SC_OK;
	v_list_t *list=NULL;
	int dknum, cc, i;
	scIORawStatus iorawstat;

	perfstat_disk_t *pstat;
	perfstat_id_t firstdisk;

	list = NULL;

	if ((dknum = perfstat_disk(NULL,NULL,sizeof(perfstat_disk_t),0)) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] perfstat_disk error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	if ((pstat = calloc(dknum, sizeof(perfstat_disk_t))) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] calloc error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	strcpy(firstdisk.name,"");

	if ((cc = perfstat_disk(&firstdisk,pstat,sizeof(perfstat_disk_t),dknum)) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] calloc error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		err = SC_ERR;
		goto err_quit;
	}

	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] create node error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		goto err_quit;
	}

	/* setup all the entries */
	for (i = 0; i < cc; i++) {
		/* initialize first */
		memset(&iorawstat,0x00,sizeof(scIORawStatus));

		if (scCoreSysSetupEachIORawStatus(&iorawstat, pstat+i) != SC_ERR) {
			/* make new entry */
			ll_insert_node(list,&iorawstat,sizeof(scIORawStatus),NULL);
		}
	}

err_quit:
	if (pstat)
		free(pstat);

	return list;

#else
# if defined(SunOS)

	scIORawStatus iorawstat;
	v_list_t *list;

	/* kernel specific */
	kstat_t *ksp;
	kstat_io_t kio;

	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	/* scan all the kstat entries */
	for (ksp = KCTL(core)->kc_chain; ksp != NULL; ksp = ksp->ks_next) {
		if (ksp->ks_type != KSTAT_TYPE_IO
				|| strcmp(ksp->ks_class, "disk") != 0
				|| kstat_read(KCTL(core), ksp, &kio) == -1)
			continue;

		/* initialize first */
		memset(&iorawstat,0x00,sizeof(scIORawStatus));

		/* setup the each entries */
		sprintf(iorawstat.device,"%s",ksp->ks_name);

		iorawstat.nread    = kio.nread    >> U_LOG1024; /* kilo */
		iorawstat.nwritten = kio.nwritten >> U_LOG1024; /* kilo */
		iorawstat.reads    = kio.reads;
		iorawstat.writes   = kio.writes;
		iorawstat.spare_1  = 0; 
		iorawstat.spare_2  = 0;
		iorawstat.spare_3  = 0;

		/* make new entry */
		ll_insert_node(list,&iorawstat,sizeof(scIORawStatus),NULL);
	}

	return list;

# else
#  if defined(HPUX)

	scIORawStatus iorawstat;
	v_list_t *list=NULL;
	int num;

	struct pst_diskinfo  pdisk;

	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	num = 0;
	while (pstat_getdisk(&pdisk,sizeof(pdisk),(size_t)1,num++) > 0) {
		char *device;

		/* initialize first */
		memset(&iorawstat,0x00,sizeof(scIORawStatus));

		device = (char *)scCoreLookupDevice(core, &pdisk.psd_cdev);
		if (device)
			sprintf(iorawstat.device,"%s", device);
		else
			sprintf(iorawstat.device,"device-%d", num);

		iorawstat.nread    = 0;
		iorawstat.nwritten = pdisk.psd_dkwds; 
		iorawstat.reads    = 0;
		iorawstat.writes   = pdisk.psd_dkxfer;
		iorawstat.spare_1  = 0; 
		iorawstat.spare_2  = 0;
		iorawstat.spare_3  = 0;

		/* make new entry */
		ll_insert_node(list,&iorawstat,sizeof(scIORawStatus),NULL);
	}

	return list;

#  else /* HPUX */
#   if defined(Linux)

	v_list_t *list;
	// 새로운 코드 추가 kernel 2.6에서는 diskstats파일과 partitions를 참조함.
	list = scCoreSysIORawStatus_2_6(core);
	if (list != NULL) {
		return list;
	}

	char buf[U_MAXBUFSIZE], line[1024], *p;
	int  totlen, len;

	scIORawStatus iorawstat;

	if ((len = f2b(SC_PROC_STAT,buf,sizeof(buf))) == 0) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	totlen = 0, p = NULL, list = NULL;

	while ((len = b2ln(buf+totlen,line,sizeof(line))) != 0) {
		/* disk io */
		if (!strncmp(line,"disk_io: ",9)
				&& (p = skip_token(line)) != NULL
				&& (p = strtok(p," \t\n")) != NULL)
			break;

		totlen += len;
	}

	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	/* found */
	while (p) {
		/* initialize first */
		memset(&iorawstat,0x00,sizeof(scIORawStatus));

		if (scCoreSysSetupEachIORawStatus(&iorawstat, p) != SC_ERR) {
			/* make new entry */
			ll_insert_node(list,&iorawstat,sizeof(scIORawStatus),NULL);
		}

		/* next token */
		p = strtok(NULL," \t\n");
	}

	return list;
#elif defined(CYGWIN)

	scIORawStatus iorawstat;
	v_list_t *list;

	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	collectData(core->h_Diskquery);

	for(int i=0; i < core->disk_item.size(); i++) {
		/* initialize first */
		memset(&iorawstat,0x00,sizeof(scIORawStatus));

		ITEM item = core->disk_item[i];

		if (scCoreSysSetupEachIORawStatus(&iorawstat, item) != SC_ERR) {
			/* make new entry */
			ll_insert_node(list, &iorawstat, sizeof(scIORawStatus), NULL);
		}
	}

	return list;

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */

}


#if defined(AIX)
int scCoreSysSetupEachIORawStatus(scIORawStatus *iorawstat, perfstat_disk_t *pstat)
{
	sprintf(iorawstat->device,"%s", pstat->name);
	iorawstat->nread    = pstat->rblks / 2.0; /* 512 BYTE to 1 K BYTE */
	iorawstat->nwritten = pstat->wblks / 2.0;
	iorawstat->reads    = 0;
	iorawstat->writes   = 0;

	return SC_OK;
}
#endif

#if defined(Linux)

int scCoreSysSetupEachIORawStatus_2_6(scIORawStatus *iorawstat, char *line, char *format)
{
	int majnum, minnum, n;
	unsigned long tmp[4];
	char name[BUFSIZ];
	memset(name, '\0', BUFSIZ);

	if ((n = sscanf(line, format,
				&majnum, &minnum, name, &tmp[0], &tmp[1])) == 5)
	{
		//sprintf(iorawstat->device,"dev%d-%d", majnum, minnum);
		strcpy(iorawstat->device, name);
		iorawstat->nread    = tmp[0];
		iorawstat->nwritten = tmp[1];
		iorawstat->reads    = 0;
		iorawstat->writes   = 0;
	}
	else
		return SC_ERR;

	return SC_OK;
}

v_list_t *scCoreSysIORawStatus_2_6(scCore *core)
{
	char buf[U_MAXBUFSIZE], line[1024], *p;
	int  totlen, len;

	  /*
		Field 1 -- # of reads issued
		Field 2 -- # of reads merged, field 6 -- # of writes merged
		Field 3 -- # of sectors read
		Field 4 -- # of milliseconds spent reading
		Field 5 -- # of writes completed
		Field 7 -- # of sectors written
		Field 8 -- # of milliseconds spent writing
		Field 9 -- # of I/Os currently in progress
		Field 10 -- # of milliseconds spent doing I/Os
		Field 11 -- weighted # of milliseconds spent doing I/Os 
     */

	char *format = " %d %d %99s %lld %*d %*d %*d %lld %*d %*d";
	if ((len = f2b(SC_PROC_DISKSTATS,buf,sizeof(buf))) == 0) {
		if ((len = f2b(SC_PROC_PARTITIONS,buf,sizeof(buf))) == 0) {
		#ifdef DEBUG
			fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
		#endif
			return NULL;
		}
		// major minor  #blocks  name     rio rmerge rsect ruse wio wmerge wsect wuse running use aveq
		format = " %d %d %*d %99s %lld %*d %*d %*d %lld %*d %*d";
	}

	v_list_t *list;

	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	char *last = NULL;
	scIORawStatus iorawstat;

	p = strtok_r(buf,"\n", &last);

	/* found */
	while (p) {
		/* initialize first */
		memset(&iorawstat,0x00,sizeof(scIORawStatus));

		if (scCoreSysSetupEachIORawStatus_2_6(&iorawstat, p, format) != SC_ERR){
			/* make new entry */
			ll_insert_node(list,&iorawstat,sizeof(scIORawStatus),NULL);
		} else {
//#ifdef DEBUG
//			fprintf(stderr, "[%s,%d] format error line[%s]\n", 
//				__FILE__, __LINE__, p);
//#endif
		}

		/* next token */
		p = strtok_r(NULL,"\n", &last);
	}

	return list;
}

int scCoreSysSetupEachIORawStatus(scIORawStatus *iorawstat, char *line)
{
	int majnum, minnum, n;
	unsigned long tmp[4];

	if ((n = sscanf(line,"(%d,%d):(%*d,%lu,%lu,%lu,%lu)",
				&majnum, &minnum, &tmp[0], &tmp[1], &tmp[2], &tmp[3])) == 6)
	{
		sprintf(iorawstat->device,"dev%d-%d", majnum, minnum);
		iorawstat->nread    = tmp[1];
		iorawstat->nwritten = tmp[3];
		iorawstat->reads    = 0;
		iorawstat->writes   = 0;
	}
	else
		return SC_ERR;

	return SC_OK;
}

#endif /* Linux */

#if defined(CYGWIN)
int scCoreSysSetupEachIORawStatus(scIORawStatus *iorawstat, ITEM item)
{

	long long nread=0, nwrite =0;

	read_counter_large_int(item.h_Counter[0], &nread); 
	read_counter_large_int(item.h_Counter[1], &nwrite); 

	sprintf(iorawstat->device,"%s", item.instance_name.c_str());
	iorawstat->nread    = nread;
	iorawstat->nwritten = nwrite;
	iorawstat->reads    = 0;
	iorawstat->writes   = 0;

	return SC_OK;
}

#endif /* CYGWIN */

v_list_t *scCoreSysFSInfo(scCore *core)
{
#if defined(AIX)
	v_list_t  *list=NULL;
	FILE   *f=NULL;
	struct mntent *ent=NULL;
	char   *mtable = MOUNTED;

	scFSInfo fsinfo;

	if ((f = setmntent(mtable,"r")) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] setmntent error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] create node error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		goto err_quit;
	}

	while ((ent = getmntent(f)) != NULL) {
		if (strcmp(ent->mnt_fsname, "none") == 0)
			continue;

		/* initialize first */
		memset(&fsinfo,0x00,sizeof(scFSInfo));

		if (scCoreSysSetupEachFSInfo(&fsinfo, ent) != SC_ERR) {
			ll_insert_node(list,&fsinfo,sizeof(scFSInfo),NULL);
		}
	}

err_quit:
	if (f)
		endmntent(f);

	return list;

#else
# if defined(SunOS)

	FILE   *f;
	struct mnttab ent;
	struct  statvfs system_info;
	char   *mtable = MNTTAB;

	scFSInfo fsinfo;
	v_list_t  *list;

	if ((f = fopen(MNTTAB, "r")) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	/* create the node */
	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		goto out;
	}

	/* access to /etc/mnttab */
	while (getmntent(f,&ent) == 0) {
		if(hasmntopt(&ent, "ignore") == 0)
		{
			if(statvfs(ent.mnt_mountp, &system_info) < 0){
				fprintf(stderr, "[%s,%d] statvfs error[%s]\n",
					__FILE__, __LINE__, strerror(errno));
				continue;
			}

			/* initialize first */
			memset(&fsinfo,0x00,sizeof(scFSInfo));
	
			/* setup each file system info */
			if (scCoreSysSetupEachFSInfo(&fsinfo,&ent) != SC_ERR) {
				/* make new entry */
				ll_insert_node(list,&fsinfo,sizeof(scFSInfo),NULL);
			}

		}

	}

out:
	/* release it */
	if (f)
		fclose(f);

	return list;

# else
#  if defined(HPUX)
	FILE   *f;
	struct mntent *ent;
	char   *mtable = MNT_MNTTAB;

	scFSInfo fsinfo;
	v_list_t  *list=NULL;

	if ((f = setmntent(MNT_MNTTAB, "r")) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	/* list */
	list = ll_create_node(NULL,1);

	while ((ent = getmntent(f)) != NULL) {
		memset(&fsinfo,0x00,sizeof(scFSInfo));

		if (scCoreSysSetupEachFSInfo(&fsinfo, ent) != SC_ERR) 
			ll_insert_node(list,&fsinfo,sizeof(scFSInfo),NULL);
	}

	/* release */
	endmntent(f);

	return list;

#  else /* HPUX */
#   if defined(Linux) || defined(CYGWIN)

	FILE   *f;
	struct mntent *ent;
	char   *mtable = MOUNTED;

	scFSInfo fsinfo;
	v_list_t  *list=NULL;

	if ((f = setmntent(mtable,"r")) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		goto out;
	}

	while ((ent = getmntent(f)) != NULL) {
		if (strcmp(ent->mnt_fsname, "none") == 0)
			continue;

		/* initialize first */
		memset(&fsinfo,0x00,sizeof(scFSInfo));

		if (scCoreSysSetupEachFSInfo(&fsinfo, ent) != SC_ERR) {
			/* make new entry */
			ll_insert_node(list,&fsinfo,sizeof(scFSInfo),NULL);
		}
	}

out:
	if (f)
		endmntent(f);

	return list;


#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */
}

#if defined(AIX)
int scCoreSysSetupEachFSInfo(scFSInfo *fsinfo, struct mntent *ent)
{
	int err=SC_OK;
	struct statvfs vfs;

	if (statfs(ent->mnt_dir, &vfs) == -1) 
		return SC_ERR;

	/* setup.. */
	snprintf(fsinfo->device  , sizeof(fsinfo->device)  , "%s", ent->mnt_fsname);
	snprintf(fsinfo->mntpoint, sizeof(fsinfo->mntpoint), "%s", ent->mnt_dir);

	/* total data blocks in file system */
	fsinfo->sizetotal = block2k(vfs.f_blocks, vfs.f_bsize);

	/* free blocks in fs */
	fsinfo->sizefree  = block2k(vfs.f_bfree, vfs.f_bsize);

	/* free blocks avail to non-superuser */
	fsinfo->sizeavail = block2k(vfs.f_bavail, vfs.f_bsize);

	/* used size */
	fsinfo->sizeused  = (fsinfo->sizetotal > fsinfo->sizefree)
				? fsinfo->sizetotal - fsinfo->sizefree : 0;

	/* usage */
	fsinfo->sizeusage = (fsinfo->sizetotal) 
				? ((double)fsinfo->sizeused / (double)fsinfo->sizetotal) * 100.0 : 0.0;

	/* block size */
	fsinfo->blocksize = vfs.f_bsize;

	/* total file nodes in file system */
	fsinfo->filetotal = vfs.f_files;

	/* free file nodes in file system */
	fsinfo->filefree  = vfs.f_ffree;

	/* not supported */
	fsinfo->fileavail = 0;

	/* used file nodes */
	fsinfo->fileused  = (fsinfo->filetotal > fsinfo->filefree) 
				? fsinfo->filetotal - fsinfo->filefree : 0;

	/* usage */
	fsinfo->fileusage = (fsinfo->filetotal)
				? ((double)fsinfo->fileused / (double)fsinfo->filetotal) * 100.0 : 0.0;

	return err;
}

#else
# if defined(SunOS)

int scCoreSysSetupEachFSInfo(scFSInfo *fsinfo, struct mnttab *ent)
{
	struct statvfs vfs;

	if (statvfs(ent->mnt_mountp, &vfs) == -1) 
		return SC_ERR;

	/* setup.. */
	snprintf(fsinfo->device  , sizeof(fsinfo->device)  , "%s", ent->mnt_special);
	snprintf(fsinfo->mntpoint, sizeof(fsinfo->mntpoint), "%s", ent->mnt_mountp);

	/* total data blocks in file system */
	fsinfo->sizetotal = block2k(vfs.f_blocks, vfs.f_frsize);

	/* free blocks in fs */
	fsinfo->sizefree  = block2k(vfs.f_bfree, vfs.f_frsize);

	/* free blocks avail to non-superuser */
	fsinfo->sizeavail = block2k(vfs.f_bavail, vfs.f_frsize);

	/* used size */
	fsinfo->sizeused  = (fsinfo->sizetotal > fsinfo->sizefree)
				? fsinfo->sizetotal - fsinfo->sizefree : 0;

	/* usage */
	fsinfo->sizeusage = (fsinfo->sizetotal) 
				? ((double)fsinfo->sizeused / (double)fsinfo->sizetotal) * 100.0 : 0.0;

	/* block size */
	fsinfo->blocksize = vfs.f_frsize;

	/* total file nodes in file system */
	fsinfo->filetotal = vfs.f_files;

	/* free file nodes in file system */
	fsinfo->filefree  = vfs.f_ffree;

	/* not supported */
	fsinfo->fileavail = 0;

	/* used file nodes */
	fsinfo->fileused  = (fsinfo->filetotal > fsinfo->filefree) 
				? fsinfo->filetotal - fsinfo->filefree : 0;

	/* usage */
	fsinfo->fileusage = (fsinfo->filetotal)
				? ((double)fsinfo->fileused / (double)fsinfo->filetotal) * 100.0 : 0.0;

	return SC_OK;
}

# else
#  if defined(HPUX)

int scCoreSysSetupEachFSInfo(scFSInfo *fsinfo, struct mntent *ent)
{
	struct statvfs vfs;

	if (statvfs(ent->mnt_dir, &vfs) == -1) 
		return SC_ERR;

	snprintf(fsinfo->device  , sizeof(fsinfo->device)  , "%s", ent->mnt_fsname);
	snprintf(fsinfo->mntpoint, sizeof(fsinfo->mntpoint), "%s", ent->mnt_dir);

	/* total data blocks in file system */
	fsinfo->sizetotal = block2k(vfs.f_blocks, vfs.f_frsize);

	/* free blocks in fs */
	fsinfo->sizefree  = block2k(vfs.f_bfree, vfs.f_frsize);

	/* free blocks avail to non-superuser */
	fsinfo->sizeavail = block2k(vfs.f_bavail, vfs.f_frsize);

	/* used size */
	fsinfo->sizeused  = (fsinfo->sizetotal > fsinfo->sizefree)
				? fsinfo->sizetotal - fsinfo->sizefree : 0;

	/* usage */
	fsinfo->sizeusage = (fsinfo->sizetotal) 
				? ((double)fsinfo->sizeused / (double)fsinfo->sizetotal) * 100.0 : 0.0;

	/* block size */
	fsinfo->blocksize = vfs.f_frsize;

	/* total file nodes in file system */
	fsinfo->filetotal = vfs.f_files;

	/* free file nodes in file system */
	fsinfo->filefree  = vfs.f_ffree;

	/* not supported */
	fsinfo->fileavail = 0;

	/* used file nodes */
	fsinfo->fileused  = (fsinfo->filetotal > fsinfo->filefree) 
				? fsinfo->filetotal - fsinfo->filefree : 0;

	/* usage */
	fsinfo->fileusage = (fsinfo->filetotal)
				? ((double)fsinfo->fileused / (double)fsinfo->filetotal) * 100.0 : 0.0;

	return SC_OK;

}

#  else /* HPUX */
#   if defined(Linux) || defined(CYGWIN)

int scCoreSysSetupEachFSInfo(scFSInfo *fsinfo, struct mntent *ent)
{
	struct statfs vfs;
	unsigned long totalsize;

	if (statfs(ent->mnt_dir, &vfs) == -1) 
		return SC_ERR;

	snprintf(fsinfo->device  , sizeof(fsinfo->device)  , "%s", ent->mnt_fsname);
	snprintf(fsinfo->mntpoint, sizeof(fsinfo->mntpoint), "%s", ent->mnt_dir);

	fsinfo->sizetotal = block2k(vfs.f_blocks, vfs.f_bsize);
	fsinfo->sizefree  = block2k(vfs.f_bfree, vfs.f_bsize);
	fsinfo->sizeavail = block2k(vfs.f_bavail, vfs.f_bsize);
	fsinfo->sizeused  = (fsinfo->sizetotal > fsinfo->sizefree)
				? fsinfo->sizetotal - fsinfo->sizefree : 0;
	if ((totalsize = fsinfo->sizeused + fsinfo->sizeavail) > 0) {
		fsinfo->sizeusage = (fsinfo->sizeused / (double)totalsize) * 100.0;
	}
	else
		fsinfo->sizeusage = 0.0;

	fsinfo->blocksize = vfs.f_bsize;
	fsinfo->filetotal = vfs.f_files;
	fsinfo->filefree  = vfs.f_ffree;
	fsinfo->fileavail = 0;
	fsinfo->fileused  = (fsinfo->filetotal > fsinfo->filefree) 
				? fsinfo->filetotal - fsinfo->filefree : 0;
	fsinfo->fileusage = (fsinfo->filetotal)
				? ((double)fsinfo->fileused / (double)fsinfo->filetotal) * 100.0 : 0.0;

	return SC_OK;
}

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */


v_list_t *scCoreSysPSInfo(scCore *core, int sumoption)
{
#if defined(AIX)
	int err=SC_OK;
	v_list_t *list=NULL;
	int  procindex, maxproc = 1000000;
	int  nprocs, at, cc, sizeofprocs;
	double elapsed;
	void *procs, *nextproc; /* struct procsinfo64 / struct procentry64 */

	scPSInfo psinfo;

	sizeofprocs = (__KERNEL_32()) 
				? sizeof(struct procsinfo64) 
				: sizeof(struct procentry64);

	/* to calculate the musage per process */
	if (g_physicalMemory == -1) 
	if (scCoreSysMemStatusPhysic(core, &g_physicalMemory) == SC_ERR) {
		return NULL;
	}

	/* prepare to calc cpu utilization */
	core->toggle = !core->toggle;
	elapsed     = getelapsed_r(&(core->pstmvalue), 1);

	/* get the total number of process running */
	procindex = 0;
	nprocs = (__KERNEL_32())
			? getprocs(NULL,sizeofprocs,NULL,0,&procindex,maxproc)
			: getprocs64(NULL,sizeofprocs,NULL,0,&procindex,maxproc);
	if (nprocs < 0 || nprocs == 0) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] getprocs error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	/* add spare slot */
	nprocs += SPARESLOT;
	if ((procs = malloc(nprocs * sizeofprocs)) == NULL) {
		return NULL;
	}

	procindex = 0;
	nprocs = (__KERNEL_32())
			? getprocs((struct procsinfo64 *)procs,sizeofprocs,NULL,0,&procindex,nprocs)
			: getprocs64((struct procentry64 *)procs,sizeofprocs,NULL,0,&procindex,nprocs);
	if (nprocs < 0 || nprocs == 0) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] getprocs error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		goto err_quit;
	}

	/* create the node */
	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] create node error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		goto err_quit;
	}

	/* scan all the process entries */
	nextproc = procs;

	for (at = 0; at < nprocs; at++) {
		/* initialize first */
		memset(&psinfo,0x00,sizeof(scPSInfo));

		cc = (__KERNEL_32())
				? scCoreSysSetupEachPSInfo32(core,&psinfo,(struct procsinfo64 *)nextproc,elapsed)
				: scCoreSysSetupEachPSInfo64(core,&psinfo,(struct procentry64 *)nextproc,elapsed);
		if (cc != SC_ERR) {
			/* make new entry */
			if (sumoption == SC_SUM_BY_PNAME) {
				psinfo_sumup_pname(list, &psinfo);
			}
			if (sumoption == SC_SUM_BY_PARGS) {
				psinfo_sumup_pargs(list, &psinfo);
			}
			else if (sumoption == SC_SUM_BY_UNAME) {
				psinfo_sumup_uname(list, &psinfo);
			}
			else
				ll_insert_node(list,&psinfo,sizeof(scPSInfo),NULL);
		}

		/* the next process */
		nextproc = nextproc + sizeofprocs;
	}

	/* update the exit one */
	pscache_update(core);

err_quit:

	if (procs)
		free(procs);

	return list;

#else
# if defined(SunOS)

	DIR   *dirp;
	struct dirent *ent;
	double elapsed;

	v_list_t *list;
	scPSInfo psinfo;

	/* to calculate the musage per process */
	if (PhysicalMemory == -1) 
	if (scCoreSysMemStatusPhysic(core, &PhysicalMemory) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	/* will scan /proc directory */
	if ((dirp = opendir("/proc")) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	/* create the node */
	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		goto out;
	}

	while ((ent = readdir(dirp)) != NULL) {
		/* skip non "/proc/#/" */
		if (ent->d_name[0] == '.') continue;

		/* initialize first */
		memset(&psinfo,0x00,sizeof(scPSInfo));

		if (scCoreSysSetupEachPSInfo(core, &psinfo, ent->d_name, elapsed) != SC_ERR) {
			/* make new entry */
			if (sumoption == SC_SUM_BY_PNAME) {
				psinfo_sumup_pname(list, &psinfo);
			}
			else if (sumoption == SC_SUM_BY_PARGS) {
				psinfo_sumup_pargs(list, &psinfo);
			}
			else if (sumoption == SC_SUM_BY_UNAME) {
				psinfo_sumup_uname(list, &psinfo);
			}
			else
				ll_insert_node(list,&psinfo,sizeof(scPSInfo),NULL);
		}
	}
out:
	/* release */
	closedir(dirp);

	return list;
# else
#  if defined(HPUX)

	double elapsed;
	v_list_t *list;
	scPSInfo psinfo;
	int i;

	if (PhysicalMemory == -1) 
	if (scCoreSysMemStatusPhysic(core, &PhysicalMemory) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	core->pstatus_index = 0;

	/* list */
	list = ll_create_node(NULL,1);

	for (i = 0; i < core->__maxproc; i++) {
		/* initialize first */
		memset(&psinfo,0x00,sizeof(scPSInfo));

		if (scCoreSysSetupEachPSInfo(core, &psinfo, elapsed) != 0) {
			if (sumoption == SC_SUM_BY_PNAME) {
				psinfo_sumup_pname(list, &psinfo);
			}
			else if (sumoption == SC_SUM_BY_PARGS) {
				psinfo_sumup_pargs(list, &psinfo);
			}
			else if (sumoption == SC_SUM_BY_UNAME) {
				psinfo_sumup_uname(list, &psinfo);
			}
			else
				ll_insert_node(list,&psinfo,sizeof(scPSInfo),NULL);
		}
		else
			break;
	}

	return list;

#  else /* HPUX */
#   if defined(Linux)

	DIR   *dirp;
	struct dirent *ent;
	double elapsed;

	v_list_t *list=NULL;
	scPSInfo psinfo;

	if (PhysicalMemory == 0) 
	if (scCoreSysMemStatusPhysic(core, &PhysicalMemory) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	core->toggle = !core->toggle;
	elapsed     = getelapsed_r(&(core->pstmvalue), 1);

	if ((dirp = opendir("/proc")) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	/* create the node */
	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		goto out;
	}


	while ((ent = readdir(dirp)) != NULL) {
		if (!isdigit(ent->d_name[0]))
			continue;

		memset(&psinfo,0x00,sizeof(scPSInfo));
		if (scCoreSysSetupEachPSInfo(core, &psinfo, ent->d_name, elapsed) != SC_ERR) {
			/* make new entry */
			if (sumoption == SC_SUM_BY_PNAME) {
				psinfo_sumup_pname(list, &psinfo);
			}
			else if (sumoption == SC_SUM_BY_PARGS) {
				psinfo_sumup_pargs(list, &psinfo);
			}
			else if (sumoption == SC_SUM_BY_UNAME) {
				psinfo_sumup_uname(list, &psinfo);
			}
			else
				ll_insert_node(list,&psinfo,sizeof(scPSInfo),NULL);
		}
	}

	pscache_update(core);
out:
	/* release */
	closedir(dirp);

	return list;

#elif defined(CYGWIN)

	DIR   *dirp;
	struct dirent *ent;
	double elapsed;

	v_list_t *list=NULL;
	scPSInfo psinfo;

	if (PhysicalMemory == 0) 
	if (scCoreSysMemStatusPhysic(core, &PhysicalMemory) == SC_ERR) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	HANDLE hProcessSnap;
	// Take a snapshot of all processes in the system.
	hProcessSnap = CreateToolhelp32Snapshot( TH32CS_SNAPPROCESS, 0 );
	if( hProcessSnap == INVALID_HANDLE_VALUE )
	{
		return NULL;
	}

	/* create the node */
	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		goto out;
	}

	PROCESSENTRY32 pe32;
	// Set the size of the structure before using it.
	pe32.dwSize = sizeof( PROCESSENTRY32 );

	// Retrieve information about the first process,
	// and exit if unsuccessful
	if( !Process32First( hProcessSnap, &pe32 ) )
	{
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] process32first\n", __FILE__, __LINE__);
#endif
		goto out;
	}

	do {
		memset(&psinfo,0x00,sizeof(scPSInfo));
		if (scCoreSysSetupEachPSInfo(core, &psinfo, &pe32) != SC_ERR) {
				/* make new entry */
				if (sumoption == SC_SUM_BY_PNAME) {
					psinfo_sumup_pname(list, &psinfo);
				}
				else if (sumoption == SC_SUM_BY_PARGS) {
					psinfo_sumup_pargs(list, &psinfo);
				}
				else if (sumoption == SC_SUM_BY_UNAME) {
					psinfo_sumup_uname(list, &psinfo);
				}
				else
					ll_insert_node(list,&psinfo,sizeof(scPSInfo),NULL);
		}
	} while ( Process32Next( hProcessSnap, &pe32 ) );

	// 리스트에 없는 process는 삭제함.
	for(map<int, ProcessInfo>::iterator it = core->processList.begin(); it != core->processList.end(); ++it) {
		DWORD pid = (*it).first;
		ProcessInfo processInfo = (*it).second;

		if (processInfo.isAlive == false && core->processList.find( pid ) != core->processList.end() ) {
			core->processList.erase( pid );
		}
	}

	pscache_update(core);

	

out:
	/* release */
	CloseHandle( hProcessSnap );

	return list;

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */

}

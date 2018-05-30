
#include "CMisc.h"
#include <string>

using namespace std;

int hrsplit(char *msg, char *del, char data[][1024])
{
    int len=0, i=0;
    char *p=NULL, *q=NULL;

    p = msg;
    for(i=0;;i++){

        char *s=NULL;
        while(isspace(*p)) p++;

        q = (char *)strstr(p, del);

        if(q){
            len = strlen(p)-strlen(q);
        }else{
            len = strlen(p);
        }

        strncpy(data[i], p, len);

        if(q==NULL) break;
        p = q += strlen(del);
        if(strlen(p)==0) break;
    }

    return i+1;
}

void initDaemonProc()
{
    int     pid;

    if((pid=fork()) < 0)    /* fork system call error */
    {
        printf("InitDaeMonProc: Fork System call Error [%s]\n",
            strerror(errno));
        exit(0);
    } else if( pid != 0)    /* if parent, then exit */
        exit(0);

    setsid();       /* become session leader */
//  chdir("/");     /* Change Working Directory in case unmount directory */

    umask(0);       /* clear out file mode creation mask */
}

void getTime(unsigned long *sec, unsigned long *usec)
{
    struct timeval tv;
    struct timezone tz;

    (void) gettimeofday(&tv, &tz);
    if(sec) *sec = tv.tv_sec;
    if(usec) *usec = tv.tv_usec;
}

void msleep(unsigned long msec)
{
    struct timeval timeOut;
    timeOut.tv_sec = msec / 1000;
    timeOut.tv_usec = (msec % 1000) * 1000;
    select(0, NULL, NULL, NULL, &timeOut);
}

int sortScanDir(const void *s1, const void *s2)
{
    st_scan_dir *d1 = (st_scan_dir *) s1;
    st_scan_dir *d2 = (st_scan_dir *) s2;
   
    return strcmp(d1->filename, d2->filename);
}

int scanDir(char *dir, st_scan_dir **namelist, int (*handler)(const void *, const void *))
{
    DIR *dirp=NULL;
    struct dirent *dp=NULL;
    st_scan_dir *_namelist=NULL, sdir;
	int fnum=0, i=0;

    if((dirp=opendir(dir))==NULL) return -1;

	while((dp=readdir(dirp))!=NULL){
        fnum++;
        if(fnum==0){
            _namelist = (st_scan_dir *)malloc(sizeof(st_scan_dir));
            memset(_namelist, 0x00, sizeof(st_scan_dir));
        }else{
            _namelist = (st_scan_dir *)realloc((void *)_namelist, sizeof(st_scan_dir)
*(fnum+1));
        }
        memset(&sdir, 0x00, sizeof(sdir));
        strcpy(sdir.filename, dp->d_name);
        sprintf(sdir.fullpath, "%s/%s", dir, dp->d_name);
        stat(sdir.fullpath, &sdir.sbuf);

        memcpy(_namelist+fnum-1, &sdir, sizeof(sdir));
    }

    (*namelist)=_namelist;
    if(dirp!=NULL) closedir(dirp);

    qsort((void *)_namelist, fnum, sizeof(st_scan_dir),
        handler==NULL ? sortScanDir : handler);

    return fnum;
}

int gethostipaddr(char *haddr)
{
	struct sockaddr_in sa;
	char hostname[128];
	unsigned long inaddr;
    struct hostent *p;

	memset(hostname, 0x00, sizeof(hostname));
	gethostname(hostname, sizeof(hostname)-1);

    if ((inaddr = inet_addr(hostname)) != -1){
        memcpy(&sa.sin_addr,&inaddr,sizeof(inaddr));
    }else {
        if ((p = gethostbyname(hostname)) == NULL) {
            return -1;
        }else{
            memcpy(&sa.sin_addr, p->h_addr_list[0], p->h_length);
        }
    }

	strcpy(haddr, inet_ntoa(sa.sin_addr));

    return 0;
}

char *get_popen_result(char *cmd, char *mode)
{
	FILE *fp=NULL;
	char buf[1024];
	int len=0, mlen=0;
	string data;

	if((fp = popen(cmd, mode))==NULL){
		return NULL;
	}

	data = "";
	memset(buf, 0x00, sizeof(buf));
	while(fgets(buf, sizeof(buf)-1, fp) != NULL){

		data = data + buf;

		memset(buf, 0x00, sizeof(buf));
	}

	char *result = (char *)malloc(data.size()+1);
	if (result != NULL) {
		memset(result, 0x00, data.size()+1);
		memcpy(result, data.c_str(), data.size());
	}


	pclose(fp);
	return result;
}

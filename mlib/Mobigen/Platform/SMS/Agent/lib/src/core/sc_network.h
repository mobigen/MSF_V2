
/*
 *
 * (C) COPYRIGHT h9mm. 2005
 *
 */

#ifndef _SC_NETWORK_H_
#define _SC_NETWORK_H_

#include "sc_core.h"

#ifdef __cplusplus
extern "C"
{
#endif

v_list_t *scCoreNetInterfaceRawStatus(scCore *core);
v_list_t *scCoreNetTCPInfo(scCore *core, int listen_only);

#if defined(HPUX)
int scCoreNetSetupPhystat(scCore *core, v_list_t *list);
int scCoreNetSetupEachInterfaceInfo(scInterfaceInfo *ifinfo, int sockfd);

extern int get_physical_stat(nmapi_phystat *, unsigned int *);
#endif

#if defined(SunOS)

#define BUFSIZE_MX 40960

static char *PushModuleList[] = {
	"arp", "tcp", "udp", NULL
};

int tcpinfo_initialize(int fd, int grpname, int tblname);
int timed_getmsg(int fd, struct strbuf *ctlp, int *flagsp, int timeout);

int scCoreNetSetupEachInterfaceInfo(scInterfaceInfo *ifinfo, int sockfd, char *ifname);
int scCoreNetSetupEachInterfaceType(char *ifname);

#endif /* SunOS */

#if defined(AIX)
int scCoreNetSetupEachInterfaceInfo(scInterfaceInfo *ifinfo, int sockfd, char *ifname, struct sockaddr_dl *sdl);
#endif

#if defined(Linux)
int scCoreNetSetupEachInterfaceInfo(scInterfaceInfo *ifinfo, int sockfd, char *ifname);
char *scCoreNetSetupEachInterfaceName(char *ifname, char *line);
int scCoreNetSetupEachInterfaceRawStatus(scInterfaceRawStatus *ifrawstat, char *line, int version);
#endif


int scCoreNetSetupEachTCPInfo(scTCPInfo *tcpinfo, char *line);
int scCoreNetSetupInterfaceRawStatus(v_list_t *list);
int scCoreNetFsrchInterfaceName(const void *v1, const void *v2);
int tcpinfo_state2kvish(int state);

#if defined(AIX)
int scCoreNetSetupEachInterfaceRawStatus(v_list_t *list, perfstat_netinterface_t *pstat);
int tcpstate_aton(char *state);
#endif /* AIX */


#ifdef __cplusplus
}
#endif
#endif /* _SC_NETWORK_H_ */




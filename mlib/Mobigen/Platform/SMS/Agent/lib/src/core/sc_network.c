
/*
 *
 * (C) COPYRIGHT h9mm. 2005
 *
 */

#ifdef CYGWIN
#include <windows.h>
#include <iphlpapi.h>
#endif 
#include "cygwin.h"
#include "sc_network.h"

#ifdef Linux
#include <linux/types.h>
#include <linux/ethtool.h>
#include <linux/sockios.h>
#endif // Linux


#if defined(AIX)

int scCoreNetSetupEachInterfaceInfo(scInterfaceInfo *ifinfo, int sockfd, char *ifname, struct sockaddr_dl *sdl)
{
	struct ifreq ifr;
	struct sockaddr_in *sinptr;
	char   *hwp;

	/* addr */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	if (ioctl(sockfd, SIOCGIFADDR, &ifr) != -1) {
		sinptr = (struct sockaddr_in *)&ifr.ifr_addr;
		ifinfo->addr = sinptr->sin_addr;
	} else
		memset((char *)&ifinfo->addr,0x00,sizeof(ifinfo->addr));

	/* broadaddr */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	if (ioctl(sockfd, SIOCGIFBRDADDR, &ifr) != -1) {
		sinptr = (struct sockaddr_in *)&ifr.ifr_addr;
		ifinfo->broadaddr = sinptr->sin_addr;
	} else
		memset((char *)&ifinfo->broadaddr,0x00,sizeof(ifinfo->broadaddr));

	/* netmask */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	if (ioctl(sockfd, SIOCGIFNETMASK, &ifr) != -1) {
		sinptr = (struct sockaddr_in *)&ifr.ifr_addr;
		ifinfo->subnetmask = sinptr->sin_addr;
	} else
		memset((char *)&ifinfo->subnetmask,0x00,sizeof(ifinfo->subnetmask));

	/* networkid */
	ifinfo->networkid.s_addr = ifinfo->addr.s_addr & ifinfo->subnetmask.s_addr;

	/* mtu */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	ifinfo->mtu = (ioctl(sockfd, SIOCGIFMTU, &ifr) == -1) ? 0 : ifr.ifr_mtu;

	/* flag */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	ifinfo->flags = (ioctl(sockfd, SIOCGIFFLAGS, &ifr) == -1) ? 0 : ifr.ifr_flags;

#if 0	/* ifspeed - not sure */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	ifinfo->speed = (ioctl(sockfd, SIOCGIFBAUDRATE, &ifr) == -1) ? 0 : ifr.ifr_baudrate;
#endif

	/* h/w addr */
	if ((hwp = LLADDR(sdl)) == NULL) 
		memset(ifinfo->hwaddr,0x00,6);
	else
		memcpy(ifinfo->hwaddr,hwp,6);

	/* type */
	ifinfo->type = (ifinfo->flags & IFF_LOOPBACK) ? SC_IF_TYPE_LOOPBACK : SC_IF_TYPE_ETHERNET;

	/* speed (show me how to calculate them) */
	ifinfo->speed = (ifinfo->type == SC_IF_TYPE_LOOPBACK) ? 1000000 : 10000000; /* bit unit */

	/* if name */
	strncpy(ifinfo->ifname, ifname, sizeof(ifinfo->ifname));
	ifinfo->ifname[ sizeof(ifinfo->ifname)-1 ] = 0;

	return SC_OK;

}

#else
# if defined(SunOS)

int scCoreNetSetupEachInterfaceInfo(scInterfaceInfo *ifinfo, int sockfd, char *ifname)
{
	struct ifreq ifr;
	struct sockaddr_in *sinptr;

	/* addr */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	if (ioctl(sockfd, SIOCGIFADDR, &ifr) != -1) {
		sinptr = (struct sockaddr_in *)&ifr.ifr_addr;
		ifinfo->addr = sinptr->sin_addr;
	} else
		memset((char *)&ifinfo->addr,0x00,sizeof(ifinfo->addr));

	/* broadaddr */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	if (ioctl(sockfd, SIOCGIFBRDADDR, &ifr) != -1) {
		sinptr = (struct sockaddr_in *)&ifr.ifr_addr;
		ifinfo->broadaddr = sinptr->sin_addr;
	} else
		memset((char *)&ifinfo->broadaddr,0x00,sizeof(ifinfo->broadaddr));

	/* netmask */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	if (ioctl(sockfd, SIOCGIFNETMASK, &ifr) != -1) {
		sinptr = (struct sockaddr_in *)&ifr.ifr_addr;
		ifinfo->subnetmask = sinptr->sin_addr;
	} else
		memset((char *)&ifinfo->subnetmask,0x00,sizeof(ifinfo->subnetmask));

	/* mtu */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	ifinfo->mtu = (ioctl(sockfd, SIOCGIFMTU, &ifr) == -1) ? 0 : ifr.ifr_metric;

	/* flag */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	ifinfo->flags = (ioctl(sockfd, SIOCGIFFLAGS, &ifr) == -1) ? 0 : ifr.ifr_flags;

	/* type */
	ifinfo->type = scCoreNetSetupEachInterfaceType(ifname);

	/* speed */
	ifinfo->speed = 0;

	/* if name */
	strncpy(ifinfo->ifname, ifname, sizeof(ifinfo->ifname));
	ifinfo->ifname[ sizeof(ifinfo->ifname)-1 ] = 0;

	/* h/w address */
	memset(&ifinfo->hwaddr,0x00,6);

	return SC_OK;
}

int scCoreNetSetupEachInterfaceType(char *ifname)
{
	int iftype;

	/* speed (show me how to calculate them) */
	switch (ifname[0]) 
	{
	case 'l':          /* le / lo / lane (ATM LAN Emulation) */
		if (ifname[1] == 'o') {
			iftype = 24;
		}
		else if (ifname[1] == 'e') {
			iftype = 6;
		}
		else
			iftype = 37;
		break;

	case 'g':          /* ge (gigabit ethernet card)  */
		iftype = 6;
		break;

	case 'h':          /* hme (SBus card) */
	case 'e':          /* eri (PCI card) */
	case 'b':          /* be */
	case 'd':          /* dmfe -- found on netra X1 */
		iftype = 6;
		break;

	case 'f':          /* fa (Fore ATM */
		iftype = 37;
		break;

	case 'q':         /* qe (QuadEther)/qa (Fore ATM)/qfe (QuadFastEther)*/
		if (ifname[1] == 'a') {
			iftype = 37;
		}
		else if (ifname[1] == 'e') {
			iftype = 6;
		}
		else
			iftype = 6;
		break;
	}

	return iftype;
}

unsigned long scCoreNetSetupEachInterfaceSpeed(char *ifname)
{
	unsigned long ifspeed;

	/* speed (show me how to calculate them) */
	switch (ifname[0]) 
	{
	case 'l':          /* le / lo / lane (ATM LAN Emulation) */
		if (ifname[1] == 'o') {
			ifspeed = 127000000;
		}
		else if (ifname[1] == 'e') {
			ifspeed = 10000000;
		}
		else
			ifspeed = 155000000;
		break;

	case 'g':          /* ge (gigabit ethernet card)  */
		ifspeed = 1000000000;
		break;

	case 'h':          /* hme (SBus card) */
	case 'e':          /* eri (PCI card) */
	case 'b':          /* be */
	case 'd':          /* dmfe -- found on netra X1 */
		ifspeed = 100000000;
		break;

	case 'f':          /* fa (Fore ATM */
		ifspeed = 155000000;
		break;

	case 'q':         /* qe (QuadEther)/qa (Fore ATM)/qfe (QuadFastEther)*/
		if (ifname[1] == 'a') {
			ifspeed = 155000000;
		}
		else if (ifname[1] == 'e') {
			ifspeed = 10000000;
		}
		else
			ifspeed = 100000000;
		break;
	}

	return ifspeed;
}

# else
#  if defined(HPUX)

int scCoreNetSetupEachInterfaceInfo(scInterfaceInfo *ifinfo, int sockfd)
{
	struct ifreq ifr;
	struct sockaddr_in *sinptr;

	/* addr */
	strncpy(ifr.ifr_name, ifinfo->ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	if (ioctl(sockfd, SIOCGIFADDR, &ifr) != -1) {
		sinptr = (struct sockaddr_in *)&ifr.ifr_addr;
		ifinfo->addr = sinptr->sin_addr;
	} else
		memset((char *)&ifinfo->addr,0x00,sizeof(ifinfo->addr));

	/* broadaddr */
	strncpy(ifr.ifr_name, ifinfo->ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	if (ioctl(sockfd, SIOCGIFBRDADDR, &ifr) != -1) {
		sinptr = (struct sockaddr_in *)&ifr.ifr_addr;
		ifinfo->broadaddr = sinptr->sin_addr;
	} else
		memset((char *)&ifinfo->broadaddr,0x00,sizeof(ifinfo->broadaddr));

	/* netmask */
	strncpy(ifr.ifr_name, ifinfo->ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	if (ioctl(sockfd, SIOCGIFNETMASK, &ifr) != -1) {
		sinptr = (struct sockaddr_in *)&ifr.ifr_addr;
		ifinfo->subnetmask = sinptr->sin_addr;
	} else
		memset((char *)&ifinfo->subnetmask,0x00,sizeof(ifinfo->subnetmask));

	/* networkid */
	ifinfo->networkid.s_addr = ifinfo->addr.s_addr & ifinfo->subnetmask.s_addr;

	/* flag */
	strncpy(ifr.ifr_name, ifinfo->ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	ifinfo->flags = (ioctl(sockfd, SIOCGIFFLAGS, &ifr) == -1) ? 0 : ifr.ifr_flags;

	return SC_OK;
}

#  else /* HPUX */
#   if defined(Linux)

int scCoreNetSetupEachInterfaceInfo(scInterfaceInfo *ifinfo, int sockfd, char *ifname)
{
	struct ifreq ifr;
	struct sockaddr_in *sinptr;

	/* addr */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	if (ioctl(sockfd, SIOCGIFADDR, &ifr) != -1) {
		sinptr = (struct sockaddr_in *)&ifr.ifr_addr;
		ifinfo->addr = sinptr->sin_addr;
	} else
		memset((char *)&ifinfo->addr,0x00,sizeof(ifinfo->addr));

	/* broadaddr */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	if (ioctl(sockfd, SIOCGIFBRDADDR, &ifr) != -1) {
		sinptr = (struct sockaddr_in *)&ifr.ifr_broadaddr;
		ifinfo->broadaddr = sinptr->sin_addr;
	} else
		memset((char *)&ifinfo->broadaddr,0x00,sizeof(ifinfo->broadaddr));

	/* netmask */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	if (ioctl(sockfd, SIOCGIFNETMASK, &ifr) != -1) {
		sinptr = (struct sockaddr_in *)&ifr.ifr_netmask;
		ifinfo->subnetmask = sinptr->sin_addr;
	} else
		memset((char *)&ifinfo->subnetmask,0x00,sizeof(ifinfo->subnetmask));

	/* networkid */
	ifinfo->networkid.s_addr = ifinfo->addr.s_addr & ifinfo->subnetmask.s_addr;

	/* mtu */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	ifinfo->mtu = (ioctl(sockfd, SIOCGIFMTU, &ifr) == -1) ? 0 : ifr.ifr_mtu;

	/* flag */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	ifinfo->flags = (ioctl(sockfd, SIOCGIFFLAGS, &ifr) == -1) ? 0 : ifr.ifr_flags;

	/* h/w addr */
	strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name));
	ifr.ifr_name[ sizeof(ifr.ifr_name)-1 ] = 0;
	if (ioctl(sockfd, SIOCGIFHWADDR, &ifr) == -1)
		memset(&ifinfo->hwaddr,0x00,6);
	else
		memcpy(&ifinfo->hwaddr,ifr.ifr_hwaddr.sa_data,6);
	
	/* type */
	ifinfo->type = (ifinfo->flags & IFF_LOOPBACK) ? \
		SC_IF_TYPE_LOOPBACK : SC_IF_TYPE_ETHERNET;

	/* speed (show me how to calculate them) */

	if (ifinfo->type == SC_IF_TYPE_LOOPBACK) {
		ifinfo->speed = 10000000;
	} else {
		// network speed 구하기.
		struct ethtool_cmd ethcmd;
		memset(&ethcmd, 0, sizeof ethcmd);	
		ethcmd.cmd = ETHTOOL_GSET;
		ifr.ifr_data = (caddr_t) &ethcmd;

		if (ioctl(sockfd, SIOCETHTOOL, &ifr) == 0) {
			ifinfo->speed = ethcmd.speed * 1000000;
		} else {
			ifinfo->speed = 0;
		}
	}

	/* if name */
	strncpy(ifinfo->ifname, ifname, sizeof(ifinfo->ifname));
	ifinfo->ifname[ sizeof(ifinfo->ifname)-1 ] = 0;

	return SC_OK;
}

#elif CYGWIN

int scCoreNetSetupEachInterfaceInfo(scInterfaceInfo *ifinfo, PIP_ADAPTER_INFO table, int speed)
{

	struct in_addr laddr;
	/* addr */
	inet_aton((const char*)table->IpAddressList.IpAddress.String, &laddr);
	ifinfo->addr = laddr;


	/* broadaddr */
	//ifinfo->broadaddr = sinptr->sin_addr;
	memset((char *)&ifinfo->broadaddr,0x00,sizeof(ifinfo->broadaddr));

	/* netmask */
	//ifinfo->subnetmask = sinptr->sin_addr;
	memset((char *)&ifinfo->subnetmask,0x00,sizeof(ifinfo->subnetmask));

	/* networkid */
	ifinfo->networkid.s_addr = ifinfo->addr.s_addr & ifinfo->subnetmask.s_addr;

	/* mtu */
	ifinfo->mtu = 0;

	/* flag */
	ifinfo->flags = 0 ;

	/* h/w addr */
	memset(&ifinfo->hwaddr,0x00,6);
	memcpy(&ifinfo->hwaddr,(char*)table->Address, 6);
	
	/* type */
	ifinfo->type = (table->Type & MIB_IF_TYPE_LOOPBACK) ? SC_IF_TYPE_LOOPBACK : SC_IF_TYPE_ETHERNET;

	/* speed (show me how to calculate them) */
	ifinfo->speed = speed; /* bit unit */

	/* if name */
	string desc = (char*)table->Description;
	replace(desc.begin(), desc.end(), '_', '/');
	strncpy(ifinfo->ifname, desc.c_str(), sizeof(ifinfo->ifname));
	ifinfo->ifname[ sizeof(ifinfo->ifname)-1 ] = 0;

	return SC_OK;
}
#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */


#if defined(AIX)
int scCoreNetSetupInterfaceRawStatus(v_list_t *list)
{
	int ifnum, cc, i, iserror;

	perfstat_netinterface_t *pstat;
	perfstat_id_t first;

	/* setup the error flag */
	iserror = 1;

	/* calculate the total number of interface */
	if ((ifnum = perfstat_netinterface(NULL,NULL,sizeof(perfstat_netinterface_t),0)) <= 0) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] perfstat_netinterface error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	/* make space for perfstat */
	if ((pstat = calloc(ifnum,sizeof(perfstat_netinterface_t))) == NULL) {
#ifdef DEBUG
				fprintf(stderr, "[%s,%d] calloc error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		goto err_quit;
	}

	/* allocate the raw stat value */
	strcpy(first.name, FIRST_NETINTERFACE);

	if ((cc = perfstat_netinterface(&first,pstat,sizeof(perfstat_netinterface_t),ifnum)) <= 0) {
#ifdef DEBUG
				fprintf(stderr, "[%s,%d] perfstat_netinterface error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		goto err_quit;
	}
	
	/* scan all the entries */
	for (i = 0; i < cc; i++) 
		scCoreNetSetupEachInterfaceRawStatus(list, pstat+i);

	iserror = 0;
err_quit:
	/* release */
	if (pstat)
		free(pstat);

	return (iserror) ? SC_ERR : SC_OK;

}


int scCoreNetSetupEachInterfaceRawStatus(v_list_t *list, perfstat_netinterface_t *pstat)
{
	scInterfaceRawStatus ifrawstat, *p;

	/* search the previously added ifrawstat */
	sprintf(ifrawstat.ifinfo.ifname,"%s",pstat->name);

	if ((p = ll_search_node_data(list,&ifrawstat,
				sizeof(scInterfaceRawStatus),scCoreNetFsrchInterfaceName)) != NULL)
	{
		p->inoctets   = pstat->ibytes;
		p->inpkts     = pstat->ipackets;
		p->inerrors   = pstat->ierrors;
		p->outoctets  = pstat->obytes;
		p->outpkts    = pstat->opackets;
		p->outerrors  = pstat->oerrors;
		p->collisions = pstat->collisions;
	}
	else
		return SC_ERR; /* not found.. */

	return SC_OK;

}

#else
# if defined(SunOS)

int scCoreNetSetupEachInterfaceRawStatus(scCore *core,
scInterfaceRawStatus *ifrawstat, char *module, char *ifname, int instance)
{
	kstat_t       *ksp;
	kstat_named_t *kn;
	unsigned long ifspeed;

	ksp = kstat_lookup(KCTL(core),module,instance,ifname);
	if (ksp && kstat_read(KCTL(core), ksp, 0) != -1) {
		/* rx_packet,, */
		kn = (kstat_named_t*)kstat_data_lookup(ksp, "ipackets");
		ifrawstat->inpkts = (kn != NULL) ? kn->value.ui32 : 0;

		/* tx_packet,, */
		kn = (kstat_named_t*)kstat_data_lookup(ksp, "opackets");
		ifrawstat->outpkts = (kn != NULL) ? kn->value.ui32 : 0;

		/* rx_bytes,, */
		kn = (kstat_named_t*)kstat_data_lookup(ksp, "rbytes");
		ifrawstat->inoctets = (kn != NULL) ? kn->value.ui32 : 0;

		/* tx_bytes,, */
		kn = (kstat_named_t*)kstat_data_lookup(ksp, "obytes");
		ifrawstat->outoctets = (kn != NULL) ? kn->value.ui32 : 0;

		/* rx_errors,, */
		kn = (kstat_named_t*)kstat_data_lookup(ksp, "ierrors");
		ifrawstat->inerrors = (kn != NULL) ? kn->value.ui32 : 0;

		/* tx_errors,, */
		kn = (kstat_named_t*)kstat_data_lookup(ksp, "oerrors");
		ifrawstat->outerrors = (kn != NULL) ? kn->value.ui32 : 0;

		/* collisions,, */
		kn = (kstat_named_t*)kstat_data_lookup(ksp, "collisions");
		ifrawstat->collisions = (kn != NULL) ? kn->value.ui32 : 0;

		/* ifspeed,, */
		kn = (kstat_named_t*)kstat_data_lookup(ksp, "ifspeed");
		ifspeed = (kn != NULL) ? kn->value.ui32 : 0;
		ifspeed = (ifspeed < 10000) ? ifspeed * 1000000 : ifspeed;
		ifrawstat->ifinfo.speed = (ifspeed) ? ifspeed : scCoreNetSetupEachInterfaceSpeed(ifname);
	}

	return SC_OK;
}

# else /* SunOS */
#  if defined(HPUX)
#  else /* HPUX */
#   if defined(Linux)
int scCoreNetSetupEachInterfaceRawStatus(scInterfaceRawStatus *ifrawstat, char *line, int version)
{
        unsigned long hole[9];
	char name[36];
	char *bp;

	/* setup the name */
	bp = scCoreNetSetupEachInterfaceName(name, line);
	if (!bp)
		return SC_ERR;

	/* setup the statistics */
        switch (version)
        {
	case 3:
		sscanf(bp, "%lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu",
									&ifrawstat->inoctets,
									&ifrawstat->inpkts,
									&ifrawstat->inerrors,
									&hole[0],
									&hole[1],
									&hole[2],
									&hole[3],
									&hole[4],
									&ifrawstat->outoctets,
									&ifrawstat->outpkts,
									&ifrawstat->outerrors,
									&hole[5],
									&hole[6],
									&ifrawstat->collisions,
									&hole[7],
									&hole[8]);
		break;

	case 2:
		sscanf(bp, "%lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu",
									&ifrawstat->inoctets,
									&ifrawstat->inpkts,
									&ifrawstat->inerrors,
									&hole[0],
									&hole[1],
									&hole[2],
									&ifrawstat->outoctets,
									&ifrawstat->outpkts,
									&ifrawstat->outerrors,
									&hole[3],
									&hole[4],
									&ifrawstat->collisions,
									&hole[5]);
		break;

	case 1:
		sscanf(bp, "%lu %lu %lu %lu %lu %lu %lu %lu %lu %lu %lu",
									&ifrawstat->inpkts,
									&ifrawstat->inerrors,
									&hole[0],
									&hole[1],
									&hole[2],
									&ifrawstat->outpkts,
									&ifrawstat->outerrors,
									&hole[3],
									&hole[4],
									&ifrawstat->collisions,
									&hole[5]);
		/* don't know how to.. */
		ifrawstat->inoctets = 0;
		ifrawstat->outoctets = 0;

		break;

	default:
		return SC_ERR;
	}

	return SC_OK;
}

#elif CYGWIN
int scCoreNetSetupEachInterfaceRawStatus(scInterfaceRawStatus *ifrawstat, ITEM item)
{
/*

	&ifrawstat->inoctets,
	&ifrawstat->inpkts,
	&ifrawstat->inerrors,
	&ifrawstat->outoctets,
	&ifrawstat->outpkts,
	&ifrawstat->outerrors,
	&ifrawstat->collisions,
*/
	long long inpkts = 0, outpkts = 0, inerrors = 0, outerrors = 0, inoct=0, outoct=0;



	read_counter_large_int(item.h_Counter[0], &inpkts); 
	read_counter_large_int(item.h_Counter[1], &outpkts);
	read_counter_large_int(item.h_Counter[2], &inerrors); 
	read_counter_large_int(item.h_Counter[3], &outerrors); 
	read_counter_large_int(item.h_Counter[4], &inoct); 
	read_counter_large_int(item.h_Counter[5], &outoct); 

	ifrawstat->inpkts = inpkts;
	ifrawstat->outpkts = outpkts;
	ifrawstat->inerrors = inerrors;
	ifrawstat->outerrors = outerrors;
	ifrawstat->inoctets = inoct;
	ifrawstat->outoctets = outoct;

	/* don't know how to.. */

	ifrawstat->collisions = 0;

	return SC_OK;
}

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */

#if defined(Linux) || defined(CYGWIN)

char *scCoreNetSetupEachInterfaceName(char *ifname, char *line)
{
	char *p = line;

        while (isspace(*p))
                p++;
        while (*p) {
                if (isspace(*p))
                        break;
                if (*p == ':') {        /* could be an alias */
                        char *dot = p, *dotname = ifname;
                        *ifname++ = *p++;
                        while (isdigit(*p))
                                *ifname++ = *p++;
                        if (*p != ':') {        /* it wasn't, backup */
                                p = dot;
                                ifname = dotname;
                        }
                        if (*p == '\0')
                                return NULL;
                        p++;
                        break;
                }
                *ifname++ = *p++;
        }
        *ifname++ = '\0';

        return p;
}

#endif /* Linux */

#if defined(AIX)
int tcpstate_aton(char *state)
{
	if(strstr(state, "CLOSED"))
		return SC_TCP_CLOSE;
	else if(strstr(state, "LISTEN"))
		return SC_TCP_LISTEN;
	else if(strstr(state, "SYN_SENT"))
		return SC_TCP_SYN_SENT;
	else if(strstr(state, "SYN_RCVD"))
		return SC_TCP_SYN_RECV;
	else if(strstr(state, "ESTABLISHED"))
		return SC_TCP_ESTABLISHED;
	else if(strstr(state, "CLOSE_WAIT"))
		return SC_TCP_CLOSE_WAIT;
	else if(strstr(state, "FIN_WAIT_1"))
		return SC_TCP_FIN_WAIT1;
	else if(strstr(state, "CLOSING"))
		return SC_TCP_CLOSING;
	else if(strstr(state, "LAST_ACK"))
		return SC_TCP_LAST_ACK;
	else if(strstr(state, "FIN_WAIT_2"))
		return SC_TCP_FIN_WAIT2;
	else if(strstr(state, "TIME_WAIT"))
		return SC_TCP_TIME_WAIT;
	else
		return SC_TCP_UNKNOWN;
}

#endif /* AIX */

int scCoreNetFsrchInterfaceName(const void *v1, const void *v2)
{
	char *ifname1 = ((scInterfaceRawStatus *)v1)->ifinfo.ifname;
	char *ifname2 = ((scInterfaceRawStatus *)v2)->ifinfo.ifname;

	return !strcmp(ifname1, ifname2) ? NODE_FOUND : NODE_NOT_FOUND;
}

v_list_t *scCoreNetTCPInfo(scCore *core, int listen_only)
{
#if defined(AIX)

	v_list_t *list = NULL; /* initialize first */
	scTCPInfo tcpinfo;
	FILE *fp=NULL;
	char buf[256], *p=NULL, *q=NULL;
	unsigned rq, sq;
	char data[7][128];
	struct in_addr localaddr, remoteaddr;
	unsigned short localport, remoteport;

	if((fp = popen("netstat -an | grep tcp", "r"))==NULL)
	{
		return NULL;
	}

	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}
	
	memset(buf, 0x00, sizeof(buf));
	while(fgets(buf, sizeof(buf)-1, fp))
	{
		buf[strlen(buf)-1] = 0x00;
		memset(data, 0x00, 7*128);
		if(sscanf(buf, "%s %c %c %s %s %s %s",
			data[0], data[1], data[2],
			data[3], data[4], data[5])!=6) goto read_cont;
		rq = atoi(data[1]); sq = atoi(data[2]);
		if((p = strrchr(data[3], '.'))==NULL) goto read_cont;
		if((q = strrchr(data[4], '.'))==NULL) goto read_cont;
		*p = 0x00; p++;
		*q = 0x00; q++;

		if(*p=='*') localport = 0;
		else localport = atoi(p);
		if(*q == '*') remoteport = 0;
		else remoteport = atoi(q);

		if(data[3][0] == '*') strcpy(data[3], "0.0.0.0");
		if(data[4][0] == '*') strcpy(data[4], "0.0.0.0");

		memset(&localaddr, 0x00, sizeof(struct in_addr));
		memset(&remoteaddr, 0x00, sizeof(struct in_addr));

		inet_aton(data[3], &localaddr);
		strcpy(data[3], inet_ntoa(localaddr));
		inet_aton(data[4], &remoteaddr);
		strcpy(data[4], inet_ntoa(remoteaddr));
#if 0
		printf("rq[%x], sq[%x], local[%s][%d], remote[%s][%d], state[%d]\n",
			rq, sq, data[3], localport, data[4], remoteport, tcpstate_aton(data[5]));
#endif

		memset(&tcpinfo,0x00,sizeof(scTCPInfo));

		tcpinfo.localaddr.s_addr  = localaddr.s_addr;
		tcpinfo.remoteaddr.s_addr = remoteaddr.s_addr;
		tcpinfo.localport  = htons((unsigned short)localport);
		tcpinfo.remoteport = htons((unsigned short)remoteport);

		/* setup the rest */
		tcpinfo.state   = tcpstate_aton(data[5]);
		tcpinfo.sndque  = sq;
		tcpinfo.rcvque  = rq;
		tcpinfo.count   = 1;

		/* make new entriy */
		ll_insert_node(list,&tcpinfo,sizeof(scTCPInfo),NULL);

read_cont:
		memset(buf, 0x00, sizeof(buf));
	}

	pclose(fp);
	return list;
#else
# if defined(SunOS)

	int fd, i;
	int flags, cc, icount;

	v_list_t *list = NULL; /* initialize first */
	scTCPInfo tcpinfo;

	struct strbuf strbuf;
	mib2_tcpConnEntry_t tcpconns;

	/* open stream device */
	if ((fd = open("/dev/ip", O_RDWR)) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	/* push module */
	for (i = 0; PushModuleList[i] != NULL; i++) {
		if (ioctl(fd,I_PUSH,PushModuleList[i]) == -1) {
#ifdef DEBUG
			fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
			goto out;
		}
	}

	/* lookup all the entries */
	if (tcpinfo_initialize(fd, MIB2_TCP, MIB2_TCP_13) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		goto out;
	}
	
	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		goto out;
	}

	/* initialize */
	strbuf.buf     = (char *)(&tcpconns);
	strbuf.maxlen  = sizeof(tcpconns);
	strbuf.len     = 0;
	icount = flags = 0;

	do {
		if ((cc = getmsg(fd, NULL, &strbuf, &flags)) == -1) {
#ifdef DEBUG
			fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
			goto out;
		}

		/* initailize & setup the proper value */
		memset(&tcpinfo,0x00,sizeof(scTCPInfo));

		tcpinfo.localaddr.s_addr  = tcpconns.tcpConnLocalAddress;
		tcpinfo.remoteaddr.s_addr = tcpconns.tcpConnRemAddress;
		tcpinfo.localport  = htons((unsigned short)tcpconns.tcpConnLocalPort);
		tcpinfo.remoteport = htons((unsigned short)tcpconns.tcpConnRemPort);

		/* setup the rest */
		tcpinfo.state   = tcpinfo_state2kvish(tcpconns.tcpConnState);
		tcpinfo.sndque  = 0; // tcpconns.tcpConnEntryInfo.ce_swnd;
		tcpinfo.rcvque  = 0; // tcpconns.tcpConnEntryInfo.ce_rwnd;
		tcpinfo.count   = 1;

		/* make new entriy */
		ll_insert_node(list,&tcpinfo,sizeof(scTCPInfo),NULL);
	} while (cc == MOREDATA);

out:
	if (fd != -1)
		close(fd);

	return list;

# else
#  if defined(HPUX)

	struct nmparms p;
	int fd, val, i, tcptabsize;
	unsigned int ulen;

	v_list_t *list = NULL; /* initialize first */
	scTCPInfo tcpinfo;

	mib_tcpConnEnt *table = NULL;

	ulen     = sizeof(int);
	p.objid  = ID_tcpConnNumEnt;
	p.buffer = (void *)&val;
	p.len    = &ulen;

	if ((fd = open_mib("/dev/ip", O_RDONLY, 0, NM_ASYNC_OFF)) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] open_mib error[%s]\n", __FILE__, __LINE__,
			strerror(errno));
#endif
		return NULL;
	}

	if (get_mib_info(fd, &p) != 0 || val <= 0) {
		close_mib(fd);
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] get_mib_info error[%s]\n", __FILE__, __LINE__,
			strerror(errno));
#endif
		return NULL;
	}

	tcptabsize = val;

	ulen = (unsigned)tcptabsize * sizeof(mib_tcpConnEnt);
	table = (mib_tcpConnEnt *)malloc(ulen);

	p.objid  = ID_tcpConnTable;
	p.buffer = (void *)table;

	if (get_mib_info(fd, &p) < 0) {
		/* release first */
		close_mib(fd);
		free(table);

#ifdef DEBUG
		fprintf(stderr, "[%s,%d] get_mib_info error[%s]\n", __FILE__, __LINE__,
			strerror(errno));
#endif
		return NULL;
	}

	/* create list */
	list = ll_create_node(NULL,1);

	for (i = 0; i < tcptabsize; i++) {
		/* setup.. */
		memset(&tcpinfo,0x00,sizeof(scTCPInfo));
		tcpinfo.localaddr.s_addr  = table[i].LocalAddress;
		tcpinfo.remoteaddr.s_addr = table[i].RemAddress;
		tcpinfo.localport  = (unsigned short)table[i].LocalPort;
		tcpinfo.remoteport = (unsigned short)table[i].RemPort;

		/* setup the rest */
		tcpinfo.state   = tcpinfo_state2kvish(table[i].State);
		tcpinfo.sndque  = 0; /* don't know how come.. */
		tcpinfo.rcvque  = 0;
		tcpinfo.count   = 1;

		/* skip unconcerned info */
		if (listen_only && tcpinfo.state != SC_TCP_LISTEN)
			continue;

		ll_insert_node(list,&tcpinfo,sizeof(scTCPInfo),NULL);
	}

	/* release */
	close(fd);
	free(table);

	return list;

#  else /* HPUX */
#   if defined(Linux) 
	FILE *f;
	char line[2048];

	v_list_t *list;
	scTCPInfo tcpinfo;

	if ((f = fopen(SC_PROC_NET_TCP,"r")) == NULL) {
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

	while (fgets(line,sizeof(line)-1,f) != NULL) {
		/* initialize first */
		memset(&tcpinfo,0x00,sizeof(scTCPInfo));

		if (scCoreNetSetupEachTCPInfo(&tcpinfo, line) != SC_ERR) {
			if (listen_only && tcpinfo.state != SC_TCP_LISTEN) 
				continue;

			ll_insert_node(list,&tcpinfo,sizeof(scTCPInfo),NULL);
		}
	}

out:
	/* release */
	fclose(f);

	return list;

#elif CYGWIN

	v_list_t *list;
	scTCPInfo tcpinfo;

	DWORD dwRetVal;
	// Declare and initialize variables
	PMIB_TCPTABLE pTcpTable;

	pTcpTable = (MIB_TCPTABLE*) malloc(sizeof(MIB_TCPTABLE));
	DWORD dwSize = 0;

	// Make an initial call to GetTcpTable to
	// get the necessary size into the dwSize variable
	if (GetTcpTable(pTcpTable, &dwSize, TRUE) == ERROR_INSUFFICIENT_BUFFER) {
		free(pTcpTable);
		pTcpTable = (MIB_TCPTABLE*) malloc ((UINT) dwSize);
	}

	/* create the node */
	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		goto out;
	}

	if ((dwRetVal = GetTcpTable(pTcpTable, &dwSize, TRUE)) != NO_ERROR) {
		goto out;
	}

	for (int i = 0; i < (int) pTcpTable->dwNumEntries; i++) {
		/* initialize first */
		memset(&tcpinfo,0x00,sizeof(scTCPInfo));

		MIB_TCPROW tcp_table = pTcpTable->table[ i ] ;

		if (scCoreNetSetupEachTCPInfo(&tcpinfo, (char*)&tcp_table) != SC_ERR) {
			if (listen_only && tcpinfo.state != SC_TCP_LISTEN) 
				continue;

			ll_insert_node(list,&tcpinfo,sizeof(scTCPInfo),NULL);
		}
	}

out:
	free(pTcpTable); pTcpTable = NULL;

	return list;

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */

}

#if defined(SunOS)

int tcpinfo_initialize(int fd, int grpname, int tblname)
{
	char buff[BUFSIZE_MX];
	int flags, rc;

	struct strbuf strbuf;
	struct T_optmgmt_req *tor = (struct T_optmgmt_req *)buff;
	struct T_optmgmt_ack *toa = (struct T_optmgmt_ack *)buff;
	struct T_error_ack   *tea = (struct T_error_ack *)buff;
	struct opthdr        *req; /* option which include group name, group table */

	/* func name,, */
	printout(__F__,"tcpinfo_initialize");

	/* initialize */
	memset(buff,0x00,sizeof(buff));

	/* for T_optmgmt_req */
	tor->PRIM_type  = T_OPTMGMT_REQ;
	tor->OPT_offset = sizeof(struct T_optmgmt_req);
	tor->OPT_length = sizeof(struct opthdr);
	tor->MGMT_flags = T_CURRENT;

	/* for opthdr : this should be located after tor */
	req        = (struct opthdr *)(tor + 1);
	req->level = grpname;
	req->name  = tblname;
	req->len   = 0;

	/* for strbuf */
	strbuf.buf    = buff;
	strbuf.maxlen = BUFSIZE_MX;
	strbuf.len    = tor->OPT_length + tor->OPT_offset; /* size of optmgmt + size of option */

	/* write mesg to STREAMS Head */
	flags = 0;
	if ((rc = putmsg(fd, &strbuf, NULL, flags)) == -1) {
		printout(__K__,"tcpinfo_initialize: fail to putmsg.");
		return -1;
	}

	req = (struct opthdr *)(toa + 1);

	for ( ; ; ) {
		flags = 0;

		/* read mesg from STREAMS Head */
		/* if ((rc = getmsg(fd, &strbuf, NULL, &flags)) == -1) { */
		if ((rc = timed_getmsg(fd, &strbuf, &flags, 3)) == -1) {
			printout(__K__,"tcpinfo_initialize: fail to getmsg.");
			return -1;
		}

		/* error check routine 1 */
		if (rc == 0
				&& (int)(strbuf.len) >= (int)sizeof(struct T_optmgmt_ack)
				&& toa->PRIM_type == T_OPTMGMT_ACK
				&& toa->MGMT_flags == T_SUCCESS
				&& req->len == 0)
		{
			printout(__K__,"tcpinfo_initialize: error(#1) occured.");
			return -1;
		}

		/* error check routine 2 */
		if (rc == 0
				&& (int)(strbuf.len) >= (int)sizeof(struct T_error_ack)
				&& tea->PRIM_type == T_ERROR_ACK)
		{
			printout(__K__,"tcpinfo_initialize: error(#2) occured.");
			return -1;
		}

		/* error check routine 3 */
		if (rc != MOREDATA
				|| (int)(strbuf.len) < (int)sizeof(struct T_optmgmt_ack)
				|| toa->PRIM_type != T_OPTMGMT_ACK
				|| toa->MGMT_flags != T_SUCCESS)
		{
			printout(__K__,"tcpinfo_initialize: error(#3) occured.");
			return -1;
		}

		/* check option */
		if (req->level != grpname || req->name != tblname) {
			strbuf.buf    = buff;
			strbuf.maxlen = BUFSIZE_MX;

			do {
				/* just pop up unconcerned entries from the queue */
				rc = getmsg(fd, NULL, &strbuf, &flags);

			} while ( rc == MOREDATA );

			continue;
		} else
			return 1; /* found what i looked for */
	}

	return 1; /* Never Reach here!! */
}

int timed_getmsg(int fd, struct strbuf *ctlp, int *flagsp, int timeout)
{
	struct pollfd	pfd;
	int		ret;

	pfd.fd = fd;

	pfd.events = POLLIN | POLLRDNORM | POLLRDBAND | POLLPRI;
	if ((ret = poll(&pfd, 1, timeout * 1000)) == 0) {
		printout(__K__,"timed_getmsg: timed out.");
		return -1;
	}
	else if (ret == -1) {
		printout(__K__,"timed_getmsg: fail to poll.");
		return -1;
	}

	/* poll returned > 0 for this fd so getmsg should not block */
	return getmsg(fd, ctlp, NULL, flagsp);
}

#endif /* SunOS */


int scCoreNetSetupEachTCPInfo(scTCPInfo *tcpinfo, char *line)
{
#if defined(AIX)

#else
# if defined(SunOS)
# else
#  if defined(HPUX)
#  else /* HPUX */
#   if defined(Linux)

	unsigned tmp[7];
	int n;

	/* hm.... */
	n = sscanf(line,"%*d: %x:%x %x:%x %x %x:%x %*X %*X %*X %*d",
						&tmp[0], &tmp[1],  /* local  addr:port */
						&tmp[2], &tmp[3],  /* remote addr:port */
						&tmp[4],           /* state */
						&tmp[5], &tmp[6]); /* send/recv queue  */
	if (n != 7)
		return SC_ERR;

	/* setup the address (in a network byte order) */
        tcpinfo->localaddr.s_addr  = tmp[0];
        tcpinfo->remoteaddr.s_addr = tmp[2];
        tcpinfo->localport  = htons((unsigned short)tmp[1]);
        tcpinfo->remoteport = htons((unsigned short)tmp[3]);

	/* setup the rest */
	tcpinfo->state   = tcpinfo_state2kvish(tmp[4]);
        tcpinfo->sndque  = tmp[5];
        tcpinfo->rcvque  = tmp[6];
        tcpinfo->count = 1;
	
	return SC_OK;
#elif CYGWIN

	PMIB_TCPROW table = (PMIB_TCPROW) line;
	/* setup the address (in a network byte order) */
	tcpinfo->localaddr.s_addr  = table->dwLocalAddr;
	tcpinfo->remoteaddr.s_addr = table->dwRemoteAddr;
	tcpinfo->localport  = table->dwLocalPort;
	tcpinfo->remoteport = table->dwRemotePort ;

	/* setup the rest */
	tcpinfo->state = tcpinfo_state2kvish(table->dwState);

	if (tcpinfo->state == SC_TCP_LISTEN) {
		tcpinfo->remoteaddr.s_addr = 0;
		tcpinfo->remoteport = 0;
	}

    tcpinfo->sndque  = 0;
    tcpinfo->rcvque  = 0;
    tcpinfo->count = 1;

	return SC_OK;

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */
}


int tcpinfo_state2kvish(int state)
{
#if defined(AIX)  || defined(Linux)
	switch (state) {
		case 1: 
			return SC_TCP_ESTABLISHED;
	
		case 2: 
			return SC_TCP_SYN_SENT;

		case 3:
			return SC_TCP_SYN_RECV;

		case 4:
			return SC_TCP_FIN_WAIT1;

		case 5:
			return SC_TCP_FIN_WAIT2;

		case 6:
			return SC_TCP_TIME_WAIT;

		case 7:
			return SC_TCP_CLOSE;

		case 8:
			return SC_TCP_CLOSE_WAIT;

		case 9:
			return SC_TCP_LAST_ACK;

		case 10:
			return SC_TCP_LISTEN;

		case 11:
			return SC_TCP_CLOSING;

		default:
			return SC_TCP_UNKNOWN;
	}

	return SC_TCP_UNKNOWN;

#else
# if defined(SunOS)

	switch (state) {
		case MIB2_TCP_established: 
			return SC_TCP_ESTABLISHED;
	
		case MIB2_TCP_synSent: 
			return SC_TCP_SYN_SENT;

		case MIB2_TCP_synReceived:
			return SC_TCP_SYN_RECV;

		case MIB2_TCP_finWait1:
			return SC_TCP_FIN_WAIT1;

		case MIB2_TCP_finWait2:
			return SC_TCP_FIN_WAIT2;

		case MIB2_TCP_timeWait:
			return SC_TCP_TIME_WAIT;

		case MIB2_TCP_closed:
			return SC_TCP_CLOSE;

		case MIB2_TCP_closeWait:
			return SC_TCP_CLOSE_WAIT;

		case MIB2_TCP_lastAck:
			return SC_TCP_LAST_ACK;

		case MIB2_TCP_listen:
			return SC_TCP_LISTEN;

		case MIB2_TCP_closing:
			return SC_TCP_CLOSING;

		default:
			return SC_TCP_UNKNOWN;
	}

	return SC_TCP_UNKNOWN;

# else
#  if defined(HPUX)

	switch (state) {
		case TCESTABLISED: 
			return SC_TCP_ESTABLISHED;
	
		case TCSYNSENT: 
			return SC_TCP_SYN_SENT;

		case TCSYNRECEIVE:
			return SC_TCP_SYN_RECV;

		case TCFINWAIT1:
			return SC_TCP_FIN_WAIT1;

		case TCFINWAIT2:
			return SC_TCP_FIN_WAIT2;

		case TCTIMEWAIT:
			return SC_TCP_TIME_WAIT;

		case TCCLOSED:
			return SC_TCP_CLOSE;

		case TCCLOSEWAIT:
			return SC_TCP_CLOSE_WAIT;

		case TCLASTACK:
			return SC_TCP_LAST_ACK;

		case TCLISTEN:
			return SC_TCP_LISTEN;

		case TCCLOSING:
			return SC_TCP_CLOSING;

		default:
			return SC_TCP_UNKNOWN;
	}

	return SC_TCP_UNKNOWN;
#else
#ifdef CYGWIN
	switch (state) {
		case MIB_TCP_STATE_ESTAB: 
			return SC_TCP_ESTABLISHED;
	
		case MIB_TCP_STATE_SYN_SENT: 
			return SC_TCP_SYN_SENT;

		case MIB_TCP_STATE_SYN_RCVD:
			return SC_TCP_SYN_RECV;

		case MIB_TCP_STATE_FIN_WAIT1:
			return SC_TCP_FIN_WAIT1;

		case MIB_TCP_STATE_FIN_WAIT2:
			return SC_TCP_FIN_WAIT2;

		case MIB_TCP_STATE_TIME_WAIT:
			return SC_TCP_TIME_WAIT;

		case MIB_TCP_STATE_CLOSING:
			return SC_TCP_CLOSE;

		case MIB_TCP_STATE_CLOSE_WAIT:
			return SC_TCP_CLOSE_WAIT;

		case MIB_TCP_STATE_LAST_ACK:
			return SC_TCP_LAST_ACK;

		case MIB_TCP_STATE_LISTEN:
			return SC_TCP_LISTEN;

		case MIB_TCP_STATE_CLOSED:
			return SC_TCP_CLOSING;

		default:
			return SC_TCP_UNKNOWN;
	}

	return SC_TCP_UNKNOWN;
#endif // CYGWIN

#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */

}


#if defined(HPUX)
int scCoreNetSetupPhystat(scCore *core, v_list_t *list)
{
	unsigned int ulen;
	int i, ifnumber = list->count;

	static nmapi_phystat *hp11stat = NULL;

	ulen = (unsigned int)ifnumber * sizeof(nmapi_phystat);
	if (!hp11stat) 
	if ((hp11stat = (nmapi_phystat *)malloc(ulen)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}
	memset(hp11stat,0x00,ulen);

	/* get ifstats */
	if (get_physical_stat(hp11stat, &ulen) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return SC_ERR;
	}

	/* scan all the entries */
	for (i = 0; i < ifnumber; i++) {
		scInterfaceRawStatus *ifrawstat;
		int at = 0;

		/* lookup the entry.. */
		while ((ifrawstat = (scInterfaceRawStatus*)ll_element_at(list, at++)) != NULL
				&& strcmp(ifrawstat->ifinfo.ifname, hp11stat[i].nm_device) != 0)
			;
		
		/* not found.. */
		if (!ifrawstat) continue;

		/* ifindex */
		ifrawstat->ifinfo.index = hp11stat[i].if_entry.ifIndex;

		/* iftype */
		ifrawstat->ifinfo.type = hp11stat[i].if_entry.ifType;

		/* mtu */
		ifrawstat->ifinfo.mtu = hp11stat[i].if_entry.ifMtu;

		/* speed */
		ifrawstat->ifinfo.speed = hp11stat[i].if_entry.ifSpeed;

		/* physical address */
		memcpy(ifrawstat->ifinfo.hwaddr, hp11stat[i].if_entry.ifPhysAddress.o_bytes, 6);

		/* inpkts */
		ifrawstat->inpkts = hp11stat[i].if_entry.ifInUcastPkts
					+ hp11stat[i].if_entry.ifInNUcastPkts;

		/* outpkts */
		ifrawstat->outpkts = hp11stat[i].if_entry.ifOutUcastPkts
					+ hp11stat[i].if_entry.ifOutNUcastPkts;

		/* inoctets */
		ifrawstat->inoctets = hp11stat[i].if_entry.ifInOctets;

		/* outoctets */
		ifrawstat->outoctets = hp11stat[i].if_entry.ifOutOctets;

		/* inerrors */
		ifrawstat->inerrors = hp11stat[i].if_entry.ifInErrors;

		/* outerrors */
		ifrawstat->outerrors = hp11stat[i].if_entry.ifOutErrors;

		/* collisions */
		ifrawstat->collisions = 0;
		
	}

	return SC_OK;
}
#endif



v_list_t *scCoreNetInterfaceRawStatus(scCore *core)
{
#if defined(AIX)
	int   sockfd, lastlen, len, n;
	char *buf;

	struct ifconf  ifc;
	struct ifreq  *ifr;

	v_list_t *list;

	if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] socket error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	/* initial buffer size guess */
	len = 100 * sizeof(struct ifreq);
	lastlen = 0;

	/* allocate memory to hold ifinfo data */
	for ( ; ;) {
		buf = (char *)malloc(len);
		ifc.ifc_len = len;
		ifc.ifc_buf = buf;

		if (ioctl(sockfd, SIOCGIFCONF, &ifc) == -1) {
			if (errno != EINVAL || lastlen != 0) {
#ifdef DEBUG
				fprintf(stderr, "[%s,%d] ioctl error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
				goto err_quit;
			}
		} else {
			/* success */
			if (ifc.ifc_len == lastlen)
				break;

			lastlen = ifc.ifc_len;
		}

		len += sizeof(struct ifreq) * 10;
		free(buf);
	}

	/* setup the each ifinfo */
	n   = 0;
	ifr = ifc.ifc_req;

	/* create the node */
	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
				fprintf(stderr, "[%s,%d] create node error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
#endif
		goto err_quit;
	}

	while (n < ifc.ifc_len) {
		char *ifname = ifr->ifr_name;
		struct sockaddr_dl *sdl = (struct sockaddr_dl *)&ifr->ifr_addr;
		scInterfaceRawStatus ifrawstat;

		/* AF_LINK sock-address family is only concerned.. */
		if (ifr->ifr_addr.sa_family == AF_LINK || ifr->ifr_addr.sa_family == AF_INET) {
			/* initialize first */
			memset(&ifrawstat,0x00,sizeof(scInterfaceRawStatus));
		
			/* setup the rest */
			if (scCoreNetSetupEachInterfaceInfo(&(ifrawstat.ifinfo),sockfd,ifname,sdl) != SC_ERR) {
				/* make new entry */
				ll_insert_node(list,&ifrawstat,sizeof(scInterfaceRawStatus),NULL);
			}
		}

		/* the next one */
		n = n + sizeof(struct ifreq);
		ifr++;
	}

	/* setup ifstat */
	scCoreNetSetupInterfaceRawStatus(list);

err_quit:
	/* release */
	if (sockfd != -1) close(sockfd);
	if (buf) free(buf);

	return list;

#else
# if defined(SunOS)

	int   sockfd, lastlen, len, n;
	char *buf;

	struct ifconf  ifc;
	struct ifreq  *ifr;

	v_list_t *list;

	if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	/* initial buffer size guess */
	len = 100 * sizeof(struct ifreq);
	lastlen = 0;

	/* allocate memory to hold ifinfo data */
	for ( ; ;) {
		buf = (char *)malloc(len);
		ifc.ifc_len = len;
		ifc.ifc_buf = buf;

		if (ioctl(sockfd, SIOCGIFCONF, &ifc) == -1) {
			if (errno != EINVAL || lastlen != 0) {
#ifdef DEBUG
				fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
				goto out;
			}
		} else {
			/* success */
			if (ifc.ifc_len == lastlen)
				break;

			lastlen = ifc.ifc_len;
		}

		len += sizeof(struct ifreq) * 10;
		free(buf);
	}

	/* create the node */
	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		goto out;
	}

	/* setup the each ifinfo */
	n   = 0;
	ifr = ifc.ifc_req;
	while (n < ifc.ifc_len) {
		char *ifname = ifr->ifr_name;

		/* user defined */
		scInterfaceRawStatus ifrawstat;

		/* initialize first */
		memset(&ifrawstat,0x00,sizeof(scInterfaceRawStatus));

		/* setup the rest */
		if (scCoreNetSetupEachInterfaceInfo(&(ifrawstat.ifinfo),sockfd,ifname) != SC_ERR) {
			int  instance, i;
			char module[16];

			/* set the module */
			i = 0;
			while(!isdigit((int)ifname[i]) && ifname[i] != '\0') {
				module[i] = ifname[i];
				i++;
			}
			module[i] = '\0';

			/* setup the instance */
			instance = atoi(&ifname[i]);

			/* if statistics */ 
			scCoreNetSetupEachInterfaceRawStatus(core, &ifrawstat, module, ifname, instance);

			/* make new entry */
			ll_insert_node(list,&ifrawstat,sizeof(scInterfaceRawStatus),NULL);
		}

		/* the next one */
		n = n + sizeof(struct ifreq);
		ifr++;
	}

out:
	/* release */
	if (sockfd != -1) close(sockfd);
	if (buf) free(buf);


	return list;

# else
#  if defined(HPUX)
	int   sockfd, lastlen, len, n;
	char *buf;

	struct ifconf  ifc;
	struct ifreq  *ifr;

	v_list_t *list;

	if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
#ifdef DEBUG
		fprintf(stderr,"[%s,%d] socket error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	/* initial buffer size guess */
	len = 100 * sizeof(struct ifreq);
	lastlen = 0;

	/* allocate memory to hold ifinfo data */
	for ( ; ;) {
		buf = (char *)malloc(len);
		ifc.ifc_len = len;
		ifc.ifc_buf = buf;

		if (ioctl(sockfd, SIOCGIFCONF, &ifc) == -1) {
			if (errno != EINVAL || lastlen != 0) {
				/* release first */
#ifdef DEBUG
				fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
				close(sockfd);
				free(buf);
				return NULL;
			}
		} else {
			/* success */
			if (ifc.ifc_len == lastlen)
				break;

			lastlen = ifc.ifc_len;
		}

		len += sizeof(struct ifreq) * 10;
		free(buf);
	}

	/* create the list */
	list = ll_create_node(NULL,1);

	/* setup the each ifinfo */
	n = 0; ifr = ifc.ifc_req;
	while (n < ifc.ifc_len) {
		int cc;
		scInterfaceRawStatus ifrawstat;

		/* initialize first */
		memset(&ifrawstat,0x00,sizeof(scInterfaceRawStatus));
		sprintf(ifrawstat.ifinfo.ifname,"%s",ifr->ifr_name);

		/* setup the rest */
		cc = scCoreNetSetupEachInterfaceInfo(&(ifrawstat.ifinfo),sockfd);
		if (cc != SC_ERR)
			ll_insert_node(list,&ifrawstat,sizeof(scInterfaceRawStatus),NULL);

		/* the next one */
		n += sizeof(struct ifreq); ifr++;
	}

	/* release.. */
	close(sockfd);
	free(buf);

	scCoreNetSetupPhystat(core, list);

	return list;

#  else /* HPUX */
#   if defined(Linux)

	int   sockfd, lastlen, len, n;
	char *buf;

	struct ifconf  ifc;
	struct ifreq  *ifr;

	v_list_t *list;

	if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		return NULL;
	}

	/* initial buffer size guess */
	len = 100 * sizeof(struct ifreq);
	lastlen = 0;

	/* allocate memory to hold ifinfo data */
	for ( ; ;) {
		buf = (char *)malloc(len);
		ifc.ifc_len = len;
		ifc.ifc_buf = buf;

		if (ioctl(sockfd, SIOCGIFCONF, &ifc) == -1) {
			if (errno != EINVAL || lastlen != 0) {
#ifdef DEBUG
				fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
				goto out;
			}
		} else {
			/* success */
			if (ifc.ifc_len == lastlen)
				break;

			lastlen = ifc.ifc_len;
		}

		len += sizeof(struct ifreq) * 10;
		free(buf);
	}

	/* setup the each ifinfo */
	n   = 0;
	ifr = ifc.ifc_req;

	/* create the node */
	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		goto out;
	}

	while (n < ifc.ifc_len) {
		char *ifname = ifr->ifr_name;
		char block[8192];
		int  version;
		scInterfaceRawStatus ifrawstat;

		/* initialize */
		memset(block,0x00,sizeof(block));

		if (f2b(SC_PROC_NET_DEV,block,sizeof(block)) == 0) {
			/* go out or do continue..?? */
#ifdef DEBUG
			fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		}

		/* version check */
		version = (strstr(block,"compressed") != NULL) ? 3
						: (strstr(block,"bytes")) ? 2 : 1;

		/* initialize first */
		memset(&ifrawstat,0x00,sizeof(scInterfaceRawStatus));

		/* setup the rest */
		if (scCoreNetSetupEachInterfaceInfo(&(ifrawstat.ifinfo),sockfd,ifname) != SC_ERR) {
			char line[1024], *cp, *ep;

			if ((cp = strstr(block,ifname)) != NULL
					&& (ep = strchr(cp,'\n')) != NULL)
			{
				int linelen = ep - cp;

				memset(line,0x00,sizeof(line));
				memcpy(line,cp  ,linelen);

				scCoreNetSetupEachInterfaceRawStatus(&ifrawstat, line, version);
			}

			/* make new entry */
			ll_insert_node(list,&ifrawstat,sizeof(scInterfaceRawStatus),NULL);
		}

		/* the next one */
		n = n + sizeof(struct ifreq);
		ifr++;
	}

out:
	/* release */
	if (sockfd != -1) close(sockfd);
	if (buf) free(buf);

	return list;
#elif CYGWIN
	PIP_ADAPTER_INFO pAdapterInfo;
	PIP_ADAPTER_INFO pAdapter = NULL;
	DWORD dwSize = 0;
	DWORD dwRetVal = 0;
	v_list_t *list;
	int i = 0;

	pAdapterInfo = (IP_ADAPTER_INFO *) malloc( sizeof(IP_ADAPTER_INFO) );
	ULONG ulOutBufLen = sizeof(IP_ADAPTER_INFO);

	// Make an initial call to GetAdaptersInfo to get
	// the necessary size into the ulOutBufLen variable
	if (GetAdaptersInfo( pAdapterInfo, &ulOutBufLen) == ERROR_BUFFER_OVERFLOW) {
		free(pAdapterInfo); pAdapterInfo = NULL;
		pAdapterInfo = (IP_ADAPTER_INFO *) malloc (ulOutBufLen); 
	}

	if ((dwRetVal = GetAdaptersInfo( pAdapterInfo, &ulOutBufLen)) != NO_ERROR) {
		free(pAdapterInfo); pAdapterInfo=NULL;
		return NULL;
	}

	/* create the node */
	if ((list = ll_create_node(NULL,1)) == NULL) {
#ifdef DEBUG
		fprintf(stderr, "[%s,%d] error[%s]\n", __FILE__, __LINE__, strerror(errno));
#endif
		goto out;
	}


	// pdh 정보 구하기.
	collectData(core->h_Networkquery);

	pAdapter = pAdapterInfo;
	while (pAdapter) {
		scInterfaceRawStatus ifrawstat;

		MIB_IFROW mibIfRow;

		/* initialize first */
		memset(&ifrawstat,0x00,sizeof(scInterfaceRawStatus));

		int linkSpeed = 0;
		mibIfRow.dwIndex = pAdapter->Index;
		if (GetIfEntry(&mibIfRow) == NO_ERROR) {
			linkSpeed = mibIfRow.dwSpeed;
		}

		/* setup the rest */
		if (scCoreNetSetupEachInterfaceInfo(&(ifrawstat.ifinfo), pAdapter, linkSpeed) != SC_ERR) {

			if (i < core->network_item.size()) {
				ITEM item = core->network_item[ i ];
				scCoreNetSetupEachInterfaceRawStatus(&ifrawstat, item);
				ll_insert_node(list, &ifrawstat, sizeof(scInterfaceRawStatus), NULL);
			}

			/*
			// 찾기...
			for (int j=0; j < core->network_item.size(); j++) {
				
				
				if (strncmp(ifrawstat.ifinfo.ifname, item.instance_name.c_str(), strlen(ifrawstat.ifinfo.ifname)) == 0) {
					scCoreNetSetupEachInterfaceRawStatus(&ifrawstat, item);

					ll_insert_node(list, &ifrawstat, sizeof(scInterfaceRawStatus), NULL);
					break;
				}
			}
			*/
		}

		i = i + 1;
		pAdapter = pAdapter->Next;
	}

out:
	free(pAdapterInfo); pAdapterInfo=NULL;
	return list;

#   endif /* Linux */
#  endif /* HPUX */
# endif /* SunOS */
#endif /* AIX */

}


#ifndef __CYGWIN_H__
#define __CYGWIN_H__

#ifdef CYGWIN


#include <string>
#include <vector>
#include <map>
#include <algorithm> // replace
#include <windows.h>


using namespace std;

#define PDH_DISK "LogicalDisk"

#define PDH_DISKIOREAD "\\LogicalDisk(%s)\\Disk Read Bytes/sec"
#define PDH_DISKIOWRITE "\\LogicalDisk(%s)\\Disk Write Bytes/sec"

#define PDH_NET "Network Interface"

#define PDH_NETPACKIN     "\\Network Interface(%s)\\Packets Received/sec"
#define PDH_NETPACKOUT    "\\Network Interface(%s)\\Packets Sent/sec"
#define PDH_NETPACKINERR  "\\Network Interface(%s)\\Packets Received Errors"
#define PDH_NETPACKOUTERR "\\Network Interface(%s)\\Packets Outbound Errors"
#define PDH_NETOCTIN	  "\\Network Interface(%s)\\Bytes Received/sec"
#define PDH_NETOCTOUT     "\\Network Interface(%s)\\Bytes Sent/sec"

#define UNINSTALL_KEY "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall" // SWConf, PatchConf

#ifndef HCOUNTER
#define HCOUNTER void*
#endif

#ifndef HQUERY
#define HQUERY void *
#endif

typedef struct {
	std::string instance_name;
	HCOUNTER h_Counter[10];
} ITEM;

typedef struct {
	bool isAlive;
	FILETIME ftKernel;
	FILETIME ftUser;
	LARGE_INTEGER qpcount;
} ProcessInfo;

std::vector<ITEM> init_disk(HQUERY *h_query);
std::vector<ITEM> init_network(HQUERY *h_query);

void collectData(HQUERY h_query);

int read_counter_large_int(HCOUNTER hcounter, long long *result);

void close_handle(HQUERY h_query);


#endif // CYGWIN

#endif //__CYGWIN_H__

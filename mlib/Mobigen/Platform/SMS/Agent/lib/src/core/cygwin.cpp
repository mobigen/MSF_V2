#include <stdio.h>

#ifdef CYGWIN

#include "pdh.h"
#include "pdhmsg.h"
#include <windows.h>
#include <iphlpapi.h>

#include "cygwin.h"


#ifdef WIN32_1
#define snprintf _snprintf
#define sleep(x) Sleep(x * 1000)
#endif // WIN32

int add_counter(HQUERY h_query, const char *fullCounterPath, HCOUNTER &phCounter)
{
	PDH_STATUS pdh_status;

	pdh_status = PdhAddCounter(h_query, fullCounterPath,
			0, &phCounter);
	if(pdh_status != ERROR_SUCCESS) {
		phCounter = NULL;
		return -1;
	}
	return 0;
}

char *get_instances(const char *object)
{
	PDH_STATUS pdh_status;
	char *instancelistbuf;
	DWORD instancelistsize = 0;
	char *counterlistbuf;
	DWORD counterlistsize = 0;

	/* Get necessary size of buffers */
	pdh_status = PdhEnumObjectItems(NULL, NULL, object, NULL,
			&counterlistsize, NULL, &instancelistsize,
			PERF_DETAIL_WIZARD, 0);
	/* 2k is dodgy and returns ERROR_SUCCESS even though the buffers were
	 * NULL */
	if(pdh_status == PDH_MORE_DATA || pdh_status == ERROR_SUCCESS) {
		instancelistbuf = (char *) malloc(instancelistsize * sizeof(TCHAR));
		counterlistbuf = (char *) malloc(counterlistsize * sizeof(TCHAR));

		if (instancelistbuf != NULL && counterlistbuf != NULL) {
			pdh_status = PdhEnumObjectItems(NULL, NULL, object,
					counterlistbuf, &counterlistsize,
					instancelistbuf, &instancelistsize,
					PERF_DETAIL_WIZARD, 0);

			if (pdh_status == ERROR_SUCCESS) {
				free(counterlistbuf); counterlistbuf = NULL;
				return instancelistbuf;
			}
		}
		if (counterlistbuf != NULL)
			free(counterlistbuf);
		if(instancelistbuf != NULL)
			free(instancelistbuf);
	}
	return NULL;
}

vector<string> get_instance_list(const char *object)
{
	char *thisinstance = NULL;
	char *instances = NULL;
	vector<string> list;

	instances = get_instances(object);
	if (instances == NULL)
		return list;

	//printf("instances [%s]\n", instances);

	for (thisinstance = instances; *thisinstance != 0;
			thisinstance += strlen(thisinstance) + 1) {
		/* Skip over the _Total item */
		if (strcmp(thisinstance,"_Total") == 0) continue;
		list.push_back( thisinstance );
	}
	free (instances); instances = NULL;
	return list;
}

int read_counter_large_int(HCOUNTER hcounter, long long *result)
{
	PDH_STATUS pdh_status;
	PDH_FMT_COUNTERVALUE item_buf;

	if(hcounter == NULL)
		return -1;

	pdh_status = PdhGetFormattedCounterValue(hcounter, PDH_FMT_LARGE, NULL,
			&item_buf);
	if(pdh_status != ERROR_SUCCESS) {
		return -1;
	}

	*result = item_buf.largeValue;
	return 0;
}

void init_item(ITEM *item) {
	item->instance_name = "";
	for (int i=0; i < 10; i++) {
		item->h_Counter[i] = NULL;
	}
}

void init_handle(HQUERY *h_query)
{
	*h_query = NULL;
	PdhOpenQuery(NULL, 0, &(*h_query));
}

void close_handle(HQUERY h_query) {
	if (h_query != NULL) {
		PdhCloseQuery(h_query);
		h_query = NULL;
	}
}

vector<ITEM> init_disk(HQUERY *h_query) 
{
	char tmp[BUFSIZ];
	vector<ITEM> itemList;
	vector<string> list;

	
	init_handle(h_query);

	list = get_instance_list( PDH_DISK );
	for(int i=0; i < list.size(); i++) {
		ITEM item;
		init_item(&item);

		item.instance_name = list[i];

		snprintf(tmp, sizeof(tmp), PDH_DISKIOREAD, list[i].c_str());
		add_counter(*h_query, tmp, item.h_Counter[0]);

		snprintf(tmp, sizeof(tmp), PDH_DISKIOWRITE, list[i].c_str());
		add_counter(*h_query, tmp, item.h_Counter[1]);

		itemList.push_back( item );
	}

	return itemList;
}


vector<ITEM> init_network(HQUERY *h_query) 
{
	char tmp[BUFSIZ];
	vector<ITEM> itemList;
	vector<string> list;

	
	init_handle(h_query);

	list = get_instance_list( PDH_NET );
	for(int i=0; i < list.size(); i++) {
		ITEM item;
		init_item(&item);



		snprintf(tmp, sizeof(tmp), PDH_NETPACKIN, list[i].c_str());
		add_counter(*h_query, tmp, item.h_Counter[0]);

		snprintf(tmp, sizeof(tmp), PDH_NETPACKOUT, list[i].c_str());
		add_counter(*h_query, tmp, item.h_Counter[1]);

		snprintf(tmp, sizeof(tmp), PDH_NETPACKINERR, list[i].c_str());
		add_counter(*h_query, tmp, item.h_Counter[2]);

		snprintf(tmp, sizeof(tmp), PDH_NETPACKOUTERR, list[i].c_str());
		add_counter(*h_query, tmp, item.h_Counter[3]);

		snprintf(tmp, sizeof(tmp), PDH_NETOCTIN, list[i].c_str());
		add_counter(*h_query, tmp, item.h_Counter[4]);

		snprintf(tmp, sizeof(tmp), PDH_NETOCTOUT, list[i].c_str());
		add_counter(*h_query, tmp, item.h_Counter[5]);

		item.instance_name = list[i];
		replace(item.instance_name.begin(), item.instance_name.end(), '_', '/');
		replace(item.instance_name.begin(), item.instance_name.end(), '[', '(');
		replace(item.instance_name.begin(), item.instance_name.end(), ']', ')');


		itemList.push_back( item );
	}

	return itemList;
}

void collectData(HQUERY h_query)
{
	PdhCollectQueryData(h_query);
}

#ifdef CYGWIN_TEST_MAIN

void getData(HQUERY h_query, vector<ITEM> itemlist)
{
	PDH_STATUS pdh_status;
	pdh_status = PdhCollectQueryData(h_query);

	if(pdh_status != ERROR_SUCCESS) {
		return;
	}

	printf("DISK\tread\twrite\n");
	for (int i=0; i < itemlist.size(); i++) {

		ITEM item = itemlist[i];

		long long read,write;
		read = write = 0;
		read_counter_large_int(item.h_Counter[0], &read); 
		read_counter_large_int(item.h_Counter[1], &write); 
		printf("%s\t%lld\t%lld\n", item.instance_name.c_str(), read, write);
	}
}

void getNetworkData(HQUERY h_query, vector<ITEM> itemlist)
{
	PDH_STATUS pdh_status;
	pdh_status = PdhCollectQueryData(h_query);

	if(pdh_status != ERROR_SUCCESS) {
		return;
	}

	printf("Instance\tPacketIn\tPacketOut\tPacketInError\tPacketOutError\tCollision\n");
	for (int i=0; i < itemlist.size(); i++) {

		ITEM item = itemlist[i];

		long long read,write,inerr,outerr,inoct,outoct;
		read = write = inerr = outerr = 0;
		read_counter_large_int(item.h_Counter[0], &read); 
		read_counter_large_int(item.h_Counter[1], &write); 
		read_counter_large_int(item.h_Counter[2], &inerr); 
		read_counter_large_int(item.h_Counter[3], &outerr); 
		read_counter_large_int(item.h_Counter[4], &inoct); 
		read_counter_large_int(item.h_Counter[5], &outoct); 
		printf("%s\t%lld\t%lld\t%lld\t%lld\t0\t%lld\t%lld\n", item.instance_name.c_str(), read, write, inerr, outerr, inoct,outoct);
	}
}
int main()
{
	HQUERY h_query = NULL;


	if (0) {
	vector<ITEM> itemList = init_disk(&h_query);

	getData(h_query, itemList);
	}

	if (1) {
		vector<ITEM> itemList = init_network(&h_query);
		getNetworkData(h_query, itemList);
	}

	return 0;
}

#endif // CYGWIN_TEST_MAIN

#endif // CYGWIN

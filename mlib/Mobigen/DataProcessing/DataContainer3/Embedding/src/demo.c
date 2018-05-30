#include <Python.h>
#include <time.h>
#include "DataContainer.h"

int
main(int argc, char *argv[])
{
	char buf[1024];
	PyObject *pModule;
	CDataContainer *pDC;

	Py_Initialize();

	pDC = new CDataContainer(".", "a", 4, 12,1, 1);
	pDC->Put("20061210120000", "1234567");
	pDC->Put("20061210130000", "1234567");
	pDC->Put("20071210120000", "1234567");
	pDC->Put("20061210130000", "1234567");
	pDC->Put("20061210120000", "1234567");
//	for (int i=0; i < 100; i++) { sprintf(buf, "%d", i);	pDC->Put("20061210120000", buf); }
/*
	pDC = new CDataContainer(".", true);
	DCDATA 	data;
	if(pDC->Get("20061210120000", 0, data))
		printf("%s %lld %s %lld %s\n", data.ftime, data.mtime, data.option, data.index, data.data);
//	if(pDC->GetLast(data)) 
//		printf("%s %lld %s %lld %s\n", data.ftime, data.mtime, data.option, data.index, data.data);

	while(pDC->Next(data)) 
	{
		printf("%s %lld %s %lld %s\n", data.ftime, data.mtime, data.option, data.index, data.data);
	}
*/
	delete(pDC);

	PyErr_Clear();
	Py_Finalize();
	return 0;
}

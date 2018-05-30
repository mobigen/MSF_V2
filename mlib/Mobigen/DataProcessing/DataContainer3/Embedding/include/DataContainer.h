#if !defined __DATA_CONTAINER_WAPPER_HEADER__
#define __DATA_CONTAINER_WAPPER_HEADER__

#include <Python.h>

typedef struct _TAG_DCDATA
{
	char * ftime;
	unsigned long long mtime;
	char * option;
	unsigned long long index;
	char * data;
	unsigned long long length;
} DCDATA;


class CDataContainer
{
private :
	PyObject * m_pModule;
	PyObject * m_pDataContainer;

public :
	CDataContainer(const char *strDir, const bool nonBlock = false);
	CDataContainer(const char *strDir, const char *cMode, const int nKeepHour, const int nFileTimeInterval, const int nBufSize, const int nAutoRecover, const bool nBlock = false);
	~CDataContainer();

	bool Next(DCDATA & data);
	bool GetLast(DCDATA & data);
	bool Get(const char * strFileTime, const int nIndex, DCDATA & data);
	void Put(const char * strFileTime, const char * strBuffer, const char * strOption = NULL );

	PyObject * Next();
	PyObject * GetLast();
	PyObject * Get(const char * strFileTime, const int nIndex);

	int		ErrorCheck();
};

#endif // __DATA_CONTAINER_WAPPER_HEADER__

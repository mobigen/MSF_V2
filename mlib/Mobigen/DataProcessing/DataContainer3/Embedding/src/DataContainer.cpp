#include "DataContainer.h"

CDataContainer::CDataContainer(const char *strDir, bool nonBlock /*= false */ )
{
	m_pModule = NULL;
	m_pDataContainer = NULL;

	m_pModule = PyImport_ImportModule("Mobigen.Archive.DataContainer2");
	if(m_pModule) PyErr_Print();

//	m_pDataContainer = PyObject_CallMethod(m_pModule, "DataContainer", "s", strDir);
	PyObject *pArgs = Py_None;
	pArgs = Py_BuildValue("{s:s,s:O}", "HomeDir", strDir, "NonBlock", PyBool_FromLong(nonBlock));
	m_pDataContainer = PyObject_CallMethod(m_pModule, "DataContainer", "O", pArgs);
	Py_DECREF(pArgs);

	if(m_pDataContainer) PyErr_Print();
}

CDataContainer::CDataContainer(const char *strDir, const char *cMode, const int nKeepHour, const int nFileTimeInterval,
							   const int nBufSize, const int nAutoRecover, const bool nonBlock /* = false */)
{
	m_pModule = NULL;
	m_pDataContainer = NULL;

	m_pModule = PyImport_ImportModule("Mobigen.Archive.DataContainer2");
	if(m_pModule) PyErr_Print();

	PyObject *pArgs = Py_None;
	pArgs = Py_BuildValue("{s:s,s:s,s:i,s:i,s:i,s:i,s:O}",
				 "HomeDir", strDir, "Mode", cMode, "KeepHour", nKeepHour, "FileTimeInterval", nFileTimeInterval,
                 "BufSize", nBufSize, "AutoRecover", nAutoRecover, "NonBlock", PyBool_FromLong(nonBlock));
	m_pDataContainer = PyObject_CallMethod(m_pModule, "DataContainer", "O", pArgs);
	Py_DECREF(pArgs);
	if(m_pDataContainer) PyErr_Print();
}

CDataContainer::~CDataContainer()
{
	Py_XDECREF(m_pDataContainer);
	Py_XDECREF(m_pModule);
}

void 
CDataContainer::Put(const char * strFileTime, const char * strBuffer, const char * strOption /* = NULL */)
{
	PyObject *pParam = NULL;
	PyObject *pValue = NULL;

	if(strOption == NULL )	
		pParam = Py_BuildValue("ss", strFileTime, strBuffer);
	else 
		pParam = Py_BuildValue("sss", strFileTime, strBuffer, strOption);

	pValue = PyObject_CallMethod(m_pDataContainer, "put", "O", pParam);
	Py_XDECREF(pParam);
	Py_XDECREF(pValue);
}

bool
CDataContainer::Get(const char * strFileTime, const int nIndex, DCDATA &retData)
{
	bool retValue = false;
	PyObject *pParam = NULL;
	PyObject *pValue = NULL;

	pParam = Py_BuildValue("si", strFileTime, nIndex);

	pValue = PyObject_CallMethod(m_pDataContainer, "get", "O", pParam);
	Py_XDECREF(pParam);

	if(pValue)
	{
		PyArg_ParseTuple(pValue, "sKsKs", &retData.ftime, &retData.mtime, &retData.option, &retData.index, &retData.data);
		retData.length = PyString_Size(PyTuple_GET_ITEM(pValue, 4));
		retValue = true;
	}

	Py_XDECREF(pValue);
	return retValue; 
}

bool
CDataContainer::GetLast(DCDATA &retData)
{
	bool retValue = false;
	PyObject *pValue = NULL;

	pValue = PyObject_CallMethod(m_pDataContainer, "getLast", "");

	if(pValue)
	{
		PyArg_ParseTuple(pValue, "sKsKs", &retData.ftime, &retData.mtime, &retData.option, &retData.index, &retData.data);
		retData.length = PyString_Size(PyTuple_GET_ITEM(pValue, 4));
		retValue = true;
	}

	Py_XDECREF(pValue);
	return retValue;
}

bool
CDataContainer::Next(DCDATA &retData)
{
	bool retValue = false;
	PyObject *pValue = NULL;

	pValue = PyObject_CallMethod(m_pDataContainer, "next", "");

	if(pValue)
	{
		PyArg_ParseTuple(pValue, "sKsKs", &retData.ftime, &retData.mtime, &retData.option, &retData.index, &retData.data);
		retData.length = PyString_GET_SIZE(PyTuple_GET_ITEM(pValue, 4));
		retValue = true;
	}

	Py_XDECREF(pValue);
	return retValue;
}

PyObject *
CDataContainer::Get(const char * strFileTime, const int nIndex)
{
	PyObject *pParam = NULL;

	pParam = Py_BuildValue("si", strFileTime, nIndex);

	return PyObject_CallMethod(m_pDataContainer, "get", "O", pParam);
}

PyObject *
CDataContainer::GetLast()
{
	return PyObject_CallMethod(m_pDataContainer, "getLast", "");
}

PyObject *
CDataContainer::Next()
{
	return PyObject_CallMethod(m_pDataContainer, "next", "");
}

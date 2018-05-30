

#ifndef __CCOLLECTORHEADER_H__
#define __CCOLLECTORHEADER_H__ 1

#include "CPatchConfCollector.h"
#include "CSWConfCollector.h"
#include "CCPUConfCollector.h"
#include "CMemoryConfCollector.h"
#include "CDiskConfCollector.h"
#include "CHostConfCollector.h"
#include "CIFConfCollector.h"
#include "CCPUPerfCollector.h"
#include "CCPULoadPerfCollector.h"
#include "CMemoryPerfCollector.h"
#include "CDiskPerfCollector.h"
#include "CDiskIOPerfCollector.h"
#include "CIFPerfCollector.h"
#include "CProcessPerfCollector.h"
#include "CTopCPUProcessPerfCollector.h"
#include "CTopMemoryProcessPerfCollector.h"
#include "CLogCheckCollector.h"
#include "CShellCommandCollector.h"
#include "CNetworkSessionCollector.h"
#include "CAgentConfCollector.h"
#include "CAlarmProcessor.h"
#include "CProcessHealthCollector.h"

#if defined(ORACLE_ENABLE)
#include "COraConfCollector.h"
#include "COraHitRatioCollector.h"
#include "COraTopSqlCollector.h"
#include "COraSessionCountCollector.h"
#include "COraDBLinkCollector.h"
#include "COraTableSpaceCollector.h"
#include "COraRollbackCollector.h"
#include "COraConfCollector.h"
#endif /* ORACLE_ENABLE */

#endif /* __CCOLLECTORHEADER_H__ */

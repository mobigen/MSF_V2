#!/bin/sh

if [ $# != 1 ]
then
	echo "\nUsage:\n\t $0 [start|stop|status]"
	exit 1
fi

AGENT_HOME=$HOME/mlib/Mobigen/Platform/SMS/Agent
export AGENT_HOME


# for oralce 

ORACLE_BASE=/opt/oracle/app/oracle
export ORACLE_BASE
ORACLE_HOME=$ORACLE_BASE/product/920
export ORACLE_HOME
ORACLE_SID=BEORA9
export ORACLE_SID
ORACLE_OWNER=oracle
export ORACLE_OWNER
ORACLE_LOG=$ORACLE_BASE/admin/BEORA9/bdump
export ORACLE_LOG
ORA_NLS33=$ORACLE_HOME/ocommon/nls/admin/data
export ORA_NLS33
TNS_ADMIN=/opt/oracle/app/oracle/product/920/network/admin
export TNS_ADMIN


PATH=/bin:/usr/bin:/usr/sbin:/usr/local/bin::$HOME/bin
export PATH
SHLIB_PATH=/usr/lib:$HOME/lib:$ORACLE_HOME/lib32:$ORACLE_HOME/lib:/usr/local/lib
export SHLIB_PATH


sc_start()
{
	pcnt=`ps -eaf | grep scagent | grep -v grep | wc -l`
	if [ $pcnt -eq 0 ]
	then
		$AGENT_HOME/bin/scagent.exe >/dev/null 2>/dev/null &
	else
		echo "scagent.exe already started!!"
	fi

	exit 0
}

sc_stop()
{
	pcnt=`ps -eaf | grep scagent | grep -v grep | wc -l`

	if [ $pcnt -eq 0 ]
	then
		echo "scagent.exe already Killed."
	else
		kill -9 `ps -eaf | grep scagent | grep -v grep | awk '{print $2}'`
		sc_status
	fi

	exit 0
}

sc_status()
{
	pcnt=`ps -eaf | grep scagent | grep -v grep | wc -l`

	if [ $pcnt -eq 0 ]
	then
		echo "scagent.exe not Running."
	else
		echo "scagent.exe Running."
	fi

	exit 0
}


case $1 in

	start)
		sc_start
		;;
	stop)
		sc_stop
		;;
	status)
		sc_status
		;;
	*)
		echo "unknown tag[$1]"
		exit 0
		;;
esac





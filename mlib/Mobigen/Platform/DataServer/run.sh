#!/bin/sh

PID_FILE=dataserver.pid

if [ -e $PID_FILE ]
then
	PID=`cat $PID_FILE`
else
	PID=''
fi

start()
{
	if [ -z $PID ]
	then
		echo 'start dataserver'
		python -O dataserver.py >& /dev/null &
	else
		echo 'dataserver is already running.'
	fi
}

stop()
{
	if [ -z $PID ]
	then
		echo 'dataserver is not running.'
	else
		echo 'stop dataserver'
		/bin/kill -9 $PID
		/bin/rm $PID_FILE
	fi
}

status()
{
	if [ -z $PID ]
	then
		echo 'dataserver is not running.'
	else
		echo 'dataserver is running. pid:'$PID
	fi
}


# Running
case $1 in
'start')
	start ;;

'stop')
	stop ;;

'status')
	status ;;
*)
	echo 'Usage: run.sh [start|stop|status]';
esac

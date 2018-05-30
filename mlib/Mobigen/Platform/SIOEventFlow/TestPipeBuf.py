#!/usr/bin/python
import select, subprocess

ps1 = subprocess.Popen( "ev1.py", shell=True, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)

ps2 = subprocess.Popen( "ev2.py", shell=True, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)

while True :
	readReady, tmp, tmp = select.select( [ps1.stdout], [], [], 1 )
	if len(readReady) == 0 :
		print "PB : no data read"
	else :
		line = ps1.stdout.readline()

		while True :
			tmp, writeReady, tmp = select.select( [], [ps2.stdin], [], 1 )
			if len(writeReady) == 0 :
				print "PB : no ready write"
			else :
				break

		print "PB : before write"
		ps2.stdin.write( line )
		ps2.stdin.flush()
		print "PB : after write"

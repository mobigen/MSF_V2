#!/usr/bin/python
import select, subprocess

ps1 = subprocess.Popen( "ev1.py", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
print "ev1.py pid=%s" % ps1.pid

ps11 = subprocess.Popen( "ev1.py", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
print "ev11.py pid=%s" % ps11.pid

ps2 = subprocess.Popen( "ev2.py", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
print "ev2.py pid=%s" % ps2.pid

while True :
	readReady, tmp, tmp = select.select( [ps1.stdout, ps11.stdout], [], [], 1 )
	print ps1.poll()
	print ps11.poll()
	if len(readReady) == 0 :
		print "no data read"
	else :
		ps2.stdin.write( ps1.stdout.readline() )
		ps2.stdin.flush()
		print ps2.stdout.readline()

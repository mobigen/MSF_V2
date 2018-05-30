#!/usr/bin/env python

import subprocess, time

pros = subprocess.Popen( "ev2.py", shell=True, bufsize=0, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
time.sleep(1)
print pros.poll()
pros.terminate()
time.sleep(1)
print pros.poll()
pros.terminate()
time.sleep(1)
print pros.poll()

#!/usr/bin/env python

import sys
import time

time.sleep(3)

msg = "file://s1\n"
sys.stdout.write(msg)
sys.stdout.flush()

sys.stderr.write(msg)
sys.stderr.flush()

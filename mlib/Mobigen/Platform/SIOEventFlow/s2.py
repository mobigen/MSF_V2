#!/usr/bin/env python

import sys

msg = "file://s2\n"
sys.stdout.write(msg)
sys.stdout.flush()

sys.stderr.write(msg)
sys.stderr.flush()

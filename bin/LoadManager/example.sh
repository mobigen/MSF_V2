#!/bin/sh
python example.py
sleep 1
echo file://conf/TEST.conf | python LoadManager.py testsubject conf/IrisManager.conf &
sleep 7
kill -9 $!

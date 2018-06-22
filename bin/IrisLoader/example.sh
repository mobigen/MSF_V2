#!/bin/sh
python create_table.py conf/IrisLoader.conf
sleep 1
echo file://data/k_20110616000000.dat | python IrisLoader.py IRIS conf/IrisLoader.conf & 
sleep 2
kill -9 $!

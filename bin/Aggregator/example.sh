#!/bin/sh
# data/test_file.csv

echo file://data/test_file.csv | python Aggregator.py TEST1 conf/Aggregator.conf &
sleep 1;
kill -9 $!

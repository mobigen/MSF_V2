#!/bin/sh
python SSHTailCollector.py TEST conf/SSHTailCollector.conf &

echo 'Sunny day sweepin the clouds away
On my way where the air is sweet
Can you tell how to get, how to get to Sesame street' > data/test_20180628.txt
echo 'Come and play, Everything is A-OK
Friendly neighbors there, that is where we meet
Can you tell me how to get, how to get to Sesame street' > data/test_20180629.txt

sleep 30
kill -9 $!

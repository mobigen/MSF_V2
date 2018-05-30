echo "SFProtocol Test Suite Stating...."
echo ""
echo "Function Test!!!"
echo "Protocol Type 6"
CTS.py -p6 localhost 9999
CUS.py -p6 localhost 9997
CS.py -p6

echo ""
echo "Protocol Type 1"
CTS.py -p1 localhost 9999
CUS.py -p1 localhost 9997
CS.py -p1

echo ""
echo "UUDP Test"
CUUS.py

echo ""
echo "Performance Test!!!"
echo "Protocol Type 6"
CTS-P.py -p6 localhost 9999
CS-P.py -p6

echo ""
echo "Protocol Type 1"
CTS-P.py -p1 localhost 9999
CS-P.py -p1

echo ""
echo "SFProtocol Test Suite End."

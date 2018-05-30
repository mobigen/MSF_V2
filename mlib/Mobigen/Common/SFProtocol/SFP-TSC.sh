CTC.py -p6 localhost 9999
CUC.py -p6 localhost 9998
echo ""
sleep 2
CTC.py -p1 localhost 9999
CUC.py -p1 localhost 9998
echo ""
sleep 2
CUUC.py

echo ""
sleep 2
CTC-P.py -p6 localhost 9999

echo ""
sleep 2
CTC-P.py -p1 localhost 9999

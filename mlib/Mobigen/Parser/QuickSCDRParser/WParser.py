#!/bin/env python
# -*- coding: cp949 -*-

import Mobigen.Common.Log as Log; Log.Init()

BINMAP = {}
BINMAP['0']="0000"; BINMAP['1']="0001"; BINMAP['2']="0010"; BINMAP['3']="0011";
BINMAP['4']="0100"; BINMAP['5']="0101"; BINMAP['6']="0110"; BINMAP['7']="0111";
BINMAP['8']="1000"; BINMAP['9']="1001"; BINMAP['A']="1010"; BINMAP['B']="1011";
BINMAP['C']="1100"; BINMAP['D']="1101"; BINMAP['E']="1110"; BINMAP['F']="1111";

def ToBinString(data) :
	data = data.upper()
	binList = []
	for ch in data : binList.append(BINMAP[ch])
	return "".join(binList)

def parseCellIdentifier(rawdata) :
	if(not rawdata) : return [-1, -1, -1]
	bin = ToBinString(rawdata)

	sector = int(bin[0:3], 2)
	rnc = int(bin[3:8], 2)
	nodeb = int(bin[8:16], 2)

	if (rnc == 14) :
		sector = 0
		nodeb = int ("%s%s" % (bin[8:16] , bin[0:3]) , 2)

	return [sector, rnc, nodeb]

QOSFILEDSIZE = [8,8,2,3,3,4,1,3,3,5,3,2,3,8,8,8,4,4,6,2,8,8,3,1,4,8,8]
def parseQOS(rawdata) :
	bin = ToBinString(rawdata)
	retList = []

	pos = 0
	for size in QOSFILEDSIZE :
		val = bin[pos:pos+size]
		if(not val) : val = None
		retList.append(val)
		pos = pos + size

	return retList

#type = 1 MS to Network
#type = 2 Network to MS
def parseQOSforPerson(rawdata, type=1) :
	if (not rawdata) :
		return [None] * 27

	retList = []

	qosList = parseQOS(rawdata)

	for i in range(len(qosList)) :
		retList.append(QOS2String(i, qosList[i], type))

	return retList 

qosValueMap = {}

qosValueMap[3] = {}
qosValueMap[3]['000'] = 'Subscribed delay class'
qosValueMap[3]['001'] = 'Delay class 1'
qosValueMap[3]['010'] = 'Delay class 2'
qosValueMap[3]['011'] = 'Delay class 3'
qosValueMap[3]['100'] = 'Delay class 4(best effort)'
qosValueMap[3]['111'] = 'Reserved'

qosValueMap[4] = {}
qosValueMap[4]['000'] = 'Subscribed reliability class'
qosValueMap[4]['001'] = 'Acknowledged GTP, LLC, and RLC; Protected data'
qosValueMap[4]['010'] = 'Unacknowleded GTP, Acknowledged LLC and RLC, Protected data'
qosValueMap[4]['011'] = 'Unacknowleded GTP and LLC, Acknowledged RLC, Protected data'
qosValueMap[4]['100'] = 'Unacknowleded GTP LLC and RLC, Protected data'
qosValueMap[4]['101'] = 'Unacknowleded GTP LLC and RLC, Unprotected data'
qosValueMap[4]['111'] = 'Reserved'

qosValueMap[5] = {}
qosValueMap[5]['0000'] = 'Subscribed peak throughput'
qosValueMap[5]['0001'] = 'Up to 1 000 octet/s'
qosValueMap[5]['0010'] = 'Up to 2 000 octet/s'
qosValueMap[5]['0011'] = 'Up to 4 000 octet/s'
qosValueMap[5]['0100'] = 'Up to 8 000 octet/s'
qosValueMap[5]['0101'] = 'Up to 16 000 octet/s'
qosValueMap[5]['0110'] = 'Up to 32 000 octet/s'
qosValueMap[5]['0111'] = 'Up to 64 000 octet/s'
qosValueMap[5]['1000'] = 'Up to 128 000 octet/s'
qosValueMap[5]['1001'] = 'Up to 256 000 octet/s'
qosValueMap[5]['1111'] = 'Reserved'

qosValueMap[7] = {}
qosValueMap[7]['000'] = 'Subscribed precedence'
qosValueMap[7]['001'] = 'High priority'
qosValueMap[7]['010'] = 'Normal Proiority'
qosValueMap[7]['011'] = 'Low priority'
qosValueMap[7]['111'] = 'Reserved'

qosValueMap[9] = {}
qosValueMap[9]['00000'] = 'Subscribed mean throughput'
qosValueMap[9]['00001'] = '100 octet/h'
qosValueMap[9]['00010'] = '200 octet/h'
qosValueMap[9]['00011'] = '500 octet/h'
qosValueMap[9]['00100'] = '1 000 octet/h'
qosValueMap[9]['00101'] = '2 000 octet/h'
qosValueMap[9]['00110'] = '5 000 octet/h'
qosValueMap[9]['00111'] = '10 000 octet/h'
qosValueMap[9]['01000'] = '20 000 octet/h'
qosValueMap[9]['01001'] = '50 000 octet/h'
qosValueMap[9]['01010'] = '100 000 octet/h'
qosValueMap[9]['01011'] = '200 000 octet/h'
qosValueMap[9]['01100'] = '500 000 octet/h'
qosValueMap[9]['01101'] = '1 000 000 octet/h'
qosValueMap[9]['01110'] = '2 000 000 octet/h'
qosValueMap[9]['01111'] = '5 000 000 octet/h'
qosValueMap[9]['10000'] = '10 000 000 octet/h'
qosValueMap[9]['10001'] = '20 000 000 octet/h'
qosValueMap[9]['10010'] = '50 000 000 octet/h'
qosValueMap[9]['11110'] = 'Reserved'
qosValueMap[9]['11111'] = 'Best effort'

qosValueMap[10] = {}
qosValueMap[10]['000'] = 'Subscribed traffic class'
qosValueMap[10]['001'] = 'Conversational class'
qosValueMap[10]['010'] = 'Streanming class'
qosValueMap[10]['011'] = 'Interactive class'
qosValueMap[10]['100'] = 'Background class'
qosValueMap[10]['111'] = 'Reserved'

qosValueMap[11] = {}
qosValueMap[11]['00'] = 'Subscribed delivery order'
qosValueMap[11]['01'] = "With delivery order('yes')"
qosValueMap[11]['10'] = "Without delivery order('no')"
qosValueMap[11]['11'] = 'Reserved'

qosValueMap[12] = {}
qosValueMap[12]['000'] = 'Subscribed delivery of erroneous SDUs'
qosValueMap[12]['001'] = "No detect('-')"
qosValueMap[12]['010'] = "Erroneous SDUs are delivered('yes')"
qosValueMap[12]['011'] = "Erroneous SDUs are delivered('no')"
qosValueMap[12]['111'] = 'Reserved'

qosValueMap[13] = {}
qosValueMap[13]['00000000'] = 'Subscribed maximum SDU size'
qosValueMap[13]['11111111'] = 'Reserved'
qosValueMap[13]['10010111'] = '1502 octets'
qosValueMap[13]['10011000'] = '1510 octets'
qosValueMap[13]['10011001'] = '1520 octets'

qosValueMap[14] = {}
qosValueMap[14]['00000000'] = 'Subscribed maximum bit rate for uplink'
qosValueMap[14]['00000001'] = 'The maximum bit rate is binary codedin 8 bits, using a granularity of 1kbps'
qosValueMap[14]['00111111'] = 'giving a range of values from 1 kbps to 63 kbps in 1 kbps increments.'
qosValueMap[14]['01000000'] = 'The maximum bit rate is 64 kbps +((the binary coded value in 8 bits - 01000000) * 8 kbps)'
qosValueMap[14]['01111111'] = 'giving a range of values from 64 kbps to 568 kbps in 8 kbps increments.'
qosValueMap[14]['10000000'] = 'The maximum bit rate is 576 kbps +((the binary coded value in 8 bits - 10000000) * 64 kbps)'
qosValueMap[14]['11111110'] = 'giving a range of values from 576 kbps to 8640 kbps in 64 kbps increments.'
qosValueMap[14]['11111111'] = '0 kbps'

qosValueMap[16] = {}
qosValueMap[16]['0000'] = 'Subscribed residual BER'
qosValueMap[16]['0001'] = '5 * 10_-2'
qosValueMap[16]['0010'] = '1 * 10_-2'
qosValueMap[16]['0011'] = '5 * 10_-3'
qosValueMap[16]['0100'] = '4 * 10_-3'
qosValueMap[16]['0101'] = '1 * 10_-3'
qosValueMap[16]['0110'] = '1 * 10_-4'
qosValueMap[16]['0111'] = '1 * 10_-5'
qosValueMap[16]['1000'] = '1 * 10_-6'
qosValueMap[16]['1001'] = '6 * 10_-8'
qosValueMap[16]['1111'] = 'Reserved'

qosValueMap[17] = {}
qosValueMap[17]['0000'] = 'Subscribed SDU error ratio'
qosValueMap[17]['0001'] = '1 * 10_-2'
qosValueMap[17]['0010'] = '7 * 10_-3'
qosValueMap[17]['0011'] = '1 * 10_-3'
qosValueMap[17]['0100'] = '1 * 10_-4'
qosValueMap[17]['0101'] = '1 * 10_-5'
qosValueMap[17]['0110'] = '1 * 10_-6'
qosValueMap[17]['0111'] = '1 * 10_-1'
qosValueMap[17]['1111'] = 'Reserved'

qosValueMap[18] = {}
qosValueMap[18]['000000'] = 'Subscribed transfer delay'
qosValueMap[18]['000001'] = 'The Transfer delay is  binary coded in 6bits, using a granularity of 10 ms'
qosValueMap[18]['001111'] = 'giving a range of values from 10 ms to 150 ms in 10 ms increments'
qosValueMap[18]['010000'] = 'The transfer delay is 200 ms + ((the binary coded value in 6bits - 010000) * 50 ms)'
qosValueMap[18]['011111'] = 'giving a range of values from 200 ms to 950 ms in 50ms increments'
qosValueMap[18]['100000'] = 'The transfer delay is 1000 ms + ((the binary coded value in 6bits - 100000) * 100 ms)'
qosValueMap[18]['111110'] = 'giving a range of values from 1000 ms to 4000 ms in 500ms increments'
qosValueMap[18]['111111'] = 'Reserved'

qosValueMap[23] = {}
qosValueMap[23]['0'] = 'Not optimised for signalling traffic'
qosValueMap[23]['1'] = 'Optimised for signalling traffic'

qosValueMap[24] = {}
qosValueMap[24]['0000'] = 'unknown'
qosValueMap[24]['0001'] = 'speech'

qosValueMap[25] = {}
qosValueMap[25]['00000000'] = 'Use the value indicated by the Maximum bit rate for downlink in octet 9'
qosValueMap[25]['00000001'] = 'Ignore the value indicated by the Maximum bit rate for downlink in octet 9'
qosValueMap[25]['01001010'] = 'The maximum bit rate is 8600kbps + ((the binary coded value in 8 bits) * 100 kbps), giving a range of values from 8700 kbps to 16000 kbps in 100kbps increments.'

qosValueMap[26] = {}
qosValueMap[26]['00000000'] = 'Use the value indicated by the Guaranteed bit rate for downlink in octet 13'
qosValueMap[26]['00000001'] = 'Ignore the value indicated by the Guaranteed bit rate for downlink in octet 13'
qosValueMap[26]['01001010'] = 'The maximum bit rate is 8600kbps + ((the binary coded value in 8 bits) * 100 kbps), giving a range of values from 8700 kbps to 16000 kbps in 100kbps increments.'

def QOS2String(index, value, type) :
	retValue = None

	if(value==None) : return value

	if type==2  :
		if index not in [23,24,25] : 
			if int(value, 2) == 0 :
				return "Reserved"
		elif index == 13 and value == "11111111" :
			return "Reserved"

	try : retValue =  qosValueMap[index][value]
	except : retValue = value
	return  retValue

def parseLAC(lacCode) :
	if (not lacCode) : return None
	hexLAC = int(lacCode, 16)
	mscID = (hexLAC & 0x0FF0) >> 4
	mscID = str(mscID + 201)
	return mscID

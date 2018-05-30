#!/bin/env python
# -*- coding: cp949 -*-

import sys
import types
import struct
from TLVReader import QTLVReader

###############################################################################
# ASN.1 Types
T_PRIMITIVE_MIN = 0
T_Boolean = 1
T_Integer = 2
T_String = 3
T_OctetString = 4
T_OctetStringR = 5
T_TimeStamp = 6
T_IPAddress = 7
T_ISDNAddressString = 8
T_Unknown = 9
T_PRIMITIVE_MAX = 9

T_CONSTRUCTOR_MIN = 10
T_SEQUENCE = 11
T_CHOICE = 12
T_SET = 13
T_SEQUENCEOF = 14
T_CONSTRUCTOR_MAX = 19

# ASN.1 Type Names
ASN1_OpName = {}
ASN1_OpName[T_Boolean] = "Boolean"
ASN1_OpName[T_Integer] = "Integer"
ASN1_OpName[T_String] = "String"
ASN1_OpName[T_OctetString] = "OctetString"
ASN1_OpName[T_OctetStringR] = "OctetStringR"
ASN1_OpName[T_TimeStamp] = "TimeStamp"
ASN1_OpName[T_IPAddress] = "IPAddress"
ASN1_OpName[T_ISDNAddressString] = "ISDNAddressString"
ASN1_OpName[T_Unknown] = "Unknown"
ASN1_OpName[T_SEQUENCE] = "SEQUENCE"
ASN1_OpName[T_CHOICE] = "CHOICE"
ASN1_OpName[T_SET] = "SET"
ASN1_OpName[T_SEQUENCEOF] = "SEQUENCEOF"
###############################################################################
S_recordType = "recordType"
S_networkInitiation = "networkInitiation"
S_servedIMSI = "servedIMSI"
S_servedIMEI = "servedIMEI"
S_SGSNAddress = "SGSNAddress"
S_msNetworkCapability = "msNetworkCapability"
S_routingArea = "routingArea"
S_locationAreaCode = "locationAreaCode"
S_cellIdentifier = "cellIdentifier"
S_chargingID = "chargingID"
S_GGSNAddressUsed = "GGSNAddressUsed"
S_accessPointNameNI = "accessPointNameNI"
S_pdpType = "pdpType"
S_ServedPDPAddress = "ServedPDPAddress"
S_qosRequested = "qosRequested"
S_qosNegotiated = "qosNegotiated"
S_dataVolumeGPRSUplink = "dataVolumeGPRSUplink"
S_dataVolumeGPRSDownlink = "dataVolumeGPRSDownlink"
S_changeCondition = "changeCondition"
S_changeTime = "changeTime"
S_recordOpeningTime = "recordOpeningTime"
S_duration = "duration"
S_sgsnChange = "sgsnChange"
S_causeForRecClosing = "causeForRecClosing"
S_gsm0408Cause = "gsm0408Cause"
S_gsm0902MapErrorValue = "gsm0902MapErrorValue"
S_ccittQ767Cause = "ccittQ767Cause"
S_networkSpecificCause = "networkSpecificCause"
S_manufacturerSpecificCause = "manufacturerSpecificCause"
S_recordSequenceNumber = "recordSequenceNumber"
S_nodeID = "nodeID"
S_recordExtensions = "recordExtensions"
S_localSequenceNumber = "localSequenceNumber"
S_apnSelectionMode = "apnSelectionMode"
S_accessPointNameOI = "accessPointNameOI"
S_servedMSISDN = "servedMSISDN"
S_chargingCharacteristics = "chargingCharacteristics"
S_systemType = "systemType"
S_sCFAddress = "sCFAddress"
S_serviceKey = "serviceKey"
S_defaultTransactionHandling = "defaultTransactionHandling"
S_cAMELAccessPointNameNI = "cAMELAccessPointNameNI"
S_cAMELAccessPointNameOI = "cAMELAccessPointNameOI"
S_numberOfDPEncountered = "numberOfDPEncountered"
S_levelOfCAMELService = "levelOfCAMELService"
S_freeFormatData = "freeFormatData"
S_fFDAppendIndicator = "fFDAppendIndicator"
S_rNCUnsentDownlinkVolume = "rNCUnsentDownlinkVolume"
S_chChSelectionMode = "chChSelectionMode"
S_dynamicAddressFlag = "dynamicAddressFlag"
S_iPBinV4Address = "iPBinV4Address"
S_iPTextV4Address = "iPTextV4Address"
S_IPAddress = "IPAddress"
S_ChangeOfCharCondition = "ChangeOfCharCondition"
S_ListOfTrafficVolumes = "ListOfTrafficVolumes"
S_Diagnostics = "Diagnostics"
S_CAMELInformationPDP = "CAMELInformationPDP"
S_GGSNAddress = "GGSNAddress"
S_sgsnPLMNIdentifier = "sgsnPLMNIdentifier"
S_SGSNPDPRecord = "SGSNPDPRecord"
S_GGSNPDPRecord = "GGSNPDPRecord"
###############################################################################
# 3GPP TS32.215 Parsing Rules
RULE_IPAddress = {}
RULE_PDPAddress = {}
RULE_ChangeOfCharCondition = {}
RULE_ChangeOfCharConditionOf = {}
RULE_Diagnostics = {}
RULE_CAMELInformationPDP = {}
RULE_SGSNPDPRecord = {}
RULE_GGSNPDPRecord = {}
RULE_UnknownRecord = {}
RULE_RootRule = {}
###############################################################################
RULE_IPAddress[0x80] = [ S_iPBinV4Address, T_IPAddress, None, True ]
RULE_IPAddress[0x82] = [ S_iPTextV4Address, T_String, None, True ]
###############################################################################
RULE_PDPAddress[0xA0] = [ S_IPAddress, T_CHOICE, RULE_IPAddress, True ]
###############################################################################
RULE_ChangeOfCharCondition[0x81] = [ S_qosRequested, T_OctetString, None, True ]
RULE_ChangeOfCharCondition[0x82] = [ S_qosNegotiated, T_OctetString, None, True ]
RULE_ChangeOfCharCondition[0x83] = [ S_dataVolumeGPRSUplink, T_Integer, None, True ]
RULE_ChangeOfCharCondition[0x84] = [ S_dataVolumeGPRSDownlink, T_Integer, None, True ]
RULE_ChangeOfCharCondition[0x85] = [ S_changeCondition, T_Integer, None, True ]
RULE_ChangeOfCharCondition[0x86] = [ S_changeTime, T_TimeStamp, None, True ]
###############################################################################
RULE_ChangeOfCharConditionOf[0x30] = [ S_ChangeOfCharCondition, T_SEQUENCE, RULE_ChangeOfCharCondition, True ]
###############################################################################
RULE_Diagnostics[0x80] = [ S_gsm0408Cause, T_Integer, None, True ]
RULE_Diagnostics[0x81] = [ S_gsm0902MapErrorValue, T_Integer, None, True ]
RULE_Diagnostics[0x82] = [ S_ccittQ767Cause, T_Integer, None, True ]
RULE_Diagnostics[0xA3] = [ S_networkSpecificCause, T_Unknown, None, True ]
RULE_Diagnostics[0x84] = [ S_manufacturerSpecificCause, T_Unknown, None, True ]
###############################################################################
RULE_CAMELInformationPDP[0x81] = [ S_sCFAddress, T_OctetStringR, None, True ]
RULE_CAMELInformationPDP[0x82] = [ S_serviceKey, T_Integer, None, True ]
RULE_CAMELInformationPDP[0x83] = [ S_defaultTransactionHandling, T_Integer, None, True ]
RULE_CAMELInformationPDP[0x84] = [ S_cAMELAccessPointNameNI, T_String, None, True ]
RULE_CAMELInformationPDP[0x85] = [ S_cAMELAccessPointNameOI, T_String, None, True ]
RULE_CAMELInformationPDP[0x86] = [ S_numberOfDPEncountered, T_Integer, None, True ]
RULE_CAMELInformationPDP[0x87] = [ S_levelOfCAMELService, T_OctetString, None, True ]
RULE_CAMELInformationPDP[0x88] = [ S_freeFormatData, T_OctetString, None, True ]
RULE_CAMELInformationPDP[0x89] = [ S_fFDAppendIndicator, T_Boolean, None, True ]
###############################################################################
RULE_SGSNPDPRecord[0x80] = [ S_recordType, T_Integer, None, True ]
RULE_SGSNPDPRecord[0x81] = [ S_networkInitiation, T_Boolean, None, True ]
RULE_SGSNPDPRecord[0x83] = [ S_servedIMSI, T_OctetStringR, None, True ]
RULE_SGSNPDPRecord[0x84] = [ S_servedIMEI, T_OctetStringR, None, True ]
RULE_SGSNPDPRecord[0xA5] = [ S_SGSNAddress, T_CHOICE, RULE_IPAddress, True ]
RULE_SGSNPDPRecord[0x86] = [ S_msNetworkCapability, T_OctetString, None, True ]
RULE_SGSNPDPRecord[0x87] = [ S_routingArea, T_OctetString, None, True ]
RULE_SGSNPDPRecord[0x88] = [ S_locationAreaCode, T_OctetString, None, True ]
RULE_SGSNPDPRecord[0x89] = [ S_cellIdentifier, T_OctetString, None, True ]
RULE_SGSNPDPRecord[0x8A] = [ S_chargingID, T_Integer, None, True ]
RULE_SGSNPDPRecord[0xAB] = [ S_GGSNAddressUsed, T_CHOICE, RULE_IPAddress, True ]
RULE_SGSNPDPRecord[0x8C] = [ S_accessPointNameNI, T_String, None, True ]
RULE_SGSNPDPRecord[0x8D] = [ S_pdpType, T_OctetString, None, True ]
RULE_SGSNPDPRecord[0xAE] = [ S_ServedPDPAddress, T_CHOICE, RULE_PDPAddress, True ]
RULE_SGSNPDPRecord[0xAF] = [ S_ListOfTrafficVolumes, T_SEQUENCEOF, RULE_ChangeOfCharConditionOf, False ]
RULE_SGSNPDPRecord[0x90] = [ S_recordOpeningTime, T_TimeStamp, None, True ]
RULE_SGSNPDPRecord[0x91] = [ S_duration, T_Integer, None, True ]
RULE_SGSNPDPRecord[0x92] = [ S_sgsnChange, T_Boolean, None, True ]
RULE_SGSNPDPRecord[0x93] = [ S_causeForRecClosing, T_Integer, None, True ]
RULE_SGSNPDPRecord[0xB4] = [ S_Diagnostics, T_CHOICE, RULE_Diagnostics, False ]
RULE_SGSNPDPRecord[0x95] = [ S_recordSequenceNumber, T_Integer, None, True ]
RULE_SGSNPDPRecord[0x96] = [ S_nodeID, T_String, None, True ]
RULE_SGSNPDPRecord[0x97] = [ S_recordExtensions, T_Unknown, None, True ]
RULE_SGSNPDPRecord[0x98] = [ S_localSequenceNumber, T_Integer, None, True ]
RULE_SGSNPDPRecord[0x99] = [ S_apnSelectionMode, T_Integer, None, True ]
RULE_SGSNPDPRecord[0x9A] = [ S_accessPointNameOI, T_String, None, True ]
RULE_SGSNPDPRecord[0x9B] = [ S_servedMSISDN, T_ISDNAddressString, None, True ]
RULE_SGSNPDPRecord[0x9C] = [ S_chargingCharacteristics, T_OctetString, None, True ]
RULE_SGSNPDPRecord[0x9D] = [ S_systemType, T_Integer, None, True ]
RULE_SGSNPDPRecord[0xBE] = [ S_CAMELInformationPDP, T_SET, RULE_CAMELInformationPDP, False ]
RULE_SGSNPDPRecord[0x9F1F] = [ S_rNCUnsentDownlinkVolume, T_Integer, None, True ]
RULE_SGSNPDPRecord[0x9F20] = [ S_chChSelectionMode, T_Integer, None, True ]
RULE_SGSNPDPRecord[0x9F21] = [ S_dynamicAddressFlag, T_Boolean, None, True ]
###############################################################################
RULE_GGSNPDPRecord[0x80] = [ S_recordType, T_Integer, None, True ]
RULE_GGSNPDPRecord[0x81] = [ S_networkInitiation, T_Boolean, None, True ]
RULE_GGSNPDPRecord[0x83] = [ S_servedIMSI, T_OctetStringR, None, True ]
RULE_GGSNPDPRecord[0xA4] = [ S_GGSNAddress, T_CHOICE, RULE_IPAddress, True ]
RULE_GGSNPDPRecord[0x85] = [ S_chargingID, T_Integer, None, True ]
RULE_GGSNPDPRecord[0xA6] = [ S_SGSNAddress, T_SEQUENCEOF, RULE_IPAddress, True ]
RULE_GGSNPDPRecord[0x87] = [ S_accessPointNameNI, T_String, None, True ]
RULE_GGSNPDPRecord[0x88] = [ S_pdpType, T_OctetString, None, True ]
RULE_GGSNPDPRecord[0xA9] = [ S_ServedPDPAddress, T_CHOICE, RULE_PDPAddress, True ]
RULE_GGSNPDPRecord[0x8B] = [ S_dynamicAddressFlag, T_Boolean, None, True ]
RULE_GGSNPDPRecord[0xAC] = [ S_ListOfTrafficVolumes, T_SEQUENCEOF, RULE_ChangeOfCharConditionOf, False ]
RULE_GGSNPDPRecord[0x8D] = [ S_recordOpeningTime, T_TimeStamp, None, True ]
RULE_GGSNPDPRecord[0x8E] = [ S_duration, T_Integer, None, True ]
RULE_GGSNPDPRecord[0x8F] = [ S_causeForRecClosing, T_Integer, None, True ]
RULE_GGSNPDPRecord[0xB0] = [ S_Diagnostics, T_CHOICE, RULE_Diagnostics, False ]
RULE_GGSNPDPRecord[0x91] = [ S_recordSequenceNumber, T_Integer, None, True ]
RULE_GGSNPDPRecord[0x92] = [ S_nodeID, T_String, None, True ]
RULE_GGSNPDPRecord[0x93] = [ S_recordExtensions, T_Unknown, None, True ]
RULE_GGSNPDPRecord[0x94] = [ S_localSequenceNumber, T_Integer, None, True ]
RULE_GGSNPDPRecord[0x95] = [ S_apnSelectionMode, T_Integer, None, True ]
RULE_GGSNPDPRecord[0x96] = [ S_servedMSISDN, T_ISDNAddressString, None, True ]
RULE_GGSNPDPRecord[0x97] = [ S_chargingCharacteristics, T_OctetString, None, True ]
RULE_GGSNPDPRecord[0x98] = [ S_chChSelectionMode, T_Integer, None, True ]
RULE_GGSNPDPRecord[0x9B] = [ S_sgsnPLMNIdentifier, T_OctetStringR, None, True ]
###############################################################################
RULE_RootRule[0x12] = [ S_SGSNPDPRecord, T_SET, RULE_SGSNPDPRecord, False ]
RULE_RootRule[0x13] = [ S_GGSNPDPRecord, T_SET, RULE_GGSNPDPRecord, False ]
###############################################################################
ByteHexStr = [ '00', '01', '02', '03', '04', '05', '06', '07', \
	'08', '09', '0A', '0B', '0C', '0D', '0E', '0F', \
	'10', '11', '12', '13', '14', '15', '16', '17', \
	'18', '19', '1A', '1B', '1C', '1D', '1E', '1F', \
	'20', '21', '22', '23', '24', '25', '26', '27', \
	'28', '29', '2A', '2B', '2C', '2D', '2E', '2F', \
	'30', '31', '32', '33', '34', '35', '36', '37', \
	'38', '39', '3A', '3B', '3C', '3D', '3E', '3F', \
	'40', '41', '42', '43', '44', '45', '46', '47', \
	'48', '49', '4A', '4B', '4C', '4D', '4E', '4F', \
	'50', '51', '52', '53', '54', '55', '56', '57', \
	'58', '59', '5A', '5B', '5C', '5D', '5E', '5F', \
	'60', '61', '62', '63', '64', '65', '66', '67', \
	'68', '69', '6A', '6B', '6C', '6D', '6E', '6F', \
	'70', '71', '72', '73', '74', '75', '76', '77', \
	'78', '79', '7A', '7B', '7C', '7D', '7E', '7F', \
	'80', '81', '82', '83', '84', '85', '86', '87', \
	'88', '89', '8A', '8B', '8C', '8D', '8E', '8F', \
	'90', '91', '92', '93', '94', '95', '96', '97', \
	'98', '99', '9A', '9B', '9C', '9D', '9E', '9F', \
	'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', \
	'A8', 'A9', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', \
	'B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', \
	'B8', 'B9', 'BA', 'BB', 'BC', 'BD', 'BE', 'BF', \
	'C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', \
	'C8', 'C9', 'CA', 'CB', 'CC', 'CD', 'CE', 'CF', \
	'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', \
	'D8', 'D9', 'DA', 'DB', 'DC', 'DD', 'DE', 'DF', \
	'E0', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', \
	'E8', 'E9', 'EA', 'EB', 'EC', 'ED', 'EE', 'EF', \
	'F0', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', \
	'F8', 'F9', 'FA', 'FB', 'FC', 'FD', 'FE', 'FF' ]

RevHexStr = [ '00', '10', '20', '30', '40', '50', '60', '70', \
	'80', '90', 'A0', 'B0', 'C0', 'D0', 'E0', 'F0', \
	'01', '11', '21', '31', '41', '51', '61', '71', \
	'81', '91', 'A1', 'B1', 'C1', 'D1', 'E1', 'F1', \
	'02', '12', '22', '32', '42', '52', '62', '72', \
	'82', '92', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', \
	'03', '13', '23', '33', '43', '53', '63', '73', \
	'83', '93', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', \
	'04', '14', '24', '34', '44', '54', '64', '74', \
	'84', '94', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', \
	'05', '15', '25', '35', '45', '55', '65', '75', \
	'85', '95', 'A5', 'B5', 'C5', 'D5', 'E5', 'F5', \
	'06', '16', '26', '36', '46', '56', '66', '76', \
	'86', '96', 'A6', 'B6', 'C6', 'D6', 'E6', 'F6', \
	'07', '17', '27', '37', '47', '57', '67', '77', \
	'87', '97', 'A7', 'B7', 'C7', 'D7', 'E7', 'F7', \
	'08', '18', '28', '38', '48', '58', '68', '78', \
	'88', '98', 'A8', 'B8', 'C8', 'D8', 'E8', 'F8', \
	'09', '19', '29', '39', '49', '59', '69', '79', \
	'89', '99', 'A9', 'B9', 'C9', 'D9', 'E9', 'F9', \
	'0A', '1A', '2A', '3A', '4A', '5A', '6A', '7A', \
	'8A', '9A', 'AA', 'BA', 'CA', 'DA', 'EA', 'FA', \
	'0B', '1B', '2B', '3B', '4B', '5B', '6B', '7B', \
	'8B', '9B', 'AB', 'BB', 'CB', 'DB', 'EB', 'FB', \
	'0C', '1C', '2C', '3C', '4C', '5C', '6C', '7C', \
	'8C', '9C', 'AC', 'BC', 'CC', 'DC', 'EC', 'FC', \
	'0D', '1D', '2D', '3D', '4D', '5D', '6D', '7D', \
	'8D', '9D', 'AD', 'BD', 'CD', 'DD', 'ED', 'FD', \
	'0E', '1E', '2E', '3E', '4E', '5E', '6E', '7E', \
	'8E', '9E', 'AE', 'BE', 'CE', 'DE', 'EE', 'FE', \
	'0F', '1F', '2F', '3F', '4F', '5F', '6F', '7F', \
	'8F', '9F', 'AF', 'BF', 'CF', 'DF', 'EF', 'FF' ]
###############################################################################

class InvalidSCDRException(Exception) : 
	def __init__(self) :
		Exception.__init__(self)

class UnknownTypeException(Exception) :
	def __init__(self, type) :
		Exception.__init__(self)
		self.type = type

class UnknownTagException(Exception) : 
	def __init__(self, tag, value) :
		Exception.__init__(self)
		self.tag = tag
		self.value = value	

class QASNParser :
	def __init__(self, debug = False) :
		self.dbgFlag = debug
		self.dbgDepth = 0
		self.parseStack = []

	def ToInteger(self, length, value) :
		if(length == 1) : format =  'B'
		elif(length == 2) : format =  'H'
		elif(length == 3) :
			value = "\0" + value
			format =  'I'
		elif(length == 4) : format =  'I'
		elif(length == 5) :
			value = value[1:]
			format = 'L'
		return struct.unpack(">%s" % format, value)[0]

	def ToIPAddress(self, value) :
		ip = "%s.%s.%s.%s" % \
			( ord(value[0]), ord(value[1]), ord(value[2]), ord(value[3]))
		return ip

	def ToISDNAddressString(self, length, value) :
		bufString = ByteHexStr[ord(value[0])]
		for i in xrange(1, length) :
			bufString += RevHexStr[ord(value[i])]
		if (bufString[-1] =='F') :
			return bufString[:-1]
		else :
			return bufString

	def ToOctetStringR(self, length, value) :
		bufString = ""
		for i in xrange(length) :
			bufString += RevHexStr[ord(value[i])]
		if (bufString[-1] =='F') :
			return bufString[:-1]
		else :
			return bufString

	def ToOctetString(self, length, value) :
		bufString = ""
		for i in xrange(length) :
			bufString += ByteHexStr[ord(value[i])]
		return bufString

	def ToTimeStamp(self, length, value) :
		bufString = "20"
		if length > 6 :
			length = 6
		for i in xrange(length) :
			bufString += ByteHexStr[ord(value[i])]
		return bufString

	def ToString(self, value) :
		return str(value)

	def ParseCore(self, retDict, ruleDict, tag, length, value) :
		try :
			tagName = ruleDict[tag][0]
			op = ruleDict[tag][1]
			isBackTrack = ruleDict[tag][3]
		except :
			raise UnknownTagException(tag, value)

		# push current tag name to parsing stack
		if isBackTrack :
			self.parseStack.append(tagName)

		if (op >= T_CONSTRUCTOR_MIN) and (op <= T_CONSTRUCTOR_MAX) :
			###################################################################
			#if self.dbgFlag :
			#	sys.stdout.write("%s%s(0x%04X,%d,%s) = {\n" % \
			#		("  "*self.dbgDepth, tagName, tag, length, ASN1_OpName[op]))
			#	self.dbgDepth += 1
			###################################################################

			if (op == T_SEQUENCE) or (op == T_CHOICE) or (op == T_SET) :
				# traverse through sub fields
				subRule = ruleDict[tag][2]
				reader = QTLVReader(value, QTLVReader.STRING_MODE)
				for subTag, subLen, subVal in reader :
					self.ParseCore(retDict, subRule, subTag, subLen, subVal)
			elif (op == T_SEQUENCEOF) :
				# traverse through sub fields
				subRule = ruleDict[tag][2]
				reader = QTLVReader(value, QTLVReader.STRING_MODE)
				for subTag, subLen, subVal in reader :
					# push index key
					idxCount = reader.getRecCount()
					idxStr = "%s[%d]" % (tagName, idxCount-1)
					self.parseStack.append(idxStr)
					# process sub node
					self.ParseCore(retDict, subRule, subTag, subLen, subVal)
					# pop index key
					self.parseStack.pop()
					#
				# put count value ino the result
				if tagName in retDict :
					retDict[tagName] = str(reader.getRecCount())

				##############################################################
				#if self.dbgFlag :
				#	sys.stdout.write("%s = %d\n" % (tagName, reader.getRecCount()))
				##############################################################

			###################################################################
			#if self.dbgFlag :
			#	self.dbgDepth -= 1
			#	sys.stdout.write("%s} (%s=%d)\n" % \
			#		("  "*self.dbgDepth, tagName, reader.getRecCount()))
			###################################################################
		elif (op >= T_PRIMITIVE_MIN) and (op <= T_PRIMITIVE_MAX) :
			# we've reached leaf node of parse tree
			# generate unique parsing key from the current parsing stack
			UniqueKeyStr ="/".join(self.parseStack)
			# check if we have matched data field for the unique key
			if UniqueKeyStr not in retDict :
				# pop current tag name from parsing stack
				if isBackTrack :
					self.parseStack.pop()
				return

			# get the result value
			resStr = None
			if (op == T_ISDNAddressString) :
				resStr = self.ToISDNAddressString(length, value)
			elif (op == T_TimeStamp) :
				resStr = self.ToTimeStamp(length, value)
			elif (op == T_Boolean) :
				if(self.ToInteger(length, value)) :
					resStr = "true" 
				else :
					resStr = "false"
			elif (op == T_Integer) :
				tmpVal = self.ToInteger(length, value)
				resStr = str(tmpVal)
			elif (op == T_String) :
				resStr = self.ToString(value)
			elif (op == T_OctetString) :
				resStr = self.ToOctetString(length, value)
			elif (op == T_OctetStringR) :
				resStr = self.ToOctetStringR(length, value)
			elif (op == T_IPAddress) :
				resStr = self.ToIPAddress(value)
			elif (op == T_Unknown) :
				resStr = self.ToOctetString(length, value)

			###################################################################
			#if self.dbgFlag :
			#	sys.stdout.write("%s = %s\n" % (UniqueKeyStr, resStr))
			###################################################################

			###################################################################
			#if self.dbgFlag :
			#	sys.stdout.write("%s%s(0x%04X,%d,%s) = \'%s\'\n" % \
			#		("  "*self.dbgDepth, tagName, tag, length, ASN1_OpName[op], resStr))
			###################################################################

			# put the result value
			retDict[UniqueKeyStr] = resStr
		else :
			# undefined operation!!
			# normally, this should not happen (parsing configuration error)
			pass

		#######################################################################
		# pop current tag name from parsing stack
		if isBackTrack :
			self.parseStack.pop()
		#######################################################################

		return

	def Parse(self, tag, length, value, retDict) :
		# parse record type field
		recordTypeTag = ord(value[0])
		recordTypeLen = ord(value[1])
		if (recordTypeTag == 0x80) and (recordTypeLen == 1) :
			recordType = ord(value[2])
		else :
			raise InvalidSCDRException()

		if (recordType != 0x12) and (recordType != 0x13) :
			raise UnknownTypeException(recordType)

		#if self.dbgFlag :
		#	self.dbgDepth = 0

		self.ParseCore(retDict, RULE_RootRule, recordType, length, value)

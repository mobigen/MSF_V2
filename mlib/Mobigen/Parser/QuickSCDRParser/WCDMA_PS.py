# ASN.1 Types
T_Boolean = 1
T_Integer = 2
T_String = 3
T_OctetString = 4
T_OctetStringR = 5
T_TimeStamp = 6
T_IPAddress = 7
T_ISDNAddressString = 8
T_Unknown = 9
T_SEQUENCE = 11
T_CHOICE = 12
T_SET = 13
T_SEQUENCEOF = 14

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

# 3GPP TS32.215 Parsing Rules
RULE_IPAddress = {}
RULE_ServedPDPAddress = {}
RULE_ChangeOfCharCondition = {}
RULE_ChangeOfCharConditionOf = {}
RULE_Diagnostics = {}
RULE_DiagnosticsR = {}
RULE_CAMELInformationPDP = {}
RULE_SGSNPDPRecord = {}
RULE_GGSNPDPRecord = {}
RULE_UnknownRecord = {}
RULE_RootRule = {}

RULE_IPAddress[0x80] = [ "iPBinV4Address", T_IPAddress ]
RULE_IPAddress[0x82] = [ "iPTextV4Address", T_String ]

RULE_ServedPDPAddress[0xA0] = [ "ServedPDPAddress", T_CHOICE, RULE_IPAddress ]

RULE_ChangeOfCharCondition[0x81] = [ "qosRequested", T_OctetString ]
RULE_ChangeOfCharCondition[0x82] = [ "qosNegotiated", T_OctetString ]
RULE_ChangeOfCharCondition[0x83] = [ "dataVolumeGPRSUplink", T_Integer ]
RULE_ChangeOfCharCondition[0x84] = [ "dataVolumeGPRSDownlink", T_Integer ]
RULE_ChangeOfCharCondition[0x85] = [ "changeCondition", T_Integer ]
RULE_ChangeOfCharCondition[0x86] = [ "changeTime", T_TimeStamp ]

RULE_ChangeOfCharConditionOf[0x30] = [ "changeOfCharCondition", T_SEQUENCE, RULE_ChangeOfCharCondition ]

RULE_Diagnostics[0x80] = [ "gsm0408Cause", T_Integer ]
RULE_Diagnostics[0x81] = [ "gsm0902MapErrorValue", T_Integer ]
RULE_Diagnostics[0x82] = [ "ccittQ767Cause", T_Integer ]
RULE_Diagnostics[0xA3] = [ "networkSpecificCause", T_Unknown, None ]
RULE_Diagnostics[0x84] = [ "manufacturerSpecificCause", T_Unknown, None ]

RULE_DiagnosticsR[0xA3] = [ "Diagnostics", T_CHOICE, RULE_Diagnostics ]

RULE_CAMELInformationPDP[0x81] = [ "sCFAddress", T_OctetStringR ]
RULE_CAMELInformationPDP[0x82] = [ "serviceKey", T_Integer ]
RULE_CAMELInformationPDP[0x83] = [ "defaultTransactionHandling", T_Integer ]
RULE_CAMELInformationPDP[0x84] = [ "cAMELAccessPointNameNI", T_String ]
RULE_CAMELInformationPDP[0x85] = [ "cAMELAccessPointNameOI", T_String ]
RULE_CAMELInformationPDP[0x86] = [ "numberOfDPEncountered", T_Integer ]
RULE_CAMELInformationPDP[0x87] = [ "levelOfCAMELService", T_OctetString ]
RULE_CAMELInformationPDP[0x88] = [ "freeFormatData", T_OctetString ]
RULE_CAMELInformationPDP[0x89] = [ "fFDAppendIndicator", T_Boolean ]

RULE_SGSNPDPRecord[0x80] = [ "RecordType", T_Integer ]
RULE_SGSNPDPRecord[0x81] = [ "NetworkInitiation", T_Boolean ]
RULE_SGSNPDPRecord[0x83] = [ "ServedIMSI", T_OctetStringR ]
RULE_SGSNPDPRecord[0x84] = [ "ServedIMEI", T_OctetString ]
RULE_SGSNPDPRecord[0xA5] = [ "SGSNAddress", T_CHOICE, RULE_IPAddress ]
RULE_SGSNPDPRecord[0x86] = [ "MSNetworkCapability", T_OctetString ]
RULE_SGSNPDPRecord[0x87] = [ "RoutingArea", T_OctetString ]
RULE_SGSNPDPRecord[0x88] = [ "LocationAreaCode", T_OctetString ]
RULE_SGSNPDPRecord[0x89] = [ "CellIdentifier", T_OctetString ]
RULE_SGSNPDPRecord[0x8A] = [ "ChargingID", T_Integer ]
RULE_SGSNPDPRecord[0xAB] = [ "GGSNAddress", T_CHOICE, RULE_IPAddress ]
RULE_SGSNPDPRecord[0x8C] = [ "AccessPointNameNI", T_String ]
RULE_SGSNPDPRecord[0x8D] = [ "PDPType", T_OctetString ]
RULE_SGSNPDPRecord[0xAE] = [ "ServedPDPAddress", T_CHOICE, RULE_ServedPDPAddress ]
RULE_SGSNPDPRecord[0xAF] = [ "ListOfTrafficVolumes", T_SEQUENCEOF, RULE_ChangeOfCharConditionOf ]
RULE_SGSNPDPRecord[0x90] = [ "RecordOpeningTime", T_TimeStamp ]
RULE_SGSNPDPRecord[0x91] = [ "Duration", T_Integer ]
RULE_SGSNPDPRecord[0x92] = [ "SGSNChange", T_Boolean ]
RULE_SGSNPDPRecord[0x93] = [ "CauseForRecClosing", T_Integer ]
RULE_SGSNPDPRecord[0xB4] = [ "Diagnostics", T_CHOICE, RULE_Diagnostics ]
RULE_SGSNPDPRecord[0x95] = [ "RecordSequenceNumber", T_Integer ]
RULE_SGSNPDPRecord[0x96] = [ "NodeID", T_String ]
RULE_SGSNPDPRecord[0x97] = [ "RecordExtensions", T_Unknown, None ]
RULE_SGSNPDPRecord[0x98] = [ "LocalSequenceNumber", T_Integer ]
RULE_SGSNPDPRecord[0x99] = [ "APNSelectionMode", T_Integer ]
RULE_SGSNPDPRecord[0x9A] = [ "AccessPointNameOI", T_String ]
RULE_SGSNPDPRecord[0x9B] = [ "ServedMSISDN", T_ISDNAddressString ]
RULE_SGSNPDPRecord[0x9C] = [ "ChargingCharacteristics", T_OctetString ]
RULE_SGSNPDPRecord[0x9D] = [ "SystemType", T_Integer ]
RULE_SGSNPDPRecord[0xBE] = [ "CAMELInformationPDP", T_SET, RULE_CAMELInformationPDP ]
RULE_SGSNPDPRecord[0x9F1F] = [ "RNCUnsentDownlinkVolume", T_Integer ]
RULE_SGSNPDPRecord[0x9F20] = [ "ChChSelectionMode", T_Integer ]
RULE_SGSNPDPRecord[0x9F21] = [ "DynamicAddressFlag", T_Boolean ]

RULE_GGSNPDPRecord[0x80] = [ "RecordType", T_Integer ]
RULE_GGSNPDPRecord[0x81] = [ "NetworkInitiation", T_Boolean ]
RULE_GGSNPDPRecord[0x83] = [ "ServedIMSI", T_OctetStringR ]
RULE_GGSNPDPRecord[0xA4] = [ "GGSNAddress", T_CHOICE, RULE_IPAddress ]
RULE_GGSNPDPRecord[0x85] = [ "ChargingID", T_Integer ]
RULE_GGSNPDPRecord[0xA6] = [ "SGSNAddress", T_CHOICE, RULE_IPAddress ]
RULE_GGSNPDPRecord[0x87] = [ "AccessPointNameNI", T_String ]
RULE_GGSNPDPRecord[0x88] = [ "PDPType", T_OctetString ]
RULE_GGSNPDPRecord[0xA9] = [ "ServedPDPAddress", T_CHOICE, RULE_ServedPDPAddress ]
RULE_GGSNPDPRecord[0x8B] = [ "DynamicAddressFlag", T_Boolean ]
RULE_GGSNPDPRecord[0xAC] = [ "ListOfTrafficVolumes", T_SEQUENCEOF, RULE_ChangeOfCharConditionOf ]
RULE_GGSNPDPRecord[0x8D] = [ "RecordOpeningTime", T_TimeStamp ]
RULE_GGSNPDPRecord[0x8E] = [ "Duration", T_Integer ]
RULE_GGSNPDPRecord[0x8F] = [ "CauseForRecClosing", T_Integer ]
RULE_GGSNPDPRecord[0xB0] = [ "Diagnostics", T_CHOICE, RULE_Diagnostics ]
RULE_GGSNPDPRecord[0x91] = [ "RecordSequenceNumber", T_Integer ]
RULE_GGSNPDPRecord[0x92] = [ "NodeID", T_String ]
RULE_GGSNPDPRecord[0x93] = [ "RecordExtensions", T_Unknown, None ]
RULE_GGSNPDPRecord[0x94] = [ "LocalSequenceNumber", T_Integer ]
RULE_GGSNPDPRecord[0x95] = [ "APNSelectionMode", T_Integer ]
RULE_GGSNPDPRecord[0x96] = [ "ServedMSISDN", T_ISDNAddressString ]
RULE_GGSNPDPRecord[0x97] = [ "ChargingCharacteristics", T_OctetString ]
RULE_GGSNPDPRecord[0x98] = [ "ChChSelectionMode", T_Integer ]
RULE_GGSNPDPRecord[0x9B] = [ "PLMN-ID", T_OctetStringR ]

RULE_UnknownRecord[0x80] = [ "recordType", T_Integer ]

RULE_RootRule[0x12] = [ "SGSNPDPRecord", T_SET, RULE_SGSNPDPRecord ]
RULE_RootRule[0x13] = [ "GGSNPDPRecord", T_SET, RULE_GGSNPDPRecord ]
RULE_RootRule[0xFF] = [ "UnknownRecord", T_SET, RULE_UnknownRecord ]

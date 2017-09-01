# niDiagCSDefs.py
# 
# use ctypes to call a DLL
from ctypes import *

# Diagnostic Toolkit exports functions with _stdcall calling convention so use windll to load DLL
niDiagCS = windll.nidiagcs

# recreate TD1 struct from c header file.
# I have not tested that any of the fields line up correctly.
# C Header file uses #pragma pack(1) in 32-bit windows (and 8 in 64-bit windows).
# If code in the future needs access to these fields, investigate how to properly specify packing
# and confirm that the field sizes are correct
class TD1(Structure):
    _fields_ = [("DiagCANHandle", c_uint32),
                ("TransportProtocol", c_uint16),
                ("ReceiveAddressExtension", c_uint8),
                ("TransmitAddressExtension", c_uint8),
                ("ReceiveCANId", c_uint32),
                ("TransmitCANId", c_uint32),
                ("DiagCANQueue", c_uint32),
                ("LogFrames", c_uint8),
                ("MyTPAddress", c_uint8),
                ("OtherTPAddress", c_uint8),
                ("T1", c_uint16),
                ("T2", c_uint16),
                ("T3", c_uint16),
                ("T4", c_uint16),
                ("TxSN", c_uint8),
                ("BlockSize", c_uint8),
                ("RxSN", c_uint8),
                ("VWTPInitialized", c_uint8),
                ("TxBlockNo", c_uint8),
                ("baudRate", c_uint32),
                ("Interface", c_uint32),
                ("ChannelDiagCANHandle", c_uint32),
                ("UDPConnectionID", c_uint32),
                ("TCPConnectionID", c_uint32),
                ("TargetIPAddr", c_uint32),
                ("SourceAddress", c_uint16),
                ("TargetAddress", c_uint16),
                ("SendHeaderNACK", c_uint8),
                ("DLLHandle", c_uint32),
                ("NAD", c_uint8),
                ("TimeStampReadFirst", c_double),
                ("TimeStampReadLast", c_double),
                ("TimeStampWriteFirst", c_double),
                ("TimeStampWriteLast", c_double),
                ("TimeStampWrite", c_double),
                ("TimeStampRead", c_double)]

class TD3(Structure):
    _fields_ = [("DTCByteLength", c_int32),
                ("StatusByteLength", c_int32),
                ("AddDataByteLength", c_int32),
                ("ByteOrder", c_uint16)]

class TD4(Structure):
    _fields_ = [("DTC", c_uint32),
                ("Status", c_uint32),
                ("AddData", c_uint32)]



# recreate function prototypes for DLL calls. Copied from nidiagcs.h

#int32_t __stdcall ndOpenDiagnostic(char CANInterface[], uint32_t baudrate, 
#	uint16_t transportProtocol, uint32_t transmitID, uint32_t receiveID, 
#	TD1 *diagRefOut);

niDiagCS.ndOpenDiagnostic.argtypes=[c_char_p, c_uint32,
                                    c_uint16, c_uint32, c_uint32,
                                    POINTER(TD1) ]
niDiagCS.ndOpenDiagnostic.restype=c_int32

#int32_t __stdcall ndCloseDiagnostic(TD1 *diagRef);
niDiagCS.ndCloseDiagnostic.argtypes=[POINTER(TD1)]
niDiagCS.ndCloseDiagnostic.restype=c_int32

#void __stdcall ndStatusToString(int32_t errorCode, char message[], 
#	int32_t *len);
niDiagCS.ndStatusToString.argtypes=[c_uint32, POINTER(c_char),
                                    POINTER(c_int32)]
niDiagCS.ndStatusToString.restype=None

#int32_t __stdcall ndOBDRequestVehicleInformation(TD1 *diagRef, 
#	uint8_t infoType, uint8_t *items, uint8_t dataOut[], int32_t *len, 
#	LVBoolean *success);

niDiagCS.ndOBDRequestVehicleInformation.argtypes=[POINTER(TD1),
                                                  c_uint8, POINTER(c_uint8), POINTER(c_uint8) , POINTER(c_int32),
                                                  POINTER(c_uint8)]
niDiagCS.ndOBDRequestVehicleInformation.restype=c_int32


#long ndOBDRequestEmissionRelatedDTCs(
#                                   TD1 *diagRef,
#                                   TD3 *DTCDescriptor,
#                                   TD4 DTCs[],
#                                   long *len,
#                                   LVBoolean *success);
niDiagCS.ndOBDRequestEmissionRelatedDTCs.argtypes=[POINTER(TD1),
                                   POINTER(TD3),
                                   POINTER(TD4),
                                   POINTER(c_int32),
                                   POINTER(c_uint8)]
niDiagCS.ndOBDRequestEmissionRelatedDTCs.restype=c_int32

#void ndDTCToString(unsigned long DTCNum,
#                   char DTCString[],
#                   long *len);
niDiagCS.ndDTCToString.argtypes=[c_uint32,
                                POINTER(c_char),
                                POINTER(c_int32)]
niDiagCS.ndDTCToString.restype=None

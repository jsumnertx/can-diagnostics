# This program will use NI-CAN to read the VIN of the Vehicle from an OBD-II port
# See section "Settings" for potential things to change.
# To run without a vehicle, connect a loopback cable between CAN ports 0 and 1 and
#   run the NI ECU simulator - found in the LabVIEW Example Finder under
#   Toolkits and Modules->Automotive Diagnostic Command Set->Demo ECU->Diagnostic Demo ECU.vi.
#   Set the Demo ECU to run as shown in the comments below
#   When run with that example, the output will be "VIN:DiagnosticDemoECU"
# This example is derived from the LabVIEW Example program OBD Request Vehicle Number.vi found
#   in the example finder under Automotive Diagnostic Command Set->OBD
# Developed/Tested on NI Automotive Diagnostic Command Set 15.0, NI-CAN 15.0, Python 2.7.13
# Also tested with NI-CAN 17.0, NI-XNET 17.0.1
# Hardware Supported:
# NI USB-8473, NI USB-8502
# 

# Settings
# IF using USB-8473
#   1) Un-comment "port=CAN1" below
#   2) If using a demo ECU implemented via a second USB-8473 with a loopback cable (NI Part Number 192017-02)
#       Set the LabVIEW Demo ECU to run with NI-CAN as the HW Select and "CAN1" as the CAN Interface,
#       and the Diagnostic protocol as OBD-II.

#port = "CAN0"  # un-comment if using USB-8473

#ELSE IF using USB-8502
#   1) Un-comment "CAN2@nixnet" below
#   2) If using a demo ECU implemented via a USB-8502 with a loopback cable (NI Part Number 192017-02)
#       Set the LabVIEW Demo ECU to run with NI-XNET as the HW Select and "CAN2" as the CAN Interface,
#       and the Diagnostic protocol as OBD-II.
port = "CAN1@nixnet"  #un-comment if using USB-8502

# other possible parameters to set. Defaults should be fine
baud=500000
transmitID=0x7E0 #broadcast ID to use
receiveID=0x7E8  #receive ID to expect - will fail if not set properly


# Program Code

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


# Program code

#Set up error print buffer for use by ndStatusToString
errBuf=create_string_buffer(255)
bufLen=c_int32(255)

# using the defaults found in the OBD Request Vehicle Number.vi exmple
transportProtocol=0
# create TD1 structure to hold session information
td1 = TD1()

# Open the port
result=niDiagCS.ndOpenDiagnostic(port, baud, transportProtocol, transmitID, receiveID, pointer(td1))

# 0 if success
if result!=0:
    niDiagCS.ndStatusToString(result, errBuf, pointer(bufLen))
    print repr(errBuf.value)

# wait one second before sending the next command (as found in the example)
import time
time.sleep(1)

# To read VIN number, send request

#PID 0x2 SID 0x9 - VIN Request
infoType=0x2

# Command returns information in a byte buffer passed to the command. Create the byte buffer and the return variables
# Items passed by pointer are initiatized using the type expected
numItemsReturned=c_uint8(0)
numArrayBytes=c_int32(20)
# magic number 20 needs to match numArrayBytes initialization. originally tried c_uint8 * numArrayBytes but didn't work.
resultArray=(c_uint8 * 20)()
successFail=c_uint8(0)

# Attempt to send the command and read the information
result=niDiagCS.ndOBDRequestVehicleInformation(pointer(td1),
                                               infoType,
                                               pointer(numItemsReturned),
                                               resultArray,
                                               pointer(numArrayBytes),
                                               pointer(successFail))

# 0 if success

if result!=0:
    niDiagCS.ndStatusToString(result, errBuf, pointer(bufLen))
    print repr(errBuf.value)
else:
    print "VIN:"+"".join(map(chr, resultArray))  #converts array of bytes in resultArray to a string
                          
# close the port now that it is done
result=niDiagCS.ndCloseDiagnostic(pointer(td1))
# 0 if success
if result!=0:
    niDiagCS.ndStatusToString(result, errBuf, pointer(bufLen))
    print repr(errBuf.value)

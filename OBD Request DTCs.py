# This program will use NI-CAN to read the Diagnostic Trouble Codes (DTC)
# of the Vehicle from an OBD-II port
# See section "Settings" for potential things to change.
# To run without a vehicle, connect a loopback cable between CAN ports 0 and 1 and
#   run the NI ECU simulator - found in the LabVIEW Example Finder under
#   Toolkits and Modules->Automotive Diagnostic Command Set->Demo ECU->Diagnostic Demo ECU.vi.
#   Set the Demo ECU to run as shown in the comments below
# This example is derived from the LabVIEW Example program OBD Get DTCs.vi found
#   in the example finder under Automotive Diagnostic Command Set->OBD
# Developed/Tested on NI Automotive Diagnostic Command Set 15.0, NI-XNET 17.0.1, Python 2.7.13
# Hardware Supported:
# NI USB-8502
# 

# Settings
# IF using USB-8473
#   1) Un-comment "port=CAN1" below
#   2) If using a demo ECU implemented via a second USB-8473 with a loopback cable (NI Part Number 192017-02)
#       Set the LabVIEW Demo ECU to run with NI-CAN as the HW Select and "CAN0" as the CAN Interface,
#       and the Diagnostic protocol as OBD-II.

#port = "CAN1"  # un-comment if using USB-8473

#ELSE IF using USB-8502
#   1) Un-comment "CAN2@nixnet" below
#   2) If using a demo ECU implemented via a USB-8502 with a loopback cable (NI Part Number 192017-02)
#       Set the LabVIEW Demo ECU to run with NI-XNET as the HW Select and "CAN1" as the CAN Interface,
#       and the Diagnostic protocol as OBD-II.
port = "CAN2@nixnet"  #un-comment if using USB-8502

# other possible parameters to set. Defaults should be fine
baud=500000
transmitID=0x7E0 #broadcast ID to use
receiveID=0x7E8  #receive ID to expect - will fail if not set properly

#load the NI Diagnostic Commandset DLL and define all of the functions and
#classes.  Assumes niDiagCSDefs.py is in the same directory as this file
import niDiagCSDefs
from niDiagCSDefs import *

# Program Code



# Program code
from ctypes import *

#Set up error print buffer for use by ndStatusToString
errBuf=create_string_buffer(255)
bufLen=c_int32(255)

# using the defaults found in the OBD Request Vehicle Number.vi exmple
transportProtocol=0
# create TD1 structure to hold session information
session = TD1()

# Open the port
result=niDiagCS.ndOpenDiagnostic(port, baud, transportProtocol, transmitID, receiveID, pointer(session))

# 0 if success
if result!=0:
    niDiagCS.ndStatusToString(result, errBuf, pointer(bufLen))
    print repr(errBuf.value)

# wait one second before sending the next command (as found in the example)
import time
time.sleep(1)

# To read DTCs , construct request
descriptor = TD3()
descriptor.DTCByteLength=2
descriptor.StatusByteLength=1
descriptor.AddDataByteLength=0
descriptor.ByteOrder=0 #Set to 0 for MSB First (i.e. Motorola)


#allocate space for 30 elements in the TD Array
resultTDArray=(TD4 * 30)()
dtcArrayLen=c_int32(30)

#init return area
successYN=c_uint8(0)


# Attempt to send the command and read the information
result=niDiagCS.ndOBDRequestEmissionRelatedDTCs(pointer(session),
                                                pointer(descriptor),
                                                resultTDArray,
                                                pointer(dtcArrayLen),
                                                pointer(successYN))
                                                

# 0 if success

if result!=0:
    niDiagCS.ndStatusToString(result, errBuf, pointer(bufLen))
    print repr(errBuf.value)
else:
    print "Read "+str(dtcArrayLen)+" DTCs"  
                          
# close the port now that it is done
result=niDiagCS.ndCloseDiagnostic(pointer(session))
# 0 if success
if result!=0:
    niDiagCS.ndStatusToString(result, errBuf, pointer(bufLen))
    print repr(errBuf.value)

#!/usr/bin/env python3
"""
Kamstrup Multical 402 to Domoticz integration script.

Reads data from a Kamstrup Multical 402 heat meter via IR optical probe
and sends it to Domoticz home automation system.

Original work by Poul-Henning Kamp (Beer-ware license)
Modified by Ronald van der Meer, Frank Reijn, Paul Bonnemaijers, and Hans van Schoot
Refactored for better maintainability and code quality.
"""
import sys
import os
import argparse
import logging
from datetime import datetime
from typing import List

from config import KAMSTRUP_402_VARIABLES
from kamstrup_reader import KamstrupReader, KamstrupCommunicationError
from domoticz_client import DomoticzClient, DomoticzError
from value_processor import ValueParameter, ValueProcessor


def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        verbose: Enable INFO level logging
        debug: Enable DEBUG level logging
    """
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def validate_parameters(parameters: List[str]) -> List[ValueParameter]:
    """
    Validate and parse parameter strings.
    
    Args:
        parameters: List of parameter strings in format 'idx:CommandNr:opt[:idx2]'
        
    Returns:
        List of parsed ValueParameter objects
        
    Raises:
        SystemExit: If any parameter is invalid
    """
    parsed_params = []
    
    for param_string in parameters:
        try:
            param = ValueParameter.from_string(param_string)
            parsed_params.append(param)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    return parsed_params


def test_kamstrup(reader: KamstrupReader) -> None:
    """
    Test the Kamstrup interface by reading all known variables.
    
    Args:
        reader: Initialized KamstrupReader instance
    """
    print("\n=== Testing Kamstrup Interface ===\n")
    
    for command_number, name in KAMSTRUP_402_VARIABLES.items():
        value, unit = reader.read_variable(command_number)
        print(f"CommandNr {command_number:4d}: {name:25s} {value} {unit}")
    
    print("\n=== Test Complete ===\n")


def test_domoticz(client: DomoticzClient) -> None:
    """
    Test the Domoticz connection by listing all devices.
    
    Args:
        client: Initialized DomoticzClient instance
    """
    print("\n=== Testing Domoticz Connection ===\n")
    
    try:
        devices = client.get_all_devices()
        
        for device in devices:
            print(f"idx: {device.idx:5d}, Name: {device.name:60s}, Value: {device.value}")
        
        print(f"\n=== Found {len(devices)} devices ===\n")
        
    except DomoticzError as e:
        print(f"Error: Failed to connect to Domoticz: {e}")
        sys.exit(1)


def print_header(timestamp: str) -> None:
    """Print formatted header for data output."""
    print("=" * 87)
    print(f"Kamstrup Multical 402 serial optical data received: {timestamp}")
    print("Meter vendor/type: Kamstrup M402")
    print("-" * 87)


def print_footer(timestamp: str) -> None:
    """Print formatted footer for data output."""
    print("-" * 87)
    print(f"End data received: {timestamp}")
    print("=" * 87)
        while i < len(b) - 1:
            if b[i] == 0x1b:
                v = b[i + 1] ^ 0xff
                if v not in escapes:
                    self.debug_msg(
                        "Missing Escape %02x" % v)
                c.append(v)
                i += 2
            else:
                c.append(b[i])
                i += 1
        if crc_1021(c):
            self.debug_msg("CRC error")
        return c[:-2]

    def readvar(self, nbr):
        # I wouldn't be surprised if you can ask for more than
        # one variable at the time, given that the length is
        # encoded in the response.  Havn't tried.

        self.send(0x80, (0x3f, 0x10, 0x01, nbr >> 8, nbr & 0xff))

        b = self.recv()
        if b == None:
            return (None, None)
        if b[0] != 0x3f or b[1] != 0x10:
            return (None, None)
        
        if b[2] != nbr >> 8 or b[3] != nbr & 0xff:
           return (None, None)

        if b[4] in units:
            u = units[b[4]]
        else:
            u = None

        # Decode the mantissa
        x = 0
        for i in range(0,b[5]):
            x <<= 8
            x |= b[i + 7]

        # Decode the exponent
        i = b[6] & 0x3f
        if b[6] & 0x40:
            i = -i
        i = math.pow(10,i)
        if b[6] & 0x80:
            i = -i
        x *= i

        if False:
            # Debug print
            s = ""
            for i in b[:4]:
                s += " %02x" % i
            s += " |"
            for i in b[4:7]:
                s += " %02x" % i
            s += " |"
            for i in b[7:]:
                s += " %02x" % i

            print(s, "=", x, units[b[4]])

        return (x, u)
            



if __name__ == "__main__":

    import time
    import argparse
    import os
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Values are expected in the format:
   "idx:CommandNr:opt" (for opt=0) 
   "idx:CommandNr:opt:idx2" (for opt=1 or opt=2). 
CommandNr can be found using the --test_kamstrup option 
idx can be found in the "Setup > Devices" list of the Domoticz web interface,
  or by using the --test_domoticz option. 

Devices (Virtual Sensors) must be defined before they can be used! To do this,
   start by adding a "Dummy" type hardware entry. This Dummy hardware then allows
   for creating "Create Virtual Sensors". 
   For example, a Virtual Sensor of type "Custom Sensor" with Axis Label "Gj" can 
   be used for recording the "Heat Energy (E1)".

opt=0 writes the value from "CommandNr" to Domoticz device "idx".
opt=1 takes the value from  "CommandNr", subtracts the value of Domoticz "idx2", and stores this in "idx".
opt=2 takes the value from "CommandNr", adds the value of Domoticz device "idx2", and stores this in "idx".
"""
            )
    parser.add_argument("-d", "--device", type=str, help="Device to use. Example: /dev/ttyUSB0", required=True)
    parser.add_argument("--ip", type=str, help="Domoticz ip address. Defaults to localhost", default="localhost")
    parser.add_argument("--port", type=int, help="Domoticz port. Defaults to 8080", default=8080)
    parser.add_argument("--verbose", help="Make this script more verbose", action="store_true")
    parser.add_argument("--debug", help="Make this script print debug output", action="store_true")
    parser.add_argument("--test_kamstrup", help="Test the IR interface of the Kamstrup and exit", action="store_true")
    parser.add_argument("--test_domoticz", help="Test the connection with Domoticz and exit ", action="store_true")
    parser.add_argument("values", type=str, help="idx:CommandNr:opt or idx:CommandNR:opt:idx2", nargs='*')
    
    args = parser.parse_args()
    
    # some sanity checks
    if not os.path.exists(args.device):
        print("Error! failed to locate specified device: %s" %(args.device))
        sys.exit(1)
    for value in args.values:
        # check they have the correct format
        blub=0
        try:
            blub=len(value.split(':'))
        except:
            print("Error! make sure to format your values correctly!")
            sys.exit(1)
        if not (blub == 3 or blub == 4):
            print("Error! make sure to format your values correctly!")
            sys.exit(1)
    if not (args.test_kamstrup or args.test_domoticz) and len(args.values) == 0:
        print("This script needs values to do someting! Check --help to see how it works!")
        sys.exit()

    # some easier names
    domoip = args.ip
    domoport = args.port

    foo = kamstrup( args.device )
    heat_timestamp=datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d %H:%M:%S" )
    
    if args.test_kamstrup:
        for i in kamstrup_402_var:
            x,u = foo.readvar(i)
            print("CommandNr %4i: %-25s" %(i, kamstrup_402_var[i]), x, u)
        sys.exit()

    if args.test_domoticz:
        requestGet = ( "http://" + str(domoip) + ":" + str(domoport) + "/json.htm?type=devices" )
        domo_data = json.load(reader(urllib.request.urlopen(requestGet)))
        for device in domo_data['result']:
            device_idx = device['idx']
            device_name = device['Name']
            device_value = device['Data']
            print("idx: %5s, Name: %-60s, Value: %s" %(device_idx, device_name, device_value))
        # if args.debug:
        #     print("+ Last stored value for device: " + device_name + " was " + device_value)
        sys.exit()
#    print(args.values)
    
print ("=======================================================================================")
print ("Kamstrup Multical 402 serial optical data received: %s" % heat_timestamp)
print ("Meter vendor/type: Kamstrup M402")
print ("---------------------------------------------------------------------------------------")

for i in kamstrup_402_var:
    r = 0
        
    for y in args.values:
        paramater = y.split(':')
        idx = int(paramater[0],0)
        dcNr = int(paramater[1],0)
        opt = int(paramater[2],0)

        try:
            compare_idx = int(paramater[3],0)
        except IndexError:
            compare_idx = 0
            
        
        # If decimal number matches the command given as argv[2]
        if i == dcNr:
            x,u = foo.readvar(i)
          
            print("%-25s" % kamstrup_402_var[i], x, u)
           
            value = round(x,2)

            # Retrieve devicename and devicedata
            requestGet = ( "http://" + str(domoip) + ":" + str(domoport) + "/json.htm?type=devices&rid=" + str(idx) )
            device_data = json.load(reader(urllib.request.urlopen(requestGet)))
            device_name = device_data['result'][0]['Name']
            device_value = device_data['result'][0]['Data']
            if args.debug:
                print("+ Last stored value for device: " + device_name + " was " + device_value)

            
            if args.debug: 
                print("+ Processing parameter: " + str(y) + "")

            # 0 = Update current
            # 1 = Substraction
            # 2 = Addition
            if opt == 0:
                # Submit the current value to the device
                if args.debug:
                    print("  + F" + str(opt) + " Debug: Overwrite: " + str(device_name) + " (idx: " + str(idx) + ") with latest value: " + str(value)) 
                dummyvar = 0
            elif opt == 1:
                if compare_idx > 0:
                    requestGet = ( "http://" + str(domoip) + ":" + str(domoport) + "/json.htm?type=devices&rid=" + str(compare_idx) )
                    device_compare_data = json.load(reader(urllib.request.urlopen(requestGet)))
                    device_compare_name = device_compare_data['result'][0]['Name']
                    device_compare_value = device_compare_data['result'][0]['Data']
                    device_compare_value = device_compare_value.split(' ')
                    device_compare_value = device_compare_value[0]
                    diff = float(value) - float(device_compare_value)
                    diff = round(diff,2) 

                    if args.debug: 
                        print("  + F" + str(opt) + " Debug: Substract " + str(device_compare_value) + " (idx:" + str(compare_idx) + ") from " + str(value) + " (idx:" + str(idx) + ") = " + str(diff) )
                    
                    value = diff

            elif opt == 2:
                if compare_idx > 0:
                    device_value = device_value.split(' ')
                    device_value = device_value[0]
                    
                    requestGet = ( "http://" + str(domoip) + ":" + str(domoport) + "/json.htm?type=devices&rid=" + str(compare_idx) )
                    device_compare_data = json.load(reader(urllib.request.urlopen(requestGet)))
                    device_compare_name = device_compare_data['result'][0]['Name']
                    device_compare_value = device_compare_data['result'][0]['Data']
                    device_compare_value = device_compare_value.split(' ')
                    device_compare_value = device_compare_value[0]
                    diff = float(value) - float(device_compare_value)
                    diff = round(diff,2) 
                    
                    addup = float(diff) + float(device_value)
                    addup = round(addup,2) 
                    
                    if args.debug: 
                        print("  + F" + str(opt) + " Debug: Addition " + str(device_value) + " (idx:" + str(idx) + ") + " + str(diff) + " (" + str(value) + " (idx:" + str(idx) + ") - " + str(device_compare_value) + " (idx:" + str(compare_idx) + ")) = " + str(addup) )

                    value = addup

            # Upload the current value to the device
            print("  + F" + str(opt) + " Submit value " + str(value) + " to '" + str(device_name) + "' (idx: " + str(idx) + ")") 
            requestPost = ( "http://" + str(domoip) + ":" + str(domoport) + "/json.htm?type=command&param=udevice&idx=" + str(idx) + "&svalue=" + str(value) )
            #print(requestPost)
            resultPost = urllib.request.urlopen(requestPost)
            
        
print ("---------------------------------------------------------------------------------------")
print ("End data received: %s" % heat_timestamp)
print ("=======================================================================================") 




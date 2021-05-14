#!/usr/bin/python3
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <phk@FreeBSD.ORG> wrote this file.  As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.   Poul-Henning Kamp
# ----------------------------------------------------------------------------
#
# Modified for Domotics and single request.
#
# Modified by Ronald van der Meer, Frank Reijn and Paul Bonnemaijers for the
# Kamstrup Multical 402
# Later modified by Hans van Schoot for easier usage
#

from __future__ import print_function

# You need pySerial 
import serial
import math
import sys
import datetime
import json
import urllib
import urllib.request
import codecs

# Variables

reader = codecs.getreader("utf-8")

kamstrup_402_var = {                # Decimal Number in Command
 0x003C: "Heat Energy (E1)",         #60
 0x0050: "Power",                   #80
 0x0056: "Temp1",                   #86
 0x0057: "Temp2",                   #87
 0x0059: "Tempdiff",                #89
 0x004A: "Flow",                    #74
 0x0044: "Volume",                  #68
 0x008D: "MinFlow_M",               #141
 0x008B: "MaxFlow_M",               #139
 0x008C: "MinFlowDate_M",           #140
 0x008A: "MaxFlowDate_M",           #138
 0x0091: "MinPower_M",              #145
 0x008F: "MaxPower_M",              #143
 0x0095: "AvgTemp1_M",              #149
 0x0096: "AvgTemp2_M",              #150
 0x0090: "MinPowerDate_M",          #144
 0x008E: "MaxPowerDate_M",          #142
 0x007E: "MinFlow_Y",               #126
 0x007C: "MaxFlow_Y",               #124
 0x007D: "MinFlowDate_Y",           #125
 0x007B: "MaxFlowDate_Y",           #123
 0x0082: "MinPower_Y",              #130
 0x0080: "MaxPower_Y",              #128
 0x0092: "AvgTemp1_Y",              #146
 0x0093: "AvgTemp2_Y",              #147
 0x0081: "MinPowerDate_Y",          #129
 0x007F: "MaxPowerDate_Y",          #127
 0x0061: "Temp1xm3",                #97
 0x006E: "Temp2xm3",                #110
 0x0071: "Infoevent",               #113
 0x03EC: "HourCounter",             #1004
}

#######################################################################
# Units, provided by Erik Jensen

units = {
    0: '', 1: 'Wh', 2: 'kWh', 3: 'MWh', 4: 'GWh', 5: 'j', 6: 'kj', 7: 'Mj',
    8: 'Gj', 9: 'Cal', 10: 'kCal', 11: 'Mcal', 12: 'Gcal', 13: 'varh',
    14: 'kvarh', 15: 'Mvarh', 16: 'Gvarh', 17: 'VAh', 18: 'kVAh',
    19: 'MVAh', 20: 'GVAh', 21: 'kW', 22: 'kW', 23: 'MW', 24: 'GW',
    25: 'kvar', 26: 'kvar', 27: 'Mvar', 28: 'Gvar', 29: 'VA', 30: 'kVA',
    31: 'MVA', 32: 'GVA', 33: 'V', 34: 'A', 35: 'kV',36: 'kA', 37: 'C',
    38: 'K', 39: 'l', 40: 'm3', 41: 'l/h', 42: 'm3/h', 43: 'm3xC',
    44: 'ton', 45: 'ton/h', 46: 'h', 47: 'hh:mm:ss', 48: 'yy:mm:dd',
    49: 'yyyy:mm:dd', 50: 'mm:dd', 51: '', 52: 'bar', 53: 'RTC',
    54: 'ASCII', 55: 'm3 x 10', 56: 'ton x 10', 57: 'GJ x 10',
    58: 'minutes', 59: 'Bitfield', 60: 's', 61: 'ms', 62: 'days',
    63: 'RTC-Q', 64: 'Datetime'
}

#######################################################################
# Kamstrup uses the "true" CCITT CRC-16
#

def crc_1021(message):
        poly = 0x1021
        reg = 0x0000
        for byte in message:
                mask = 0x80
                while(mask > 0):
                        reg<<=1
                        if byte & mask:
                                reg |= 1
                        mask>>=1
                        if reg & 0x10000:
                                reg &= 0xffff
                                reg ^= poly
        return reg

#######################################################################
# Byte values which must be escaped before transmission
#

escapes = {
    0x06: True,
    0x0d: True,
    0x1b: True,
    0x40: True,
    0x80: True,
}

#######################################################################
# And here we go....
#

class kamstrup(object):

    def __init__(self, serial_port):
        self.debug_fd = open("/tmp/_kamstrup", "a")
        self.debug_fd.write("\n\nStart\n")
        self.debug_id = None

        self.ser = serial.Serial(
            port = serial_port,
            baudrate = 1200,
            timeout = 5.0,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_TWO)
#            xonxoff = 0,
#            rtscts = 0)
#           timeout = 20

    def debug(self, dir, b):
        for i in b:
            if dir != self.debug_id:
                if self.debug_id != None:
                    self.debug_fd.write("\n")
                self.debug_fd.write(dir + "\t")
                self.debug_id = dir
            self.debug_fd.write(" %02x " % i)
        self.debug_fd.flush()

    def debug_msg(self, msg):
        if self.debug_id != None:
            self.debug_fd.write("\n")
        self.debug_id = "Msg"
        self.debug_fd.write("Msg\t" + msg)
        self.debug_fd.flush()

    def wr(self, b):
        b = bytearray(b)
        self.debug("Wr", b);
        self.ser.write(b)

    def rd(self):
        a = self.ser.read(1)
        if len(a) == 0:
            self.debug_msg("Rx Timeout")
            return None
        b = bytearray(a)[0]
        self.debug("Rd", bytearray((b,)));
        return b

    def send(self, pfx, msg):
        b = bytearray(msg)

        b.append(0)
        b.append(0)
        c = crc_1021(b)
        b[-2] = c >> 8
        b[-1] = c & 0xff

        c = bytearray()
        c.append(pfx)
        for i in b:
            if i in escapes:
                c.append(0x1b)
                c.append(i ^ 0xff)
            else:
                c.append(i)
        c.append(0x0d)
        self.wr(c)

    def recv(self):
        b = bytearray()
        while True:
            d = self.rd()
            if d == None:
                return None
            if d == 0x40:
                b = bytearray()
            b.append(d)
            if d == 0x0d:
                break
        c = bytearray()
        i = 1;
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




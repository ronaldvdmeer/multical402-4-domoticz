# multical402-4-domoticz
  
This script is developed for use with domoticz and a Kamstrup Multical 402 (city heating)  
  
Dependency:
 * Software: linux, python3 and python3-serial  
 * Hardware: IR Optical Probe IEC1107 IEC61107  
  
usage: multical.py [-h] -d DEVICE [--ip IP] [--port PORT] [--verbose]
                   [--debug] [--test_kamstrup] [--test_domoticz]
                   [values [values ...]]

positional arguments:
  values                idx:CommandNr:opt or idx:CommandNR:opt:idx2

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        Device to use. Example: /dev/ttyUSB0
  --ip IP               Domoticz ip address. Defaults to localhost
  --port PORT           Domoticz port. Defaults to 8080
  --verbose             Make this script more verbose
  --debug               Make this script print debug output
  --test_kamstrup       Test the IR interface of the Kamstrup and exit
  --test_domoticz       Test the connection with Domoticz and exit

Values are expected in the format:
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


You must atleast execute this script once every 30 minutes or else the IR port on the Kamstrup will be disabled until you press a physical button on the device itself. This can be done with cron: `crontab -e` and then add something like:

`*/20 *  * * * /usr/bin/python3 /path/to/your/script/multical402-4-domoticz.py -d /dev/ttyUSB1 88:60:0 89:80:0`

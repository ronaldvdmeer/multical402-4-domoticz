# multical402-4-domoticz

This script is developed for domoticz and a Kamstrup Multical 402 (city heating)  

Dependency:
 * Software: linux, python3 and python3-serial  
 * Hardware: IR Optical Probe IEC1107 IEC61107  

Syntax:  `multical402-4-domoticz.py <DEVICE> <IDX>:<DECIMALNUMBER>:<FUNCTION>,<IDX>:<DECIMALNUMBER>:<FUNCTION>,...`  
Example: `multical402-4-domoticz.py /dev/ttyUSB2 321:60:0,322:60:1:321`

There are two different functions that must be defined by etiher 0 or 1
 * `0` = Overwrite with latest value  
 * `1` = Compare with other device in domoticz

If `1` is specified another device must be defined so this program can compare both (the example above has both functions).  

[![domoticz.png](https://s14.postimg.org/m4apmfvb5/domoticz.png)](https://postimg.org/image/af6pyh4cd/)  

You must atleast execute this script every 30 minutes or else the IR port on the Kamstrup will be disabled until you press the button on the device.
In my case i'm executing this scripting every 2 minutes

`*/20 *  * * *   root    /usr/bin/python3 /usr/local/sbin/multical402-4-domoticz/multical402-4-domoticz.py /dev/ttyUSB2 321:60:0,322:60:1:321`

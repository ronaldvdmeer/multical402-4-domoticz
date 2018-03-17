# multical402-4-domoticz

This script is developed for domoticz and a Kamstrup Multical 402 (city heating)  

Dependency:
 * Software: linux, python3 and python3-serial  
 * Hardware: IR Optical Probe IEC1107 IEC61107  

Syntax:  `multical402-4-domoticz.py <DEVICE> <IDX>:<DECIMALNUMBER>:<FUNCTION>,<IDX>:<DECIMALNUMBER>:<FUNCTION>:<OPTIONALDEVICE>,...`  
Example: `multical402-4-domoticz.py /dev/ttyUSB2 321:60:0,322:60:1:321`

There are two different functions that must be defined by etiher 0 or 1
 * `0` = Overwrite with latest value  
 * `1` = Compare with other device in domoticz
 * `2` = Add value of device to another device  

If `1` or `2` is specified another device must be defined so this program can compare both (the example above has both functions).  

[![domoticz-heatusage.png](https://s14.postimg.org/zd6pmx4vl/domoticz-heatusage.png)](https://postimg.org/image/70b7wgj59/)

You must atleast execute this script every 30 minutes or else the IR port on the Kamstrup will be disabled until you press the button on the device.  

`*/20 *  * * *   root    /usr/bin/python3 /usr/local/sbin/multical402-4-domoticz/multical402-4-domoticz.py /dev/ttyUSB2 324:60:2:323,325:60:2:323,325:60:2:323,326:60:2:323,327:60:2:323,322:60:1:323,323:60:0`

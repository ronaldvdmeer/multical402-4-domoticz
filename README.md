# multical402-4-domoticz
  
This script is developed for use with domoticz and a Kamstrup Multical 402 (city heating)  
  
Dependency:
 * Software: linux, python3 and python3-serial  
 * Hardware: IR Optical Probe IEC1107 IEC61107  
  
Syntax:  `multical402-4-domoticz.py <DEVICE> <IDX>:<DECIMALNUMBER>:<FUNCTION>,<IDX>:<DECIMALNUMBER>:<FUNCTION>:<OPTIONALDEVICE>,...`  
Example: `multical402-4-domoticz.py /dev/ttyUSB2 327:60:2:323,322:60:1:323,323:60:0`
  
You are able to define multiple idx > decimalnumber calculations by seperating them with commas. In the example above three virtual devices (domoticz) are updated all in one run and with different calculatoins. 
  
There are three different functions that must be defined by etiher 0, 1 or 2
 * `0` = Overwrite device (in domoticz) with latest value (multical) 
 * `1` = Substract current value (Multical) minus last known value (in domoticz) which results in usage between runs
 * `2` = Add value (for example the current value) of one device to another device  
  
If `1` or `2` is specified another device must be defined so this script can compare both (the example above has both functions).  
  
In the example above there are 3 calculations done:
 * `327:60:2:323` = The device idx 327 (domoticz) is linked to value defined as the decimal number 60 (multical). Because function 2 is selected it will add the value of idx 323 to idx 327 
 * `322:60:1:323` = The device idx 322 (domoticz) is linked to value defined as the decimal number 60 (multical). Because function 1 is selected it will substract the value of idx 323 and calculate the difference and write it to idx 322
 * `323:60:0` = The device idx 323 (domoticz) is linked to value defined as the decimal number 60 (multical). Because function 0 is selected the value in domoticz is overwritten with the current value from the multical. 
  
[![domoticz-heatusage.png](https://s14.postimg.org/zd6pmx4vl/domoticz-heatusage.png)](https://postimg.org/image/70b7wgj59/)

You must atleast execute this script once every 30 minutes or else the IR port on the Kamstrup will be disabled until you press a physical button on the device itself.    

`*/20 *  * * *   root    /usr/bin/python3 /usr/local/sbin/multical402-4-domoticz/multical402-4-domoticz.py /dev/ttyUSB2 324:60:2:323,325:60:2:323,325:60:2:323,326:60:2:323,327:60:2:323,322:60:1:323,323:60:0`

# multical402-4-domoticz

Dependency: python3 and python3-serial  

Syntax: `/usr/bin/python3 /usr/local/sbin/multical402-4-domoticz/multical402-4-domoticz.py <DEVICE> <DECIMALNUMBER> <IDX>`  
Example: `/usr/bin/python3 /usr/local/sbin/multical402-4-domoticz/multical402-4-domoticz.py /dev/ttyUSB2 60 322`

[![domoticz.png](https://s14.postimg.org/m4apmfvb5/domoticz.png)](https://postimg.org/image/af6pyh4cd/)  

You must execute this script within every 30 minutes or else the IR port will be disabled until you press the button on the Multical.
In my case i'm executing this scripting every 2 minutes

`*/20 *  * * *   root    /usr/bin/python3 /usr/local/sbin/multical402-4-domoticz/multical402-4-domoticz.py /dev/ttyUSB2 60 322`

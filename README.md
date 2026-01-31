# multical402-4-domoticz

[![Python 3.7+](https://img.shields.io/badge/Python-3.7%2B-blue)](https://python.org/)
[![Type Hints](https://img.shields.io/badge/type%20hints-100%25-green)](https://docs.python.org/3/library/typing.html)
[![Code Style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-blue)](https://peps.python.org/pep-0008/)
[![License: Beer-ware](https://img.shields.io/badge/License-Beer--ware-yellow)](https://en.wikipedia.org/wiki/Beerware)
[![Status: Archived](https://img.shields.io/badge/status-archived-red)](https://github.com/ronaldvdmeer/multical402-4-domoticz)

**⚠️ ARCHIVED REPOSITORY: The original author no longer uses Domoticz and has switched to Home Assistant. For an alternative, check out [PyKMP](https://github.com/gertvdijk/PyKMP)**

---

## 🎉 Refactored Version Available!

This project has been **completely refactored** with modern Python best practices:
- ✅ Modular architecture (5 separate modules)
- ✅ Full type hints and documentation
- ✅ Proper error handling and logging
- ✅ Clean, maintainable code

**See [README_REFACTORED.md](README_REFACTORED.md) for the improved version!**

---

## Original Documentation

This script reads data from a Kamstrup Multical 402 heat meter (city heating) and sends it to Domoticz.

### Dependencies
- **Software:** Linux, Python 3.7+, pyserial
- **Hardware:** IR Optical Probe IEC1107/IEC61107

### Usage

```
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
opt=1 takes the value from "CommandNr", subtracts the value of Domoticz "idx2", 
      and stores this in "idx".
opt=2 takes the value from "CommandNr", adds the value of Domoticz device "idx2", 
      and stores this in "idx".
```

### ⚠️ Important: Automatic Execution Required

You must execute this script **at least once every 30 minutes** to prevent the Kamstrup IR port from disabling itself. If disabled, you'll need to press a physical button on the device to re-enable it.

Set up automatic execution with cron:

```bash
crontab -e
```

Add this line (adjust paths as needed):

```bash
*/20 * * * * /usr/bin/python3 /path/to/your/script/multical402-4-domoticz.py -d /dev/ttyUSB1 88:60:0 89:80:0
```

---

## 📚 Further Information

For detailed documentation on the refactored version, including:
- Complete API documentation
- Architecture diagrams
- Usage examples and troubleshooting
- Installation guide

**Please refer to [README_REFACTORED.md](README_REFACTORED.md)**

---

## Credits

Original work by Poul-Henning Kamp (Beer-ware license)  
Modified by Ronald van der Meer, Frank Reijn, Paul Bonnemaijers, and Hans van Schoot  
Refactored for improved maintainability and modern Python standards

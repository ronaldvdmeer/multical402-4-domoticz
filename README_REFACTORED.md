# Kamstrup Multical 402 to Domoticz - Refactored Version

[![Python 3.7+](https://img.shields.io/badge/Python-3.7%2B-blue)](https://python.org/)
[![Type Hints](https://img.shields.io/badge/type%20hints-100%25-green)](https://docs.python.org/3/library/typing.html)
[![Code Style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-blue)](https://peps.python.org/pep-0008/)
[![License: Beer-ware](https://img.shields.io/badge/License-Beer--ware-yellow)](https://en.wikipedia.org/wiki/Beerware)
[![Status: Archived](https://img.shields.io/badge/status-archived-red)](https://github.com/ronaldvdmeer/multical402-4-domoticz)

**⚠️ Note: This repository is archived by the original author who switched to Home Assistant. For alternatives, see [PyKMP](https://github.com/gertvdijk/PyKMP).**

---

## Overview

This refactored version provides a modern, maintainable Python implementation for reading data from a **Kamstrup Multical 402** heat meter via IR optical probe and sending it to the **Domoticz** home automation system.

### Why This Refactored Version?

The original monolithic script has been completely restructured with:
- ✅ **Modular architecture** - 5 separate modules for better organization
- ✅ **Type safety** - Full type hints throughout the codebase
- ✅ **Professional logging** - Using Python's logging framework
- ✅ **Comprehensive error handling** - Custom exceptions and proper error recovery
- ✅ **Clean code** - Follows PEP 8 and modern Python best practices
- ✅ **Maintainability** - Clear separation of concerns, DRY principle applied

---

## Requirements

### Hardware
- Kamstrup Multical 402 heat meter (city heating)
- IR Optical Probe (IEC1107/IEC61107 compatible)
- Serial/USB adapter

### Software
- Python 3.7 or higher
- pyserial library

---

## Installation

```bash
# Clone or download the repository
cd multical402-4-domoticz

# Install dependencies
pip install -r requirements.txt

# Make script executable (Linux/Mac)
chmod +x multical402.py
```

---

## Project Structure

```
multical402-4-domoticz/
├── config.py                    # Constants, units, and configuration
├── kamstrup_reader.py           # Serial communication with Kamstrup device
├── domoticz_client.py           # Domoticz API client
├── value_processor.py           # Value processing logic (modes 0, 1, 2)
├── multical402.py               # Main application entry point ⭐
├── multical402_legacy.py        # Original legacy script (for reference)
├── requirements.txt             # Python dependencies
├── README.md                    # Original documentation
├── README_REFACTORED.md         # This file
├── REFACTORING_NOTES.md         # Detailed refactoring documentation
└── ARCHITECTURE.md              # Architecture diagrams and flow charts
```

### Module Descriptions

**config.py**  
Centralized configuration containing all Kamstrup variable definitions, unit mappings, protocol constants, and processing mode enums.

**kamstrup_reader.py**  
Handles low-level serial communication with the Kamstrup device, including CRC checking, escape sequences, and response parsing.

**domoticz_client.py**  
Clean API wrapper for all Domoticz interactions with proper error handling, device management, and value updates.

**value_processor.py**  
Implements the three processing modes with clear separation of logic:
- Mode 0: Direct value overwrite
- Mode 1: Subtract comparison value
- Mode 2: Add difference to stored value

**multical402.py** ⭐  
The main refactored script - use this for new deployments! Features clean application flow, comprehensive error handling, and proper logging.

---

## Quick Start

### 1. Test Kamstrup Connection

Verify communication with your Kamstrup device:

```bash
python multical402.py -d /dev/ttyUSB0 --test_kamstrup
```

This will read and display all available variables from the device.

### 2. Test Domoticz Connection

Verify connection to your Domoticz server:

```bash
python multical402.py --ip 192.168.1.100 --test_domoticz
```

This will list all devices in your Domoticz installation with their indices.

### 3. Read and Update Values

Read values from Kamstrup and update Domoticz devices:

```bash
python multical402.py -d /dev/ttyUSB0 88:60:0 89:80:0
```

---

## Usage

### Command Line Syntax

```bash
python multical402.py [OPTIONS] [VALUES...]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-d DEVICE` | Serial device path (required) | - |
| `--ip HOST` | Domoticz IP address | localhost |
| `--port PORT` | Domoticz port number | 8080 |
| `--verbose` | Enable verbose output | Off |
| `--debug` | Enable debug logging | Off |
| `--debug-file FILE` | Path to debug log file | /tmp/_kamstrup |
| `--test_kamstrup` | Test Kamstrup interface and exit | - |
| `--test_domoticz` | Test Domoticz connection and exit | - |

### Value Parameters

Parameters follow the format: `idx:CommandNr:mode[:idx2]`

- **idx** - Domoticz device index (find using `--test_domoticz`)
- **CommandNr** - Kamstrup command number (find using `--test_kamstrup`)
- **mode** - Processing mode: 0, 1, or 2
- **idx2** - Comparison device index (required for modes 1 and 2)

### Processing Modes

#### Mode 0: Overwrite (Direct Update)
Writes the raw reading value directly to the Domoticz device.

**Example:**
```bash
88:60:0  # Write Heat Energy (command 60) to device 88
```

**Use case:** Simple direct sensor readings like current temperature, power, or flow rate.

---

#### Mode 1: Subtract
Subtracts a comparison device's value from the current reading before storing.

**Example:**
```bash
89:80:1:90  # Read Power (80), subtract device 90's value, store in device 89
```

**Use case:** Calculate differences or deltas between measurements.

---

#### Mode 2: Add (Cumulative)
Calculates the difference from a comparison device and adds it to the target device's current value.

**Example:**
```bash
91:68:2:92  # Read Volume (68), calculate difference from device 92, 
            # add to device 91's current value
```

**Use case:** Accumulating incremental changes, useful for total energy consumption tracking.

---

## Complete Examples

### Basic Setup

Read heat energy and power, update Domoticz:

```bash
python multical402.py -d /dev/ttyUSB0 \
    100:60:0 \    # Heat Energy to device 100
    101:80:0      # Power to device 101
```

### Advanced Setup with Calculations

```bash
python multical402.py -d /dev/ttyUSB0 --ip 192.168.1.50 \
    100:60:0 \        # Direct heat energy reading
    101:80:0 \        # Direct power reading
    102:68:2:103 \    # Cumulative volume (subtract device 103, add to 102)
    104:86:0 \        # Temperature 1
    105:87:0          # Temperature 2
```

### With Verbose Logging

```bash
python multical402.py -d /dev/ttyUSB0 --verbose \
    88:60:0 89:80:0
```

### Debug Mode

For troubleshooting communication issues:

```bash
python multical402.py -d /dev/ttyUSB0 --debug \
    --debug-file /var/log/kamstrup_debug.log \
    88:60:0
```

---

## Domoticz Setup

### Creating Virtual Sensors

Before running the script, you must create Virtual Sensors in Domoticz:

1. **Add Dummy Hardware**
   - Go to **Setup → Hardware**
   - Add **Dummy** hardware type
   - Give it a meaningful name (e.g., "Kamstrup Sensors")

2. **Create Virtual Sensors**
   - Click **Create Virtual Sensors** for your Dummy hardware
   - Create sensors based on your needs:

| Measurement | Sensor Type | Axis Label | Example Name |
|-------------|-------------|------------|--------------|
| Heat Energy | Custom Sensor | Gj | Kamstrup Heat Energy |
| Power | Custom Sensor | kW | Kamstrup Power |
| Temperature | Temperature | - | Kamstrup Temp 1 |
| Volume | Custom Sensor | m³ | Kamstrup Volume |
| Flow | Custom Sensor | m³/h | Kamstrup Flow |

3. **Note Device Indices**
   - Go to **Setup → Devices**
   - Note the **idx** number for each sensor
   - Or use: `python multical402.py --test_domoticz`

---

## Command Number Reference

Common Kamstrup Multical 402 command numbers:

| Command | Variable Name | Unit | Typical Use |
|---------|---------------|------|-------------|
| 60 (0x3C) | Heat Energy (E1) | Gj | Total energy consumption |
| 80 (0x50) | Power | kW | Current power usage |
| 86 (0x56) | Temp1 | °C | Supply temperature |
| 87 (0x57) | Temp2 | °C | Return temperature |
| 89 (0x59) | Tempdiff | °C | Temperature difference |
| 74 (0x4A) | Flow | m³/h | Current flow rate |
| 68 (0x44) | Volume | m³ | Total volume |
| 141 (0x8D) | MinFlow_M | m³/h | Minimum flow (month) |
| 139 (0x8B) | MaxFlow_M | m³/h | Maximum flow (month) |
| 145 (0x91) | MinPower_M | kW | Minimum power (month) |
| 143 (0x8F) | MaxPower_M | kW | Maximum power (month) |

**Get full list:** Use `--test_kamstrup` to see all available variables.

---

## Automated Execution

### ⚠️ Critical: Keep IR Port Active

**You MUST execute this script at least once every 30 minutes** or the Kamstrup IR port will automatically disable itself. If this happens, you'll need physical access to the device to press a button to re-enable it.

### Setting Up Cron

Edit your crontab:

```bash
crontab -e
```

Add one of these lines:

**Every 20 minutes (recommended):**
```bash
*/20 * * * * /usr/bin/python3 /path/to/multical402.py -d /dev/ttyUSB0 88:60:0 89:80:0
```

**Every 15 minutes (safer margin):**
```bash
*/15 * * * * /usr/bin/python3 /path/to/multical402.py -d /dev/ttyUSB0 88:60:0 89:80:0
```

**With logging:**
```bash
*/20 * * * * /usr/bin/python3 /path/to/multical402.py -d /dev/ttyUSB0 88:60:0 89:80:0 >> /var/log/kamstrup.log 2>&1
```

### Verify Cron is Working

Check your logs:
```bash
tail -f /var/log/kamstrup.log
```

Or check Domoticz device updates in the web interface.

---

## Troubleshooting

### Device Not Found

**Error:**
```
Error: Device not found: /dev/ttyUSB0
```

**Solutions:**
1. Check device is connected: `ls -l /dev/ttyUSB*`
2. Check permissions: `sudo chmod 666 /dev/ttyUSB0`
3. Add user to dialout group: `sudo usermod -a -G dialout $USER` (requires logout)
4. Check device name (might be `/dev/ttyUSB1` or `/dev/ttyACM0`)

### Communication Timeout

**Symptoms:** No response from Kamstrup device

**Solutions:**
1. Enable debug mode: `--debug`
2. Check IR probe placement on the device
3. Ensure probe has power
4. Clean the optical sensor area on the meter
5. Check serial cable connections

### CRC Errors

**Error in debug log:**
```
CRC error
```

**Solutions:**
1. Check for electromagnetic interference near the cable
2. Try a shorter/better quality serial cable
3. Reduce baud rate (requires code modification)
4. Check IR probe is firmly attached

### Domoticz Connection Failed

**Error:**
```
Error: Cannot connect to Domoticz: [Errno 111] Connection refused
```

**Solutions:**
1. Verify Domoticz is running: `systemctl status domoticz`
2. Check IP address: `--ip 192.168.1.x`
3. Check port: `--port 8080` (default)
4. Test with: `curl http://localhost:8080/json.htm?type=devices`
5. Check firewall settings

### Invalid Parameter Format

**Error:**
```
Error: Invalid parameter format: abc:def
```

**Solutions:**
1. Use correct format: `idx:CommandNr:mode[:idx2]`
2. Check values are numeric (hex supported with 0x prefix)
3. Ensure mode 1 or 2 has idx2: `89:80:1:90`

### Permission Denied

**Error:**
```
Permission denied: /dev/ttyUSB0
```

**Solutions:**
```bash
# Temporary (until reboot)
sudo chmod 666 /dev/ttyUSB0

# Permanent
sudo usermod -a -G dialout $USER
# Then logout and login again
```

---

## Advanced Topics

### Custom Debug File Location

```bash
python multical402.py -d /dev/ttyUSB0 \
    --debug \
    --debug-file /var/log/kamstrup_$(date +%Y%m%d).log \
    88:60:0
```

### Multiple Meters

If you have multiple Kamstrup meters:

```bash
# Meter 1
python multical402.py -d /dev/ttyUSB0 100:60:0 101:80:0

# Meter 2
python multical402.py -d /dev/ttyUSB1 200:60:0 201:80:0
```

### Monitoring Script Execution

Create a wrapper script for better monitoring:

```bash
#!/bin/bash
LOG="/var/log/kamstrup.log"
echo "$(date): Starting Kamstrup read" >> $LOG
/usr/bin/python3 /path/to/multical402.py -d /dev/ttyUSB0 88:60:0 89:80:0 >> $LOG 2>&1
echo "$(date): Finished (exit code: $?)" >> $LOG
```

---

## Comparison: Original vs Refactored

| Aspect | Original | Refactored | Benefit |
|--------|----------|------------|---------|
| **Structure** | 1 file, 450 lines | 5 modules, ~350 lines main | Better organization |
| **Type Safety** | No type hints | Full type coverage | IDE support, fewer bugs |
| **Error Handling** | Basic | Comprehensive | Better reliability |
| **Logging** | File writes | Logging framework | Professional debugging |
| **Documentation** | Minimal | Extensive | Easier to understand |
| **Testability** | Difficult | Easy | Enables unit testing |
| **Maintainability** | Low | High | Easier to modify |
| **Code Duplication** | Significant | None | DRY principle |

**Both versions are functionally identical** - same CLI, same results, same compatibility.

---

## Development

### Running Tests

Currently no automated tests, but you can test manually:

```bash
# Test Kamstrup communication
python multical402.py -d /dev/ttyUSB0 --test_kamstrup

# Test Domoticz API
python multical402.py --test_domoticz

# Test with verbose output
python multical402.py -d /dev/ttyUSB0 --verbose 88:60:0
```

### Future Improvements

Potential enhancements for contributors:

1. **Unit Tests** - Add pytest test suite
2. **Async I/O** - Support for concurrent meter reading
3. **Configuration File** - YAML/TOML config instead of CLI args
4. **MQTT Support** - Publish to MQTT in addition to Domoticz
5. **Web Interface** - Simple dashboard for monitoring
6. **Docker Support** - Containerized deployment
7. **Home Assistant Integration** - Direct HASS support

---

## License

**Beer-ware License (Revision 42)** by Poul-Henning Kamp:

> As long as you retain this notice you can do whatever you want with this stuff.  
> If we meet some day, and you think this stuff is worth it, you can buy me a beer in return.

**Contributors:**
- Original work by Poul-Henning Kamp
- Modified by Ronald van der Meer, Frank Reijn, Paul Bonnemaijers, and Hans van Schoot
- Refactored for improved code quality and maintainability

---

## Related Projects

- **[PyKMP](https://github.com/gertvdijk/PyKMP)** - Python library for Kamstrup meters with Meter-Bus protocol
- **[Home Assistant](https://www.home-assistant.io/)** - Open source home automation (original author switched to this)
- **[Domoticz](https://www.domoticz.com/)** - Open source home automation system

---

## Support

This is an archived community project. For issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [REFACTORING_NOTES.md](REFACTORING_NOTES.md) for implementation details
3. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
4. Review original author's alternative: [PyKMP](https://github.com/gertvdijk/PyKMP)

---

## Changelog

### Refactored Version (2026)
- ✅ Complete modular restructure
- ✅ Added type hints throughout
- ✅ Implemented proper logging
- ✅ Enhanced error handling
- ✅ Comprehensive documentation
- ✅ Code quality improvements

### Original Version
- Basic functionality for Kamstrup Multical 402
- Single file implementation
- Domoticz integration

---

**Happy monitoring! 🌡️💧⚡**

"""
Configuration constants for Kamstrup Multical 402 reader.
"""
from enum import IntEnum
from typing import Dict

# Kamstrup Multical 402 variables with their command numbers
KAMSTRUP_402_VARIABLES: Dict[int, str] = {
    0x003C: "Heat Energy (E1)",         # 60
    0x0050: "Power",                    # 80
    0x0056: "Temp1",                    # 86
    0x0057: "Temp2",                    # 87
    0x0059: "Tempdiff",                 # 89
    0x004A: "Flow",                     # 74
    0x0044: "Volume",                   # 68
    0x008D: "MinFlow_M",                # 141
    0x008B: "MaxFlow_M",                # 139
    0x008C: "MinFlowDate_M",            # 140
    0x008A: "MaxFlowDate_M",            # 138
    0x0091: "MinPower_M",               # 145
    0x008F: "MaxPower_M",               # 143
    0x0095: "AvgTemp1_M",               # 149
    0x0096: "AvgTemp2_M",               # 150
    0x0090: "MinPowerDate_M",           # 144
    0x008E: "MaxPowerDate_M",           # 142
    0x007E: "MinFlow_Y",                # 126
    0x007C: "MaxFlow_Y",                # 124
    0x007D: "MinFlowDate_Y",            # 125
    0x007B: "MaxFlowDate_Y",            # 123
    0x0082: "MinPower_Y",               # 130
    0x0080: "MaxPower_Y",               # 128
    0x0092: "AvgTemp1_Y",               # 146
    0x0093: "AvgTemp2_Y",               # 147
    0x0081: "MinPowerDate_Y",           # 129
    0x007F: "MaxPowerDate_Y",           # 127
    0x0061: "Temp1xm3",                 # 97
    0x006E: "Temp2xm3",                 # 110
    0x0071: "Infoevent",                # 113
    0x03EC: "HourCounter",              # 1004
}

# Units mapping (provided by Erik Jensen)
UNITS: Dict[int, str] = {
    0: '', 1: 'Wh', 2: 'kWh', 3: 'MWh', 4: 'GWh', 5: 'j', 6: 'kj', 7: 'Mj',
    8: 'Gj', 9: 'Cal', 10: 'kCal', 11: 'Mcal', 12: 'Gcal', 13: 'varh',
    14: 'kvarh', 15: 'Mvarh', 16: 'Gvarh', 17: 'VAh', 18: 'kVAh',
    19: 'MVAh', 20: 'GVAh', 21: 'kW', 22: 'kW', 23: 'MW', 24: 'GW',
    25: 'kvar', 26: 'kvar', 27: 'Mvar', 28: 'Gvar', 29: 'VA', 30: 'kVA',
    31: 'MVA', 32: 'GVA', 33: 'V', 34: 'A', 35: 'kV', 36: 'kA', 37: 'C',
    38: 'K', 39: 'l', 40: 'm3', 41: 'l/h', 42: 'm3/h', 43: 'm3xC',
    44: 'ton', 45: 'ton/h', 46: 'h', 47: 'hh:mm:ss', 48: 'yy:mm:dd',
    49: 'yyyy:mm:dd', 50: 'mm:dd', 51: '', 52: 'bar', 53: 'RTC',
    54: 'ASCII', 55: 'm3 x 10', 56: 'ton x 10', 57: 'GJ x 10',
    58: 'minutes', 59: 'Bitfield', 60: 's', 61: 'ms', 62: 'days',
    63: 'RTC-Q', 64: 'Datetime'
}

# Byte values which must be escaped before transmission
ESCAPE_BYTES: Dict[int, bool] = {
    0x06: True,
    0x0d: True,
    0x1b: True,
    0x40: True,
    0x80: True,
}

# CRC polynomial for CCITT CRC-16
CRC_POLYNOMIAL = 0x1021

# Serial communication settings
SERIAL_BAUDRATE = 1200
SERIAL_TIMEOUT = 5.0

# Protocol bytes
PROTOCOL_PREFIX = 0x80
PROTOCOL_START = 0x40
PROTOCOL_END = 0x0d
PROTOCOL_ESCAPE = 0x1b
PROTOCOL_CMD_READ = 0x3f
PROTOCOL_CMD_TYPE = 0x10


class ProcessingMode(IntEnum):
    """Processing modes for value calculations."""
    OVERWRITE = 0      # Update with current value
    SUBTRACT = 1       # Subtract comparison value from current
    ADD = 2            # Add difference to stored value

"""
Kamstrup Multical 402 serial communication handler.

This module provides a clean interface for reading data from a Kamstrup Multical 402
heat meter via serial communication using an IR optical probe.
"""
import logging
import math
from typing import Optional, Tuple
import serial

from config import (
    ESCAPE_BYTES, CRC_POLYNOMIAL, SERIAL_BAUDRATE, SERIAL_TIMEOUT,
    PROTOCOL_PREFIX, PROTOCOL_START, PROTOCOL_END, PROTOCOL_ESCAPE,
    PROTOCOL_CMD_READ, PROTOCOL_CMD_TYPE, UNITS
)


logger = logging.getLogger(__name__)


class KamstrupCommunicationError(Exception):
    """Raised when communication with the Kamstrup device fails."""
    pass


class KamstrupReader:
    """
    Reader for Kamstrup Multical 402 heat meter.
    
    Handles serial communication with proper CRC checking and escape sequences.
    """
    
    def __init__(self, serial_port: str, debug_file: Optional[str] = None):
        """
        Initialize the Kamstrup reader.
        
        Args:
            serial_port: Path to the serial device (e.g., '/dev/ttyUSB0')
            debug_file: Optional path to debug log file for raw communication
        """
        self.serial_port = serial_port
        self.debug_file = debug_file
        self._debug_fd = None
        self._debug_id = None
        
        if debug_file:
            try:
                self._debug_fd = open(debug_file, "a")
                self._debug_fd.write("\n\n=== Session Start ===\n")
            except IOError as e:
                logger.warning(f"Could not open debug file {debug_file}: {e}")
        
        try:
            self.serial_connection = serial.Serial(
                port=serial_port,
                baudrate=SERIAL_BAUDRATE,
                timeout=SERIAL_TIMEOUT,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_TWO
            )
            logger.info(f"Serial connection established on {serial_port}")
        except serial.SerialException as e:
            logger.error(f"Failed to open serial port {serial_port}: {e}")
            raise KamstrupCommunicationError(f"Cannot open serial port: {e}") from e
    
    def __del__(self):
        """Clean up resources."""
        self.close()
    
    def close(self):
        """Close the serial connection and debug file."""
        if hasattr(self, 'serial_connection') and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info("Serial connection closed")
        
        if self._debug_fd:
            self._debug_fd.close()
            self._debug_fd = None
    
    def _debug_log(self, direction: str, data: bytearray) -> None:
        """
        Log raw communication data to debug file.
        
        Args:
            direction: 'Tx' for transmit, 'Rx' for receive
            data: Bytes to log
        """
        if not self._debug_fd:
            return
        
        try:
            if direction != self._debug_id:
                if self._debug_id is not None:
                    self._debug_fd.write("\n")
                self._debug_fd.write(f"{direction}\t")
                self._debug_id = direction
            
            for byte in data:
                self._debug_fd.write(f" {byte:02x} ")
            self._debug_fd.flush()
        except IOError as e:
            logger.warning(f"Debug logging failed: {e}")
    
    def _debug_message(self, message: str) -> None:
        """Log a debug message to the debug file."""
        if not self._debug_fd:
            return
        
        try:
            if self._debug_id is not None:
                self._debug_fd.write("\n")
            self._debug_id = "Msg"
            self._debug_fd.write(f"Msg\t{message}\n")
            self._debug_fd.flush()
        except IOError as e:
            logger.warning(f"Debug logging failed: {e}")
    
    def _write(self, data: bytearray) -> None:
        """Write bytes to serial port."""
        self._debug_log("Tx", data)
        self.serial_connection.write(data)
    
    def _read_byte(self) -> Optional[int]:
        """
        Read a single byte from serial port.
        
        Returns:
            The byte value or None on timeout
        """
        raw_data = self.serial_connection.read(1)
        if len(raw_data) == 0:
            self._debug_message("Rx Timeout")
            return None
        
        byte_value = bytearray(raw_data)[0]
        self._debug_log("Rx", bytearray((byte_value,)))
        return byte_value
    
    @staticmethod
    def _calculate_crc(message: bytearray) -> int:
        """
        Calculate CCITT CRC-16 checksum.
        
        Args:
            message: Data to calculate CRC for
            
        Returns:
            16-bit CRC value
        """
        register = 0x0000
        
        for byte in message:
            mask = 0x80
            while mask > 0:
                register <<= 1
                if byte & mask:
                    register |= 1
                mask >>= 1
                if register & 0x10000:
                    register &= 0xffff
                    register ^= CRC_POLYNOMIAL
        
        return register
    
    def _send_command(self, prefix: int, message: bytearray) -> None:
        """
        Send a command with CRC and escape sequences.
        
        Args:
            prefix: Protocol prefix byte
            message: Command message
        """
        # Add CRC placeholder
        message.append(0)
        message.append(0)
        
        # Calculate and insert CRC
        crc = self._calculate_crc(message)
        message[-2] = crc >> 8
        message[-1] = crc & 0xff
        
        # Build escaped message
        escaped_message = bytearray()
        escaped_message.append(prefix)
        
        for byte in message:
            if byte in ESCAPE_BYTES:
                escaped_message.append(PROTOCOL_ESCAPE)
                escaped_message.append(byte ^ 0xff)
            else:
                escaped_message.append(byte)
        
        escaped_message.append(PROTOCOL_END)
        self._write(escaped_message)
    
    def _receive_response(self) -> Optional[bytearray]:
        """
        Receive and unescape a response message.
        
        Returns:
            Unescaped message without CRC, or None on timeout/error
        """
        raw_message = bytearray()
        
        # Read until end marker
        while True:
            byte = self._read_byte()
            if byte is None:
                return None
            
            if byte == PROTOCOL_START:
                raw_message = bytearray()
            
            raw_message.append(byte)
            
            if byte == PROTOCOL_END:
                break
        
        # Unescape the message
        unescaped = bytearray()
        i = 1  # Skip start byte
        
        while i < len(raw_message) - 1:  # Skip end byte
            if raw_message[i] == PROTOCOL_ESCAPE:
                unescaped_byte = raw_message[i + 1] ^ 0xff
                if unescaped_byte not in ESCAPE_BYTES:
                    self._debug_message(f"Invalid escape sequence: {unescaped_byte:02x}")
                unescaped.append(unescaped_byte)
                i += 2
            else:
                unescaped.append(raw_message[i])
                i += 1
        
        # Verify CRC
        if self._calculate_crc(unescaped):
            self._debug_message("CRC error")
            logger.warning("CRC verification failed")
            return None
        
        # Return message without CRC
        return unescaped[:-2]
    
    def read_variable(self, command_number: int) -> Tuple[Optional[float], Optional[str]]:
        """
        Read a variable from the Kamstrup device.
        
        Args:
            command_number: The variable command number to read
            
        Returns:
            Tuple of (value, unit) or (None, None) on error
            
        Raises:
            KamstrupCommunicationError: If communication fails
        """
        logger.debug(f"Reading variable {command_number:#06x}")
        
        # Build and send command
        command = bytearray([
            PROTOCOL_CMD_READ,
            PROTOCOL_CMD_TYPE,
            0x01,
            command_number >> 8,
            command_number & 0xff
        ])
        
        self._send_command(PROTOCOL_PREFIX, command)
        
        # Receive response
        response = self._receive_response()
        if response is None:
            logger.error(f"No response received for command {command_number:#06x}")
            return (None, None)
        
        # Validate response
        if len(response) < 7:
            logger.error(f"Response too short: {len(response)} bytes")
            return (None, None)
        
        if response[0] != PROTOCOL_CMD_READ or response[1] != PROTOCOL_CMD_TYPE:
            logger.error("Invalid response header")
            return (None, None)
        
        if response[2] != (command_number >> 8) or response[3] != (command_number & 0xff):
            logger.error("Response command number mismatch")
            return (None, None)
        
        # Parse unit
        unit_code = response[4]
        unit = UNITS.get(unit_code)
        if unit is None:
            logger.warning(f"Unknown unit code: {unit_code}")
            unit = ""
        
        # Parse mantissa
        mantissa_length = response[5]
        mantissa = 0
        for i in range(mantissa_length):
            mantissa <<= 8
            mantissa |= response[i + 7]
        
        # Parse exponent
        exponent_byte = response[6]
        exponent = exponent_byte & 0x3f
        if exponent_byte & 0x40:
            exponent = -exponent
        
        # Calculate value
        value = mantissa * math.pow(10, exponent)
        if exponent_byte & 0x80:
            value = -value
        
        logger.debug(f"Read value: {value} {unit}")
        return (value, unit)

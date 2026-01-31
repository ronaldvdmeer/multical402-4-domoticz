"""
Value processing logic for Kamstrup readings.

This module handles the different processing modes for combining
Kamstrup readings with Domoticz device values.
"""
import logging
from typing import Optional
from dataclasses import dataclass

from config import ProcessingMode
from domoticz_client import DomoticzClient


logger = logging.getLogger(__name__)


@dataclass
class ValueParameter:
    """Represents a value processing parameter from command line."""
    device_idx: int
    command_number: int
    mode: ProcessingMode
    compare_idx: Optional[int] = None
    
    @classmethod
    def from_string(cls, param_string: str) -> 'ValueParameter':
        """
        Parse a parameter string in format 'idx:CommandNr:opt[:idx2]'.
        
        Args:
            param_string: Parameter string to parse
            
        Returns:
            ValueParameter object
            
        Raises:
            ValueError: If the format is invalid
        """
        parts = param_string.split(':')
        
        if len(parts) not in [3, 4]:
            raise ValueError(
                f"Invalid parameter format: {param_string}. "
                "Expected 'idx:CommandNr:opt' or 'idx:CommandNr:opt:idx2'"
            )
        
        try:
            device_idx = int(parts[0], 0)  # Support hex with 0x prefix
            command_number = int(parts[1], 0)
            mode = ProcessingMode(int(parts[2], 0))
            compare_idx = int(parts[3], 0) if len(parts) == 4 else None
            
            # Validate that compare_idx is provided when needed
            if mode in (ProcessingMode.SUBTRACT, ProcessingMode.ADD) and compare_idx is None:
                raise ValueError(
                    f"Mode {mode.name} requires a comparison device idx (idx2)"
                )
            
            return cls(
                device_idx=device_idx,
                command_number=command_number,
                mode=mode,
                compare_idx=compare_idx
            )
            
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid parameter format: {param_string}") from e


class ValueProcessor:
    """
    Processes Kamstrup readings according to different modes.
    
    Supports three processing modes:
    - OVERWRITE (0): Use current reading directly
    - SUBTRACT (1): Subtract comparison device value from current reading
    - ADD (2): Add difference to stored device value
    """
    
    def __init__(self, domoticz_client: DomoticzClient):
        """
        Initialize the value processor.
        
        Args:
            domoticz_client: Client for accessing Domoticz devices
        """
        self.domoticz = domoticz_client
    
    def process_value(
        self,
        current_value: float,
        parameter: ValueParameter
    ) -> Optional[float]:
        """
        Process a value according to the specified mode.
        
        Args:
            current_value: The raw value from Kamstrup
            parameter: Processing parameters
            
        Returns:
            Processed value or None if processing fails
        """
        value = round(current_value, 2)
        
        if parameter.mode == ProcessingMode.OVERWRITE:
            return self._process_overwrite(value, parameter)
        
        elif parameter.mode == ProcessingMode.SUBTRACT:
            return self._process_subtract(value, parameter)
        
        elif parameter.mode == ProcessingMode.ADD:
            return self._process_add(value, parameter)
        
        else:
            logger.error(f"Unknown processing mode: {parameter.mode}")
            return None
    
    def _process_overwrite(
        self,
        value: float,
        parameter: ValueParameter
    ) -> float:
        """
        Mode 0: Simply return the current value.
        
        Args:
            value: Current reading value
            parameter: Processing parameters
            
        Returns:
            The unchanged value
        """
        logger.debug(
            f"Mode OVERWRITE: Using value {value} for device {parameter.device_idx}"
        )
        return value
    
    def _process_subtract(
        self,
        value: float,
        parameter: ValueParameter
    ) -> Optional[float]:
        """
        Mode 1: Subtract comparison device value from current reading.
        
        Args:
            value: Current reading value
            parameter: Processing parameters (must include compare_idx)
            
        Returns:
            Difference value or None if comparison device cannot be read
        """
        if parameter.compare_idx is None:
            logger.error("SUBTRACT mode requires compare_idx")
            return None
        
        compare_value = self.domoticz.get_device_numeric_value(parameter.compare_idx)
        if compare_value is None:
            logger.error(
                f"Could not read comparison device {parameter.compare_idx} "
                f"for SUBTRACT mode"
            )
            return None
        
        difference = value - compare_value
        difference = round(difference, 2)
        
        logger.debug(
            f"Mode SUBTRACT: {value} - {compare_value} "
            f"(idx:{parameter.compare_idx}) = {difference}"
        )
        
        return difference
    
    def _process_add(
        self,
        value: float,
        parameter: ValueParameter
    ) -> Optional[float]:
        """
        Mode 2: Add difference to stored device value.
        
        This mode:
        1. Gets current value from target device
        2. Gets value from comparison device
        3. Calculates: difference = current_reading - comparison_device
        4. Returns: target_device + difference
        
        Args:
            value: Current reading value
            parameter: Processing parameters (must include compare_idx)
            
        Returns:
            Sum value or None if device values cannot be read
        """
        if parameter.compare_idx is None:
            logger.error("ADD mode requires compare_idx")
            return None
        
        # Get stored value from target device
        device_value = self.domoticz.get_device_numeric_value(parameter.device_idx)
        if device_value is None:
            logger.error(
                f"Could not read target device {parameter.device_idx} "
                f"for ADD mode"
            )
            return None
        
        # Get comparison value
        compare_value = self.domoticz.get_device_numeric_value(parameter.compare_idx)
        if compare_value is None:
            logger.error(
                f"Could not read comparison device {parameter.compare_idx} "
                f"for ADD mode"
            )
            return None
        
        # Calculate difference and add to stored value
        difference = value - compare_value
        result = device_value + difference
        result = round(result, 2)
        
        logger.debug(
            f"Mode ADD: {device_value} (idx:{parameter.device_idx}) + "
            f"({value} - {compare_value} (idx:{parameter.compare_idx})) = {result}"
        )
        
        return result

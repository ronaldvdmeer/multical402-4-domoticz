"""
Domoticz API client for device management and data updates.

This module provides a clean interface for interacting with the Domoticz
home automation system via its JSON API.
"""
import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


logger = logging.getLogger(__name__)


class DomoticzError(Exception):
    """Raised when Domoticz API communication fails."""
    pass


@dataclass
class DomoticzDevice:
    """Represents a Domoticz device with its properties."""
    idx: int
    name: str
    value: str
    
    @classmethod
    def from_api_response(cls, device_data: Dict[str, Any]) -> 'DomoticzDevice':
        """Create a DomoticzDevice from API response data."""
        return cls(
            idx=int(device_data['idx']),
            name=device_data['Name'],
            value=device_data['Data']
        )


class DomoticzClient:
    """
    Client for interacting with Domoticz home automation system.
    
    Handles device queries and value updates through the JSON API.
    """
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        """
        Initialize the Domoticz client.
        
        Args:
            host: Domoticz server hostname or IP address
            port: Domoticz server port number
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        logger.info(f"Domoticz client initialized for {self.base_url}")
    
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """
        Make an HTTP request to the Domoticz API.
        
        Args:
            endpoint: API endpoint (without base URL)
            
        Returns:
            Parsed JSON response
            
        Raises:
            DomoticzError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(f"Making request to: {url}")
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
        except urllib.error.URLError as e:
            logger.error(f"Failed to connect to Domoticz at {url}: {e}")
            raise DomoticzError(f"Cannot connect to Domoticz: {e}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Domoticz: {e}")
            raise DomoticzError(f"Invalid JSON response: {e}") from e
    
    def get_device(self, idx: int) -> Optional[DomoticzDevice]:
        """
        Get device information by index.
        
        Args:
            idx: Device index number
            
        Returns:
            DomoticzDevice object or None if not found
            
        Raises:
            DomoticzError: If the API request fails
        """
        try:
            endpoint = f"/json.htm?type=devices&rid={idx}"
            data = self._make_request(endpoint)
            
            if 'result' not in data or len(data['result']) == 0:
                logger.warning(f"Device with idx {idx} not found")
                return None
            
            device = DomoticzDevice.from_api_response(data['result'][0])
            logger.debug(f"Retrieved device {idx}: {device.name} = {device.value}")
            return device
            
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected API response format: {e}")
            raise DomoticzError(f"Invalid device data format: {e}") from e
    
    def get_all_devices(self) -> List[DomoticzDevice]:
        """
        Get all devices from Domoticz.
        
        Returns:
            List of DomoticzDevice objects
            
        Raises:
            DomoticzError: If the API request fails
        """
        try:
            endpoint = "/json.htm?type=devices"
            data = self._make_request(endpoint)
            
            if 'result' not in data:
                logger.warning("No devices found in Domoticz")
                return []
            
            devices = [
                DomoticzDevice.from_api_response(device_data)
                for device_data in data['result']
            ]
            logger.info(f"Retrieved {len(devices)} devices from Domoticz")
            return devices
            
        except (KeyError, TypeError) as e:
            logger.error(f"Unexpected API response format: {e}")
            raise DomoticzError(f"Invalid devices data format: {e}") from e
    
    def update_device(self, idx: int, value: float) -> bool:
        """
        Update a device with a new value.
        
        Args:
            idx: Device index number
            value: New value to set
            
        Returns:
            True if update was successful, False otherwise
            
        Raises:
            DomoticzError: If the API request fails
        """
        try:
            endpoint = f"/json.htm?type=command&param=udevice&idx={idx}&svalue={value}"
            data = self._make_request(endpoint)
            
            # Check if update was successful
            status = data.get('status', '').lower()
            success = status == 'ok'
            
            if success:
                logger.info(f"Successfully updated device {idx} to {value}")
            else:
                logger.warning(f"Update may have failed for device {idx}: status={status}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update device {idx}: {e}")
            raise DomoticzError(f"Device update failed: {e}") from e
    
    def get_device_numeric_value(self, idx: int) -> Optional[float]:
        """
        Get the numeric value from a device, parsing it from the Data field.
        
        Args:
            idx: Device index number
            
        Returns:
            Numeric value or None if device not found or value cannot be parsed
        """
        device = self.get_device(idx)
        if device is None:
            return None
        
        try:
            # Extract numeric part (values often come as "123.45 Unit")
            value_str = device.value.split()[0]
            return float(value_str)
        except (ValueError, IndexError) as e:
            logger.warning(f"Could not parse numeric value from '{device.value}': {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test the connection to Domoticz.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self._make_request("/json.htm?type=devices")
            logger.info("Domoticz connection test successful")
            return True
        except DomoticzError:
            logger.error("Domoticz connection test failed")
            return False

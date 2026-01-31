#!/usr/bin/env python3
"""
Kamstrup Multical 402 to Domoticz integration script.

Reads data from a Kamstrup Multical 402 heat meter via IR optical probe
and sends it to Domoticz home automation system.

Original work by Poul-Henning Kamp (Beer-ware license)
Modified by Ronald van der Meer, Frank Reijn, Paul Bonnemaijers, and Hans van Schoot
Refactored for better maintainability and code quality.
"""
import sys
import os
import argparse
import logging
from datetime import datetime
from typing import List

from config import KAMSTRUP_402_VARIABLES
from kamstrup_reader import KamstrupReader, KamstrupCommunicationError
from domoticz_client import DomoticzClient, DomoticzError
from value_processor import ValueParameter, ValueProcessor


def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        verbose: Enable INFO level logging
        debug: Enable DEBUG level logging
    """
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def validate_parameters(parameters: List[str]) -> List[ValueParameter]:
    """
    Validate and parse parameter strings.
    
    Args:
        parameters: List of parameter strings in format 'idx:CommandNr:opt[:idx2]'
        
    Returns:
        List of parsed ValueParameter objects
        
    Raises:
        SystemExit: If any parameter is invalid
    """
    parsed_params = []
    
    for param_string in parameters:
        try:
            param = ValueParameter.from_string(param_string)
            parsed_params.append(param)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    return parsed_params


def test_kamstrup(reader: KamstrupReader) -> None:
    """
    Test the Kamstrup interface by reading all known variables.
    
    Args:
        reader: Initialized KamstrupReader instance
    """
    print("\n=== Testing Kamstrup Interface ===\n")
    
    for command_number, name in KAMSTRUP_402_VARIABLES.items():
        value, unit = reader.read_variable(command_number)
        print(f"CommandNr {command_number:4d}: {name:25s} {value} {unit}")
    
    print("\n=== Test Complete ===\n")


def test_domoticz(client: DomoticzClient) -> None:
    """
    Test the Domoticz connection by listing all devices.
    
    Args:
        client: Initialized DomoticzClient instance
    """
    print("\n=== Testing Domoticz Connection ===\n")
    
    try:
        devices = client.get_all_devices()
        
        for device in devices:
            print(f"idx: {device.idx:5d}, Name: {device.name:60s}, Value: {device.value}")
        
        print(f"\n=== Found {len(devices)} devices ===\n")
        
    except DomoticzError as e:
        print(f"Error: Failed to connect to Domoticz: {e}")
        sys.exit(1)


def print_header(timestamp: str) -> None:
    """Print formatted header for data output."""
    print("=" * 87)
    print(f"Kamstrup Multical 402 serial optical data received: {timestamp}")
    print("Meter vendor/type: Kamstrup M402")
    print("-" * 87)


def print_footer(timestamp: str) -> None:
    """Print formatted footer for data output."""
    print("-" * 87)
    print(f"End data received: {timestamp}")
    print("=" * 87)


def process_parameters(
    reader: KamstrupReader,
    client: DomoticzClient,
    parameters: List[ValueParameter],
    verbose: bool = False
) -> None:
    """
    Process all parameters: read from Kamstrup, calculate, and update Domoticz.
    
    Args:
        reader: KamstrupReader instance
        client: DomoticzClient instance
        parameters: List of parameters to process
        verbose: Enable verbose output
    """
    processor = ValueProcessor(client)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print_header(timestamp)
    
    # Collect all unique command numbers to read
    commands_to_read = {param.command_number for param in parameters}
    
    for command_number in sorted(commands_to_read):
        # Only read variables that are needed
        if command_number not in KAMSTRUP_402_VARIABLES:
            logging.warning(f"Unknown command number: {command_number}")
            continue
        
        variable_name = KAMSTRUP_402_VARIABLES[command_number]
        
        # Read value from Kamstrup
        try:
            raw_value, unit = reader.read_variable(command_number)
            if raw_value is None:
                logging.error(f"Failed to read {variable_name}")
                continue
            
            print(f"{variable_name:25s} {raw_value} {unit}")
            
        except KamstrupCommunicationError as e:
            logging.error(f"Communication error reading {variable_name}: {e}")
            continue
        
        # Process all parameters using this command number
        for param in parameters:
            if param.command_number != command_number:
                continue
            
            try:
                # Calculate processed value
                processed_value = processor.process_value(raw_value, param)
                if processed_value is None:
                    logging.error(f"Failed to process value for device {param.device_idx}")
                    continue
                
                # Get device name for logging
                device = client.get_device(param.device_idx)
                device_name = device.name if device else f"idx:{param.device_idx}"
                
                # Update Domoticz
                print(
                    f"  + Mode {param.mode.value}: Submit value {processed_value} "
                    f"to '{device_name}' (idx: {param.device_idx})"
                )
                
                client.update_device(param.device_idx, processed_value)
                
            except DomoticzError as e:
                logging.error(f"Domoticz error for device {param.device_idx}: {e}")
                continue
    
    print_footer(timestamp)


def main() -> None:
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Read Kamstrup Multical 402 data and send to Domoticz",
        epilog="""
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

Examples:
  %(prog)s -d /dev/ttyUSB0 88:60:0 89:80:0
  %(prog)s -d /dev/ttyUSB0 --ip 192.168.1.100 88:60:0 89:80:1:90
"""
    )
    
    parser.add_argument(
        "-d", "--device",
        type=str,
        required=True,
        help="Serial device to use (e.g., /dev/ttyUSB0)"
    )
    parser.add_argument(
        "--ip",
        type=str,
        default="localhost",
        help="Domoticz IP address (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Domoticz port (default: 8080)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output and logging"
    )
    parser.add_argument(
        "--debug-file",
        type=str,
        default="/tmp/_kamstrup",
        help="Debug file for raw serial communication (default: /tmp/_kamstrup)"
    )
    parser.add_argument(
        "--test_kamstrup",
        action="store_true",
        help="Test the Kamstrup interface and exit"
    )
    parser.add_argument(
        "--test_domoticz",
        action="store_true",
        help="Test the Domoticz connection and exit"
    )
    parser.add_argument(
        "values",
        type=str,
        nargs='*',
        help="Value parameters in format idx:CommandNr:opt[:idx2]"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose, debug=args.debug)
    
    # Validate device exists
    if not os.path.exists(args.device):
        print(f"Error: Device not found: {args.device}")
        sys.exit(1)
    
    # Validate that we have something to do
    if not (args.test_kamstrup or args.test_domoticz) and len(args.values) == 0:
        print("Error: No values specified. Use --help to see usage.")
        sys.exit(1)
    
    # Initialize clients
    try:
        debug_file = args.debug_file if args.debug else None
        reader = KamstrupReader(args.device, debug_file=debug_file)
        client = DomoticzClient(host=args.ip, port=args.port)
    except (KamstrupCommunicationError, DomoticzError) as e:
        print(f"Error: Initialization failed: {e}")
        sys.exit(1)
    
    try:
        # Handle test modes
        if args.test_kamstrup:
            test_kamstrup(reader)
            return
        
        if args.test_domoticz:
            test_domoticz(client)
            return
        
        # Parse and validate parameters
        parameters = validate_parameters(args.values)
        
        # Process all parameters
        process_parameters(reader, client, parameters, verbose=args.verbose)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.exception("Unexpected error occurred")
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        reader.close()


if __name__ == "__main__":
    main()

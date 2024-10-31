# Student name: Linda Mafunu
# Student number: 2216686
# Date: 12 Sep 2024

# Fuzzing script to send sequental CAN messages to the BCM
# Uses pre-defined sequence of inputs in incrementing oder
# each input is generated basd on the previous one creating a predicatble pattern
##### Code Source: 
#    https://github.com/FrostTusk/CAN-Fuzzer/blob/master/fuzzer.py

import can
import time
import logging
import os
from logging.handlers import RotatingFileHandler

class Linear_Fuzzer:
    def __init__(self, interface):
        # Set up logging
        log_path = 'Fuzzer/Fuzzing.log'
        handler = RotatingFileHandler(log_path, mode='w', maxBytes=5*1024*1024, backupCount=2)
        with open(log_path, 'w'):
            pass
        logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s')
        
        try:
            self.bus = can.interface.Bus(interface, bustype='socketcan')
        except Exception as e:
            logging.error(f"Failed to initialize CAN interface: {e}")
            exit(1)
        self.d_msg = 'None'
        
    def log_message(self, message):
        can_id = message.arbitration_id
        data = message.data
        log_entry = (
            f"CAN ID: {can_id}\n"
            f"Data: {data}\n"
            f"Diagnostic message: {self.d_msg}"
        )
        logging.info(log_entry)

    def generate_linear_message(self, start_id, end_id, start_data, end_data):
        """Generate linearly increasing CAN message."""
        current_id = start_id  # Start with the initial CAN ID
        current_data_len = start_data  # Start with initial data length

        while current_id <= end_id:
            data = [current_id & 0xFF] * current_data_len  # Fill data with CAN ID byte
            message = can.Message(
                arbitration_id=current_id,
                data=data,
                is_extended_id=False
            )
            yield message

            current_id += 1
            current_data_len = min(current_data_len + 1, end_data)  # Increment data length up to end_data

    def fuzz_can_bus(self):
        """Send linearly increasing CAN messages to the bus with retry handling."""
        start_id = 0x000
        end_id = 0x7FF
        start_data = 1
        end_data = 8

        message_generator = self.generate_linear_message(start_id, end_id, start_data, end_data)
        max_retries = 5
        
        for message in message_generator:
            retry_count = 0
            while retry_count < max_retries:
                try:
                    self.bus.send(message)
                    self.d_msg = "Linear Fuzzing"
                    self.log_message(message)
                    break  # Message sent successfully, exit retry loop
                except can.CanError as e:
                    if "Transmit buffer full" in str(e):
                        self.d_msg = "Transmit buffer full, retrying..."
                        logging.warning(self.d_msg)
                        retry_count += 1
                        time.sleep(0.5)  # Short pause before retrying
                    else:
                        self.d_msg = f"Failed to send Linear fuzzing message: {e}"
                        logging.error(self.d_msg)
                        break  # Break if it's a different error

            # Restart CAN interface if max retries exceeded
            if retry_count == max_retries:
                logging.error("Max retries reached, restarting CAN interface.")
                self.restart_can_interface('can0', 500000)

    def restart_can_interface(self, interface, bitrate):
        """Restart CAN interface to clear buffer if max retries reached."""
        os.system(f"sudo ip link set {interface} down")
        time.sleep(1)
        os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")
        os.system(f"sudo ifconfig {interface} txqueuelen 5000")
        time.sleep(2)
        logging.info(f"{interface} interface restarted with bitrate {bitrate}.")

    def run(self, duration):
        """Run linear fuzzing for a specified duration."""
        try:
            start_time = time.time()
            while time.time() - start_time < duration:
                self.fuzz_can_bus()
                time.sleep(0.02)  # Delay between sequences
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt detected, stopping fuzzing.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

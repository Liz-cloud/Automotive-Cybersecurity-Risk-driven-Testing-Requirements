# Student name: Linda Mafunu
# Student number: 2216686
# Date: 10 Sep 2024

# Fuzzing script to send random CAN messages to the BCM

# SOURCE1: https://www.fuzzingbook.org/html/Fuzzer.html
# source2: https://github.com/FrostTusk/CAN-Fuzzer/blob/master/fuzzer.py


import can
import time
import random
import logging
import os
from logging.handlers import RotatingFileHandler

class Random_Fuzzer:
    def __init__(self, interface):
        # Set up logging
        log_path = '/home/linda-mafunu/Desktop/Automotive-Cybersecurity-Risk-driven-Testing-Requirements/Fuzzer/Fuzzing.log'
        handler = RotatingFileHandler(log_path, mode='w', maxBytes=5*1024*1024, backupCount=2)
        with open(log_path, 'w'):
            pass
        logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s')

        try:
            print('CAN Interface UP!')
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

    def generate_random_message(self):
        """Generate a random CAN message."""
        can_id = random.randint(0, 0x7FF)  # Standard CAN ID (11 bits)
        data = [random.randint(0, 0xFF) for _ in range(8)]  # Random CAN data bytes (0-8)

        message = can.Message(
            arbitration_id=can_id,
            data=data,
            is_extended_id=False
        )
        return message

    def fuzz_can_bus(self):
        """Send random CAN messages to the bus."""
        message = self.generate_random_message()
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.bus.send(message)
                self.d_msg = "Random Fuzzing"
                self.log_message(message)
                break  # Message sent successfully, exit loop
            except can.CanError as e:
                if "Transmit buffer full" in str(e):
                    self.d_msg = "Transmit buffer full, retrying..."
                    logging.warning(self.d_msg)
                    retry_count += 1
                    time.sleep(0.5)  # Brief pause before retrying
                else:
                    self.d_msg = f"Failed to send Random fuzzing message: {e}"
                    logging.error(self.d_msg)
                    break  # Exit if it's a different error
          

        # If max retries reached, log and restart CAN interface
        if retry_count == max_retries:
            logging.error("Max retries reached, restarting CAN interface.")
            self.restart_can_interface('can0', 500000)

    def restart_can_interface(self, interface, bitrate):
        os.system(f"sudo ip link set {interface} down")
        time.sleep(1)
        os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")
        os.system(f"sudo ifconfig {interface} txqueuelen 5000")
        time.sleep(2)  # Give the interface time to stabilize
        logging.info(f"{interface} interface restarted with bitrate {bitrate}.")

    def run(self, duration):
        """Send random CAN messages to the bus in time interval."""
        try:
            start_time = time.time()
            while time.time() - start_time < duration:
                self.fuzz_can_bus()
                time.sleep(0.02)  # Delay between messages
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt detected, stopping fuzzing.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")


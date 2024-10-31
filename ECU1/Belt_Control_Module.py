# Student name: Linda Mafunu
# Student number: 2216686
# Date: 10 Sep 2024

# This script simulates belt status messages sent to the BCM.
# It sends a message to update the belt status (ON/OFF).
# Priority is MEDIUM
# This status is important but not as safety-critical as headlight status.

# Code foundation :  https://github.com/hardbyte/python-can/tree/main 

import can
import time
import random
import logging
import hmac
import os
import hashlib
from logging.handlers import RotatingFileHandler

class Belt_Status_Module:

    def __init__(self, interface):
        # Set up logging
        log_path = '/home/lindamafunu/Desktop/Automotive-Cybersecurity-Risk-driven-Testing-Requirements/ECU1/Sensor.log'
        handler = RotatingFileHandler(log_path, mode='w', maxBytes=5*1024*1024, backupCount=2)

        # Clear the log file at the start of each run
        with open(log_path, 'w'):
            pass  # this will clear the file content
        logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s')

        try:
            self.bus = can.interface.Bus(interface, bustype='socketcan')
        except Exception as e:
            logging.error(f"Failed to initialize CAN interface: {e}")
            exit(1)

        self.BELT_STATUS_ID = 0x100  # CAN ID for belt status
        self.SECRET_KEY = b'key'
        self.last_status_sent = None  # Track last status to avoid redundancy
        self.destination = 'BCM'
        self.origin = 'BSM'
        self.d_msg = 'None'
        self.error = 'None'

    # Source: https://github.com/nishantm77/sha256converter/blob/main/sourcefile.py
    def generate_mac(self, data):
        mac = hmac.new(self.SECRET_KEY, data, hashlib.sha256).digest()
        return mac[:3]  # Use first 3 bytes of SHA-256 hash

    def log_message(self, message):
        can_id = message.arbitration_id
        data = message.data
        # Prepare the log entry
        log_entry = (
            f'CAN ID: {can_id}\n'
            f'Data: {data}\n'
            f'Origin: {self.origin}\n'
            f'Destination: {self.destination}\n'
            f'Diagnostic Msg: {self.d_msg}\n'
            f'Error: {self.error}\n'
        )

        # Log the entry
        logging.info(log_entry)

    def send_bcm_command(self, status, max_retries=3):
        """Send belt status to BCM with retries and CAN interface restart."""

        retry_count = 0
        while retry_count < max_retries:
            # Avoid sending the same status repeatedly
            if self.last_status_sent == status:
                return  # Avoid redundant messages

            self.last_status_sent = status

            # Add a timestamp to the message
            timestamp = int(time.time())  # Current time in seconds
            timestamp_bytes = timestamp.to_bytes(4, 'big')
            msg_data = [status] + list(timestamp_bytes)

            # Authenticate CAN messages by adding MAC tags
            mac = self.generate_mac(bytearray(msg_data))
            msg_data = msg_data + list(mac)
            msg_data = msg_data[:8]  # Truncate to 8 bytes

            status_message = can.Message(
                arbitration_id=self.BELT_STATUS_ID,
                data=msg_data,
                is_extended_id=False
            )

            try:
                self.bus.send(status_message)
                self.log_message(status_message)
                break  # Exit loop on success
            except can.CanError as e:
                self.error = f"Failed to send status message: {e}"
                retry_count += 1
                logging.error(f"Retry {retry_count}/{max_retries} - CAN send failed: {e}")
                time.sleep(0.5)

            # If max retries are reached, restart CAN interface
            if retry_count == max_retries:
                logging.error("Max retries reached, restarting CAN interface.")
                self.restart_can_interface('can0', 500000)

    def restart_can_interface(self, interface, bitrate):
        """Restart CAN interface with specified bitrate and txqueuelen."""
        os.system(f"sudo ip link set {interface} down")
        time.sleep(1)
        os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")
        os.system(f"sudo ifconfig {interface} txqueuelen 5000")
        time.sleep(2)
        logging.info(f"{interface} interface restarted with bitrate {bitrate}.")

    def send_belt_data(self, duration):
        """Continuously send belt status for a specified duration."""
        
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                elapsed_time = time.time() - start_time
                # Define probabilities for belt_off and belt_on based on elapsed time
                # belt_off_weight = max(0.1, 1 - (elapsed_time / duration))  # Gradually decreases
                # belt_on_weight = 1 - belt_off_weight  # Increases as belt_off_weight decreases

                # belt_status = random.choices([0x04, 0x05], weights=[belt_off_weight, belt_on_weight])[0]
                belt_status=0x04
                self.d_msg = 'Belt is OFF' if belt_status == 0x04 else 'Belt is ON'

                self.send_bcm_command(belt_status)
                time.sleep(0.1)  # Adjust the sleep duration as needed

            except KeyboardInterrupt:
                logging.info("KeyboardInterrupt detected, stopping belt status transmission.")
                break

# if __name__ == '__main__':
#     bsm = Belt_Status_Module('can0')
#     bsm.send_belt_data(duration=30)

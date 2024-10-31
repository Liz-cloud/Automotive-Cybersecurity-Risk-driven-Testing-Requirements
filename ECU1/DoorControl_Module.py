
# Student name: Linda Mafunu
# Student number: 2216686
# Date: 03 Sep 2024

# This script simulates sensors and sends commands to the BCM. 
# When a door is unlocked it sends a command to turn on interior lights (yellow LED)
# CAN IDS range from 0x00-0x7FF
# Door lock status sensor systems range from 0x200 - 0x2FF
# Priority is Medium
# This status is important but not as safety-critical as seatbelt status.

# Code foundation :  https://github.com/hardbyte/python-can/tree/main

import can
import time
import can
import time
import logging
import os
import random
import hmac
import hashlib
from logging.handlers import RotatingFileHandler

class DoorControlECU:

    def __init__(self, interface):
        #setup logging
        log_path='/home/lindamafunu/Desktop/Automotive-Cybersecurity-Risk-driven-Testing-Requirements/ECU1/Sensor.log'
        handler = RotatingFileHandler(log_path, mode='w', maxBytes=5*1024*1024, backupCount=2)

        # Clear the log file at the start of each run
        with open(log_path,'w'):
            pass #this will clear the file content

        logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s')

        try:
            self.bus = can.interface.Bus(interface, bustype='socketcan')
        except Exception as e:
            logging.error(f"Failed to initialize CAN interface: {e}")
            exit(1)

        self.LOCK_STATUS_ID = 0x200
        self.SECRET_KEY = b'key'
        self.is_locked = False  # Track door lock status
        self.last_command_sent=None # keep track of command sent to avoid redudancy

        # for can messeging logging
        self.destination='BCM'
        self.origin='DCM'
        self.d_msg='None'
        self.error='None'

      #logg messages
    def log_message(self,message):
        can_id=message.arbitration_id
        data=message.data
        # Prepare the log entry
        log_entry = (
            f'CAN ID: {can_id}\n'
            f'Data: {data}\n'
            f'Origin: {self.origin}\n'
            f'Destination: { self.destination}\n'
            f'Diagnostic Msg: {self.d_msg}\n'
            f'Error:{self.error}\n')

        # Log the entry
        logging.info(log_entry)

# source: https://github.com/nishantm77/sha256converter/blob/main/sourcefile.py
    def generate_mac(self, data):
        """Generate a Message Authentication Code (MAC) using HMAC with SHA-256."""
        mac = hmac.new(self.SECRET_KEY, data, hashlib.sha256).digest()
        return mac[:3]  # Using first 3 bytes of SHA-256 hash

    def send_lock_status(self, lock_status, max_retries=3):
        """Send the door lock status message via CANwith retries and CAN interface restart."""
        retry_count = 0
        while retry_count < max_retries:
    
            # Avoid sending the same command repeatedly
            if self.last_command_sent == lock_status:
                return  # If the command is the same as the last one, do not send it again
            
            self.last_command_sent = lock_status

            # Add a timestamp to the message
            timestamp = int(time.time())  # Current time in seconds

            timestamp_bytes = timestamp.to_bytes(4, 'big')
            msg_data = [lock_status] + list(timestamp_bytes)

            # Authenticate CAN messages by adding MAC tags to CAN messages
            mac = self.generate_mac(bytearray(msg_data))
            msg_data = msg_data + list(mac)

            msg_data = msg_data[:8]  # Truncate to 8 bytes

            response_message = can.Message(
                arbitration_id=self.LOCK_STATUS_ID,
                data=msg_data,
                is_extended_id=False
            )

            try:
                self.bus.send(response_message)
                self.log_message(response_message)
                break  # Exit loop on success
            except can.CanError as e:
                self.error=f"Failed to send lock status response: {e}"
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

    def continuous_send(self,duration):
        """Continuously send door lock status until keyboard interrupt."""
    
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                elapsed_time = time.time() - start_time
                # Define probabilities for door locked and door unlocked based on elapsed time
                door_unlocked_weight = max(0.1, 1 - (elapsed_time / duration))  # Gradually decreases
                door_locked_weight = 1 - door_unlocked_weight # Increases as door_unlocked_weight decreases

                lock_status = random.choices([0x02, 0x03], weights=[door_unlocked_weight, door_locked_weight])[0]
                self.d_msg = 'Door is Unlocked' if lock_status == 0x04 else 'Door is Locked'

                self.send_lock_status(lock_status)
                time.sleep(0.1 ) # Adjust the sleep duration as needed

            except KeyboardInterrupt:
                logging.info("KeyboardInterrupt detected, stopping belt status transmission.")
                break


 

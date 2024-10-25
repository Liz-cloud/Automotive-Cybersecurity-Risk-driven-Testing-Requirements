# Student name: Linda Mafunu
# Student number: 2216686
# Date: 03 Sep 2024

# This script simulates sensors sends to the BCM. 
# When the light level drops below a 
# threshold, it sends a message to turn on the headlights to headligt control.(BLUE LED)
# light sensor and visibilty systems rangle from 0x400 - 0x4FF
# Priority is LOW-MEDIUM
# This status is important but not as safety-critical as seatbelt status.
# Code foundation :  https://github.com/hardbyte/python-can/tree/main


import can 
import time 
import random 
import os
import logging
import hmac 
import hashlib 
from logging.handlers import RotatingFileHandler

class Headlight_Control_Module: 

    def __init__(self, interface): 
        #set up logging
        log_path='/home/lindamafunu/Desktop/Final-Project/ECU1/HCM_short.log'
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

        self.LIGHT_SENSOR_ID = 0x400
        self.LIGHT_THRESHOLD = 0x3F # sensor threshold
        self.SECRET_KEY=b'key'
        self.last_command_sent = None  # Keep track of the last command sent to avoid redundant messages

        self.destination='BCM'
        self.origin='HCM'
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
            f'Error:{self.error}\n'
        )

        # Log the entry
        logging.info(log_entry)

    # The function generate_mac you've provided is designed to
    # generate a Message Authentication Code (MAC) using
    # HMAC (Hash-based Message Authentication Code) with 
    # SHA-256 as the hashing algorithm. 
    # The MAC is then truncated to the first 4 bytes of the 
    # SHA-256 hash. This function can be useful for 
    # ensuring the integrity and authenticity of data in secure communications.
    # source: https://github.com/nishantm77/sha256converter/blob/main/sourcefile.py
    
    def generate_mac(self, data): 
        mac= hmac.new(self.SECRET_KEY, data, hashlib.sha256).digest()
        return mac[:3]  # Using first 4 bytes of SHA-256 hash 
    
    def send_bcm_command(self, command, max_retries=3):
        """Send command to BCM to turn on/off headlights."""
        retry_count = 0
        
        while retry_count < max_retries:
            # Avoid sending the same command repeatedly
            if self.last_command_sent == command:
                return  # If the command is the same as the last one, do not send it again
            
            self.last_command_sent = command

            # Add a timestamp to the message
            timestamp = int(time.time())  # Current time in seconds
            timestamp_bytes = timestamp.to_bytes(4, 'big')
            msg_data = [command] + list(timestamp_bytes)

            # Authenticate CAN messages by adding MAC tags to CAN messages
            mac = self.generate_mac(bytearray(msg_data))
            msg_data = msg_data + list(mac)
            msg_data = msg_data[:8]  # Truncate to 8 bytes

            command_message = can.Message(
                arbitration_id=self.LIGHT_SENSOR_ID,
                data=msg_data,
                is_extended_id=False
            )
            
            try:
                self.bus.send(command_message)
                self.log_message(command_message)
                break  # Exit the loop on successful send
            except can.CanError as e:
                self.error = f"Failed to send command message: {e}"
                retry_count += 1
                logging.error(f"Retry {retry_count}/{max_retries} - CAN send failed: {e}")
                time.sleep(0.5)  # Short wait before retrying

            # If max retries reached, log and restart CAN interface
            if retry_count == max_retries:
                logging.error("Max retries reached, restarting CAN interface.")
                self.restart_can_interface('can0', 500000)

    def restart_can_interface(self, interface, bitrate):
        """Restart the CAN interface with specified bitrate and txqueuelen."""
        os.system(f"sudo ip link set {interface} down")
        time.sleep(1)
        os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")
        os.system(f"sudo ifconfig {interface} txqueuelen 5000")
        time.sleep(2)  # Give the interface time to stabilize
        logging.info(f"{interface} interface restarted with bitrate {bitrate}.")

    # # send command to head light control to tun on or off lights
    # def send_bcm_command(self, command):
    #     """Send command to BCM to turn on/off headlights."""

    #     # Avoid sending the same command repeatedly
    #     if self.last_command_sent == command:
    #         return  # If the command is the same as the last one, do not send it again
        
    #     self.last_command_sent = command

    #     # logging.info(f"Light Sensor ECU: Sending command {command:#04X} to BCM")

    #     # Add a timestamp to the message
    #     timestamp = int(time.time())  # Current time in seconds
    #     timestamp_bytes = timestamp.to_bytes(4, 'big')
    #     # msg_data = [command]+list(timestamp_bytes[-8:])
    #     msg_data = [command]+list(timestamp_bytes)
   
    #     # Authenticate CAN messages by adding MAC tags to CAN messages
    #     mac=self.generate_mac(bytearray(msg_data))
    #     msg_data=msg_data+list(mac)
    
    #     msg_data = msg_data[:8]  # Truncate to 8 bytes
               
    #     command_message = can.Message( 
    #         arbitration_id=self.LIGHT_SENSOR_ID, 
    #         data=msg_data, 
    #         is_extended_id=False 
    #     ) 
    #     try:
    #         self.bus.send(command_message)
    #     except can.CanError as e:
    #         #logging.error(f"Failed to send command message: {e}")
    #         self.error=f"Failed to send command message: {e}"
    #     self.log_message(command_message)


    def send_light_data(self, duration): 
        """Continuously send headlight staus until keyboard interrupt."""
        
        start_time=time.time()
        while time.time()-start_time <duration:
            try:
                elasped_time=time.time()- start_time
                #define the probabiliitoes for light_off and light_on based on elasped time
                light_off_weight=max(0.1,1-(elasped_time/duration)) #gradually decreases
                light_on_weight=1- light_off_weight # increases as light_off_weiht decreases
                light_level = random.choices([0x00, 0xFF], weights=[light_off_weight,light_on_weight])[0]  # Randomly simulate light on or off
    
                # Check if light level is below the threshold
                if light_level < self.LIGHT_THRESHOLD: 
                    self.send_bcm_command(0x01)  # Command to turn on headlights
                    self.d_msg='Headlights ON'
                else:
                    self.send_bcm_command(0x00)  # Command to turn off headlights
                    self.d_msg='Headlights OFF'
                time.sleep(0.01) 
            except KeyboardInterrupt:
                logging.info("KeyboardInterrupt detected, stopping status transmission.")
                break

# if __name__ == '__main__': 
#     hcm = Headlight_Control_Module('can0') 
#     try:
#         hcm.send_light_data(duration=30) 
#     except KeyboardInterrupt:
#         logging.info("Program terminated by user.")

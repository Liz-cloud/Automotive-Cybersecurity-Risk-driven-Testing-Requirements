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
import hashlib 
from logging.handlers import RotatingFileHandler

#set up logging

log_path='/home/lindamafunu/Desktop/Final-Project/ECU1/BeltStatus_short.log'

handler = RotatingFileHandler(log_path, mode='w', maxBytes=5*1024*1024, backupCount=2)

# Clear the log file at the start of each run
with open(log_path,'w'):
    pass # This will clear the file content

logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s')

class Belt_Status_Module: 

    def __init__(self, interface): 

        try: 
            self.bus = can.interface.Bus(interface, bustype='socketcan') 
        except Exception as e: 
            logging.error(f"Failed to initialize CAN interface: {e}") 
            exit(1) 

        self.BELT_STATUS_ID = 0x100  # CAN ID for belt status
        self.SECRET_KEY = b'key'
        self.last_status_sent = None  # Keep track of the last status sent to avoid redundant messages
        self.destination='BCM'
        self.origin='BSM'
        self.d_msg='None'
        self.error='None'

# source: https://github.com/nishantm77/sha256converter/blob/main/sourcefile.py
    def generate_mac(self, data): 
        mac = hmac.new(self.SECRET_KEY, data, hashlib.sha256).digest()
        return mac[:3]  # Using first 3 bytes of SHA-256 hash 

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
        
    def send_bcm_command(self, status):
        """Send belt status to BCM."""
        
        # Avoid sending the same status repeatedly
        if self.last_status_sent == status:
            return  # If the status is the same as the last one, do not send it again
        
        self.last_status_sent = status

        # Add a timestamp to the message
        timestamp = int(time.time())  # Current time in seconds
        timestamp_bytes = timestamp.to_bytes(4, 'big')
        msg_data = [status] + list(timestamp_bytes)
   
        # Authenticate CAN messages by adding MAC tags to CAN messages
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
        except can.CanError as e:
            #logging.error(f"Failed to send status message: {e}")
            self.error=f"Failed to send status message: {e}"
        self.log_message(status_message)

    def send_belt_data(self,duration): 
        """Continuously send belt status until specified duartion elapses."""
        
        start_time=time.time()
        while time.time() -start_time <duration:
            try:
                elasped_time=time.time()- start_time
                #define the probabiliitoes for belt_off mand belt_on based on elasped time
                belt_off_weight=max(0.1,1-(elasped_time/duration)) #gradually decreases
                belt_on_weight=1- belt_off_weight # increases as belt_off_weiht decreases
                
                belt_on = random.choices([0x04, 0x05], weights=[belt_off_weight,belt_on_weight])[0]  # Randomly simulate belt on or off
                
                if belt_on==0x04: self.d_msg='Belt is OFF'
                elif belt_on==0x05 : self.d_msg='Belt is ON'
                
                self.send_bcm_command(belt_on)
                time.sleep(0.1)  # Adjust the sleep duration as needed
                
            except KeyboardInterrupt:
                logging.info("KeyboardInterrupt detected, stopping status transmission.")
                break

if __name__ == '__main__': 
    bsm = Belt_Status_Module('can0') 
    try:
        bsm.send_belt_data(duration=30) 
    except KeyboardInterrupt:
        logging.info("Program terminated by user.")

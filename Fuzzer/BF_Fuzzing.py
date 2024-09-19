# Student name: Linda Mafunu
# Student number: 2216686
# Date: 10 Sep 2024

# Fuzzing script to exhaustively send random CAN messages to the BCM

import can
import time
import itertools
import logging
from logging.handlers import RotatingFileHandler

# setup logging
log_path='/home/linda-mafunu/Desktop/Final-Project/Fuzzer/BF_Fuzzing.log'
handler = RotatingFileHandler(log_path, mode='w', maxBytes=5*1024*1024, backupCount=2)

with open(log_path,'w'):
    pass

logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s')

class BruteForce_Fuzzer:
    def __init__(self, interface):
        try:
            self.bus = can.interface.Bus(interface, bustype='socketcan')
        except Exception as e:
            logging.error(f"Failed to initialize CAN interface: {e}")
            exit(1)

        
        self.d_msg='None'
    
    def log_message(self,message):
        can_id = message.arbitration_id
        data =message.data
        log_entry = (
                     f"CAN ID: {can_id}\n"
                     f"Data: {data}\n"
                     f"Diagonistic message: {self.d_msg}")
        logging.info(log_entry)

    def brute_force_fuzz(self,duration):
        """Send random CAN messages to the bus in time interval"""
        start_time=time.time()
        end_time=start_time +duration
        try:
            #iterate over the sensor can ids
            can_ids=[0x100,0x200,0x400]
            for can_id in can_ids:
                # iterate over all possible payloads (8 bytes of data)
                for payload in itertools.product(range(256), repeat=8):

                    if time.time() >end_time:
                        return
                    #construct can message
                    message = can.Message(
                    arbitration_id=can_id,
                    data=payload,
                    is_extended_id=False
                    )

                    try:
                        self.bus.send(message)
                        time.sleep(0.001)  # short delay between messages, since its brute force
                        self.d_msg="Brute Force Fuzzing"
                        self.log_message(message)
                    except can.CanError as e:
                        self.d_msg=(f"Failed to send fuzzing message: {e}")
                        self.log_message(message)
                  
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt detected, stopping fuzzing.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
     
if __name__ == '__main__':
    fuzzer = BruteForce_Fuzzer('can0')
    fuzzer.brute_force_fuzz(duration=60)

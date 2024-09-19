# Student name: Linda Mafunu
# Student number: 2216686
# Date: 10 Sep 2024

# Fuzzing script to exhaustively send random CAN messages to the BCM

import can
import time
import random
import os
import logging
from logging.handlers import RotatingFileHandler

# Set up logging
log_path='/home/linda-mafunu/Desktop/Final-Project/Fuzzer/Random_Fuzzing.log'

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

    def generate_random_message(self,can_id,payload):
        """Generate a CAN message with a specified ID and payload"""
        message = can.Message(
            arbitration_id=can_id,
            data=payload,
            is_extended_id=False
        )
        return message


    def brute_force_fuzz(self):
        """Send random CAN messages to the bus in time interval"""
               
        try:
            #iterattte over all possible can IDS (11 bit ids)
            for can_id in range(0x000,0x800):
                # iterate over all possible payloads (8 bytes of data)
                for byte1 in range(0x100):
                    for byte2 in range(0x100):
                        for byte3 in range(0x100):
                            for byte4 in range(0x100):
                                for byte5 in range(0x100):
                                    for byte6 in range(0x100):
                                        for byte7 in range(0x100):
                                            for byte8 in range(0x100):
                                                payload=[byte1,byte2,byte3,byte4,byte5,byte6,byte7,byte8]
                                                message = self.generate_random_message(can_id,payload)
                                                try:
                                                    self.bus.send(message)
                                                    time.sleep(1)  # Random delay between messages
                                                    logging.info(f"Sent fuzzing message: ID={message.arbitration_id}, Data={message.data.hex()}")
                                                except can.CanError as e:
                                                    logging.error(f"Failed to send fuzzing message: {e}")

        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt detected, stopping fuzzing.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
     
if __name__ == '__main__':
    fuzzer = BruteForce_Fuzzer('can0')
    fuzzer.brute_force_fuzz()

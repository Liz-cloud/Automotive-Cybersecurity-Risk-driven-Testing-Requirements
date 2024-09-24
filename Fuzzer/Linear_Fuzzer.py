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
import random
import logging
from logging.handlers import RotatingFileHandler

# Set up logging
log_path='/home/linda-mafunu/Desktop/Final-Project/Fuzzer/Linear_Fuzzing.log'
handler = RotatingFileHandler(log_path, mode='w', maxBytes=5*1024*1024, backupCount=2)
with open(log_path,'w'):
    pass
logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s')

class Linear_Fuzzer:
    
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

    def generate_linear_message(self, start_id,end_id,start_data,end_data):
        """Generate linearing increasing CAN message."""

        current_id = start_id # Standard CAN ID (11 bits)
        current_data = start_data#  CAN data bytes (0-8)

        while current_id <=end_id:
            data=[current_id & 0xFF] +[0] * (current_data -1)

            message = can.Message(
                arbitration_id=current_id,
                data=data,
                is_extended_id=False
            )
            yield message # return temporary to caller alowing the function to pause temporary and resume sequesnce later

            current_id +=1
            current_data=min(current_data +1,end_data) # MAX CAN data len 8 bytes

    def fuzz_can_bus(self):
        """Send linearly increasing CAN messages to the bus."""

        start_id=0x000
        end_id=0x7FF
        start_data=1
        end_data=8

        message_generator = self.generate_linear_message(start_id,end_id,start_data,end_data)
        try:
            for message in message_generator:
                self.bus.send(message)
                self.d_msg="Linear Fuzzing"
                time.sleep(0.001) #add small delay
                self.log_message(message)
        except can.CanError as e:
            logging.error(f"Failed to send linear fuzzing message: {e}")

    def run(self, duration):
        """Send lineary increasing CAN messages to the bus in time interval"""
        try:
            start_time = time.time()
            while time.time() - start_time < duration:
                self.fuzz_can_bus()
                #time.sleep(interval)  # Adjust the interval for fuzzing speed
                time.sleep(random.uniform(0.5, 2))  # Random delay between messages
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt detected, stopping fuzzing.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

if __name__ == '__main__':
    fuzzer = Linear_Fuzzer('can0')
    fuzzer.run(duration=60)

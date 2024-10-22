# Student name: Linda Mafunu
# Student number: 2216686
# Date: 10 Sep 2024

# Fuzzing script to send mutated can messages to BCM
# take set of legitimate inputs and making small modifications to them to create test cases
# SOURCE: https://www.fuzzingbook.org/html/MutationFuzzer.html
# https://github.com/cmu-pasta/mu2


import can
import time
import copy
import logging
import random
import os
from logging.handlers import RotatingFileHandler

# Set up logging
log_path='/home/linda-mafunu/Desktop/Final-Project/Fuzzer/MB_Fuzzing.log'
handler = RotatingFileHandler(log_path, mode='w', maxBytes=5*1024*1024, backupCount=2)
with open(log_path,'w'):
    pass
logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s')

# Function to check the status of the CAN interface
def is_can_interface_up(interface='can0'):
    # Use the 'ip' command to check if the interface is already up
    result = os.system(f"ip link show {interface} | grep 'state UP' > /dev/null 2>&1")
    return result == 0 # If the command returns 0, the interface is up

# Function to bring up the CAN interface only if it is down
def bring_up_can_interface(interface='can0', bitrate=500000):
    if is_can_interface_up(interface):
        logging.info(f"{interface} is already up, no need to bring it up.")
    else:
        try:
            logging.info(f"Bringing up {interface} with bitrate {bitrate}...")
            os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")
            os.system(f"sudo ifconfig {interface} txqueuelen 1000")  # Optional: Increase transmit queue length if needed
            logging.info(f"{interface} is up with bitrate {bitrate}.")
        except Exception as e:
            logging.error(f"Failed to bring up CAN interface {interface}: {e}")
            exit(1)


class Mutation_Based_Fuzzer:
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

    
    def mutated_message(self,original_message):
        '''Mutated the original message using diffreent strategies'''
        
        mutated_msg=copy.deepcopy(original_message)

        #1. change message id
        if random.random()<0.3: # 30% chance to change CAN ID
            mutated_msg.arbitration_id=random.choice([0x100, 0x200, 0x400])
        
        #2. Flip bits in data
        if random.random()<0.2: # 20% to flip bits in data 
            mutated_msg.data= [byte ^ (1 << random.randint(0,7)) for byte in mutated_msg.data]
        
        # 3. Trancuate data
        if random.random()< 0.1: #10% chance to  trancuate data
            if(len(mutated_msg.data)>1):
                trancate_len=random.randint(1,len(mutated_msg.data)-1)
                mutated_msg.data=mutated_msg.data[:trancate_len]

        return mutated_msg
    
    def mutation_based_fuzzing(self,duration):
        '''Perform mutation based fuzzing with a set of legimate messages.'''

        original_mesages={
            0x100: can.Message(arbitration_id=0x100, data=[0x04,0x00, 0x00, 0x00, 0x00]),# belt status on
            0x200: can.Message(arbitration_id=0x200, data=[0x02,0x00, 0x00, 0x00, 0x00]),# door unlocked
            0x400: can.Message(arbitration_id=0x400, data=[0x01,0x00, 0x00, 0x00, 0x00]),# light levels low
        }
        start_time=time.time()
        end_time=start_time +duration
        try:

            while time.time() < end_time:
                for id, msg in original_mesages.items():
                    mutated_msg=self.mutated_message(msg)

                    try:
                        self.bus.send(mutated_msg)
                        time.sleep(random.uniform(0.5, 2))  # Random delay between messages
                        self.d_msg='Mutated Based Fuzzing'
                        self.log_message(mutated_msg)
                    except can.CanError as e:
                        logging.error(f"Failed to send fuzzing message: {e}")

        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt detected, stopping fuzzing.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

if __name__ == '__main__':
    # Bring up the CAN interface before setting up the button and fuzzing
    bring_up_can_interface(interface='can0', bitrate=500000)
    mbf=Mutation_Based_Fuzzer('can0')
    mbf.mutation_based_fuzzing(duration=120)
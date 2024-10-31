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

class Mutation_Based_Fuzzer:
    def __init__(self, interface):
        # Set up logging
        log_path = '/home/linda-mafunu/Desktop/Automotive-Cybersecurity-Risk-driven-Testing-Requirements/Fuzzer/Fuzzing.log'
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

    def mutated_message(self, original_message):
        """Mutate the original message using various mutation strategies"""
        mutated_msg = copy.deepcopy(original_message)

        # 1. Change CAN ID
        if random.random() < 0.3:
            mutated_msg.arbitration_id = random.choice([0x100, 0x200, 0x400])
        
        # 2. Flip bits in data
        if random.random() < 0.2:
            mutated_msg.data = [byte ^ (1 << random.randint(0, 7)) for byte in mutated_msg.data]
        
        # 3. Truncate data
        if random.random() < 0.1:
            if len(mutated_msg.data) > 1:
                truncate_len = random.randint(1, len(mutated_msg.data) - 1)
                mutated_msg.data = mutated_msg.data[:truncate_len]

        return mutated_msg

    def mutation_based_fuzzing(self, duration):
        """Perform mutation-based fuzzing on a set of legitimate messages."""
        original_messages = {
            0x100: can.Message(arbitration_id=0x100, data=[0x04, 0x00, 0x00, 0x00, 0x00]),  # belt status on
            0x200: can.Message(arbitration_id=0x200, data=[0x02, 0x00, 0x00, 0x00, 0x00]),  # door unlocked
            0x400: can.Message(arbitration_id=0x400, data=[0x01, 0x00, 0x00, 0x00, 0x00]),  # light levels low
        }
        start_time = time.time()
        end_time = start_time + duration
        max_retries = 5  # Maximum retries for CAN message sending

        try:
            while time.time() < end_time:
                for msg_id, msg in original_messages.items():
                    mutated_msg = self.mutated_message(msg)
                    retry_count = 0

                    while retry_count < max_retries:
                        try:
                            self.bus.send(mutated_msg)
                            self.d_msg = 'Mutated Based Fuzzing'
                            self.log_message(mutated_msg)
                            time.sleep(random.uniform(0.5, 2))  # Random delay between messages
                            break  # Exit retry loop if send succeeds
                        except can.CanError as e:
                            if "Transmit buffer full" in str(e):
                                self.d_msg = "Transmit buffer full, retrying..."
                                logging.warning(self.d_msg)
                                retry_count += 1
                                time.sleep(0.5)  # Short pause before retry
                            else:
                                self.d_msg = f"Failed to send fuzzing message: {e}"
                                logging.error(self.d_msg)
                                break

                    # Restart CAN interface if max retries are exceeded
                    if retry_count == max_retries:
                        logging.error("Max retries reached, restarting CAN interface.")
                        self.restart_can_interface('can0', 500000)

        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt detected, stopping fuzzing.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    def restart_can_interface(self, interface, bitrate):
        """Restart CAN interface if buffer overflow persists."""
        os.system(f"sudo ip link set {interface} down")
        time.sleep(1)
        os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")
        os.system(f"sudo ifconfig {interface} txqueuelen 5000")
        time.sleep(2)
        logging.info(f"{interface} interface restarted with bitrate {bitrate}.")

# if __name__ == '__main__':
#     # Bring up the CAN interface before setting up the button and fuzzing
#     bring_up_can_interface(interface='can0', bitrate=500000)
#     mbf = Mutation_Based_Fuzzer('can0')
#     mbf.mutation_based_fuzzing(duration=120)

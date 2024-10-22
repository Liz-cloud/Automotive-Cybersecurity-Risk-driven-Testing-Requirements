# Student name: Linda Mafunu
# Student number: 2216686
# Date: 10 Sep 2024

# Fuzzing script to send random CAN messages to the BCM

# SOURCE1: https://www.fuzzingbook.org/html/Fuzzer.html
# source2: https://github.com/FrostTusk/CAN-Fuzzer/blob/master/fuzzer.py

import can
import time
import random
import os
import logging
from logging.handlers import RotatingFileHandler
from gpiozero import Button  # Import Button from gpiozero
from signal import pause
from threading import Thread

# Set up logging
log_path='/home/linda-mafunu/Desktop/Final-Project/Fuzzer/Random_Fuzzing_mac.log'
handler = RotatingFileHandler(log_path, mode='w', maxBytes=5*1024*1024, backupCount=2)
with open(log_path,'w'):
    pass
logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s')

# # Function to check the status of the CAN interface
# def is_can_interface_up(interface='can0'):
#     # Use the 'ip' command to check if the interface is already up
#     result = os.system(f"ip link show {interface} | grep 'state UP' > /dev/null 2>&1")
#     return result == 0 # If the command returns 0, the interface is up

# # Function to bring up the CAN interface only if it is down
# def bring_up_can_interface(interface='can0', bitrate=500000):
#     if is_can_interface_up(interface):
#         logging.info(f"{interface} is already up, no need to bring it up.")
#     else:
#         try:
#             logging.info(f"Bringing up {interface} with bitrate {bitrate}...")
#             os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")
#             os.system(f"sudo ifconfig {interface} txqueuelen 1000")  # Optional: Increase transmit queue length if needed
#             logging.info(f"{interface} is up with bitrate {bitrate}.")
#         except Exception as e:
#             logging.error(f"Failed to bring up CAN interface {interface}: {e}")
#             exit(1)

class Random_Fuzzer:
    
    #ECU to send random CAN messages to the BCM ECU every interval. 
    # Generated random CAN ids over a range of 0x00-0x7FF and 
    # payload (data = [random.randint(0, 0xFF) for _ in range(8)] # Random data bytes)'
    
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
        try:
            self.bus.send(message)
            self.d_msg="Random Fuzzing"
        except can.CanError as e:
            self.d_msg=f"Failed to send Random fuzzing message: {e}"

        self.log_message(message)

    def run(self, duration):
        """Send random CAN messages to the bus in time interval"""
        try:
            start_time = time.time()
            while time.time() - start_time < duration:
                self.fuzz_can_bus()
                time.sleep(random.uniform(0.5, 2))  # Random delay between messages
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt detected, stopping fuzzing.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

if __name__ == '__main__':
    # # Bring up the CAN interface before setting up the button and fuzzing
    # bring_up_can_interface(interface='can0', bitrate=500000)
    fuzzer = Random_Fuzzer('can0')
    fuzzer.run(duration=120)

# # Function to start fuzzing
# def start_fuzzing():
#     logging.info("Button pressed! Starting random fuzzing...")
    
#     def run_fuzzer():
#         fuzzer = Random_Fuzzer('can0')
#         fuzzer.run(duration=120)  # Adjust the duration as needed
    
#     fuzz_thread = Thread(target=run_fuzzer)
#     fuzz_thread.start()

# # Bring up the CAN interface before setting up the button and fuzzing
# bring_up_can_interface(interface='can0', bitrate=500000)
# # Set up the physical button on GPIO pin 17
# button = Button(17)  # GPIO pin 17

# # Register the button press event to trigger fuzzing
# button.when_pressed = start_fuzzing

# # Keep the program running and listen for button press
# pause()  # This will keep it running on button press
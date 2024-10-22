# Student name: Linda Mafunu
# Student number: 2216686
# Date: 12 Sep 2024

# Fuzzing script to send Replayed CAN messages to the BCM
# capture CAN frames from CAN bus store them and the  replay them in a loop
###### Code Source: 
#  https://github.com/FrostTusk/CAN-Fuzzer/blob/master/fuzzer.py

import can
import time
import pickle
import logging
from logging.handlers import RotatingFileHandler
import os

# Set up logging
log_path='/home/linda-mafunu/Desktop/Final-Project/Fuzzer/Replay_Fuzzing_Door_mac.log'
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

class Replay_Fuzzer:
    
    def __init__(self, interface,duration,interval):
        'Initialise the Replay fuzzer witth CAN interface and capture mesages in duration '
        self.capture_frames=[]
        self.capture_duration=duration
        self.replay_interval=interval
        self.d_msg='None'
        self.error='None'
        
        try:
            self.bus = can.interface.Bus(interface, bustype='socketcan')
        except Exception as e:
            logging.error(f"Failed to initialize CAN interface: {e}")
            exit(1)
    
    def log_message(self,message):
        can_id = message.arbitration_id
        data =message.data
        log_entry = (
                     f"CAN ID: {can_id}\n"
                     f"Data: {data}\n"
                     f"Diagonistic message: {self.d_msg}\n"
                     f"Error: {self.error}\n"
        )
        logging.info(log_entry)

    def capture_can_frames(self):
        start_time=time.time()
        print('Start Capturing ...')
        while time.time() -start_time < self.capture_duration:
            try:
                frame =self.bus.recv(timeout=0.1)
                if frame:
                    self.capture_frames.append(frame)
                    self.d_mesg='Caputered frame'
                    self.log_message(frame)
            except can.CanError as e:
                self.error(f'Failed to send fuzzing message: {e}')
                self.log_message(frame)

        print('Can message capture Complete')
        self.save_captured_messages()
    
    def save_captured_messages(self,filename='captured_frames.pkl'):
        'Save the captured CAN messages to a file'
        with open(filename,'wb') as f:
            pickle.dump(self.capture_frames,f)
        self.d_mesg=(f'Captured framaes saved to {filename}')
    
    def replay_frames(self):
         'Replay the captured CAN messages to CAN bus'

         for frame in self.capture_frames:
            try:
                self.bus.send(frame)
                self.d_mesg='Replayed frame'
                time.sleep(self.replay_interval) # delay between replays to simulate original timing
            except can.CanError as e:
                self.error(f'Failed to replay message message: {e}')
            self.log_message(frame)

    def run(self):
        '''Send captured CAN message to the bus for a specified duration'''
        try:
            self.capture_can_frames()
            self.replay_frames()
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt detected, stopping fuzzing.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

if __name__ == '__main__':
    # Bring up the CAN interface before setting up the button and fuzzing
    bring_up_can_interface(interface='can0', bitrate=500000)
    rf=Replay_Fuzzer('can0', duration=120, interval=0.01)
    rf.run()
   


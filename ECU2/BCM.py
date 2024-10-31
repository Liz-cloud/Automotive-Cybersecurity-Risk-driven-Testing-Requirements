# Student name: Linda Mafunu 
# Student number: 2216686 
# Date: 03 Sep 2024 

# This script processed sensor data in the BCM and trigger events viewed on the console, 
# this script is acting as a combination of BCM and Infotainment Unit (Diagonostic Displays).  
# Seat Belt Status (On/off), CAN ID =0x100, Priotity High - safety-critical signal -> buzzer ON/OFF
# Door Status (Locked/Unlocked), CAN ID =0x200, Priotity Medium - safety none critical signal -Yellow LED  ON/OFF
# Headlights (On/off), CAN ID =0x400, Priotity Low/Medium - safety not critical signal - Blue LED ON/OFF

import can 
import time  
import logging 
import hmac  
import hashlib 
import os
import numpy as np
from gpiozero import LED,Buzzer,BadPinFactory, Device
from logging.handlers import RotatingFileHandler 
from gpiozero.pins.native import NativeFactory

class BCM:  
    # Intilise CAN interface  
    def __init__(self, interface,bitrate):

        # reset pins
        Device.pin_factory=NativeFactory()

        #set up logging
        log_path='/ECU2/BCM.log'
        handler = RotatingFileHandler(log_path, mode='w',maxBytes=5*1024*1024, backupCount=2) 
        # Clear the log file at the start of each run
        with open(log_path, 'w'):
            pass  # This will clear the file content
        logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s') 

        try: 
            # Bring up the CAN interface before setting up the button and fuzzing
            self.bring_up_can_interface(interface, bitrate) 
            self.bus = can.interface.Bus(interface, bustype='socketcan') 
        except Exception as e: 
            logging.error(f"Failed to initialize CAN interface: {e}") 
            exit(1) 

        #initialise output devices using gpio pins
        try: 
            self.warning=Buzzer(24) # unverified can messages
            self.headlights=LED(23) # blue led 
            self.interior_lights=LED(27) # yellow led 
            self.belt_status=LED(22)#RED LED 
        except BadPinFactory as e: 
            logging.error(f'Failed to set pins for Buzzer and LED') 
            exit(1) 

        #Message IDS 
        self.HEADLIGHT_SENSOR_ID = 0X400 #TURN ON/OFF HEADLIGHTS 
        self.LOCK_STATUS__ID = 0x200 # DOOR LOCKED/UNLOCKED 
        self.BELT_STATUS_ID = 0x100 # BELT ON/NOT 

        # Shared secret key (this should be securely shared between sender and receiver)  
        self.SECRET_KEY = b'key' 

        # Initialize the last message time to the current time
        self.last_message_time = time.time()

        # Set a timeout period (e.g., 10 seconds) after which sensors should turn off
        self.message_timeout = 40 # in seconds 

        # List to store latency values
        self.latency_values = []
        
        # for can messages logging 
        self.sensor_status='None' # status of sensors
        self.origin='None' # origin of can message
        self.destination='BCM' # Destination is BCM

    # Function to check the status of the CAN interface
    def is_can_interface_up(self,interface):
        # Use the 'ip' command to check if the interface is already up
        result = os.system(f"ip link show {interface} | grep 'state UP' > /dev/null 2>&1")
        return result == 0 # If the command returns 0, the interface is up

    # Function to bring up the CAN interface only if it is down
    def bring_up_can_interface(self,interface, bitrate):
        if self.is_can_interface_up(interface):
            print(f"{interface} is already up, no need to bring it up.")
        else:
            try:
                print(f"Bringing up {interface} with bitrate {bitrate}...")
                os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")
                os.system(f"sudo ifconfig {interface} txqueuelen 1000")  # Optional: Increase transmit queue length if needed
                print(f"{interface} is up with bitrate {bitrate}.")
            except Exception as e:
                print(f"Failed to bring up CAN interface {interface}: {e}")
                exit(1)
    
    # The function generate_mac you've provided is designed to 
    # generate a Message Authentication Code (MAC) using 
    # HMAC (Hash-based Message Authentication Code) with  
    # SHA-256 as the hashing algorithm.  
    # The MAC is then truncated to the first 4 bytes of the  
    # SHA-256 hash. This function can be useful for  
    # ensuring the integrity and authenticity of data in secure communications. 

    def generate_mac(self, data):  
        mac= hmac.new(self.SECRET_KEY, data, hashlib.sha256).digest() 
        return mac[:3] # Using first 3 bytes of SHA-256 hash  

    def verify_mac(self, data, received_mac): 
        """Verify the MAC of an incoming message."""  
        # Generate MAC using the same key and data  
        expected_mac = self.generate_mac(data)  
        # Compare generated MAC with received MAC  
        return hmac.compare_digest(expected_mac, received_mac) 

    def log_message(self,message,latency,error):
        # timestamp=time.strftime('%Y-m%m-%d %H:%M:%S',time.localtime())
        can_id=message.arbitration_id
        data=message.data
        log_entry=(
            f'CAN ID:{can_id}\n'
            f'Data:{data}\n'
            f'Origin:{self.origin}\n'
            f'Destination:{self.destination}\n'
            f'Status:{self.sensor_status}\n'
            f'Error:{error}\n'
            f'Latency:{latency}'
        )
        logging.info(log_entry)

        
    def process_can_Messages(self): 
        """Process incoming CAN messages in a loop."""
        try:
            while True:  
                message =self.bus.recv(timeout=0.01)
                
                # Check for timeout
                if time.time() - self.last_message_time > self.message_timeout:
                    self.cleanup()
                    print("No CAN messages received. Sensors turned off due to timeout.")

                if message: 
                    # Update the last message time when a new message is received
                    self.last_message_time = time.time()
                    
                    error='None' # Errors
                    #Extract MAC - comment out lnes 98-11 to tesat without MAC
                    mac_bytes=message.data[5:8] #received ma
                    Time_stamp= message.data[1:5] #time stamp 
                    
                    # Verify CAN message MAC tag received
                    if not self.verify_mac(message.data[:5],bytes(mac_bytes)):
                        error='MAC verification failed'
                        self.warning.on()
                        #log before continuing
                        latency=0 # latency not calculated for failed MAC
                        self.log_message(message,latency,error)
                        continue # to see how many messages fail
                    else:
                        error='MAC verification successful'
                        self.warning.off()
                
                    #Process messages based on arbitration ID  
                    if message.arbitration_id == self.BELT_STATUS_ID:
                        self.origin='BSM'   # Belt status
                        self.handle_belt_status(message) 

                    elif message.arbitration_id == self.LOCK_STATUS__ID :
                        self.origin='DCM'   #Door Control Module
                        self.handle_lock_status(message) 
                    
                    elif message.arbitration_id == self.HEADLIGHT_SENSOR_ID:
                        self.origin='HCM'  
                        self.handle_headlight_status(message)  

                    else: 
                        #logging.warning(f'Abnormal message received: ID = {message.arbitration_id}, Data = {message.data.hex()}')  
                        error='Abnormal message received'
                        self.warning.on()
                  
                    # Calculate latency after finishing mac verification
                    latency = self.calculate_latency(Time_stamp) 
                    
                    #logg messages
                    self.log_message(message,latency,error)
    
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt detected, exiting gracefully.")
            self.cleanup()

    def handle_headlight_status(self,message):  

        """Handle headlight status updates."""  

        if len(message.data) >= 1:  
            status = message.data[0]   # can dat

            if status == 0x01: 
                self.headlights.on() 
                self.sensor_status='Headlights ON'
          
            elif status ==0x00:  
                self.headlights.off() 
                self.sensor_status='Headlights OFF'
               

    def handle_lock_status(self, message):  
        """Handle lock status updates."""  

        if len(message.data) >= 1:  
            status = message.data[0]   # can data 

            if status == 0x02: 
                self.interior_lights.on()
                self.sensor_status='Door is Unlocked'
             
            elif status ==0x03:  
                self.interior_lights.off()
                self.sensor_status='Door is Locked'

    def handle_belt_status(self, message):  
        """Handle belt status updates.""" 
        if len(message.data) >= 1:  
            status = message.data[0]   # can data
       
            if status == 0x04: 
                self.belt_status.on()
                self.sensor_status='Belt is OFF'
               
            elif status ==0x05:  
                self.belt_status.off()
                self.sensor_status='Belt is ON'
               
        
    def calculate_latency(self,  timestamp_bytes):
        """Calculate message latency.""" 
        #unpack time stamp:
        rec_timestamp = int.from_bytes(timestamp_bytes, 'big')*1000# Extract timestamp in miscroseconds 
        #print('rec',rec_timestamp)
        current_timestamp = int(time.time()*1000)  # Current time in milliseconds
        #print('current time=',current_timestamp)
        latency = current_timestamp - rec_timestamp  # Calculate latency
        #print('lat',latency)
        self.latency_values.append(latency)
        # logging.info(f'latency = {latency: .2f} millisecs')
        return latency

    def calculate_statistics(self):
        mean_latency=np.mean(self.latency_values)
        median_latency=np.median(self.latency_values)
        min_latency=np.min(self.latency_values)
        max_latency=np.max(self.latency_values)
        std_dev=np.std(self.latency_values)
        
        return {
            "mean": mean_latency,
            "median": median_latency,
            "min": min_latency,
            "max": max_latency,
            "std_dev": std_dev
        }
   
    def cleanup(self):
        """Perform any cleanup before exiting."""
        logging.info("Cleaning up resources...")
        # Turn off all LEDs and buzzer
        self.warning.off()
        self.headlights.off()
        self.interior_lights.off()
        self.belt_status.off()
        
        # Calculate and log the average latency
        if self.latency_values:
            stats = self.calculate_statistics()
            logging.info("Latency Statistics:")
            for metric, value in stats.items():
                logging.info(f"{metric.capitalize()}: {value:.2f} ms")
            
        else:
          logging.info("No latency values recorded.")

        logging.info("Cleanup complete. Exiting program.")

if __name__ == '__main__': 
    bcm = BCM('can0',500000)  
    bcm.process_can_Messages() 

 

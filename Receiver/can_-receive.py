# Author: Linda Mafunu
# Student Number: 2216686
# Date: 01/07/2024

# import can 
# import logging
# import hmac 
# import hashlib 

# # Set up logging
# logging.basicConfig(filename='Mac_Messages.log', level=logging.INFO,filemode='w', format='%(asctime)s %(message)s')

# # Shared secret key (this should be securely shared between sender and receiver) 
# SECRET_KEY = b'supersecretkey' 

# class RecipientECU:
#     def __init__(self) -> None:
#         self.bus = can.interface.Bus(channel='can0', bustype='socketcan') 
    
#     def generate_mac(self, data): 
#         return hmac.new(SECRET_KEY, data, hashlib.sha256).digest()[:4]  # Using first 4 bytes of SHA-256 hash 
    
#     #log message format
#     def log_message(self, msg):
#         logging.info(f"Message received: ID={msg.arbitration_id}, Data={msg.data}")


#     def detect_anomalies(self, msg):
#         # Example: Detect messages with unexpected IDs
#         if msg.arbitration_id >0x500:
#             logging.warning(f"Anomaly detected: Unexpected message ID {msg.arbitration_id}")
    
#     def verify_message(self, msg): 
#         data = msg.data[:-4]  # Extract data without MAC 
#         received_mac = msg.data[-4:]  # Extract received MAC 
#         calculated_mac = self.generate_mac(data) 

#         if hmac.compare_digest(received_mac, calculated_mac): 
#             logging.info(f"Message authenticated successfully: ID={msg.arbitration_id}, Data={data}") 
#             print(f"Message authenticated successfully: ID={msg.arbitration_id}, Data={data}") 
#         else: 
#             logging.warning(f"Message authentication failed: ID={msg.arbitration_id}") 
#             print(f"Message authentication failed: ID={msg.arbitration_id}") 


#     def receive_can_message(self): 
#         print("Waiting for CAN message...")
#         while True: 
#             message = self.bus.recv()
#             if message:
#                 self.log_message(message)
#                 self.detect_anomalies(message)
    

# if __name__ == "__main__":
#     recipient_ecu = RecipientECU()
#     recipient_ecu.receive_can_message()
#     # print('All messages recieved')

import can 
import hmac 
import hashlib 
import logging 

# Set up logging
logging.basicConfig(filename='receive_macs.log', level=logging.INFO,filemode='w',
                     format='%(asctime)s %(message)s') 

# Shared secret key (this should be securely shared between sender and receiver) 
SECRET_KEY = b'key' 

class ReceiverECU: 

    def __init__(self, channel='can0', bustype='socketcan'): 

        self.bus = can.interface.Bus(channel=channel, bustype=bustype) 

    def generate_mac(self, data): 

        return hmac.new(SECRET_KEY, data, hashlib.sha256).digest()[:4]  # Using first 4 bytes of SHA-256 hash 

    def verify_message(self, msg): 
        data = msg.data[:-4]  # Extract data without MAC 
        received_mac = msg.data[-4:]  # Extract received MAC 
        calculated_mac = self.generate_mac(data)

        if hmac.compare_digest(received_mac, calculated_mac): 
            logging.info(f"Message authenticated successfully: ID={msg.arbitration_id}, Data={data}") 
            print(f"Message authenticated successfully: ID={msg.arbitration_id}, Data={data}") 
        else: 
            logging.warning(f"Message authentication failed: ID={msg.arbitration_id}") 
            print(f"Message authentication failed: ID={msg.arbitration_id}") 

    def run(self): 
        while True: 
            msg = self.bus.recv() 
            if msg: 
                self.verify_message(msg) 

  
if __name__ == "__main__": 

    receiver_ecu = ReceiverECU() 
    receiver_ecu.run() 
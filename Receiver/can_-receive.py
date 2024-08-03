import can 
import logging

# Set up logging
logging.basicConfig(filename='log1.log', level=logging.INFO,filemode='w', format='%(asctime)s %(message)s')

class RecipientECU:
    def __init__(self) -> None:
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan') 
    
    #log message format
    def log_message(self, msg):
        logging.info(f"Message received: ID={msg.arbitration_id}, Data={msg.data}")


    def detect_anomalies(self, msg):
        # Example: Detect messages with unexpected IDs
        if msg.arbitration_id >0x500:
            logging.warning(f"Anomaly detected: Unexpected message ID {msg.arbitration_id}")
    
    def receive_can_message(self): 
        while True: 
            message = self.bus.recv()
            if message:
                self.log_message(message)
                self.detect_anomalies(message)
    

if __name__ == "__main__":
    recipient_ecu = RecipientECU()
    recipient_ecu.receive_can_message()
    print('All messages recieved')
# Author: Linda Mafunu
# Student Number: 2216686
# Date: 01/07/2024

import can
import logging

# Set up logging
logging.basicConfig(filename='receiver_ecu.log', level=logging.INFO,filemode='w', format='%(asctime)s %(message)s')

class ReceiverECU:
    def __init__(self, channel='can0', bustype='socketcan'):
        self.bus = can.interface.Bus(channel=channel, bustype=bustype)

    def log_message(self, msg):
        logging.info(f"Message received: ID={msg.arbitration_id}, Data={msg.data}")

    def detect_anomalies(self, msg):
        # Example: Detect messages with unexpected IDs
        if msg.arbitration_id not in [0x100, 0x200, 0x300]:
            logging.warning(f"Anomaly detected: Unexpected message ID {msg.arbitration_id}")

    def run(self):
        while True:
            msg = self.bus.recv()
            if msg:
                self.log_message(msg)
                self.detect_anomalies(msg)

if __name__ == "__main__":
    receiver_ecu = ReceiverECU()
    receiver_ecu.run()

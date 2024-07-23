import can
import logging
import time 
import random

# Set up logging
logging.basicConfig(filename='log1.log', level=logging.INFO, format='%(asctime)s %(message)s')

class SenderECU:
    def __init__(self, channel='can0', bustype='socketcan'):
        self.bus = can.interface.Bus(channel=channel, bustype=bustype)

    # basic can fuzzer by sending a large number of semi random inputs to system
    def generate_random_message(self):
        arbitration_id = random.randint(0, 0x7FF)  # Standard CAN ID (11 bits)
        # data_length = random.randint(0, 8)  # CAN data length (0-8 bytes)
        # data = [random.randint(0, 255) for _ in range(data_length)]
        data=(b'Hello123')
        return can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=False)
    
    #send can message and 
    # def send_message(self, data, arbitration_id=0x100):
    def send_message(self,msg):

        # msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=False)
        try:
            self.bus.send(msg)
            logging.info(f"Message sent: ID={msg.arbitration_id}, Data={msg.data}")
            print(f"Message sent: ID={msg.arbitration_id}, Data={msg.data}")
        except can.CanError as e:
            logging.error(f"CAN Error: {e}")
            print(f"CAN Error: {e}")
         
    

    def run(self, interval=0.1, duration=60):
        start_time = time.time()
        while time.time() - start_time < duration:
            msg = self.generate_random_message()
            self.send_message(msg)
            time.sleep(interval)  #

if __name__ == "__main__":
    sender_ecu = SenderECU()
    sender_ecu.run(interval=0.1, duration=60)  # Fuzz for 60 seconds
    print('done sending messages')
    # sender_ecu.send_message(b'Hello123')  # Example data

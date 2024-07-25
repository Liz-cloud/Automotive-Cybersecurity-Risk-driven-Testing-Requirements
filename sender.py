import can 
import random
import time 
import logging

# Set up logging
logging.basicConfig(filename='message_injections.log', level=logging.INFO, format='%(asctime)s %(message)s')

class SenderECU:
    def __init__(self) -> None:
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan')

     # basic can fuzzer by sending a large number of semi random inputs to system
    def generate_random_message(self):
        id= random.randint(0, 0x7FF)  # Standard CAN ID (11 bits)
        # id=0x100
        data_length = random.randint(0, 8)  # CAN data length (0-8 bytes)
        data = [random.randint(0, 255) for _ in range(data_length)]
        return can.Message(arbitration_id=id, data=data, is_extended_id=False)  # id= random.randint(0, 0x7FF)  # Standard CAN ID (11 bits)
        
    def send_can_message(self): 
        msg=self.generate_random_message()
        try:
            self.bus.send(msg)
            logging.info(f"Message sent: ID={msg.arbitration_id}, Data={msg.data}")
        except can.CanError as e:

            logging.error(f"CAN Error: {e}")

if __name__ == "__main__": 
    #creater a sender_ecu object
    sender_ecu=SenderECU()

    #sending messages util keyboard interrupt
    while True: 
        try:
            sender_ecu.send_can_message() 
        except Exception as e:
            logging.error(f'Failed to send message:{e}')
            print(f'Failed to send message:{e}')
        time.sleep(1) 
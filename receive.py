import can 
import logging

logging.basicConfig(filename='DOS_rec.log', level=logging.INFO, format='%(asctime)s %(message)s')


class RecipientECU:
    def __init__(self) -> None:
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan') 


    def receive_can_message(self): 
        try:
            message= self.bus.recv()
            if message:
                logging.info(f"Message received: ID={message.arbitration_id}, Data={message.data}")
        except can.CanError as e:
            logging.error(f'CAN Error: {e}')

if __name__ == "__main__": 
    recipient_ecu = RecipientECU()
    while True:
        recipient_ecu.receive_can_message()
        
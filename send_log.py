import can
import logging

# Set up logging
logging.basicConfig(filename='sender_ecu_security.log', level=logging.INFO, format='%(asctime)s %(message)s')

class SenderECU:
    def __init__(self, channel='can0', bustype='socketcan'):
        self.bus = can.interface.Bus(channel=channel, bustype=bustype)

    def send_message(self, data, arbitration_id=0x100):

        while True: 
            msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=False)
            try:
                self.bus.send(msg)
                logging.info(f"Message sent: ID={msg.arbitration_id}, Data={msg.data}")
                print(f"Message sent: ID={msg.arbitration_id}, Data={msg.data}")
            except can.CanError as e:
                logging.error(f"CAN Error: {e}")
                print(f"CAN Error: {e}")
                

if __name__ == "__main__":
    sender_ecu = SenderECU()
    sender_ecu.send_message(b'Hello123')  # Example data

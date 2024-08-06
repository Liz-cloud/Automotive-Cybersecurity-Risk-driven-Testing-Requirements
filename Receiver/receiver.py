# Author: Linda Mafunu
# Student Number: 2216686
# Date: 01/07/2024   

import can
import logging
from gpiozero import LED, Buzzer, BadPinFactory
import threading
import hmac
import hashlib

# Set up logging
logging.basicConfig(filename='buzzer_led.log', level=logging.INFO, filemode='w', format='%(asctime)s %(message)s')

# GPIO Pin Numbers
GREEN_LED = 17
BLUE_LED = 23
YELLOW_LED = 27
RED_LED = 22
BUZZER_PIN = 24

# Time in seconds after which LED turns off if no message is received
led_timeout = 5

# Shared secret key (this should be securely shared between sender and receiver)
SECRET_KEY = b'key'

# Set up LEDs and buzzer
try:
    green = LED(GREEN_LED)
    red = LED(RED_LED)
    blue = LED(BLUE_LED)
    yellow = LED(YELLOW_LED)
    buzzer = Buzzer(BUZZER_PIN)
except BadPinFactory as e:
    logging.error(f"Failed to initialize devices: {e}")

class RecipientECU:
    def __init__(self) -> None:
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan')
        # filter messages based on these ids
        self.allowed_ids = [
            (0x000, 0x1FF),
            (0x200, 0x2FF),
            (0x300, 0x3FF),
            (0x500, 0x5FF)
        ]
        self.timer = threading.Timer(led_timeout, self.turn_off_devices)
        self.timer.start()

    def turn_off_devices(self):
        red.off()
        green.off()
        blue.off()
        yellow.off()
        buzzer.off()
        logging.info("LEDs and Buzzer turned OFF due to timeout")

    def reset_timer(self):
        self.timer.cancel()
        self.timer = threading.Timer(led_timeout, self.turn_off_devices)
        self.timer.start()

    def generate_mac(self, data):
        return hmac.new(SECRET_KEY, data, hashlib.sha256).digest()[:4]  # Using first 4 bytes of SHA-256 hash

    def verify_message(self, msg): 
        data = msg.data[:-4]  # Extract data without MAC
        received_mac = msg.data[-4:]  # Extract received MAC
        calculated_mac = self.generate_mac(data)

        if any(start <= msg.arbitration_id <= end for start, end in self.allowed_ids):
            if hmac.compare_digest(received_mac, calculated_mac):
                logging.info(f"Message authenticated successfully: ID={msg.arbitration_id}, Data={data}")
                return True
            else:
                logging.warning(f"Message authentication failed: ID={msg.arbitration_id}")
                return False
        else:
            logging.warning(f"Anomaly detected: Unexpected message ID {msg.arbitration_id}")
            return False

    def receive_can_message(self):
        while True:
            try:
                message = self.bus.recv()
                if message:
                    logging.info(f"Message received: ID={message.arbitration_id}, Data={message.data}")

                    if self.verify_message(message):
                        can_id = message.arbitration_id
                        if can_id < 0x200: 
                            green.on()
                            logging.info(f"Engine turned ON for CAN ID: {can_id}")

                        elif 0x200 <= can_id < 0x300:
                            red.on()
                            logging.info(f"Brake System fault on CAN ID: {can_id}")

                        elif 0x300 <= can_id < 0x400:
                            yellow.on()
                            logging.info(f"Battery System fault on CAN ID: {can_id}")

                        elif 0x500 <= can_id < 0x600:
                            blue.on()
                            logging.info(f"Light and Visibility Systems issue on CAN ID: {can_id}")

                    else:
                        buzzer.on()

                self.reset_timer()
            except can.CanError as e:
                logging.error(f'CAN Error: {e}')

if __name__ == "__main__":
    recipient_ecu = RecipientECU()

    try:
        print("Waiting for CAN message...")
        recipient_ecu.receive_can_message()
        
    except KeyboardInterrupt:
        logging.info("Exiting program...")
        green.off()  
        red.off() 
        blue.off()  
        yellow.off()
        buzzer.off()
        recipient_ecu.timer.cancel()


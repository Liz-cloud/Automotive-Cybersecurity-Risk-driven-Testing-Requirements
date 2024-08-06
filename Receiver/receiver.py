# Author: Linda Mafunu
# Student Number: 2216686
# Date: 01/07/2024   

import can
import logging
from gpiozero import LED,Pin, Buzzer,BadPinFactory
import threading


logging.basicConfig(filename='buzzer & led.log', level=logging.INFO, filemode='w', format='%(asctime)s %(message)s')

# SET LED and buzzer  GPIO PIN
GREEN_LED = 17
BLUE_LED = 23
YELLOW_LED = 27
RED_LED = 22
BUZZER_PIN = 24

#led_pins = [17, 23, 27, 22]
#buzzer pin =24



# Time in seconds after which LED turns off if no message is received
led_timeout = 5 

# Set up LEDs and buzzer
try:
    green = LED(GREEN_LED)
    red = LED(RED_LED)
    blue = LED(BLUE_LED)
    yellow=LED(YELLOW_LED)
    buzzer = Buzzer(BUZZER_PIN)
except BadPinFactory as e:
    logging.error(f"Failed to initialize devices: {e}")

class RecipientECU:
    #  Initializes the CAN bus interface,
    #  sets up a timer to turn off the LED after a timeout, and starts the timer.
    def __init__(self) -> None:
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan')
        self.allowed_ids = [
            (0x100F, 0x3FF),
            (0x500, 0x55F)
        ]
        self.allowed_patterns = [b'\x01\x02', b'\x03\x04']  # Example data patterns 
        self.timer = threading.Timer(led_timeout, self.turn_off_devices)
        self.timer.start()

    # Turns off the LED and buzzer and logs the accleartion.
    def turn_off_devices(self):
        red.off()
        green.off()
        blue.off()
        yellow.off()
        buzzer.off()
        logging.info("LEDs and Buzzer turned OFF due to timeout")

    # Cancels the current timer 
    # and starts a new one, effectively resetting the timeout countdown.
    def reset_timer(self):
        self.timer.cancel()
        self.timer = threading.Timer(led_timeout, self.turn_off_devices)
        self.timer.start()
    

    # Continuously listens for CAN bus messages.
    # Upon receiving a message, it turns on the LED if can messages are in range else tutnr on buzzer, 
    # logs the message details, and resets the timer. 
    # Continuously listens for CAN bus messages.
    # Upon receiving a message, it turns on the LED, 
    # logs the message details, and resets the timer.
    def receive_can_message(self):
        while True:
            try:
                message = self.bus.recv()
                if message:
                    logging.info(f"Message received: ID={message.arbitration_id}, Data={message.data}")
                    msg = message.data
                    can_id = message.arbitration_id

                    # Check if the message data matches any of the allowed patterns and if the ID is outside the allowed ranges
                    if not((can_id <= 0x3FF) or (0x500 <= can_id <= 0x5FF)):
                        # Diagnostic calls and Error Reporting
                        buzzer.on()
                        logging.warning(f"Anomaly detected: Unexpected message data {msg}")
                    else:
                        if can_id < 0x1FF: 
                            # Engine transmission
                            green.on()
                            logging.info(f"Enginee turned ON for CAN ID: {can_id}")
                        
                        # elif  (0X200 <= can_id < 0x2FF):
                        #     # Brake system
                        #     red.on()
                        #     logging.info(f"Faulty in Brake System on CAN ID: {can_id}")

                        elif (0X300 <= can_id <0x3FF):
                            # Battery system
                            yellow.on()
                            logging.info(f"Faulty in Battery System on CAN ID: {can_id}")
        
                        elif (0X500 < can_id < 0x5FF):
                            # Light and visibility systems
                            blue.on()
                            logging.info(f"Blue LED turned ON for CAN ID: {can_id}")
                        # else:
                        #     # Diagonistic calls and Error Reporting
                        #     buzzer.on()
                        #     logging.info(f"Anomaly detected: Unexpected message ID{can_id}")
                    
                self.reset_timer()
            except can.CanError as e:
                logging.error(f'CAN Error: {e}')

if __name__ == "__main__":
    # Creates an instance of RecipientECU.
    recipient_ecu = RecipientECU()

    # method to start listening for CAN messages.
    # Handles keyboard interrupts toshut down the script, 
    # turning off the LED, canceling the timer, and closing the GPIO pin.
    try:
        print("Waiting for CAN message...")
        recipient_ecu.receive_can_message()
    except KeyboardInterrupt:
        print("Exiting program...")

        # Ensure the LED is turned off when exiting
        green.off()  
        red.off() 
        blue.off()  
        yellow.off()
        buzzer.off()  # Ensure the buzzer is turned off when exiting

        recipient_ecu.timer.cancel()  # Cancel the timer on exit

        Pin(GREEN_LED).close()
        Pin(BLUE_LED).close()
        Pin(RED_LED).close()
        Pin(YELLOW_LED).close()
        Pin(BUZZER_PIN).close()

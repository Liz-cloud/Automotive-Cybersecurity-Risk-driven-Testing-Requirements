import can
import logging
from gpiozero import LED,Pin, Buzzer,BadPinFactory
import threading


logging.basicConfig(filename='buzzer & led.log', level=logging.INFO, filemode='w', format='%(asctime)s %(message)s')

# SET LED and buzzer  GPIO PIN
GREEN_LED = 4
RED_LED = 17
BUZZER_PIN = 27

# Set up LEDand buzzer
try:
    green = LED(GREEN_LED)
    red = LED(RED_LED)
    buzzer = Buzzer(BUZZER_PIN)
except BadPinFactory as e:
    logging.error(f"Failed to initialize GREEN_LED (Pin 4), RED_LED (Pin 17) and Buzzer (Pin 27): {e}")

# Time in seconds after which LED turns off if no message is received
led_timeout = 5 


class RecipientECU:
    #  Initializes the CAN bus interface,
    #  sets up a timer to turn off the LED after a timeout, and starts the timer.
    def __init__(self) -> None:
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan')
        self.timer = threading.Timer(led_timeout, self.turn_off_devices)
        self.timer.start()

    # Turns off the LED and buzzer and logs the action.
    def turn_off_devices(self):
        red.off()
        green.off()
        buzzer.off()
        logging.info("LED and Buzzer turned OFF due to timeout")

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
                    can_id=message.arbitration_id
                    if can_id < 0x200:
                        green.on()
                        logging.info(f"Green LED turned ON for CAN ID: {can_id}")
                    elif  (can_id > 0x200) and (can_id < 0x500):
                        red.on()
                        logging.info(f"Red LED turned ON for CAN ID: {can_id}")
                    else:
                        buzzer.on()
                        logging.info(f"Buzzer activated for CAN ID: {can_id}")
                    
                    logging.info(f"Message received: ID={message.arbitration_id}, Data={message.data}")
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
        buzzer.off()  # Ensure the buzzer is turned off when exiting
        recipient_ecu.timer.cancel()  # Cancel the timer on exit
        Pin(GREEN_LED).close()
        Pin(RED_LED).close()
        Pin(BUZZER_PIN).close()

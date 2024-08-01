import can
import logging
from gpiozero import LED,Pin, Buzzer,BadPinFactory
import threading


logging.basicConfig(filename='red_led.log', level=logging.INFO, format='%(asctime)s %(message)s')

# SET LED and buzzer  GPIO PIN
LED_PIN = 4
BUZZER_PIN = 27

# Set up LEDand buzzer
try:
    led = LED(LED_PIN)
    buzzer=Buzzer(BUZZER_PIN)
except BadPinFactory as e:
    logging.error(f"Failed to initialize LED (Pin 4) and Buzzer (Pin 27): {e}")

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
        led.off()
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
                    if 0x0 <= can_id <= 0x200:
                        led.on()
                        logging.info(f"White LED turned ON for CAN ID: {can_id}")
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
        led.off()  # Ensure the LED is turned off when exiting
        buzzer.off()  # Ensure the buzzer is turned off when exiting
        recipient_ecu.timer.cancel()  # Cancel the timer on exit
        Pin(LED_PIN).close()
        Pin(BUZZER_PIN).close()

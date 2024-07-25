import can
import logging
from gpiozero import LED
import threading
from gpiozero import Pin


# SET LED GPIO PIN
LED_PIN = 4

# Set up LED
led = LED(LED_PIN)

# Timer to turn off the LED
led_timeout = 5  # Time in seconds after which LED turns off if no message is received

logging.basicConfig(filename='red_led.log', level=logging.INFO, format='%(asctime)s %(message)s')

class RecipientECU:
    def __init__(self) -> None:
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan')
        self.timer = threading.Timer(led_timeout, self.turn_off_led)
        self.timer.start()

    def turn_off_led(self):
        led.off()
        logging.info("LED turned OFF due to timeout")

    def reset_timer(self):
        self.timer.cancel()
        self.timer = threading.Timer(led_timeout, self.turn_off_led)
        self.timer.start()

    def receive_can_message(self):
        while True:
            try:
                message = self.bus.recv()
                if message:
                    led.on()
                    logging.info(f"Message received: ID={message.arbitration_id}, Data={message.data}")
                    self.reset_timer()
            except can.CanError as e:
                logging.error(f'CAN Error: {e}')

if __name__ == "__main__":
    recipient_ecu = RecipientECU()
    try:
        print("Waiting for CAN message...")
        recipient_ecu.receive_can_message()
    except KeyboardInterrupt:
        print("Exiting program...")
        led.off()  # Ensure the LED is turned off when exiting
        recipient_ecu.timer.cancel()  # Cancel the timer on exit
        Pin(4).close()

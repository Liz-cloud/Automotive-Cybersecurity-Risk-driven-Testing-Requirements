
from gpiozero import LED, Button
from signal import pause

# GPIO pin numbers
BUTTON_PIN = 17  # Change as per your setup
LED_PIN = 4    # Change as per your setup

# Setup
led = LED(LED_PIN)
button = Button(BUTTON_PIN, pull_up=True)

# Button press and release callbacks
button.when_pressed = led.on
button.when_released = led.off

try:
    print("Press and hold the button to turn on the LED. Release to turn off the LED...")
    pause()  # Keep the script running

except KeyboardInterrupt:
    print("Exiting program...")

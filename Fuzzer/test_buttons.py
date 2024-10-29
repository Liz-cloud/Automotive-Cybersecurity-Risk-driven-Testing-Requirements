# Test the use of raspeberry pi gpio pins with sensors

import RPi.GPIO as GPIO
from time import sleep

# Set up GPIO pin 17 as an input
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        input_state = GPIO.input(18)
        if input_state == False:
            print("Button Pressed")
        sleep(0.2)
finally:
    GPIO.cleanup()  # Clean up when the program is done

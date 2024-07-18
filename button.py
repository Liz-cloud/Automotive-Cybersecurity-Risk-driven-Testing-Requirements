import sys
# Importing of relevant libraries
import datetime
import time
import RPi.GPIO as GPIO

button_pin = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
try:
    print("Waiting for button press...")
    while True:
        state=GPIO.input(button_pin)
        # if GPIO.input(button_pin):
        print('pin state: ',state)
            # print("Button Pressed")
        time.sleep(0.5)  # Debounce delay
except KeyboardInterrupt:
    GPIO.cleanup()


# def btn_pressed(channel):
#     print("Button Pressed")

#     GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=btn_pressed, bouncetime=200)
#     print("Event detection added. Waiting for button press...")
#     while True:
#         time.sleep(1)
# except RuntimeError as e:
#     print("RuntimeError:", e)
# except KeyboardInterrupt:
#     pass
# finally:
#     GPIO.cleanup()
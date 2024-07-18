import can 
import time 

bus = can.interface.Bus(channel='can0', bustype='socketcan') 

def send_can_message(): 

    msg = can.Message(arbitration_id=0x123, data=[0xDE, 0xAD, 0xBE, 0xEF], is_extended_id=False) 

    bus.send(msg) 

    print("Message sent on {}".format(bus.channel_info)) 


if __name__ == "__main__": 

    count=0
    while True: 
        if count<10:
            send_can_message() 
            time.sleep(0.2)
            count=+1
        else:
            print('--------First 10 messages send --------------')
        time.sleep(10) 
     

# import can
# import time
# import RPi.GPIO as GPIO

# # Setup CAN bus
# bus = can.interface.Bus(channel='can0', bustype='socketcan')

# # Setup GPIO
# button_pin = 17  # Assuming the button is connected to GPIO pin 17
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# def send_can_message():
#     msg = can.Message(arbitration_id=0x123, data=[0xDE, 0xAD, 0xBE, 0xEF], is_extended_id=False)
#     bus.send(msg)
#     print("Message sent on {}".format(bus.channel_info))

# if __name__ == "__main__":
#     try:
#         while True:
#             # Check if the button is pressed
#             if GPIO.input(button_pin) == GPIO.LOW:
#                 send_can_message()
#                 # Debounce delay
#                 time.sleep(0.2)
#             time.sleep(0.1)  # Polling interval
#     except KeyboardInterrupt:
#         pass
#     finally:
#         GPIO.cleanup()  # Clean up GPIO on exit


import time 
from gpiozero import Button, BadPinFactory, Device
from gpiozero.pins.native import NativeFactory
import os
import threading
import time
from Belt_Control_Module import Belt_Status_Module # bsm
from DoorControl_Module import DoorControlECU #dcm
from Headlight_Control_Module import Headlight_Control_Module #hcm

# rest pins
Device.pins_factor=NativeFactory()

# Set buttons
try:
    door_button = Button(17)  # Adjust GPIO pin for Belt Status
    light_button=Button(27) # Adjust GPIO pin for Door Control
    belt_button=Button(22)  # Adjust GPIO pin for Headlight Control
except BadPinFactory as e:
    print(f'Failed to initialize button pin: {e}')
    exit(1)

# Function to check the status of the CAN interface
def is_can_interface_up(interface):
    # Use the 'ip' command to check if the interface is already up
    result = os.system(f"ip link show {interface} | grep 'state UP' > /dev/null 2>&1")
    return result == 0 # If the command returns 0, the interface is up

# Function to bring up the CAN interface only if it is down
def bring_up_can_interface(interface, bitrate):
    if is_can_interface_up(interface):
        print(f"{interface} is already up, no need to bring it up.")
    else:
        try:
            print(f"Bringing up {interface} with bitrate {bitrate}...")
            os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")
            os.system(f"sudo ifconfig {interface} txqueuelen 5000")  # Optional: Increase transmit queue length if needed
            print(f"{interface} is up with bitrate {bitrate}.")
        except Exception as e:
            print(f"Failed to bring up CAN interface {interface}: {e}")
            exit(1)

def run_belt_status():
    print('Starting Belt Status Simulation')
    bsm = Belt_Status_Module('can0')
    bsm.send_belt_data(duration=30)
    print('Ending Belt Status Simulation')

def run_door_control():
    print('Starting Door Lock/Unlock Simulation')
    dcm = DoorControlECU('can0')
    dcm.continuous_send(duration=30)
    print('Ending Door Lock/Unlock Simulation')

def run_headlight_control():
    print('Starting Light Level status Simulation')
    hcm = Headlight_Control_Module('can0') 
    hcm.send_light_data(duration=30)
    print('Ending Light Level  status Simulation')

def main():
    #Attach the button press events to the respective functions
    belt_button.when_pressed  = lambda: threading.Thread(target=run_belt_status,daemon=True).start()
    door_button.when_pressed = lambda: threading.Thread(target=run_door_control,daemon=True).start()
    light_button.when_pressed=lambda: threading.Thread(target=run_headlight_control,daemon=True).start()
    print("Press each button to run its respective module.")
    
    # Keep the script running to listen for button presses
    try:
        while True:
            time.sleep(0.1)  # Small delay to keep the CPU load low
    except KeyboardInterrupt:
        print("Exiting program.")

if __name__ == '__main__':
    bring_up_can_interface("can0",50000)
    time.sleep(2)
    main()

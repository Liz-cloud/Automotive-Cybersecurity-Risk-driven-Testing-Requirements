
import time 
from gpiozero import Button, BadPinFactory, Device
from gpiozero.pins.native import NativeFactory
import os
import threading
import time
import subprocess
from Belt_Control_Module import Belt_Status_Module # bsm
from DoorControl_Module import DoorControlECU
from Headlight_Control_Module import Headlight_Control_Module

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


def bring_up_can_interface(interface="can0"):
    """Check if CAN interface is up; if not, bring it up and adjust queue length."""
    try:
        result = subprocess.run(["ip", "link", "show", interface], capture_output=True, text=True)
        if "state DOWN" in result.stdout:
            print(f"{interface} is down. Bringing it up...")
            subprocess.run(["sudo", "ip", "link", "set", interface, "up"])
            subprocess.run(["sudo", "ip", "link", "set", interface, "type", "can", "bitrate", "500000"])
            os.system(f"sudo ifconfig {interface} txqueuelen 2000")  # Increase transmit queue length
            print(f"{interface} is now up with transmit queue length set to 2000.")
        else:
            print(f"{interface} is already up.")
            os.system(f"sudo ifconfig {interface} txqueuelen 2000")  # Adjust transmit queue length if needed
    except Exception as e:
        print(f"Failed to check or bring up CAN interface: {e}")

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
    belt_button.when_pressed  = lambda: threading.Thread(target=run_belt_status).start()
    door_button.when_pressed = lambda: threading.Thread(target=run_door_control).start()
    light_button.when_pressed=lambda: threading.Thread(target=run_headlight_control).start()
    print("Press each button to run its respective module.")
    
    # Keep the script running to listen for button presses
    try:
        while True:
            time.sleep(0.1)  # Small delay to keep the CPU load low
    except KeyboardInterrupt:
        print("Exiting program.")

if __name__ == '__main__':
    bring_up_can_interface("can0")
    main()

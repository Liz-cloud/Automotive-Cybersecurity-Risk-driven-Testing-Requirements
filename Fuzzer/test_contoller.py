# main.py

from gpiozero import Button, BadPinFactory, Device
from gpiozero.pins.native import NativeFactory
from Random_Fuzzer import Random_Fuzzer
from Linear_Fuzzer import Linear_Fuzzer
import threading
import time
import os

#reset pins
Device.pins_factory=NativeFactory()

# Global flag to check if fuzzing is currently running
fuzzing_in_progress = False

# Create a button instance, assuming the button is connected to GPIO pin 17
try:
    random_button = Button(17)
    linear_button = Button(27)
except BadPinFactory as e:
    print('failed to set pins')
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
            os.system(f"sudo ifconfig {interface} txqueuelen 2000")  # Optional: Increase transmit queue length if needed
            print(f"{interface} is up with bitrate {bitrate}.")
        except Exception as e:
            print(f"Failed to bring up CAN interface {interface}: {e}")
            exit(1)

# Function to bring down the CAN interface
def pull_down_can_interface(interface):
    os.system(f"sudo ip link set {interface} down")
    print(f"CAN interface {interface} has been pulled down.")

# Define a function to run the fuzzing process
def start_random_fuzzing():
    """Function to start the random fuzzing process."""
    global fuzzing_in_progress
    if fuzzing_in_progress:
        print("Fuzzing is already in progress. Please wait.")
        return
    fuzzing_in_progress = True

    fuzzer = Random_Fuzzer('can0')  # Initialize the Random_Fuzzer class
    fuzzer.run(duration=20)  # Run fuzzing for 120 seconds
    print("Random fuzzing completed.")
    fuzzing_in_progress = False

# Define a function to run the fuzzing process
def start_linear_fuzzing():
    """Function to start the linear fuzzing process."""
    global fuzzing_in_progress
    if fuzzing_in_progress:
        print("Fuzzing is already in progress. Please wait.")
        return
    fuzzing_in_progress = True

    print("Starting Linear Fuzzing...")
    fuzzer = Linear_Fuzzer('can0')
    fuzzer.run(duration=20)
    print("Linear fuzzing completed.")
    fuzzing_in_progress = False
    

# Bring up the CAN interface before setting up the button and fuzzing
bring_up_can_interface('can0',500000)

# Attach the button press event to the start fuzzing function
# Attach the button press events to the respective functions
random_button.when_pressed = lambda: threading.Thread(target=start_random_fuzzing).start()
linear_button.when_pressed = lambda: threading.Thread(target=start_linear_fuzzing).start()

# pull_down_can_interface('can0')  # Pull down the CAN interface after both processes

# Keep the script running to listen for button presses
print("Press the button to start random fuzzing.")
while True:
    time.sleep(1)  # Sleep to reduce CPU usage while waiting for button presses

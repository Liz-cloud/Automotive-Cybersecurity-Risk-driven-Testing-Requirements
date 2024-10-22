import os
import logging
from gpiozero import Button
from signal import pause
from threading import Thread

# Set up logging
log_path = '/home/linda-mafunu/Desktop/Final-Project/Fuzzer/Fuzzer_Control.log'
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s %(message)s')

# Button pin mappings for each fuzzing script
random_fuzz_button = Button(17)   # Button for Random Fuzzing
linear_fuzz_button = Button(18)   # Button for Linear Fuzzing
# bruteforce_fuzz_button = Button(22)  # Button for Brute Force Fuzzing
# mutation_fuzz_button = Button(23)  # Button for Mutation-based Fuzzing
# replay_fuzz_button = Button(24)    # Button for Replay Attack
stop_button = Button(27)          # Button to stop all attacks

# Function to check the status of the CAN interface
def is_can_interface_up(interface='can0'):
    # Use the 'ip' command to check if the interface is already up
    result = os.system(f"ip link show {interface} | grep 'state UP' > /dev/null 2>&1")
    return result == 0 # If the command returns 0, the interface is up

# Function to bring up the CAN interface only if it is down
def bring_up_can_interface(interface='can0', bitrate=500000):
    if is_can_interface_up(interface):
        logging.info(f"{interface} is already up, no need to bring it up.")
    else:
        try:
            logging.info(f"Bringing up {interface} with bitrate {bitrate}...")
            os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")
            os.system(f"sudo ifconfig {interface} txqueuelen 1000")  # Optional: Increase transmit queue length if needed
            logging.info(f"{interface} is up with bitrate {bitrate}.")
        except Exception as e:
            logging.error(f"Failed to bring up CAN interface {interface}: {e}")
            exit(1)
# Bring up the CAN interface before setting up the button and fuzzing
bring_up_can_interface(interface='can0', bitrate=500000)

# Function to carry out Random Fuzzing attack
def random_fuzzing():
    logging.info("Starting Random Fuzzing Attack...")
    os.system('python3 /path/to/Random_Fuzzer.py')

# Function to carry out Linear Fuzzing attack
def linear_fuzzing():
    logging.info("Starting Linear Fuzzing Attack...")
    os.system('python3 /path/to/Linear_Fuzzer.py')

# # Function to carry out Brute Force Fuzzing attack
# def bruteforce_fuzzing():
#     logging.info("Starting Brute Force Fuzzing Attack...")
#     os.system('python3 /path/to/BruteForce_Fuzzer.py')

# # Function to carry out Mutation-Based Fuzzing attack
# def mutation_fuzzing():
#     logging.info("Starting Mutation-Based Fuzzing Attack...")
#     os.system('python3 /path/to/Mutated_Based_Fuzzing.py')

# # Function to carry out Replay Attack
# def replay_fuzzing():
#     logging.info("Starting Replay Attack...")
#     os.system('python3 /path/to/Replay_Fuzzer.py')

# Function to stop all attacks
def stop_attack():
    logging.info("Stopping all attacks...")
    os.system('pkill -f Random_Fuzzer.py')
    os.system('pkill -f Linear_Fuzzer.py')
    # os.system('pkill -f BruteForce_Fuzzer.py')
    # os.system('pkill -f Mutated_Based_Fuzzing.py')
    # os.system('pkill -f Replay_Fuzzer.py')

# Button event handlers
def on_random_fuzzing_press():
    fuzz_thread = Thread(target=random_fuzzing)
    fuzz_thread.start()

def on_linear_fuzzing_press():
    linear_thread = Thread(target=linear_fuzzing)
    linear_thread.start()

# def on_bruteforce_fuzzing_press():
#     bruteforce_thread = Thread(target=bruteforce_fuzzing)
#     bruteforce_thread.start()

# def on_mutation_fuzzing_press():
#     mutation_thread = Thread(target=mutation_fuzzing)
#     mutation_thread.start()

# def on_replay_fuzzing_press():
#     replay_thread = Thread(target=replay_fuzzing)
#     replay_thread.start()

def on_stop_press():
    stop_attack()

# Bind buttons to functions
random_fuzz_button.when_pressed = on_random_fuzzing_press
linear_fuzz_button.when_pressed = on_linear_fuzzing_press
# bruteforce_fuzz_button.when_pressed = on_bruteforce_fuzzing_press
# mutation_fuzz_button.when_pressed = on_mutation_fuzzing_press
# replay_fuzz_button.when_pressed = on_replay_fuzzing_press
stop_button.when_pressed = on_stop_press

# Keep the program running to listen for button presses
pause()

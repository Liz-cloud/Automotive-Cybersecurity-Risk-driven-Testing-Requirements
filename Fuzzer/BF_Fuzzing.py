# # Student name: Linda Mafunu
# # Student number: 2216686
# # Date: 10 Sep 2024

# # Fuzzing script to exhaustively send random CAN messages to the BCM
# ###### Code Source: 
# #   https://github.com/FrostTusk/CAN-Fuzzer/blob/master/fuzzer.py

import can
import time
import itertools
import logging
import os
from logging.handlers import RotatingFileHandler

class BruteForce_Fuzzer:
    
    def __init__(self, interface):
        # Set up logging
        log_path = '/home/linda-mafunu/Desktop/Automotive-Cybersecurity-Risk-driven-Testing-Requirements/Fuzzer/Fuzzing.log'
        handler = RotatingFileHandler(log_path, mode='w', maxBytes=5*1024*1024, backupCount=2)
        with open(log_path, 'w'):
            pass
        logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s')

        try:
            self.bus = can.interface.Bus(interface, bustype='socketcan')
        except Exception as e:
            logging.error(f"Failed to initialize CAN interface: {e}")
            exit(1)
        self.d_msg = 'None'
    
    def log_message(self, message):
        can_id = message.arbitration_id
        data = message.data
        log_entry = (
            f"CAN ID: {can_id}\n"
            f"Data: {data}\n"
            f"Diagnostic message: {self.d_msg}"
        )
        logging.info(log_entry)

    def brute_force_fuzz(self, duration):
        """Exhaustively send CAN messages with all possible payloads for specified CAN IDs."""
        start_time = time.time()
        end_time = start_time + duration
        max_retries = 5  # Max retries for CAN message sending

        try:
            can_ids = [0x100, 0x200, 0x400]
            for can_id in can_ids:
                for payload in itertools.product(range(256), repeat=8):
                    if time.time() > end_time:
                        return

                    message = can.Message(
                        arbitration_id=can_id,
                        data=payload,
                        is_extended_id=False
                    )

                    retry_count = 0
                    while retry_count < max_retries:
                        try:
                            self.bus.send(message)
                            self.d_msg = "Brute Force Fuzzing"
                            self.log_message(message)
                            time.sleep(0.02)  # Delay between messages
                            break  # Exit retry loop if send succeeds
                        except can.CanError as e:
                            if "Transmit buffer full" in str(e):
                                self.d_msg = "Transmit buffer full, retrying..."
                                logging.warning(self.d_msg)
                                retry_count += 1
                                time.sleep(0.5)  # Short pause before retry
                            else:
                                self.d_msg = f"Failed to send message: {e}"
                                logging.error(self.d_msg)
                                break  # Break on other errors

                    # Restart CAN interface if max retries exceeded
                    if retry_count == max_retries:
                        logging.error("Max retries reached, restarting CAN interface.")
                        self.restart_can_interface('can0', 500000)

        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt detected, stopping fuzzing.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    def restart_can_interface(self, interface, bitrate):
        """Restart CAN interface if buffer overflow persists."""
        os.system(f"sudo ip link set {interface} down")
        time.sleep(1)
        os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")
        os.system(f"sudo ifconfig {interface} txqueuelen 5000")
        time.sleep(2)
        logging.info(f"{interface} interface restarted with bitrate {bitrate}.")

# if __name__ == '__main__':
#     fuzzer = BruteForce_Fuzzer('can0')
#     fuzzer.brute_force_fuzz(duration=120)

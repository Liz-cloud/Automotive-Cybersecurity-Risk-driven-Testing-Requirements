# # Student name: Linda Mafunu
# # Student number: 2216686
# # Date: 12 Sep 2024

# # Fuzzing script to send Replayed CAN messages to the BCM
# # capture CAN frames from CAN bus store them and the  replay them in a loop
# ###### Code Source: 
# #  https://github.com/FrostTusk/CAN-Fuzzer/blob/master/fuzzer.py

# import can
# import time
# import pickle
# import logging
# from logging.handlers import RotatingFileHandler
# import os



# class Replay_Fuzzer:
    
#     def __init__(self, interface,duration,interval):
#         # Set up logging
#         log_path='/home/linda-mafunu/Desktop/Final-Project/Fuzzer/Replay_Fuzzing_Door_mac.log'
#         handler = RotatingFileHandler(log_path, mode='w', maxBytes=5*1024*1024, backupCount=2)
#         with open(log_path,'w'):
#             pass
#         logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s')
        
#         'Initialise the Replay fuzzer witth CAN interface and capture mesages in duration '
#         try:
#             self.bus = can.interface.Bus(interface, bustype='socketcan')
#         except Exception as e:
#             logging.error(f"Failed to initialize CAN interface: {e}")
#             exit(1)
         
#         self.capture_frames=[]
#         self.capture_duration=duration
#         self.replay_interval=interval
#         self.d_msg='None'
#         self.error='None'

#     def log_message(self,message):
#         can_id = message.arbitration_id
#         data =message.data
#         log_entry = (
#                      f"CAN ID: {can_id}\n"
#                      f"Data: {data}\n"
#                      f"Diagonistic message: {self.d_msg}\n"
#                      f"Error: {self.error}\n"
#         )
#         logging.info(log_entry)

#     def capture_can_frames(self):
#         start_time=time.time()
#         print('Start Capturing ...')
#         while time.time() -start_time < self.capture_duration:
#             try:
#                 frame =self.bus.recv(timeout=0.1)
#                 if frame:
#                     self.capture_frames.append(frame)
#                     self.d_mesg='Caputered frame'
#                     self.log_message(frame)
#             except can.CanError as e:
#                 self.error(f'Failed to send fuzzing message: {e}')
#                 self.log_message(frame)

#         print('Can message capture Complete')
#         self.save_captured_messages()
    
#     def save_captured_messages(self,filename='captured_frames.pkl'):
#         'Save the captured CAN messages to a file'
#         with open(filename,'wb') as f:
#             pickle.dump(self.capture_frames,f)
#         self.d_mesg=(f'Captured framaes saved to {filename}')
    
#     def replay_frames(self):
#          'Replay the captured CAN messages to CAN bus'

#          for frame in self.capture_frames:
#             try:
#                 self.bus.send(frame)
#                 self.d_mesg='Replayed frame'
#                 time.sleep(self.replay_interval) # delay between replays to simulate original timing
#             except can.CanError as e:
#                 self.error(f'Failed to replay message message: {e}')
#             self.log_message(frame)

#     def run(self):
#         '''Send captured CAN message to the bus for a specified duration'''
#         try:
#             self.capture_can_frames()
#             self.replay_frames()
#         except KeyboardInterrupt:
#             logging.info("KeyboardInterrupt detected, stopping fuzzing.")
#         except Exception as e:
#             logging.error(f"Unexpected error: {e}")

# # if __name__ == '__main__':
    
# #     rf=Replay_Fuzzer('can0', duration=120, interval=0.01)
# #     rf.run()
   

import can
import time
import pickle
import logging
from logging.handlers import RotatingFileHandler
import os
import pprint

class Replay_Fuzzer:
    
    def __init__(self, interface, duration, interval):
        # Set up logging
        log_path = '/home/linda-mafunu/Desktop/Final-Project/Fuzzer/Replay_Attack.log'
        handler = RotatingFileHandler(log_path, mode='w', maxBytes=5*1024*1024, backupCount=2)
        with open(log_path, 'w'):
            pass
        logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(message)s')

        try:
            self.bus = can.interface.Bus(interface, bustype='socketcan')
        except Exception as e:
            logging.error(f"Failed to initialize CAN interface: {e}")
            exit(1)
         
        self.capture_frames = []
        self.capture_duration = duration
        self.replay_interval = interval
        self.d_msg = 'None'
        self.error = 'None'
    
    def log_message(self, message):
        can_id = message.arbitration_id
        data = message.data
        log_entry = (
            f"CAN ID: {can_id}\n"
            f"Data: {data}\n"
            f"Diagnostic message: {self.d_msg}\n"
            f"Error: {self.error}\n"
        )
        logging.info(log_entry)
    
    def capture_can_frames(self):
        '''Capture CAN Messages send over CAN bus and save them'''
        start_time = time.time()
        print('Start Capturing ...')
        while time.time() - start_time < self.capture_duration:
            try:
                frame = self.bus.recv(timeout=0.1)
                if frame:
                    self.capture_frames.append(frame)
                    self.d_msg = 'Captured frame'
                    self.log_message(frame)
            except can.CanError as e:
                self.error = f'Failed to receive CAN message: {e}'
                self.log_message(None)
        print('CAN message capture complete')
        self.save_captured_messages()
    
    def save_captured_messages(self, filename='/home/linda-mafunu/Desktop/Final-Project/Fuzzer/captured_frames.pkl'):
        '''Save the captured CAN messages to a file'''
        with open(filename, 'wb') as f:
            pickle.dump(self.capture_frames, f)
        self.d_msg = f'Captured frames saved to {filename}'

    def replay_frames(self):
        '''Replay the captured CAN messages to CAN bus'''
        retry_limit = 3  # Number of retries before attempting a CAN interface restart
        for frame in self.capture_frames:
            retry_count = 0
            while retry_count < retry_limit:
                try:
                    self.bus.send(frame)
                    self.d_msg = 'Replayed frame'
                    time.sleep(self.replay_interval)
                    self.log_message(frame)
                    break  # Exit retry loop if message sent successfully
                except can.CanError as e:
                    if "Transmit buffer full" in str(e):
                        retry_count += 1
                        time.sleep(0.5)  # Wait before retrying
                        logging.warning(f"Retry {retry_count}/{retry_limit}: {e}")
                    else:
                        self.error = f"Failed to replay CAN message: {e}"
                        self.log_message(frame)
                        break  # Exit loop if the error is not recoverable

            if retry_count == retry_limit:
                logging.warning("Retries exhausted; restarting CAN interface.")
                self.restart_can_interface()

    def restart_can_interface(self, interface='can0', bitrate=500000):
        try:
            logging.info("Restarting CAN interface...")
            os.system(f"sudo ip link set {interface} down")
            time.sleep(1)
            os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")
            logging.info("CAN interface restarted successfully.")
        except Exception as e:
            logging.error(f"Failed to restart CAN interface: {e}")
            exit(1)
    
    def read_file(self):
    
        obj = pickle.load(open("/home/linda-mafunu/Desktop/Final-Project/Fuzzer/captured_frames.pkl", "rb"))

        with open("'/home/linda-mafunu/Desktop/Final-Project/Fuzzer/captured_frame.txt", "a") as f:
            print(f"Loaded {len(obj)} captured frames from captured_frames.pkl", file=f)
            print('!')
            pprint.pprint(obj, stream=f)
    
    def run(self):
        '''Send captured CAN message to the bus for a specified duration'''
        try:
            self.capture_can_frames()
            self.replay_frames()
            self.read_file()
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt detected, stopping fuzzing.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")


# if __name__ == '__main__':
    
#     rf=Replay_Fuzzer('can0', duration=60, interval=0.01)
#     rf.run()
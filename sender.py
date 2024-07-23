import can 

import time 

bus = can.interface.Bus(channel='can0', bustype='socketcan') 

def send_can_message(): 

    msg = can.Message(arbitration_id=0x123, data=[0xDE, 0xAD, 0xBE, 0xEF], is_extended_id=False) 

    bus.send(msg) 

    print("Message sent on {}".format(bus.channel_info)) 

if __name__ == "__main__": 

    while True: 

        send_can_message() 

        time.sleep(1) 
import can 

bus = can.interface.Bus(channel='can0', bustype='socketcan') 


def receive_can_message(): 

    while True: 

        message = bus.recv() 

        print(f"Message received: {message}") 

  
if __name__ == "__main__": 

    receive_can_message() 
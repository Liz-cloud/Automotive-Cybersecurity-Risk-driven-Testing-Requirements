import can 

bus = can.interface.Bus(channel='can0', bustype='socketcan') 

def receive_can_message(): 
    count=0
    while True: 
        if count <10:
            message = bus.recv() 
            print(f"Message received: {message}") 
            count+=1
        else:
            print('--------First 10 Messages Received -------')


if __name__ == "__main__": 

    receive_can_message() 
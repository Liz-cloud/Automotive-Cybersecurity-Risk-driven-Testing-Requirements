import can 
import time 
import logging

# Set up logging
logging.basicConfig(filename='sender_ecu_security.log', level=logging.INFO, format='%(asctime)s %(message)s')

class SenderECU:
    def __init__(self) -> None:
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan') 
        self.role='admin' #role based access control, set to admin
    
    #check the access rights
    def hasPermissions(self, permison):
        roles={
            'admin':['read','write','execute'],
            'user':['read'],
            'guest':[]
        }
        return permison in roles.get(self.role,[])
    

    def send_can_message(self, data): 
        if not self. hasPermissions('write'):
            logging.warning("Permission denied: Cannot send message")
            print("Permission denied: Cannot send message")
            return
        
        #generate can message
        msg = can.Message(arbitration_id=0x123, data=[0xDE, 0xAD, 0xBE, 0xEF], is_extended_id=False) 
        #send message
        self.bus.send(msg) 
        #record the log
        logging.info(f"Message sent: {msg}")

        #output
        print("Message sent on {}".format(self.bus.channel_info)) 


if __name__ == "__main__": 
    ecu1=SenderECU()
    ecu1.send_can_message(b'Hello123') #Message example


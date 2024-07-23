import can 
import logging

# Set up logging
logging.basicConfig(filename='recipient_ecu_security.log', level=logging.INFO, format='%(asctime)s %(message)s')

class RecipientECU:
    def __init__(self) -> None:
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan') 
        self.role='user' #Role based access control, set user 

    def has_permission(self, permission):
        roles={
            'admin':['read','write','execute'],
            'user':['read'],
            'guest':[]
        }
        return permission in roles.get(self.role,[])
    

    def receive_can_message(self): 

        while True: 
            message = self.bus.recv()
            if message:
                if not self.has_permission('read'):
                    logging.warning('Permission denied: Cannot read message')
                    print('Permission denied: Cannot read message') 
                    return
                #record log
                logging.info(f"Decrypted message received: {message}")
                #output message
                print(f"Message received: {message}") 
        

if __name__ == "__main__":
    recipient_ecu = RecipientECU()
    recipient_ecu.receive_can_message()
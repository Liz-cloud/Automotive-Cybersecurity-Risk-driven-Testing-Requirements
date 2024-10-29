# send_can_2.py
#test sending of CAN messages on can bus
import can
import time
import random

def generate_messages():
    id=random.choice(range(0x00,0x7FF))
    data_length=random.randint(0,8)
    #data=bytes([random.randint(0,255)for _ in range(data_length)])
    data=b'ECU1'
    msg=can.Message(arbitration_id=id, is_extended_id=False, data=data)
    return msg
    
def send_can_message_2(duration_seconds):
    # Create a bus instance using the socketcan interface
    with can.Bus(interface='socketcan', channel='can0', receive_own_messages=True) as bus:
        
        start_time = time.time()  # Record the start time
        end_time = start_time + duration_seconds  # Calculate the end time
        
        print(f"Sending CAN messages for {duration_seconds} seconds...")
        
        while time.time() < end_time:
            # Create a CAN message with ID 0x456
            #message = can.Message(arbitration_id=0x456, is_extended_id=True, data=[0x44, 0x55, 0x66])
            #generate random can messages
            message=generate_messages()
            try:
                # Send the CAN message
                bus.send(message)
                print(f"Message with ID {message.arbitration_id} with Data {message.data} sent on {bus.channel_info}")
            except can.CanError as e:
                print(f"Error sending message: {e}")
                
            # Wait a short period before sending the next messages
            time.sleep(0.1)  # Sleep for 100 milliseconds (adjust as needed)

if __name__ == "__main__":
    send_can_message_2(120) # send messages for duration

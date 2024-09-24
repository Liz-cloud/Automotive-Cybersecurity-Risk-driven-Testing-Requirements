# Pen-Testing ECU using Py-CAN

## Student name: Linda Mafunu
## Student Number: 2216686
## Date: 20/08/2024

### Receiver ECU:

#### Instructions to run  code:
    1. Bring Up the CAN Interface: 
        - Set can0 interface speed to 5s00 Kbps:  
            sudo ip link set can0 up type can bitrate 500000 sample-point 0.875  

        - Set to can0 to “steady” state (steady green led on USBD-CAN Adapter):
            sudo ip link set can0 up  

    2. To bring down interface (steady red led on USBD-CAN Adapter):  
        sudo ip link set can0 down 

    3. Check status of can
        sudo ip link
        
    4. python3 sender.py
# Pen-Testing ECU using Py-CAN

## Student name: Linda Mafunu
## Student Number: 2216686
## Date: 20/08/2024

### Receiver ECU:

#### Instructions to run  code:
    1. Bring Up the CAN Interface: 
        - Set can0 interface speed to 500 Kbps:  
            sudo ip link set can0 up type can bitrate 500000 sample-point 0.875  

        - Set to can0 to “steady” state:
            sudo ip link set can0 up  

    2. To bring down interface:  
        sudo ip link set can0 down 

    3. Check status of can
        sudo ip link

    4. Run all the modules at the same time or separately to visualize each Module's behaviour on circuit
     - python3 Headlight_Control_Module.py
     - python3 DoorControl_Module.py
     - python3 Door_Control_Module.py
         -> Press button to manipulate Door Status

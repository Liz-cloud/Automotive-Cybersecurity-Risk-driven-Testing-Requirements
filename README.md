# Automotive-Cybersecurity-Risk-driven-Testing-Requirements
## Implementing MAC Tags for Fuzz Testing Resistance and Performance Analysis in Vehicle Networks

### Student Name: Linda Mafunu
### Student Number: 2216686
### Date: 12/09/2024

#### Fuzzer Folder
- Contains Python scripts to launch fuzz tests on the Body Control Module (BCM) ECU
- Associated log files for sent fuzzing messages from sessions
  
##### Fuzz Tests:
1. Random Fuzzing
2. Linear Fuzzing
3. Brute Force Fuzzing
4. Mutation-Based Fuzzing
5. Replay Attacks
   
#### ECU2 Folder (Reciever/Listerner)
- Contains python script for Body Control Module (BCM) ECU to simulate sensors based on received CAN messages
- Recieved messages from Belt, Door and Headlight Control Modules
- Associated response log files for sessions


#### ECU1 Folder (Sender)
- Contains python script for Belt Status Module (BSM) , Door Control Modules (DCM) and Headlight Control Modules (HCM)
- CAN Messages sent to BCM to trigger sessors on circuit
- Associated log files for messages from sessions

#### Analysis Jupiter Notebook
  - Analysis the BCM log files for the ECU communication and Fuzz tests using statistical data and graphs

## How to run simulation
**1. Start the Reciever ECU (i.e. Body Control Module)**
  - If it is not recieving and can messages all output sensors should be turned off
  - If Origin is DCM it should simulate the output of interrior lights (Yellow LED)
  - Else if Origin is BSM it should simulate the output of Belt Status (Red LED)
  - Else if Origin is HCM it should simulate the output of headlights (Blue LED)
  - Else if an abnormal message is received or CAN message fails MAC verification the buzzer sounds
  - The print and error output for running the BCMM.py are found in the BCM_script.log file
  - If it is recieving CAN messages each CAN message is logged in this format for example:
    ```console
        2024-10-28 15:36:09,769 CAN ID:512
        Data:bytearray(b'\x02g\x1f\xafii5%')
        Origin:DCM
        Destination:BCM
        Status:Door is Unlocked
        Error:None
        Latency:769
    ```

**2. Start Sender ECU**
  - This will send sensor data from Door Control Module,Headlight Control Module and Belt Control Module to Body Control Module influence output sensors's behavoir
  - If you press Door button it will simulate Door Lock and Unlock status 
  - If you press Light button it will simulate Light levels (low and hight) status
  - If you press Belt button it will simulate Belt ON and OFF status
  - The print and error output for running the BCMM.py are found in the Sensor_data_script.log file 

**3. Start Attacker ECU**
  - This will lauch different kinds of fuzzing attacks onto the CAN bus to manipulate BCM behaviour
  - The print and error output for running the fuzzing scripts are found in the controller_script.log file
  - If you press Random button it will run Random Fuzzing python script
  - If you press Linear button it will run Linear Fuzzing python script
  - If you press BF button it will run Brute Force Fuzzing python script
  - If you press MBT button it will run Mutated Based Fuzzing python script
  - If you press Replay button it will run Replay Fuzzing python script


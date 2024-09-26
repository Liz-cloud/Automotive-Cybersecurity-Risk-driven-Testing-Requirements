# Pen-Testing ECU using Py-CAN

## Student Name: Linda Mafunu
## Student Number: 2216686
## Date: 12/09/2024

### Fuzzer
- Contains Python scripts to launch fuzz tests on the Body Control Module (BCM) ECU
- Associated log files for sent fuzzing messages from sessions
  
#### Fuzz Tests:
1. Random Fuzzing
2. Linear Fuzzing
3. Brute Force Fuzzing
4. Mutation-Based FUzzing
5. Replay Attacks
   
### ECU2 (Reciever/Listerner)
- Contains python script for Body Control Module (BCM) ECU to simulate sensors based on received CAN messages
- Recieved messages from Belt, Door and Headlight Control Modules
- Associated response log files for sessions


### ECU1 (Sender)
- Contains python script for Belt Status Module (BSM) , Door Control Modules (DCM) and Headlight Control Modules (HCM)
- CAN Messages sent to BCM to trigger sessors on circuit
- Associated log files for messages from sessions

### Analysis Jupiter Notebook
  - Analysis the BCM log files for the ECU communication and Fuzz tests 

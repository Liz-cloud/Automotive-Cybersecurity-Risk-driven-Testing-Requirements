# Pen-Testing ECU using Py-CAN

## Student Name: Linda Mafunu
## Student Number: 2216686
## Date: 12/09/2024

### Attacker ECU:

### Fuzzer
- Contains Python scripts to launch fuzz tests on the Body Control Module (BCM) ECU
- Fuzzing_Controller.py controlls how the tests are launched
- Associated log files for sent fuzzing messages from sessions
- test_buttons.py file is a file used to the use of input  and output devices from  gpio signals
- test_send.py file to test the sending of CAN messages via the CAN protocol to see if connection was established

#### Fuzz Tests:
1. Random Fuzzing
2. Linear Fuzzing
3. Brute Force Fuzzing
4. Mutation-Based Fuzzing
5. Replay Attacks
   
  
***NB: Lauch One attack each given time***

##### Code Source: 
   https://github.com/FrostTusk/CAN-Fuzzer/blob/master/fuzzer.py

    

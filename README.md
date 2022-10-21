# modbus

## Requirements
python >= 3.7

## Installation

Create a virtual environment

    virtualenv venv
    source ./venv/bin/activate

Install requirements 

    pip install -r requirements.txt

## Usage

### Configuration


First, you need to create a configuration for the modbus communication. 

Create a configuration file for modbus over tcp

    python ./src/main.py create-tcp-config


Create a configuration file for modbus over serial

    python ./src/main.py create-serial-config

### Read / write registers

To read input registers 

    python src/main.py do -c config_tcp.json  --slave <SLAVE_NUMBER> read-input-register <REGISTER_ADDRESS>

 
To read holding registers 

    python src/main.py do -c config_tcp.json  --slave <SLAVE_NUMBER> read-holding-register <REGISTER_ADDRESS>



To write holding registers 

    python src/main.py do -c config_tcp.json  --slave <SLAVE_NUMBER> write-holding-register <REGISTER_ADDRESS> <VALUE>

### Batch Mode

Create a file with all the commands

Format : Function, address, value

Functions are :
* 4 : Read Input Registers
* 3 : Read Holding Registers
* 6 : Write Single Holding Register
* 999: Sleep for x seconds

Example : 

4,30001, # Read input register 30001
6,40001, 10 # Write 10 in the holdind register 40001
999,10, # Sleeps for 10 seconds before the next command

To run the batch

    python src/main.py do -c config_tcp.json  --slave <SLAVE_NUMBER> batch <COMMAND_FILE> 
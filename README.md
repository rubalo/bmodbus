# modbus

## Requirements
Powershell

 Based on modpoll : https://www.modbusdriver.com/modpoll.html

## Installation

You might need to authorize powershell scripts for your session :

Open a powershell Terminal
Run the following command :

    PowerShell -ExecutionPolicy Bypass

## Usage

Go to the code root folder

run :

    .\bmodbus.ps1

### Configuration

Edit the file bmodbus.ps1 to change the baudrate / Parity / Slave address ...

### Batch files

Create Batch files in the \commands folder : 

Read Command :

    r, <REGISTER_ADDRESS_START>, <NUMBER_OF_REGISTER_TO_READ>

Write Command :

    w, <REGISTER_ADDRESS>, <VALUE>

Sleep Command :

    s, <SECONDS>


Example : 

    # Write register 1 with value 10
    w, 1, 10
    # Sleeps for 10 seconds
    s, 10
    # Read registers 1 to 4
    r, 1 , 4
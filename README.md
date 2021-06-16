TCP Modbus connection to MQTT for Givenergy Battery/PV Invertors

This project allows connection to the GivEnergy invertors via TCP Modbus. Access is through the native Wifi/Ethernet dongle can be connected to through either the local LAN network or directly through the inbuilt SSID AP.

In essence the script connects to a Modbus TCP server which runs on the wifi dongle, so all you need is somewhere to run the script on the same network. You will need the following to make it work:
* MQTT server running on the network and know its IP address
* MQTT login credentials (optional)
* IP address of the invertor
* Serial Number of the wifi/gps dongle (not the invertor) - which can be found on the portal: https://www.givenergy.cloud/GivManage/setting/deviceMenu/inverterList
* Machine/Pi/VM running Python which has following modules installed:
  * crccheck
  * paho-mqtt

# Settings
A settings.py file is required in the root directory. Use the supplied settings_template.py and populate with the relevant details. Only InvertorIP, dataloggerSN and MQTT_Address are required. All other settings must be there but can be left blank if not needed.

# Usage
GivTCP can be executed in a number of ways and can be set to output data in multiple formats. Exact usage is dependent on your use-case and needs:

## CLI
Execute the script at the command line and pass the relevant function and parameters as per the details below
## CLI Through Node-Red
Using the Exec node in Node-Red to call the script in the same way as above. This allows automation of script calling within a wider automated system
## REST Service
Deployed inside a Docker container a RESTful service calls the relevant functions using the details below through GET and POST http methods

# Output formats:
## MQTT
The script will publish directly to the nominated MQTT broker all the requested read data.
## JSON
The functions return a JSON formated object which can then be consumed by other systems or functions, default output is to stdout

# GivTCP functions
## Read functions
GivTCP is able to retrieve key information from the GivEnergy Invertors through predefined functions:

### Available read functions are:
| Function          | Payload       |  Description                      |
| ----------------- | ------------- |  -------------------------------- |
| getTimeslots      | None          | Gets all currently stored timeslots for Charge1, Discharge1 and Discharge2      |
| getCombinedStats  | None          | Gets power and Energy Stats (real-time, Today and Total)   |
| getModesandTimes  | None          | Gets the Timeslots and control state info including: Mode, Target Charge SOC, Battery Reserve, Charge and Discharge Schedule state (Paused/Active) and Battery Capacity    |
| runAll            | None          | Runs all of the above  |


## Control functions
Control is available through predefined functions. The format of the function call matches the published GivEnegry cloud based battery.api. It requires a JSON payload as per the below:

### Available control functions are:
| Function                | Payload       |  Description                      |
| ----------------------- | ------------- |  -------------------------------- |
| pauseChargeSchedule     | None          | Pauses the Charging schedule      |
| pauseDischargeSchedule  | None          | Pauses the Discharging schedule   |
| resumeChargeSchedule    | None          | Resumes the Charging schedule     |
| resumeDischargeSchedule | None          | Resumes the Discharging schedule  |
| setChargeTarget         | {"chargeToPercent":"50"}  | Sets the Target charge SOC |
| setBatteryReserve|{"dischargeToPercent":"5"}| Sets the Battery Reserve discharge cut-off limit|
| setChargeSlot1|{"start":"0100","finish":"0400","chargeToPercent":"55")| Sets the time and target SOC of the first chargeslot. Times must be expressed in hhmm format. Enable flag show in the battery.api documentation is not needed |
| setDischargeSlot1|{"start":"0100","finish":"0400","dischargeToPercent":"55")| Sets the time and target SOC of the first dischargeslot. Times must be expressed in hhmm format. Enable flag show in the battery.api documentation is not needed |
| setDischargeSlot2|{"start":"0100","finish":"0400","dischargeToPercent":"55")| Sets the time and target SOC of the first dischargeslot. Times must be expressed in hhmm format.  Enable flag show in the battery.api documentation is not needed |
|setBatteryMode|{"mode":"1"}| Sets battery operation mode. Mode value must be in the range 1-4|

# Example deployments
For each execution method there is a defined way of interacting and calling the relevat functions

## CLI

### Read
`python3 read.py {{functionName}}`

### Control
`python3 write.py {{functionName}} '{{controlPayload}}'`

An example payload can be found below and further details can be seen in the GivEnergy Docs to be found here: XXXXXXX  
Note: In order to send json payloads via CLI you will need to place the JSON string inside single quotes  

The full call to set  Charge Timeslot 1 would then be:  

`python3 write.py setChargeSlot1 '{"enable": true,"start": "0100","finish": "0400","chargeToPercent": "100"}'`  

## CLI through Node-Red



## RESTful Service
GivTCP provides a wrapper function REST.py which uses Flask to expose the read and control functions as RESTful http calls. To utilise this service you will need to either use a WSGI serivce such as gunicorn or use the pre-built Docker container

### Gunicorn
Ensure Gunicorn is installed by running:  

`pip install gunicorn`  

Then call the service by initiating the following command from the same directory as the downloaded src files:  

`gunicorn -w 4 -b 127.0.0.1:6345 REST:giv_api`  

(where the 127.0.0.1:6345 is the IP address and port you want to bind the service to)  

### Docker
The docker container can be downloaded at the Docker hub here:   
x86:https://hub.docker.com/repository/docker/britkat/giv_tcp  
ARM: https://hub.docker.com/repository/docker/britkat/giv_tcp-arm  
  
* Download the correct docker image for your achitecture (tested on x86 and rpi3)
* Create a container with the relevant ENV variables below (mimicing the settings.py file)
* Set the container to auto-restart to ensure reliability

| ENV Name                | Example       |  Description                      |
| ----------------------- | ------------- |  -------------------------------- |
| INVERTOR_IP |192.168.10.1 | Required |
| SERIAL_NUMBER | AB12345678 | Required |
| OUTPUT | MQTT | Optional (Include MQTT to publish to MQTT as well as JSON return) |
| MQTT_ADDRESS | 192.168.10.2 | Optional (but required if OUTPUT is set to MQTT) |
| MQTT_USERNAME | bob | Optional |
| MQTT_PASSWORD | cat | Optional |
| MQTT_TOPIC | GivEnergy/Data | Optional |
| DEBUG | True | Optional - if True then will write debug info to sepcified file location (default is same directory as the py files) |
| DEBUG_FILE_LOCATION | /usr/pi/data | Optional  |
| PRINT_RAW | True | Optional - If set to True the raw register values will be returned alongside the normal data |


### Calling RESTFul Functions

The following table outlines the http methods needed to call the various read and control functions. For each control function the payload is an identical JSON string as above (minus the single quotes).  
The RESTful Service will return a JSON object which you can then parse as you so desire   

URL's below are based off the root http address of http://IP:6345
(Port may change if you are running yourself using gunicorn, in which case use the details specified in the gunicorn command)

| URL                | Method       |  payload              |  Description             |
| ------------------ | ------------ |  -------------------- | -------------------------|
| READ Functions|
| /runALL| GET | None |  |
| /getTimeslots| GET | None | | 
| /getCombinedStats| GET | None | | 
| /getModesandTimes| GET | None | | 
| Control Functions|
| | | | | 
| | | | |
| | | | | 
| | | | | 
| | | | |
| | | | | 
| | | | | 
| | | | | 
| | | | | 
| | | | | 
| | | | | 
  

Not sure where to start? Check our [Quick Start Guide](/documentaion/tutorial.md)  

[Some API Documentation](/documentaion/APIDocumentation.md)  

[All the used registers are listed in here ](/documentaion/registersAndFunctions.xlsb.xlsx)
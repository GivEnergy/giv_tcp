# GivTCP
## TCP Modbus connection to MQTT/JSON for Givenergy Battery/PV Invertors

This project allows connection to the GivEnergy invertors via TCP Modbus. Access is through the native Wifi/Ethernet dongle and can be connected to through either the local LAN network or directly through the inbuilt SSID AP.

In basis of this project is a connection to a Modbus TCP server which runs on the wifi dongle, so all you need is somewhere to run the script on the same network. You will need the following to make it work:
* GivEnergy Invertor properly commissioned and working
* IP address of the invertor
* Machine/Pi/VM running Python which has  pip modules installed as per the requirements.txt file:
   
(To install these run `pip install -r requirements.txt`)

# Settings
A settings.py file is required in the root directory. Use the supplied settings_template.py and populate with the relevant details. Only InvertorIP is required as a minimum, but output should be selected to ensure the data is passed out as either JSON or MQTT. All other settings must be there but can be left blank if not needed.

# Execution of GivTCP
GivTCP can be executed in a number of ways and can be set to output data in multiple formats. Exact usage is dependent on your use-case and needs:

| Method         |  Description                    |
| ---------------| ------------------------------- |
| [CLI](#cli-usage) | Execute the script at the command line and pass the relevant function and parameters as per the details below |
| [CLI through Node-Read](#cli-through-node-red) | Using the Exec node in Node-Red to call the script in the same way as above. This allows automation of script calling within a wider automated system |
| [REST Service](#restful-service) | Deployed inside a Docker container a RESTful service calls the relevant functions using the details below through GET and POST http methods |
| [Docker container](#docker) | A docker container is available which has all code and pre-requisites installed and out of the box is set to auto-discover the invertor and publish to an internal MQTT broker. This can be changed to publish to an external broker by modifying the container ENV variables |

# Output formats:
## MQTT
The script will publish directly to the nominated MQTT broker all the requested read data.

![image](https://user-images.githubusercontent.com/69121158/122302074-847e9980-cef9-11eb-87eb-f4010b0874ed.png)
  
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
| enableChargeTarget     | None          | Sets invertor to follow setChargeTarget value when charging from grid (will stop charging when battery SOC= ChargeTarget)     |
| disableChargeTarget     | None          | Sets invertor to ignore setChargeTarget value when charging from grid (will continue to charge to 100% during ChargeSlot)     |
| pauseChargeSchedule     | None          | Pauses the Charging schedule      |
| pauseDischargeSchedule  | None          | Pauses the Discharging schedule   |
| resumeChargeSchedule    | None          | Resumes the Charging schedule     |
| resumeDischargeSchedule | None          | Resumes the Discharging schedule  |
| setChargeTarget         | {"chargeToPercent":"50"}  | Sets the Target charge SOC |
| setBatteryReserve|{"dischargeToPercent":"5"}| Sets the Battery Reserve discharge cut-off limit|
| setChargeSlot1|{"start":"0100","finish":"0400","chargeToPercent":"55")| Sets the time and target SOC of the first chargeslot. Times must be expressed in hhmm format. Enable flag show in the battery.api documentation is not needed and chargeToPercent is optional|
| setDischargeSlot1|{"start":"0100","finish":"0400","dischargeToPercent":"55")| Sets the time and target SOC of the first dischargeslot. Times must be expressed in hhmm format. Enable flag show in the battery.api documentation is not needed and dischargeToPercent is optional |
| setDischargeSlot2|{"start":"0100","finish":"0400","dischargeToPercent":"55")| Sets the time and target SOC of the first dischargeslot. Times must be expressed in hhmm format.  Enable flag show in the battery.api documentation is not needed and dischargeToPercent is optional |
|setBatteryMode|{"mode":"1"}| Sets battery operation mode. Mode value must be in the range 1-4|

# CLI Usage
GivTCP can be called from any machine running Python3. The relevant script must be called and a function name passed to it as an argument. Exmaples of how to call read and write functions are shown here: 

## Read
`python3 read.py {{functionName}}`

The full call to get all information by running the runAll function would then be:  
  
`python3 read.py runAll`  
  
## Control
`python3 write.py {{functionName}} '{{controlPayload}}'`

An example payload can be found below and further details can be seen in the GivEnergy Docs to be found here: XXXXXXX  
Note: In order to send json payloads via CLI you will need to place the JSON string inside single quotes  

The full call to set  Charge Timeslot 1 would then be:  

`python3 write.py setChargeSlot1 '{"enable": true,"start": "0100","finish": "0400","chargeToPercent": "100"}'`  

# CLI through Node-Red

Node-Red provides the ability to call the python scripts through an "Exec" node. This essentially makes a command line call to the host OS, and mimics the CLI process above. The advantage of this execution method is that it allows integration into wider automation systems and provides a stable, self-healing ability to run the script on demand. wrapping this core code in a logic flow.  
  
![image](https://user-images.githubusercontent.com/69121158/122303286-3bc7e000-cefb-11eb-93c5-bf48907bd189.png)
  
To execute this you must download the src files for this project, place them in an accessible folder on your machine running Node-Red then set the paramters of the Exec functon to call it.  
  
Example Node-Red flows are vailable here: XXXX

# RESTful Service
GivTCP provides a wrapper function REST.py which uses Flask to expose the read and control functions as RESTful http calls. To utilise this service you will need to either use a WSGI serivce such as gunicorn or use the pre-built Docker container

## Gunicorn
Ensure Gunicorn is installed by running:  

`pip install gunicorn`  

Then call the service by initiating the following command from the same directory as the downloaded src files:  

`gunicorn -w 4 -b 127.0.0.1:6345 REST:giv_api`  

(where the 127.0.0.1:6345 is the IP address and port you want to bind the service to)  

## Docker
The docker container can be downloaded at the Docker hub here:   
https://hub.docker.com/repository/docker/britkat/giv_tcp-ma
  
* Docker image is multi-architecture so docker should grab the correct version for your system (tested on x86 and rpi3)
* Create a container with the relevant ENV variables below (mimicing the settings.py file)
* Set the container to auto-restart to ensure reliability
* Out of the box the default setup enables local MQTT broker and REST service
* For Invertor autodiscovery to function your container must run on the "Host" network within docker (not Bridge). If it fails then you will need to manually add in INVERTOR_IP to the env variables

| ENV Name                | Example       |  Description                      |
| ----------------------- | ------------- |  -------------------------------- |
| INVERTOR_IP |192.168.10.1 | Docker container can auto detect Invertors if running on your host network. If this fails then add the IP manually to this ENV |
| MQTT_OUTPUT | True | Optional if set to True then MQTT_ADDRESS is required |
| MQTT_ADDRESS | 127.0.0.1 | Optional (but required if OUTPUT is set to MQTT) |
| MQTT_USERNAME | bob | Optional |
| MQTT_PASSWORD | cat | Optional |
| MQTT_TOPIC | GivEnergy/Data | Optional - default is Givenergy.<serial number>|
| DEBUG | False | Optional - if True then will write debug info to sepcified file location (default is same directory as the py files) |
| DEBUG_FILE_LOCATION | /usr/pi/data | Optional  |
| PRINT_RAW | False | Optional - If set to True the raw register values will be returned alongside the normal data |
| INFLUX_OUTPUT | False | Optional - Used to enable publishing of energy and power data to influx |
| INFLUX_TOKEN |abcdefg123456789| Optional - If using influx this is the token generated from within influxdb itself |
| INFLUX_BUCKET |giv_bucket| Optional - If using influx this is data bucket to use|
| INFLUX_ORG |giv_tcp| Optional - If using influx this is the org that the token is assigned to |
| HA_OUTPUT | False |Optional - Used to enable publishing of energy and power data to Home Assistant |
| HA_URL |https://homeassistant.local:8123| URL of Home Assistant instance (noting correct use of IP or domain name, whichever works in your browser)|
| HA_TOKEN |abcdefg123456789| Optional - If using Home Assistant this is the Long Lasting Token generated from within Home Assistant itself |


### Calling RESTFul Functions

The following table outlines the http methods needed to call the various read and control functions. For each control function the payload is an identical JSON string as above (minus the single quotes).  
The RESTful Service will return a JSON object which you can then parse as you so desire   

URL's below are based off the root http address of http://IP:6345
(Port may change if you are running yourself using gunicorn, in which case use the details specified in the gunicorn command)
  
#### Read Functions
| URL                | Method       |  payload              |
| ------------------ | ------------ |  -------------------- |
| /runALL| GET | None |  |
| /getTimeslots| GET | None | | 
| /getCombinedStats| GET | None | | 
| /getModesandTimes| GET | None | | 
  
#### Control Functions
| URL                | Method       |  payload              |
| ------------------ | ------------ |  -------------------- |
| /disableChargeTarget| POST | None | 
| /enableChargeTarget| POST | None |
| /pauseChargeSchedule| POST | None |
| /resumeChargeSchedule| POST | None |
| /pauseDischargeSchedule| POST | None |
| /resumeDischargeSchedule| POST | None | 
| /setChargeTarget| POST | {"chargeToPercent":"50"} |
| /setBatteryReserve| POST | {"dischargeToPercent":"5"} |
| /setChargeSlot1| POST | {"start":"0100","finish":"0400","chargeToPercent":"55") |
| /setChargeSlot2| POST | {"start":"0100","finish":"0400","chargeToPercent":"55") |
| /setDischargeSlot1| POST | {"start":"0100","finish":"0400","dischargeToPercent":"55") |
| /setDischargeSlot2| POST | {"start":"0100","finish":"0400","dischargeToPercent":"55") |
| /setBatteryMode| POST | {"mode":"1"} |


Not sure where to start? Check our [Quick Start Guide](/documentaion/tutorial.md)  

[Some API Documentation](/documentaion/APIDocumentation.md)  

[All the used registers are listed in here ](/documentaion/registersAndFunctions.xlsb.xlsx)

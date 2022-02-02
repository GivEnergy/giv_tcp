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

Reccomended usage is through the Docker container found here: https://hub.docker.com/repository/docker/britkat/giv_tcp-ma
This will set up a self-running service which will publish data as required and provide a REST interface for control. An internal MQTT broker can be activiated to make data avalable on the network.


# Output formats:
## MQTT
The script will publish directly to the nominated MQTT broker all the requested read data.

<img width="245" alt="image" src="https://user-images.githubusercontent.com/69121158/149670766-0d9a6c92-8ee2-44d6-9045-2d21b6db7ebf.png">
  
## JSON
The functions return a JSON formated object which can then be consumed by other systems or functions, default output is to stdout

## InfluxDB
Publish Power and energy stats to your InfluxDB database using credentials you provide.

# GivTCP functions
## Read functions

GivTCP collects all invertor ad battery data through the "runAll" function. It creates a nested data structure with all data available in a structured format.
Data Elements are:
* Energy - Today and all-time Total
    * Today
    * Total
* Power - Real-time stats and power flow data
    * Power stats (eg. Import)
    * Power Flow (eg. Grid to House)
* Invertor Details - Status details such as Serial Number
* Timeslots - Charge and Discharge
* Control - Charge/Discharge rates, Battery SOC
* Battery Details - Status and real-time cell voltages
    * Battery 1
    * Battery 2
    * ...


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
|setDateTime|{"dateTime":"dd/mm/yyyy hh:mm:ss"}| Sets invertor time, format must be as shown here|

# Docker
The docker container can be downloaded at the Docker hub here:   
https://hub.docker.com/repository/docker/britkat/giv_tcp-ma
  
* Docker image is multi-architecture so docker should grab the correct version for your system (tested on x86 and rpi3)
* Create a container with the relevant ENV variables below (mimicing the settings.py file)
* Set the container to auto-restart to ensure reliability
* Out of the box the default setup enables local MQTT broker and REST service (see below for details)
* For Invertor autodiscovery to function your container must run on the "Host" network within docker (not Bridge). If it fails then you will need to manually add in INVERTOR_IP to the env variables

| ENV Name                | Example       |  Description                      |
| ----------------------- | ------------- |  -------------------------------- |
| INVERTOR_IP |192.168.10.1 | Docker container can auto detect Invertors if running on your host network. If this fails then add the IP manually to this ENV |
| NUMBATTERIES | 1 | Number of battery units connected to the invertor |
| MQTT_OUTPUT | True | Optional if set to True then MQTT_ADDRESS is required |
| MQTT_ADDRESS | 127.0.0.1 | Optional (but required if OUTPUT is set to MQTT) |
| MQTT_USERNAME | bob | Optional |
| MQTT_PASSWORD | cat | Optional |
| MQTT_TOPIC | GivEnergy/Data | Optional - default is Givenergy.<serial number>|
| LOG_LEVEL | Error | Optional - you can choose Error, Info or Debug. Output will be sent to the debug file location if specified, otherwise it is sent to stdout|
| DEBUG_FILE_LOCATION | /usr/pi/data | Optional  |
| PRINT_RAW | False | Optional - If set to True the raw register values will be returned alongside the normal data |
| INFLUX_OUTPUT | False | Optional - Used to enable publishing of energy and power data to influx |
| INFLUX_TOKEN |abcdefg123456789| Optional - If using influx this is the token generated from within influxdb itself |
| INFLUX_BUCKET |giv_bucket| Optional - If using influx this is data bucket to use|
| INFLUX_ORG |giv_tcp| Optional - If using influx this is the org that the token is assigned to | 

# RESTful Service
GivTCP provides a wrapper function REST.py which uses Flask to expose the read and control functions as RESTful http calls. To utilise this service you will need to either use a WSGI serivce such as gunicorn or use the pre-built Docker container.

This can be used within a Node-Red flow to integrate into your automation or using Home Assistany REST sensors unsing the Home Assistant yaml package provided.
NB.This does require the Docker container running on your network.

## Calling RESTFul Functions

The following table outlines the http methods needed to call the various read and control functions. For each control function the payload is an identical JSON string as above (minus the single quotes).  
The RESTful Service will return a JSON object which you can then parse as you so desire   

URL's below are based off the root http address of http://IP:6345
(Port may change if you are running yourself using gunicorn, in which case use the details specified in the gunicorn command)
  
### Read Functions
| URL                | Method       |  payload              |
| ------------------ | ------------ |  -------------------- |
| /runAll| GET | None |  |
  
### Control Functions
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
| /setChargeSlot1| POST | {"start":"0100","finish":"0400","chargeToPercent":"55"} |
| /setChargeSlot2| POST | {"start":"0100","finish":"0400","chargeToPercent":"55"} |
| /setDischargeSlot1| POST | {"start":"0100","finish":"0400","dischargeToPercent":"55"} |
| /setDischargeSlot2| POST | {"start":"0100","finish":"0400","dischargeToPercent":"55"} |
| /setBatteryMode| POST | {"mode":"1"} |
| /setDateTime|POST | {"dateTime":"dd/mm/yyyy hh:mm:ss"}|


## Gunicorn
If you don't wish to run the docker container, you can set up your own wysg application using Gunicorn/Flask.
Ensure Gunicorn is installed by running:  

`pip install gunicorn`  

Then call the service by initiating the following command from the same directory as the downloaded src files:  

`gunicorn -w 4 -b 127.0.0.1:6345 REST:giv_api`  

(where the 127.0.0.1:6345 is the IP address and port you want to bind the service to)  

# CLI Usage
GivTCP can be called from any machine running Python3. The relevant script must be called and a function name passed to it as an argument. 

An example payload can be found below.
Note: In order to send json payloads via CLI you will need to place the JSON string inside single quotes  

The full call to set  Charge Timeslot 1 would then be:  
`python3 write.py setChargeSlot1 '{"enable": true,"start": "0100","finish": "0400","chargeToPercent": "100"}'` 
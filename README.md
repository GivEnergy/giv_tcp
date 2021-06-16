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

## Execution
### CLI
Execute the script at the command line and pass the relevant function and parameters as per the details below
### CLI Through Node-Red
Using the Exec node in Node-Red to call the script in the same way as above. This allows automation of script calling within a wider automated system
### REST Service
Deployed inside a Docker container a RESTful service calls the relevant functions using the details below through GET and POST http methods

## Outputs (Read mode):
### MQTT
The script will publish directly to the nominated MQTT broker all the requested read data.
### JSON
The functions return a JSON formated object which can then be consumed by other systems or functions

### Docker

### RESTful

### CLI

### CLI Through Node-Red

## GivTCP functions
### Read Data
To retrieve data and publish to the MQTT queue the read.py script is called with arguments as below:

`python3 read.py {{functionName}}`

Available read functions are:
| Function          | Payload       |  Description                      |
| ----------------- | ------------- |  -------------------------------- |
| getTimeslots      | None          | Gets all currently stored timeslots for Charge1, Discharge1 and Discharge2      |
| getCombinedStats  | None          | Gets power and Energy Stats (real-time, Today and Total)   |
| getModesandTimes  | None          | Gets the Timeslots and control state info including: Mode, Target Charge SOC, Battery Reserve, Charge and Discharge Schedule state (Paused/Active) and Battery Capacity    |
| runAll            | None          | Runs all of the above  |


### Control functions
Control is available through redefined functions which are called with arguments. The format of the function call matches the published GivEnegry cloud based battery.api. It requires a JSON pay load as per the below:

{
    "start": "0100",
    "finish": "0400",
    "chargeToPercent": "100"
}

Available control functions are:
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

## CLI

`python3 write.py {{functionName}} {{controlPayload}}`

An example payload can be found below and further details can be seen in the GivEnergy Docs to be found here: XXXXXXX

The full call to set  Charge Timeslot 1 would then be:

`python3 write.py setChargeSlot1 '{"enable": true,"start": "0100","finish": "0400","chargeToPercent": "100"}'`

Not sure where to start? Check our [Quick Start Guide](/documentaion/tutorial.md)

[Some API Documentation](/documentaion/APIDocumentation.md)

[All the used registers are listed in here ](/documentaion/registersAndFunctions.xlsb.xlsx)
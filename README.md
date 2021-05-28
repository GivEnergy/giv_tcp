# GivTCP
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

Set-up if through a settings.py file in the same directory which has the following data inside a class called GiV_Settings:
* invertorIP="XXX.XXX.XXX.XXX"
* dataloggerSN="XXXXXXXXX"
* MQTT_Address="XXX.XXX.XXX.XXX"
* MQTT_Username="XXXXXXX"
* MQTT_Password="XXXXXXX"

The scripts function through being called from the command line with appropriate parameters ssigned. There are both Read and Write functions, providing data acquisiation and control.

# Read
To retrieve data and publish to the MQTT queue the read.py script is called with arguments as below:

`python3 read.py {{functionName}}`

Available functions are:
* getTimeslots: Gets all currently stored timeslots for Charge1, Discharge1 and Discharge2
* getCombinedStats: Gets power and Energy Stats (real-time, Today and Total)
* getModes: Gets the control state info inclusing Mode, Target Charge SOC, Battery Reserve, Charge and Discharge Schedule state (Paused/Active) and Battery Capacity
* runAll:- Runs all of the above

# Control
Control is available through redefined functions which are called with arguments. The format of the function call matches the published GivEnegry cloud based battery.api. It requires a JSON pay load as per the below:

`python3 write.py {{functionName}} {{controlPayload}}`

An example payload can be found below and further details can be seen in the GivEnergy Docs to be found here: XXXXXXX

{
    "enable": true,
    "start": "0100",
    "finish": "0400",
    "chargeToPercent": "100"
}

The full call to set the chargeTimeslot would then be:

`python3 write.py setChargeSlot1 '{"enable": true,"start": "0100","finish": "0400","chargeToPercent": "100"}'`

Available control functions are:
| Function                | Payload       |  Description                      |
| ----------------------- | ------------- |  -------------------------------- |
| pauseChargeSchedule     | None          | Pauses the Charging schedule      |
| pauseDischargeSchedule  | None          | Pauses the Discharging schedule   |
| resumeChargeSchedule    | None          | Resumes the Charging schedule     |
| resumeDischargeSchedule | None          | Resumes the Discharging schedule  |
| setChargeTarget         | {"chargeToPercent":"50"}  | Sets the Target charge SOC |




Not sure where to start? Check our [Quick Start Guide](/documentaion/tutorial.md)

[Some API Documentation](/documentaion/APIDocumentation.md)

[All the used registers are listed in here ](/documentaion/registersAndFunctions.xlsb.xlsx)





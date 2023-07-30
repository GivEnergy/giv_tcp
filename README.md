# GivTCP
## TCP Modbus connection to MQTT/JSON for GivEnergy Battery/PV Invertors

This project opens a connection to the GivEnergy invertors via TCP Modbus. Access is given through the native Wifi/Ethernet dongle and can be connected via either LAN or directly through the inbuilt SSID AP.

The basis of this project is a connection to the Modbus TCP server which runs on the wifi dongle. All you need is run the script on the same network. The following is needed to make it work:
* GivEnergy Invertor that is commissioned and online.
* IP address of the invertor


## Docker
You can find the Docker container repo here: https://hub.docker.com/repository/docker/britkat/giv_tcp-ma
This will set up a self-running service which will publish data as required and provide a REST interface for control. An internal MQTT broker can be activiated to make data available on the network.
 
* Docker image is multi-architecture so docker should grab the correct version for your system (tested on x86 and rpi3)
* Create a container with the relevant ENV variables below (mimicing the settings.py file)
* Set the container to auto-restart to ensure reliability
* Out of the box the default setup enables local MQTT broker and REST service (see below for details)
* Configuration via ENV as outlined below

Installation via the docker-compose.yml file is recommended if not running through the Home Assistant add-on.

## Home Assistant Add-on
This container can also be used as an add-on in Home Assistant.
The add-on requires an existing MQTT broker such as Mosquito, also available to install from the Add-on store.
To install GivTCP as an add-on, add this repository (https://github.com/britkat1980/giv_tcp) to the Add-on Store repository list.
The following configuration items are mandatory before the add-on can be started:
* Inverter IP address
* MQTT username (can also be a Home Assistant user - used to authenticate againt your MQTT broker)
* MQTT password
All other configuration items can be left as-is unless you need to change them. See the ENV below for full details

### Home Assistant Usage
GivTCP will automatically create Home Assistant devices if "HA_AUTO_D" setting is True. This does require MQTT_OUTPUT to also be true and for GivTCP to publish its data to the same MQTT broker as HA is listening to.
This will populate HA with all devices and entities for control and monitoring. The key entities and their usage are outlined below:

## Settings - Environment Variables

| ENV Name                | Example       |  Description                      |
| ----------------------- | ------------- |  -------------------------------- |
| NUMINVERTORS | 1 | Number of inverters on the network. Max inverters supprted is three |
| INVERTOR_IP_1 |192.168.10.1 | IP Address of your first inverter  |
| NUMBATTERIES_1 | 1 | Number of battery units connected to the first inverter |
| INVERTOR_IP_2 |192.168.10.1 | Optional - IP Address of your second inverter |
| NUMBATTERIES_2 | 1 | Optional - Number of battery units connected to the second inverter |
| INVERTOR_IP_3 |192.168.10.1 | Optional - IP Address of your third inverter |
| NUMBATTERIES_3 | 1 | Optional - Number of battery units connected to the third inverter |
| MQTT_OUTPUT | True | Optional if set to True then MQTT_ADDRESS is required |
| MQTT_ADDRESS | 127.0.0.1 | Optional (but required if OUTPUT is set to MQTT) |
| MQTT_USERNAME | bob | Optional |
| MQTT_PASSWORD | cat | Optional |
| MQTT_TOPIC | GivEnergy/Data | Optional - default is Givenergy.<serial number>|
| MQTT_TOPIC_2 | GivEnergy/Data | Optional - Setting for second Inverter if configured. default is Givenergy.<serial number>|
| MQTT_TOPIC_2 | GivEnergy/Data | Optional - Setting for third Inverter if configured. default is Givenergy.<serial number>|
| LOG_LEVEL | Error | Optional - you can choose Error, Info or Debug. Output will be sent to the debug file location if specified, otherwise it is sent to stdout|
| DEBUG_FILE_LOCATION | /usr/pi/data | Optional  |
| PRINT_RAW | False | Optional - If set to True the raw register values will be returned alongside the normal data |
| SELF_RUN | True | Optional - If set to True the system will loop round connecting to invertor and publishing its data |
| SELF_RUN_LOOP_TIMER | 5 | Optional - The wait time bewtween invertor calls when using SELF_RUN |
| INFLUX_OUTPUT | False | Optional - Used to enable publishing of energy and power data to influx |
| INFLUX_TOKEN |abcdefg123456789| Optional - If using influx this is the token generated from within influxdb itself |
| INFLUX_BUCKET |giv_bucket| Optional - If using influx this is data bucket to use|
| INFLUX_ORG |giv_tcp| Optional - If using influx this is the org that the token is assigned to | 
| HA_AUTO_D | True | Optional - If set to true and MQTT is enabled, it will publish Home Assistant Auto Discovery messages, which will allow Home Assistant to automagically create all entitites and devices to allow read and control of your Inverter |
| HADEVICEPREFIX | GivTCP | Optional - Prefix to be placed in front of every Home Assistent entity created by the above for inverter 1 |
| HADEVICEPREFIX_2 | GivTCP | Optional - Prefix to be placed in front of every Home Assistent entity created by the above for inverter 2 |
| HADEVICEPREFIX_3 | GivTCP | Optional - Prefix to be placed in front of every Home Assistent entity created by the above for inverter 3 |
| DAYRATE | 0.155 | Optional - Cost of your daytime energy if using Economy 7 or Octopus Go |
| NIGHTRATE | 0.155 | Optional - Cost of your night time energy if using Economy 7 or Octopus Go |
| DYNAMICTARIFF | False | Optional - Allows an external automation to trigger switch to 'Day' or 'Night' tariff rates. If set to true it ignores the times set below|
| DAYRATESTART | 04:30 | Optional - Start time of your daytime energy if using Economy 7 or Octopus Go |
| NIGHTRATESTART | 00:00 | Optional - Start time of your night time energy if using Economy 7 or Octopus Go |
| HOSTIP | 192.168.1.20 | Optional - The host IP address of your container. Required to access the web dashboard from any browser |
| DATASMOOTHER | Medium | The amount of smoothing to apply to the data, to reduce the effect of sudden invalid jumps in values. Set to 'None' to disable. Values are not case-sensitive. Other values are 'High', 'Medium', 'Low, 'None' |
| SMARTTARGET | False | Optional - If set to True will use Palm SOC to predict solar forecast and use historic usage to determine overnight charge target |
| GEAPI | abcdefg12345 | Optional - (SMARTTARGET) API Key from the GivEnergy Cloud to allow historic usage stats for SMARTTARGET |
| SOLCASTAPI |  | Optional - (SMARTTARGET) API Key for Solcast to allow solar prediction for SMARTTARGET |
| SOLCASTSITEID |  | Optional - (SMARTTARGET) Solcast ID for array 1, needed for SMARTTARGET |
| SOLCASTSITEID2 |  | Optional - (SMARTTARGET) Solcast ID for array 2 (if it exists), needed for SMARTTARGET |
| PALM_WINTER | 01,02,03,10,11,12 | Optional - (SMARTTARGET) Comma delimited list of the winter months (01=January, etc) |
| PALM_SHOULDER | 04,05,09 | Optional - (SMARTTARGET) Comma delimited list of months in which consumption can vary so SOC calculation should be more cautious |
| PALM_MIN_SOC_TARGET | 25 | Optional - (SMARTTARGET) Lower limit for state of charge (summertime) |
| PALM_MAX_SOC_TARGET | 45 | Optional - (SMARTTARGET) Lower limit for SoC limit in shoulder months |
| PALM_BATT_RESERVE | 4 | Optional - (SMARTTARGET) Battery reserve for power cuts (minimum of 4%) |
| PALM_BATT_UTILISATION | 0.85 | Optional - (SMARTTARGET) Usable proportion of battery (100% less reserve and any charge limit) on a scale of 0-1 |
| PALM_CHARGE_RATE | 2.5 | Optional - (SMARTTARGET) Inverter charge/discharge rate in kW |
| PALM_BATT_CAPACITY | 10.4 | Optional - (SMARTTARGET) Nominal battery capacity in kWh |


## GivTCP Read data

GivTCP collects all inverter and battery data through the "runAll" function. It creates a nested data structure with all data available in a structured format.
Data Elements are:
* Energy - Today and all-time Total
    * Today
    * Total
* Power - Real-time stats and power flow data
    * Power stats (eg. Import)
    * Power Flow (eg. Grid to House)
* Inverter Details - Status details such as Serial Number
* Timeslots - Charge and Discharge
* Control - Charge/Discharge rates, Battery SOC
* Battery Details - Status and real-time cell voltages
    * Battery 1
    * Battery 2
    * ...

| Function      | Description                                                                        | REST URL  |
|---------------|------------------------------------------------------------------------------------|-----------|
| getData       | This connects to the inverter, collects all data and stores a cache for publishing | /getData  |
| readData      | Retrieves data from the local cache and publishes data according to the settings   | /readData |
| getCache      | Retrieves data from the local cache returns it without publishing to MQTT etc...   | /getCache |
| RunAll        | Runs both getData and pubFromPickle to refresh data and then publish               | /runAll   |

If you have enabled the "SELF_RUN" setting (recommended) then the container/add-on will automatically call "RunALL" every "SELF_LOOPTIMER" seconds and you will not need to use the REST commands here. If you wish to take data from GivTCP and push to another system, then you should call "getCache" which will return the json data without pushing to MQTT or other defined publish settings.

## GivTCP Control
| Function                | Description                                                                                                                                                                                               | REST URL                 | REST payload                                               | MQTT Topic              | MQTT Payload                                               |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|------------------------------------------------------------|-------------------------|------------------------------------------------------------|
| enableChargeTarget      | Sets   inverter to follow setChargeTarget value when charging from grid (will stop   charging when battery SOC= ChargeTarget)                                                                             | /enableChargeTarget      | {"state","enable"}                                         | enableChargeTarget      | enable                                                     |
| disableChargeTarget     | Sets   inverter to ignore setChargeTarget value when charging from grid (will   continue to charge to 100% during ChargeSlot)                                                                             | /disableChargeTarget     | {"state","enable"}                                         | disableChargeTarget     | enable                                                     |
| enableChargeSchedule    | Sets   the Charging schedule state, if disabled the battery will not charge as per   the schedule                                                                                                         | /enableChargeSchedule    | {"state","enable"}                                         | enableChargeSchedule    | enable                                                     |
| enableDischargeSchedule | Sets   the Discharging schedule state, if disabled the battery will will ignore rhe   discharge schedule and discharge as per demand (similar to eco mode)                                                | /enableDischargeSchedule | {"state","enable"}                                         | enableDischargeSchedule | enable                                                     |
| enableDischarge         | Enable/Disables Discharging to instantly pause discharging,   use 'enable' or 'disable'                                                                                                                   | /enableDischarge         | {"state","enable"}                                         | enableDischarge         | enable                                                     |
| setChargeRate           | Sets the charge power as a percentage. 100% == 2.6kW                                                                                                                                                      | /setChargeRate           | {"chargeRate","100"}                                    | setChargeRate           | 100                                                        |
| setDischargeRate        | Sets the discharge power as a percentage. 100% == 2.6kW                                                                                                                                                   | /setDischargeRate        | {"dischargeRate","100"}                                       | setDischargeRate        | 100                                                        |
| setChargeTarget         | Sets   the Target charge SOC                                                                                                                                                                              | /setChargeTarget         | {"chargeToPercent":"50"}                                   | setChargeTarget         | 50                                                         |
| setBatteryReserve       | Sets   the Battery Reserve discharge cut-off limit                                                                                                                                                        | /setBatteryReserve       | {"reservePercent":"5"}                                 | setBatteryReserve       | 5                                                          |
| setChargeSlot1          | Sets   the time and target SOC of the first chargeslot. Times must be expressed in   hhmm format. Enable flag show in the battery.api documentation is not needed   and chargeToPercent is optional       | /setChargeSlot1          | {"start":"0100","finish":"0400","chargeToPercent":"55")    | setChargeSlot1          | {"start":"0100","finish":"0400","chargeToPercent":"55")    |
| setDischargeSlot1       | Sets   the time and target SOC of the first dischargeslot. Times must be expressed   in hhmm format. Enable flag show in the battery.api documentation is not   needed and dischargeToPercent is optional | /setDischargeSlot1       | {"start":"0100","finish":"0400","dischargeToPercent":"55") | setDischargeSlot1       | {"start":"0100","finish":"0400","dischargeToPercent":"55") |
| setDischargeSlot2       | Sets   the time and target SOC of the first dischargeslot. Times must be expressed   in hhmm format. Enable flag show in the battery.api documentation is not   needed and dischargeToPercent is optional | /setDischargeSlot2       | {"start":"0100","finish":"0400","dischargeToPercent":"55") | setDischargeSlot2       | {"start":"0100","finish":"0400","dischargeToPercent":"55") |
| setBatteryMode          | Sets   battery operation mode. Mode value must be one of Eco, Timed Demand or Timed Export                                                                                                                                        | /setBatteryMode          | {"mode":"Eco"}                                               | setBatteryMode          | 1                                                          |
| setDateTime             | Sets   inverter time, format must be as define in payload                                                                                                                                                 | /setDateTime             | {"dateTime":"dd/mm/yyyy   hh:mm:ss"}                       | setDateTime             | "dd/mm/yyyy hh:mm:ss"                                      |

## Usage methods:
GivTCP data and control is generally available through two core methods. If you are using the Home Assistant Add-On then these are generally transparent to the user, but are working and available in the background.

### MQTT
By setting MQTT_OUTPUT = True, the script will publish directly to the nominated MQTT broker (MQTT_ADDRESS) all the requested read data.

Data is published to "GivEnergy/<serial_number>/" by default or you can nominate a specific root topic by setting "MQTT_TOPIC" in the settings.

<img width="245" alt="image" src="https://user-images.githubusercontent.com/69121158/149670766-0d9a6c92-8ee2-44d6-9045-2d21b6db7ebf.png">

Control is available using MQTT. By publishing data to the same MQTT broker as above you can trigger the control methods as per the above table.
Root topic for control is:
"GivEnergy/control/<serial_number>/"    - Default
"<MQTT_TOPIC>/control/<serial_number>/" - If MQTT_TOPIC is set

### RESTful Service
GivTCP provides a wrapper function REST.py which uses Flask to expose the read and control functions as RESTful http calls. To utilise this service you will need to either use a WSGI service such as gunicorn or use the pre-built Docker container.

If Docker is running in Host mode then the REST service is available on port 6345

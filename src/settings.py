# version 1.0
class GiV_Settings:
    invertorIP="192.168.2.146"           #Required - IP address of Invertor on local network
#MQTT Output Settings
    MQTT_Output="True"               #True or False
    MQTT_Address="192.168.2.83"         #IP address of MQTT broker (local or remote)
    MQTT_Username="mqtt"            #Optional - Username for MQTT broker
    MQTT_Password="mqtt2020"        #Optional - Password for MQTT broker
    MQTT_Topic=""           #Optional - Root topic for all MQTT messages. Defaults to "GivEnergy/<SerialNumber> 
    MQTT_Port=""
#Debug Settings
    debug="False"                #Optional - Enables verbose debug "True" or "False".
    Debug_File_Location=""  #Optional - Location of debug file (Default is root directory)
    Print_Raw_Registers="True"  #Optional - "True" prints all raw registers to the MQTT broker
#Influx Settings - Only works with Influx v2
    Influx_Output="False"       #True or False
    influxURL="http://localhost:8086"
    influxToken=""
    influxBucket="GivEnergy"
    influxOrg="GivTCP"
#JSON Settings
    JSON_Output="False"     #True or False
#Home Assistant Settings
    HA_Output="False"       #True or False
    HA_url="http://IPADDRESS"
    HA_token = ""   #Create a long lasting Token in Homeassistant and paste here
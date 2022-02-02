# version 2022.01.31
class GiV_Settings:
    invertorIP=""                   #Required - IP address of Invertor on local network
    numBatteries=""
#Debug Settings
    Log_Level="True"                #Optional - Enables verbose debug "True" or "False".
    Debug_File_Location=""          #Optional - Location of logs (Default is console)
    Print_Raw_Registers="False"     #Optional - "True" prints all raw registers to the MQTT broker
#MQTT Output Settings
    MQTT_Output=""                  #True or False
    MQTT_Address=""                 #IP address of MQTT broker (local or remote)
    MQTT_Username=""                #Optional - Username for MQTT broker
    MQTT_Password=""                #Optional - Password for MQTT broker
    MQTT_Topic=""                   #Optional - Root topic for all MQTT messages. Defaults to "GivEnergy/<SerialNumber> 
    MQTT_Port=""
#Influx Settings - Only works with Influx v2
    Influx_Output="False"           #True or False
    influxURL="http://localhost:8086"
    influxToken=""
    influxBucket="GivEnergy"
    influxOrg="GivTCP"
#JSON Settings
    JSON_Output="False"             #True or False
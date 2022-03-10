# version 2022.02.22

class GiV_Settings:
    invertorIP="192.168.2.146"                   #Required - IP address of Invertor on local network
    numBatteries= 1
    HA_Auto_D=True
#Debug Settings
    Log_Level="Error"               #Optional - Enables logging level. Default is "Error", but can be "Info" or "Debug"
    Debug_File_Location=""          #Optional - Location of logs (Default is console)
    Print_Raw_Registers= True      #Optional - "True" publishes all available registers.
#MQTT Output Settings
    MQTT_Output= True                  #True or False
    MQTT_Address="192.168.2.83"                 #IP address of MQTT broker (local or remote)
    MQTT_Username="mqtt"                #Optional - Username for MQTT broker
    MQTT_Password="mqtt2020"                #Optional - Password for MQTT broker
    MQTT_Topic=""                   #Optional - Root topic for all MQTT messages. Defaults to "GivEnergy/<SerialNumber> 
    MQTT_Port= 1883
#Influx Settings - Only works with Influx v2
    Influx_Output= False           #True or False
    influxURL="http://localhost:8086"
    influxToken=""
    influxBucket="GivEnergy"
    influxOrg="GivTCP"
    first_run = False
    serial_number = "SA2047G098"
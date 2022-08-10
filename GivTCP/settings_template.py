# version 2022.01.31
class GiV_Settings:
    numInvertors=1                  #Required - Number of different invertors you want to connect to (MAX 4)
    invertorIP_1=""                 #Required - IP address of first Invertor on local network
    invertorIP_2=""                 #Optional - IP address of second Invertor on local network. More lines like this can be added for each invertor. The number of these lines must match the numInvertors line above
    numBatteries_1=1                #Required - The number of batteries connected the first invertor
    numBatteries_2=1                #Optional - The number of batteries connected the second invertor. More lines like this can be added for each invertor. The number of these lines must match the numInvertors line above
    HA_Auto_D=True                  #Optional - Bool - Publishes Home assistant MQTT Auto Discovery messages to push data into HA automagically (requires MQTT to be enabled below)
    self_run_timer=1                #Required - The wait time between invertor read calls. Can be as low as 1 or longer if you want to allow the cloud portal a better chance of polling
#Debug Settings
    Log_Level="Error"               #Optional - Enables logging level. Default is "Error", but can be "Info" or "Debug"
    Debug_File_Location=""          #Optional - Location of logs (Default is console)
    Print_Raw_Registers=True        #Optional - Bool - True publishes all available registers.
#MQTT Output Settings
    MQTT_Output= True               #Optional - Bool - True or False
    MQTT_Address="127.0.0.1"        #Optional - (Required is above set to True) IP address of MQTT broker (local or remote)
    MQTT_Username=""                #Optional - Username for MQTT broker
    MQTT_Password=""                #Optional - Password for MQTT broker
    MQTT_Topic=""                   #Optional - Root topic for all MQTT messages. Defaults to "GivEnergy/<SerialNumber> 
    MQTT_Port=1883                  #Optional - Int - define port that MQTT broker is listening on (default 1883)
#Influx Settings - Only works with Influx v2
    Influx_Output= False            #True or False
    influxURL="http://localhost:8086"
    influxToken=""
    influxBucket="GivEnergy"
    influxOrg="GivTCP"
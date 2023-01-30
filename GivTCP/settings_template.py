# version 2022.01.31
class GiV_Settings:
# Invertor Info
    invertorIP="1.2.3.4"        #Required - IP address of Invertor on local network
    numBatteries=1                  #Required - The number of batteries connected this invertor
    self_run_timer = 5              #Optional - Used to loop the "Self_run" function for regular reading
    default_path = "GivTCP"         #Required - Used to ensure python execution. Should be the base folder you run GivTCP from
    givtcp_instance=1               #Required - WHich instance of GivTCP is this? Usually 1 if you only have one invertor
    
# Debug Settings
    Log_Level="Error"               #Optional - Enables logging level. Default is "Error", but can be "Info", "Critical" or "Debug"
    Print_Raw_Registers=True        #Optional - Bool - True publishes all available registers.
    cache_location="/config/GivTCP" #Optional - default is "/config/GivTCP"
    data_smoother="High"            #Required - sets the level of data smoothing applied to certain data. High, Medium, Low, or None to disable

# MQTT Output Settings
    MQTT_Output= True               #Optional - Bool - True or False
    MQTT_Address="192.168.2.83"     #Optional - (Required is above set to True) IP address of MQTT broker (local or remote)
    MQTT_Username="mqtt"            #Optional - Username for MQTT broker
    MQTT_Password="mqtt2020"        #Optional - Password for MQTT broker
    MQTT_Topic=""                   #Optional - Root topic for all MQTT messages. Defaults to "GivEnergy/<SerialNumber> 
    MQTT_Port=1883                  #Optional - Int - define port that MQTT broker is listening on (default 1883)

# Influx Settings
    Influx_Output= False            #Optional - turns on Influx as a data publisher. True or False
    influxURL="http://IP:8086"      #Optional - URL of your influx instance
    influxToken=""                  #Optional - Token for your influx instance
    influxBucket="GivEnergy"        #Optional - name of Bucket to put data into
    influxOrg="GivTCP"              #Optional - Influx Organisation to use

# Home Assistant
    HA_Auto_D=True                  #Optional - Bool - Publishes Home assistant MQTT Auto Discovery messages to push data into HA automagically (requires MQTT to be enabled below)
    ha_device_prefix=""             #Required - This is the prefix used at the start of every Home Assistant device created

# Rate Data
    day_rate=0.155                  #Required - £ per kWh of your electricity day rate
    day_rate_start="00:30"          #Required - time your day rate starts "HH:MM"
    night_rate=0.055                #Required - £ per kWh of your electricity night rate
    night_rate_start="00:00"        #Required - time your night rate starts "HH:MM"
    export_rate=0.055               #Required - £ per kWh of your electricity export rate


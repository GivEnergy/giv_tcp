class GiV_Settings:
    invertorIP=""           #Required - IP address of Invertor on local network
    dataloggerSN=""         #Required - Wifi/GPS S/N found here: https://www.givenergy.cloud/GivManage/setting/deviceMenu/inverterList
    output=""               #Required - "MQTT" or "JSON"
    MQTT_Address=""         #Required (if output=MQTT) -  IP address of MQTT broker (local or remote)
    MQTT_Username=""        #Optional - Username for MQTT broker
    MQTT_Password=""        #Optional - Password for MQTT broker
    MQTT_Topic=""           #Optional - Root topic for all MQTT messages. Defaults to "GivEnergy/<dataloggerSN> 
    debug=""                #Optional - Enables verbose debug "True" or "False".
    Debug_File_Location=""  #Optional - Location of debug file (Default is root directory)
    Print_Raw_Registers=""  #Optional - "True" prints all raw registers to the MQTT broker
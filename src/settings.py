class GiV_Settings:
  invertorIP="192.168.2.146"           #Required - IP address of Invertor on local network
  dataloggerSN="WF2036G878"         #Required - Wifi/GPS S/N found here: https://www.givenergy.cloud/GivManage/setting/deviceMenu/inverterList
  output="JSON"               #Required - "MQTT" or "JSON"
  MQTT_Address=""         #Required - if output is MQTT IP address of MQTT broker (local or remote)
  MQTT_Username=""        #Optional - Username for MQTT broker
  MQTT_Password=""        #Optional - Password for MQTT broker
  MQTT_Topic=""           #Optional - Root topic for all MQTT messages. Defaults to "GivEnergy/<dataloggerSN> 
  debug=""                #Optional - Enables verbose debug "True" or "False".
  Debug_File_Location=""  #Optional - Location of debug file (Default is root directory)
  Print_Raw_Registers="True"  #Optional - "True" prints all raw registers to the MQTT broker
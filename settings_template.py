class GiV_Settings:
  invertorIP=""           #Required - IP address of Invertor on local network
  dataloggerSN=""         #Required - Wifi/GPS S/N found here: https://www.givenergy.cloud/GivManage/setting/deviceMenu/inverterList
  MQTT_Address=""         #Required - IP address of MQTT broker (local or remote)
  MQTT_Username=""        #Optional - Username for MQTT broker
  MQTT_Password=""        #Optional - Password for MQTT broker
  MQTT_Topic=""           #Optional - Root topic for all MQTT messages. Defaults to "GivEnergy/<dataloggerSN>
  Log_To_File=""          #Optional - When used with debug this outputs logging to file 
  Debug_File_Location=""  #Optional - When used with Log_To_File this will write to specified location (Default is root directory)
  Print_Raw_Registers=""  #Optional - "True" prints all raw registers to the MQTT broker
  debug=""                #Optional - Enables verbose debug "True" or "False". Default location is stdout
  Invertor_Type=""         #"Hybrid" or "AC Coupled"
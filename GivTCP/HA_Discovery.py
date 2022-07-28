# version 2022.01.21
from array import array
from logging import Logger
import paho.mqtt.client as mqtt
import time
import datetime
import json

import logging  
from settings import GiV_Settings
from givenergy_modbus.model.inverter import Model
from mqtt import GivMQTT

if GiV_Settings.Log_Level.lower()=="debug":
    if GiV_Settings.Debug_File_Location=="":
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(filename=GiV_Settings.Debug_File_Location, encoding='utf-8', level=logging.DEBUG)
elif GiV_Settings.Log_Level.lower()=="info":
    if GiV_Settings.Debug_File_Location=="":
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(filename=GiV_Settings.Debug_File_Location, encoding='utf-8', level=logging.INFO)
else:
    if GiV_Settings.Debug_File_Location=="":
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(filename=GiV_Settings.Debug_File_Location, encoding='utf-8', level=logging.ERROR)

logger = logging.getLogger("GivTCP")

class HAMQTT():

    entity_type={
        "Last_Updated_Time":["sensor","timestamp"],
        "Time_Since_Last_Update":["sensor",""],
        "status":["sensor",""],
        "Export_Energy_Total_kWh":["sensor","energy"],
        "Battery_Throughput_Total_kWh":["sensor","energy"],
        "AC_Charge_Energy_Total_kWh":["sensor","energy"],
        "Import_Energy_Total_kWh":["sensor","energy"],
        "Invertor_Energy_Total_kWh":["sensor","energy"],
        "PV_Energy_Total_kWh":["sensor","energy"],
        "Load_Energy_Total_kWh":["sensor","energy"],
        "Battery_Charge_Energy_Total_kWh":["sensor","energy"],
        "Battery_Discharge_Energy_Total_kWh":["sensor","energy"],
        "Self_Consumption_Energy_Total_kWh":["sensor","energy"],
        "Battery_Throughput_Today_kWh":["sensor","energy"],
        "PV_Energy_Today_kWh":["sensor","energy"],
        "Import_Energy_Today_kWh":["sensor","energy"],
        "Export_Energy_Today_kWh":["sensor","energy"],
        "AC_Charge_Energy_Today_kWh":["sensor","energy"],
        "Invertor_Energy_Today_kWh":["sensor","energy"],
        "Battery_Charge_Energy_Today_kWh":["sensor","energy"],
        "Battery_Discharge_Energy_Today_kWh":["sensor","energy"],
        "Self_Consumption_Energy_Today_kWh":["sensor","energy"],
        "Load_Energy_Today_kWh":["sensor","energy"],
        "PV_Power_String_1":["sensor","power"],
        "PV_Power_String_2":["sensor","power"],
        "PV_Power":["sensor","power"],
        "PV_Voltage_String_1":["sensor","voltage"],
        "PV_Voltage_String_2":["sensor","voltage"],
        "Grid_Power":["sensor","power"],
        "Import_Power":["sensor","power"],
        "Export_Power":["sensor","power"],
        "EPS_Power":["sensor","power"],
        "Invertor_Power":["sensor","power"],
        "Load_Power":["sensor","power"],
        "AC_Charge_Power":["sensor","power"],
        "Self_Consumption_Power":["sensor","power"],
        "Battery_Power":["sensor","power"],
        "Charge_Power":["sensor","power"],
        "Discharge_Power":["sensor","power"],
        "SOC":["sensor","battery"],
        "Solar_to_House":["sensor","power"],
        "Solar_to_Battery":["sensor","power"],
        "Solar_to_Grid":["sensor","power"],
        "Battery_to_House":["sensor","power"],
        "Grid_to_Battery":["sensor","power"],
        "Grid_to_House":["sensor","power"],
        "Battery_to_Grid":["sensor","power"],
        "Battery_Type":["sensor",""],
        "Battery_Capacity_kWh":["sensor",""],
        "Invertor_Serial_Number":["sensor","",""],
        "Modbus_Version":["sensor",""],
        "Meter_Type":["sensor",""],
        "Invertor_Type":["sensor",""],
        "Invertor_Temperature":["sensor","temperature"],
        "Discharge_start_time_slot_1":["sensor",""],
        "Discharge_end_time_slot_1":["sensor",""],
        "Discharge_start_time_slot_2":["sensor",""],
        "Discharge_end_time_slot_2":["sensor",""],
        "Charge_start_time_slot_1":["sensor",""],
        "Charge_end_time_slot_1":["sensor",""],
        "Charge_start_time_slot_2":["sensor",""],
        "Charge_end_time_slot_2":["sensor",""],
        "Battery_Serial_Number":["sensor","",""],
        "Battery_SOC":["sensor","battery"],
        "Battery_Capacity":["sensor","",""],
        "Battery_Design_Capacity":["sensor","",""],
        "Battery_Remaining_Capcity":["sensor","",""],
        "Battery_Firmware_Version":["sensor",""],
        "Battery_Cells":["sensor","",""],
        "Battery_Cycles":["sensor","",""],
        "Battery_USB_present":["binary_sensor",""],
        "Battery_Temperature":["sensor","temperature"],
        "Battery_Voltage":["sensor","voltage"],
        "Battery_Cell_1_Voltage":["sensor","voltage"],
        "Battery_Cell_2_Voltage":["sensor","voltage"],
        "Battery_Cell_3_Voltage":["sensor","voltage"],
        "Battery_Cell_4_Voltage":["sensor","voltage"],
        "Battery_Cell_5_Voltage":["sensor","voltage"],
        "Battery_Cell_6_Voltage":["sensor","voltage"],
        "Battery_Cell_7_Voltage":["sensor","voltage"],
        "Battery_Cell_8_Voltage":["sensor","voltage"],
        "Battery_Cell_9_Voltage":["sensor","voltage"],
        "Battery_Cell_10_Voltage":["sensor","voltage"],
        "Battery_Cell_11_Voltage":["sensor","voltage"],
        "Battery_Cell_12_Voltage":["sensor","voltage"],
        "Battery_Cell_13_Voltage":["sensor","voltage"],
        "Battery_Cell_14_Voltage":["sensor","voltage"],
        "Battery_Cell_15_Voltage":["sensor","voltage"],
        "Battery_Cell_16_Voltage":["sensor","voltage"],
        "Battery_Cell_1_Temperature":["sensor","temperature"],
        "Battery_Cell_2_Temperature":["sensor","temperature"],
        "Battery_Cell_3_Temperature":["sensor","temperature"],
        "Battery_Cell_4_Temperature":["sensor","temperature"],
        "Mode":["select","","setBatteryMode"],
        "Battery_Power_Reserve":["number","","setBatteryReserve"],
        "Target_SOC":["number","","setChargeTarget"],
        "Enable_Charge_Schedule":["switch","","enableChargeSchedule"],
        "Enable_Discharge_Schedule":["switch","","enableDishargeSchedule"],
        "Enable_Discharge":["switch","","enableDischarge"],
        "Battery_Charge_Rate":["number","","setChargeRate"],
        "Battery_Discharge_Rate":["number","","setDischargeRate"]
        }

    if GiV_Settings.MQTT_Port=='':
        MQTT_Port=1883
    else:
        MQTT_Port=int(GiV_Settings.MQTT_Port)
    MQTT_Address=GiV_Settings.MQTT_Address
    if GiV_Settings.MQTT_Username=='':
        MQTTCredentials=False
    else:
        MQTTCredentials=True
        MQTT_Username=GiV_Settings.MQTT_Username
        MQTT_Password=GiV_Settings.MQTT_Password
    if GiV_Settings.MQTT_Topic=="":
        GiV_Settings.MQTT_Topic="GivEnergy"


    def on_connect(client, userdata, flags, rc):
        if rc==0:
            client.connected_flag=True #set flag
            logger.info("connected OK Returned code="+str(rc))
            #client.subscribe(topic)
        else:
            logger.info("Bad connection Returned code= "+str(rc))
    
    def publish_discovery(array,SN):   #Recieve multiple payloads with Topics and publish in a single MQTT connection
        mqtt.Client.connected_flag=False        			#create flag in class
        client=mqtt.Client("GivEnergy_GivTCP")
        rootTopic=str(GiV_Settings.MQTT_Topic+"/"+SN+"/")
        if HAMQTT.MQTTCredentials:
            client.username_pw_set(HAMQTT.MQTT_Username,HAMQTT.MQTT_Password)
        client.on_connect=HAMQTT.on_connect     			#bind call back function
        client.loop_start()
        logger.info ("Connecting to broker: "+ HAMQTT.MQTT_Address)
        client.connect(HAMQTT.MQTT_Address,port=HAMQTT.MQTT_Port)
        while not client.connected_flag:        			#wait in loop
            logger.info ("In wait loop")
            time.sleep(0.2)
            ##publish the status message
            client.publish(GiV_Settings.MQTT_Topic+"/"+SN+"/status","online", retain=True)
        ### For each topic create a discovery message
            for p_load in array:
                if p_load != "raw":
                    payload=array[p_load]
                    logger.info('Publishing: '+rootTopic+p_load)
                    output=GivMQTT.iterate_dict(payload,rootTopic+p_load)   #create LUT for MQTT publishing
                    for topic in output:
                        #Determine Entitiy type (switch/sensor/number) and publish the right message
                        if HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="sensor":
                            if "Battery_Details" in topic:
                                client.publish("homeassistant/sensor/GivEnergy/"+str(topic).split("/")[-2]+"_"+str(topic).split("/")[-1]+"/config",HAMQTT.create_device_payload(topic,SN),retain=True)
                            else:
                                client.publish("homeassistant/sensor/GivEnergy/"+SN+"_"+str(topic).split("/")[-1]+"/config",HAMQTT.create_device_payload(topic,SN),retain=True)
                        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="switch":
                            client.publish("homeassistant/switch/GivEnergy/"+SN+"_"+str(topic).split("/")[-1]+"/config",HAMQTT.create_device_payload(topic,SN),retain=True)
                        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="number":
                            client.publish("homeassistant/number/GivEnergy/"+SN+"_"+str(topic).split("/")[-1]+"/config",HAMQTT.create_device_payload(topic,SN),retain=True)
                    #    elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="binary_sensor":
                    #        client.publish("homeassistant2/binary_sensor/GivEnergy/"+str(topic).split("/")[-1]+"/config",HAMQTT.create_binary_sensor_payload(topic,SN),retain=True)
                        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="select":
                            client.publish("homeassistant/select/GivEnergy/"+SN+"_"+str(topic).split("/")[-1]+"/config",HAMQTT.create_device_payload(topic,SN),retain=True)
                           
        client.loop_stop()                      			#Stop loop
        client.disconnect()
        return client

    def create_device_payload(topic,SN):
        tempObj={}
        tempObj['stat_t']=str(topic).replace(" ","_")
        tempObj['avty_t'] = GiV_Settings.MQTT_Topic+"/"+SN+"/status"
        tempObj["pl_avail"]= "online"
        tempObj["pl_not_avail"]= "offline"
        tempObj['device']={}
        GiVTCP_Device=str(topic).split("/")[2]
        if "Battery_Details" in topic:
            tempObj["name"]="GivTCP "+str(topic).split("/")[3].replace("_"," ")+" "+str(topic).split("/")[-1].replace("_"," ") #Just final bit past the last "/"
            tempObj['uniq_id']=str(topic).split("/")[3]+"_"+GiVTCP_Device+"_"+str(topic).split("/")[-1]
            tempObj['device']['identifiers']=str(topic).split("/")[3]+"_"+GiVTCP_Device
            tempObj['device']['name']="GivTCP_"+str(topic).split("/")[3]+"_"+GiVTCP_Device
        else:
            tempObj['uniq_id']=SN+"_"+GiVTCP_Device+"_"+str(topic).split("/")[-1]
            tempObj['device']['identifiers']=SN+"_"+GiVTCP_Device
            tempObj['device']['name']="GivTCP_"+SN+"_"+GiVTCP_Device
            tempObj["name"]="GivTCP "+str(topic).split("/")[-1].replace("_"," ") #Just final bit past the last "/"
        tempObj['device']['manufacturer']="GivEnergy"

        try:
            tempObj['command_topic']=GiV_Settings.MQTT_Topic+"/control/"+SN+"/"+HAMQTT.entity_type[str(topic).split("/")[-1]][2]
        except:
            logger.info("No command topic avaiable, skipping")
#set device specific elements here:
        if HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="sensor":
            tempObj['unit_of_meas']=""
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="energy":
                tempObj['unit_of_meas']="kWh"
                tempObj['device_class']="Energy"
                if topic.split("/")[-2]=="Total":
                    tempObj['state_class']="total"
                else:
                    tempObj['state_class']="total_increasing"
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="power":
                tempObj['unit_of_meas']="W"
                tempObj['device_class']="Power"
                tempObj['state_class']="measurement"
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="temperature":
                tempObj['unit_of_meas']="C"
                tempObj['device_class']="Temperature"
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="voltage":
                tempObj['unit_of_meas']="V"
                tempObj['device_class']="Voltage"
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="battery":
                tempObj['unit_of_meas']="%"
                tempObj['device_class']="Battery"
            if HAMQTT.entity_type[str(topic).split("/")[-1]][1]=="timestamp":
                #if "slot" in topic:
                #    tempObj['value_template']= "{{now().replace(hour=int(value[:2]), minute=int(value[3:5]), second=0, microsecond=0).timestamp() }}"
                del(tempObj['unit_of_meas'])
                tempObj['device_class']="timestamp"
        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="switch":
            tempObj['payload_on']="enable"
            tempObj['payload_off']="disable"
    #    elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="binary_sensor":
    #        client.publish("homeassistant/binary_sensor/GivEnergy/"+str(topic).split("/")[-1]+"/config",HAMQTT.create_binary_sensor_payload(topic,SN),retain=True)
        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="select":
            options=["Eco","Timed Demand","Timed Export","Unknown", "Eco (Paused)"]
            tempObj['options']=options
        elif HAMQTT.entity_type[str(topic).split("/")[-1]][0]=="number":
            tempObj['unit_of_meas']="%"

        ## Convert this object to json string
        jsonOut=json.dumps(tempObj)
        return(jsonOut)
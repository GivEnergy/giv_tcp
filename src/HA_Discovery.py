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
            client.publish("GivEnergy/status","online", retain=True)
        ### For each topic create a discovery message
            for p_load in array:
                if p_load != "raw":
                    payload=array[p_load]
                    logger.info('Publishing: '+rootTopic+p_load)
                    output=GivMQTT.iterate_dict(payload,rootTopic+p_load)   #create LUT for MQTT publishing
                    for topic in output:
                        client.publish("homeassistant/sensor/GivEnergy/"+str(topic).split("/")[-1]+"/config",HAMQTT.create_payload(topic,SN),retain=True)
        client.loop_stop()                      			#Stop loop
        client.disconnect()
        return client

    def create_payload(topic,SN):      #Create LUT of topics and datapoints
        tempObj={}
        tempObj["name"]="GivTCP "+str(topic).split("/")[-1].replace("_"," ") #Just final bit past the last "/"
        tempObj['stat_t']=str(topic).replace(" ","_")
        tempObj['avty_t'] = "GivEnergy/status"
        tempObj["pl_avail"]= "online"
        tempObj["pl_not_avail"]= "offline"
        #tempObj['json_attr_t']=str(topic)
        tempObj['unit_of_meas']=""
        if "Energy" in str(topic):
            tempObj['unit_of_meas']="kWh"
            tempObj['device_class']="Energy"
        if "Power" in str(topic):
            tempObj['unit_of_meas']="W"
            tempObj['device_class']="Power"
        if "Temperature" in str(topic):
            tempObj['unit_of_meas']="C"
            tempObj['device_class']="Temperature"
        if "Voltage" in str(topic):
            tempObj['unit_of_meas']="V"
            tempObj['device_class']="Voltage"
        if "SOC" in str(topic):
            tempObj['unit_of_meas']="%"
            tempObj['device_class']="Battery"
        if "time" in str(topic).lower():
            tempObj['device_class']="timestamp"
            del(tempObj['unit_of_meas'])
        if "rate" in str(topic):
            tempObj['unit_of_meas']="%"
        if "Time_Since_Last_Update" in str(topic):
            tempObj['unit_of_meas']="s"
            del(tempObj['device_class'])
        tempObj['uniq_id']=SN+"_"+str(topic).split("/")[-1].replace(" ","_")
        tempObj['device']={}
        tempObj['device']['identifiers']=tempObj['uniq_id']
        tempObj['device']['name']="GivTCP_"+str(topic).split("/")[-1]
        tempObj['device']['manufacturer']="GivEnergy"
        ## Convert this object to json string
        jsonOut=json.dumps(tempObj)
        return(jsonOut)
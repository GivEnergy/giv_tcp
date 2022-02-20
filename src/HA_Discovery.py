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

class discovery_message():
        name: str
        stat_t: str
        avty_t: str
        pl_avail: str
        pl_not_avail: str
        json_attr_t: str
        unit_of_meas: str
        ic: str
        uniq_id: str
        device_class: str
        ids: str
        mf: str

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
        ### For each topic create a discovery message
            for p_load in array:
                payload=array[p_load]
                logger.info('Publishing: '+rootTopic+p_load)
                output=GivMQTT.iterate_dict(payload,rootTopic+p_load)   #create LUT for MQTT publishing
                for topic in output:
                    client.publish("homeassistant/sensor/GivEnergy/"+str(topic).split("/")[-1]+"/config",HAMQTT.create_payload(topic))
        client.loop_stop()                      			#Stop loop
        client.disconnect()
        return client

    def create_payload(topic):      #Create LUT of topics and datapoints
        tempObj={}
        tempObj["xxxx"]=str(topic).split("/")[-1] #Just final bit past the last "/"
        tempObj['avty_t'] = "Givenergy/status"
        tempObj['json_attr_t']=str(topic)
        tempObj['stat_t']=str(topic)
        tempObj['uniq_id']=tempObj["xxxx"]
        if "Energy" in str(topic):
            tempObj['unit_of_meas']="kWh"
            tempObj['device_class']="Energy"
        elif "Power" in str(topic):
            tempObj['unit_of_meas']="W"
            tempObj['device_class']="Power"
        tempObj['dev']={}
        tempObj['dev']['ids']=str(tempObj["xxxx"]).replace(" ","_")
        tempObj['dev']['mf']="GivEnergy"
        ## Convert this object to json string
        jsonOut=json.dumps(tempObj)
        jsonOut=str(jsonOut).replace("xxxx","name")
        return(jsonOut)
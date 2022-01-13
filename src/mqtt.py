# version 1.0
import paho.mqtt.client as mqtt
import time
import datetime

import logging  
from settings import GiV_Settings
from givenergy_modbus.model.inverter import Model

class GivMQTT():

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

    def on_connect(client, userdata, flags, rc):
        if rc==0:
            client.connected_flag=True #set flag
            logging.info("connected OK Returned code="+str(rc))
            #client.subscribe(topic)
        else:
            logging.info("Bad connection Returned code= "+str(rc))
    
    def multi_MQTT_publish(rootTopic,array):   #Recieve multiple payloads with Topics and publish in a single MQTT connection
        mqtt.Client.connected_flag=False        			#create flag in class
        client=mqtt.Client("GivEnergy_GivTCP")

        if GivMQTT.MQTTCredentials:
            client.username_pw_set(GivMQTT.MQTT_Username,GivMQTT.MQTT_Password)
        client.on_connect=GivMQTT.on_connect     			#bind call back function
        client.loop_start()
        logging.info ("Connecting to broker: "+ GivMQTT.MQTT_Address)
        client.connect(GivMQTT.MQTT_Address,port=GivMQTT.MQTT_Port)
        while not client.connected_flag:        			#wait in loop
            logging.info ("In wait loop")
            time.sleep(0.2)
        for p_load in array:
            payload=array[p_load]
            logging.info('Publishing: '+rootTopic+p_load)
            for reg in payload:
                client.publish(rootTopic+p_load+'/'+reg,payload[reg])
        client.loop_stop()                      			#Stop loop
        client.disconnect()
        return client
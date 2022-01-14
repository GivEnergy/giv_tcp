# version 1.0
import paho.mqtt.client as mqtt
import time
from datetime import datetime
from GivTCP import GivTCP
from settings import GiV_Settings

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
            GivTCP.debug("connected OK Returned code="+str(rc))
            #client.subscribe(topic)
        else:
            GivTCP.debug("Bad connection Returned code= "+str(rc))
    
    def multi_MQTT_publish(array):   #Recieve multiple payloads with Topics and publish in a single MQTT connection
        mqtt.Client.connected_flag=False        			#create flag in class
        client=mqtt.Client("GivEnergy_"+GivTCP.SN)

        if GiV_Settings.MQTT_Topic=="":
            GivTCP.debug ("No user defined MQTT Topic")
            rootTopic='GivEnergy/'+GivTCP.SN+'/'
        else:
            GivTCP.debug ("User defined MQTT Topic found: "+ GiV_Settings.MQTT_Topic)
            rootTopic=GiV_Settings.MQTT_Topic+'/'

        if GivMQTT.MQTTCredentials:
            client.username_pw_set(GivMQTT.MQTT_Username,GivMQTT.MQTT_Password)
        client.on_connect=GivMQTT.on_connect     			#bind call back function
        client.loop_start()
        GivTCP.debug ("Connecting to broker: "+ GivMQTT.MQTT_Address)
        client.connect(GivMQTT.MQTT_Address,port=GivMQTT.MQTT_Port)
        while not client.connected_flag:        			#wait in loop
            GivTCP.debug ("In wait loop")
            time.sleep(0.2)
        for p_load in array:
            payload=array[p_load]
            for reg in payload:
                GivTCP.debug('Publishing: '+rootTopic+p_load+'/'+str(reg)+" "+str(payload[reg]))
                client.publish(rootTopic+p_load+'/'+reg,payload[reg])
        client.loop_stop()                      			#Stop loop
        client.disconnect()
        return client


    def publish_to_MQTT(topic,payload):
        mqtt.Client.connected_flag=False        			#create flag in class
        client=mqtt.Client("GivEnergy_"+GivTCP.SN)

        if GiV_Settings.MQTT_Topic=="":
            GivTCP.debug ("No user defined MQTT Topic")
            rootTopic='GivEnergy/'+GivTCP.SN+'/'
        else:
            GivTCP.debug ("User defined MQTT Topic found"+ GiV_Settings.MQTT_Topic)
            rootTopic=GiV_Settings.MQTT_Topic+'/'

        if GivMQTT.MQTTCredentials:
            client.username_pw_set(GivMQTT.MQTT_Username,GivMQTT.MQTT_Password)
        client.on_connect=GivMQTT.on_connect     			#bind call back function
        client.loop_start()
        GivTCP.debug ("Connecting to broker "+ GivMQTT.MQTT_Address)
        client.connect(GivMQTT.MQTT_Address, port=GivMQTT.MQTT_Address)
        while not client.connected_flag:        			#wait in loop
            GivTCP.debug ("In wait loop")
            time.sleep(0.2)
        for reg in payload:
            GivTCP.debug('Publishing: '+rootTopic+topic+'/'+str(reg)+" "+str(payload[reg]))
            client.publish(rootTopic+topic+'/'+reg,payload[reg])
        client.loop_stop()                      			#Stop loop
        client.disconnect()
        return client
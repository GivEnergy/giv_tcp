# version 2022.01.21
import paho.mqtt.client as mqtt
import time
from GivLUT import GivLUT
from settings import GiV_Settings
import sys
#from HA_Discovery import HAMQTT
from givenergy_modbus.model.inverter import Model

logger = GivLUT.logger

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
            logger.debug("connected OK Returned code="+str(rc))
            #client.subscribe(topic)
        else:
            logger.error("Bad connection Returned code= "+str(rc))

    def single_MQTT_publish(Topic,value):   #Recieve multiple payloads with Topics and publish in a single MQTT connection
        mqtt.Client.connected_flag=False        			#create flag in class
        client=mqtt.Client("GivEnergy_GivTCP_"+str(GiV_Settings.givtcp_instance))

        if GivMQTT.MQTTCredentials:
            client.username_pw_set(GivMQTT.MQTT_Username,GivMQTT.MQTT_Password)
        try:
            client.on_connect=GivMQTT.on_connect     			#bind call back function
            client.loop_start()
            logger.debug ("Connecting to broker: "+ GivMQTT.MQTT_Address)
            client.connect(GivMQTT.MQTT_Address,port=GivMQTT.MQTT_Port)
            while not client.connected_flag:        			#wait in loop
                logger.debug ("In wait loop")
                time.sleep(0.2)
            client.publish(Topic,value)
        except:
            e = sys.exc_info()
            logger.error("Error connecting to MQTT Broker: " + str(e))
        client.loop_stop()                      			    #Stop loop
        client.disconnect()
        return client

    def multi_MQTT_publish(rootTopic,array):                    #Recieve multiple payloads with Topics and publish in a single MQTT connection
        mqtt.Client.connected_flag=False        			    #create flag in class
        client=mqtt.Client("GivEnergy_GivTCP_"+str(GiV_Settings.givtcp_instance))
        
        ##Check if first run then publish auto discovery message
        
        if GivMQTT.MQTTCredentials:
            client.username_pw_set(GivMQTT.MQTT_Username,GivMQTT.MQTT_Password)
        try:
            client.on_connect=GivMQTT.on_connect     			#bind call back function
            client.loop_start()
            logger.debug ("Connecting to broker: "+ GivMQTT.MQTT_Address)
            client.connect(GivMQTT.MQTT_Address,port=GivMQTT.MQTT_Port)
            while not client.connected_flag:        			#wait in loop
                logger.debug ("In wait loop")
                time.sleep(0.2)
            for p_load in array:
                payload=array[p_load]
                logger.debug('Publishing: '+rootTopic+p_load)
                output=GivMQTT.iterate_dict(payload,rootTopic+p_load)   #create LUT for MQTT publishing
                for value in output:
                    if isinstance(output[value],(int, str, float, bytearray)):      #Only publish typesafe data
                        client.publish(value,output[value])
                    else:
                        logger.error("MQTT error trying to send a "+ str(type(output[value]))+" to the MQTT broker for: "+str(value))
        except:
            e = sys.exc_info()
            logger.error("Error connecting to MQTT Broker: " + str(e))
        client.loop_stop()                      			    #Stop loop
        client.disconnect()
        return client

    def iterate_dict(array,topic):      #Create LUT of topics and datapoints
        MQTT_LUT={}
        if isinstance(array, dict):
            # Create a publish safe version of the output
            for p_load in array:
                output=array[p_load]
                if isinstance(output, dict):
                    MQTT_LUT.update(GivMQTT.iterate_dict(output,topic+"/"+p_load))
                    logger.debug('Prepping '+p_load+" for publishing")
                else:
                    MQTT_LUT[topic+"/"+p_load]=output
        else:
            MQTT_LUT[topic]=array
        return(MQTT_LUT)
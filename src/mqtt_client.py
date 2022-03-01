from logging import Logger
import paho.mqtt.client as mqtt
import time
import sys
import importlib
import datetime
import logging
import settings
from settings import GiV_Settings
import write as wr

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

def on_message(client, userdata, message):
    logger.info("MQTT Message Recieved: "+str(message.topic)+"= "+str(message.payload.decode("utf-8")))
    writecommand={}
    command=str(message.topic).split("/")[-1]
    if command=="setDischargeRate":
        writecommand['dischargeRate']=str(message.payload.decode("utf-8"))
        wr.setDischargeRate(writecommand)
    elif command=="setChargeRate":
        writecommand['chargeRate']=str(message.payload.decode("utf-8"))
        wr.setChargeRate(writecommand)
    elif command=="disableChargeTarget":
        wr.disableChargeTarget()
    elif command=="enableChargeTarget":
        wr.enableChargeTarget()
    elif command=="pauseChargeSchedule":
        wr.pauseChargeSchedule()
    elif command=="resumeChargeSchedule":
        wr.resumeChargeSchedule()
    elif command=="pauseDischargeSchedule":
        wr.pauseDischargeSchedule()
    elif command=="resumeDischargeSchedule":
        wr.resumeDischargeSchedule()
    elif command=="pauseBatteryCharge":
        wr.pauseBatteryCharge()
    elif command=="resumeBatteryCharge":
        wr.resumeBatteryCharge()
    elif command=="pauseBatteryDischarge":
        wr.pauseBatteryDischarge()
    elif command=="resumeBatteryDischarge":
        wr.resumeBatteryDischarge()
    elif command=="setChargeTarget":
        writecommand['chargeToPercent']=str(message.payload.decode("utf-8"))
        wr.setChargeTarget(writecommand)
    elif command=="setBatteryReserve":
        writecommand['dischargeToPercent']=str(message.payload.decode("utf-8"))
        wr.setBatteryReserve(writecommand)
    elif command=="setBatteryMode":
        writecommand['mode']=str(message.payload.decode("utf-8"))
        wr.setBatteryMode(writecommand)
    elif command=="setDateTime":
        writecommand['dateTime']=str(message.payload.decode("utf-8"))
        wr.setDateTime(writecommand)
## How to deal with ChargeSlots... require json payload?

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        logger.info("connected OK Returned code="+str(rc))
        #Subscribe to the control topic for this invertor - relies on serial_number being present
        client.subscribe(MQTT_Topic+"/control/"+GiV_Settings.serial_number+"/#")
        logger.info("Subscribing to "+MQTT_Topic+"/control/"+GiV_Settings.serial_number+"/#")
    else:
        logger.error("Bad connection Returned code= "+str(rc))

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
if GiV_Settings.MQTT_Topic=='':
    MQTT_Topic='GivEnergy'
else:
    MQTT_Topic=GiV_Settings.MQTT_Topic

#loop till serial number has been found
while not hasattr(GiV_Settings,'serial_number'):
    logger.error("No serial_number available waiting for first read run to occur")
    time.sleep(2)
    #del sys.modules['settings.GiV_Settings'] 
    importlib.reload(settings)
    from settings import GiV_Settings
logger.info("Serial Number retrieved: "+GiV_Settings.serial_number)


client=mqtt.Client("GivEnergy_GivTCP_Control")
mqtt.Client.connected_flag=False        			#create flag in class
if MQTTCredentials:
    client.username_pw_set(MQTT_Username,MQTT_Password)
client.on_connect=on_connect     			        #bind call back function
client.on_message=on_message                        #bind call back function
#client.loop_start()

logger.info ("Connecting to broker(sub): "+ MQTT_Address)
client.connect(MQTT_Address,port=MQTT_Port)
client.loop_forever()

if __name__ == '__main__':
    globals()[sys.argv[1]]()
from logging import Logger
import paho.mqtt.client as mqtt
import time
import sys
import importlib
import logging
from logging.handlers import TimedRotatingFileHandler
import settings
from settings import GiV_Settings
import write as wr
sys.path.append(GiV_Settings.default_path)

if GiV_Settings.Log_Level.lower()=="debug":
    if GiV_Settings.Debug_File_Location=="":
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler()])
    else:
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(),TimedRotatingFileHandler(GiV_Settings.Debug_File_Location, when='D', interval=1, backupCount=7)])
elif GiV_Settings.Log_Level.lower()=="info":
    if GiV_Settings.Debug_File_Location=="":
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler()])
    else:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(),TimedRotatingFileHandler(GiV_Settings.Debug_File_Location, when='D', interval=1, backupCount=7)])
else:
    if GiV_Settings.Debug_File_Location=="":
        logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler()])
    else:
        logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(name)s [%(levelname)s] %(message)s", handlers=[logging.StreamHandler(),TimedRotatingFileHandler(GiV_Settings.Debug_File_Location, when='D', interval=1, backupCount=7)])


logger = logging.getLogger("GivTCP_MQTT_client")

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
    time.sleep(5)
    #del sys.modules['settings.GiV_Settings']
    importlib.reload(settings)
    from settings import GiV_Settings
    count=+1
    if count==20:
        logger.error("No serial_number found in MQTT queue. MQTT Control not available.")
        break
    
logger.info("Serial Number retrieved: "+GiV_Settings.serial_number)

def on_message(client, userdata, message):
    logger.info("MQTT Message Recieved: "+str(message.topic)+"= "+str(message.payload.decode("utf-8")))
    writecommand={}
    command=str(message.topic).split("/")[-1]
    if command=="setDischargeRate":
        writecommand['dischargeRate']=str(message.payload.decode("utf-8"))
        result=wr.setDischargeRate(writecommand)
    elif command=="setChargeRate":
        writecommand['chargeRate']=str(message.payload.decode("utf-8"))
        result=wr.setChargeRate(writecommand)
    elif command=="enableChargeTarget":
        writecommand['state']=str(message.payload.decode("utf-8"))
        result=wr.enableChargeTarget(writecommand)
    elif command=="enableChargeSchedule":
        writecommand['state']=str(message.payload.decode("utf-8"))
        result=wr.enableChargeSchedule(writecommand)
    elif command=="enableDishargeSchedule":
        writecommand['state']=str(message.payload.decode("utf-8"))
        result=wr.enableDischargeSchedule(writecommand)
    elif command=="enableDischarge":
        writecommand['state']=str(message.payload.decode("utf-8"))
        result=wr.enableDischarge(writecommand)
    elif command=="setChargeTarget":
        writecommand['chargeToPercent']=str(message.payload.decode("utf-8"))
        result=wr.setChargeTarget(writecommand)
    elif command=="setBatteryReserve":
        writecommand['dischargeToPercent']=str(message.payload.decode("utf-8"))
        result=wr.setBatteryReserve(writecommand)
    elif command=="setBatteryMode":
        writecommand['mode']=str(message.payload.decode("utf-8"))
        result=wr.setBatteryMode(writecommand)
    elif command=="setDateTime":
        writecommand['dateTime']=str(message.payload.decode("utf-8"))
        result=wr.setDateTime(writecommand)
    elif command=="setShallowCharge":
        writecommand['val']=str(message.payload.decode("utf-8"))
        result=wr.setShallowCharge(writecommand)
    elif command=="setChargeSlot1":
        result=wr.setChargeSlot1(message.payload)
    elif command=="setChargeSlot2":
        result=wr.setChargeSlot2(message.payload)
    elif command=="setDischargeSlot1":
        result=wr.setDischargeSlot1(message.payload)
    elif command=="setDischargeSlot1":
        result=wr.setDischargeSlot1(message.payload)
    #Do something with the result??

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        logger.info("connected OK Returned code="+str(rc))
        #Subscribe to the control topic for this invertor - relies on serial_number being present
        client.subscribe(MQTT_Topic+"/control/"+GiV_Settings.serial_number+"/#")
        logger.info("Subscribing to "+MQTT_Topic+"/control/"+GiV_Settings.serial_number+"/#")
    else:
        logger.error("Bad connection Returned code= "+str(rc))


client=mqtt.Client("GivEnergy_GivTCP_"+str(GiV_Settings.givtcp_instance)+"_Control")
mqtt.Client.connected_flag=False        			#create flag in class
if MQTTCredentials:
    client.username_pw_set(MQTT_Username,MQTT_Password)
client.on_connect=on_connect     			        #bind call back function
client.on_message=on_message                        #bind call back function
#client.loop_start()

logger.info ("Connecting to broker(sub): "+ MQTT_Address)
client.connect(MQTT_Address,port=MQTT_Port)
client.loop_forever()
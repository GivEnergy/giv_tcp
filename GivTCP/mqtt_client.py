import paho.mqtt.client as mqtt
import time, sys, importlib, time
from os.path import exists
from settings import GiV_Settings
import write as wr
import pickle, settings
from GivLUT import GivLUT
from pickletools import read_uint1

sys.path.append(GiV_Settings.default_path)

logger = GivLUT.logger

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

logger.critical("Connecting to MQTT broker for control- "+str(GiV_Settings.MQTT_Address))
#loop till serial number has been found
count=0          # 09-July-2023  set start point
while not hasattr(GiV_Settings,'serial_number'):
    time.sleep(5)
    #del sys.modules['settings.GiV_Settings']
    importlib.reload(settings)
    from settings import GiV_Settings
    count=count + 1      # 09-July-2023  previous +1 only simply reset value to 1 so loop was infinite
    if count==20:
        logger.error("No serial_number found in MQTT queue. MQTT Control not available.")
        break
    
logger.debug("Serial Number retrieved: "+GiV_Settings.serial_number)

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def on_message(client, userdata, message):
    payload={}
    logger.debug("MQTT Message Recieved: "+str(message.topic)+"= "+str(message.payload.decode("utf-8")))
    writecommand={}         # 24-July-2023   wrap the processing of data from MQTT subscribe topics in exception handler to trap error from bad data
    try:                    #                Not trapped means exception goes up to the MQTT software and that causes subscription event to permanently fail. 
        command=str(message.topic).split("/")[-1]
        if command=="setDischargeRate":
            writecommand['dischargeRate']=str(message.payload.decode("utf-8"))
            wr.setDischargeRate(writecommand)
        elif command=="setChargeRate":
            writecommand['chargeRate']=str(message.payload.decode("utf-8"))
            wr.setChargeRate(writecommand)
        elif command=="rebootInvertor":
            wr.rebootinvertor()
        elif command=="rebootAddon":
            wr.rebootAddon()
        elif command=="setActivePowerRate":
            writecommand['activePowerRate']=str(message.payload.decode("utf-8"))
            wr.setActivePowerRate(writecommand)
        elif command=="enableChargeTarget":
            writecommand['state']=str(message.payload.decode("utf-8"))
            wr.enableChargeTarget(writecommand)
        elif command=="enableChargeSchedule":
            writecommand['state']=str(message.payload.decode("utf-8"))
            wr.enableChargeSchedule(writecommand)
        elif command=="enableDishargeSchedule":
            writecommand['state']=str(message.payload.decode("utf-8"))
            wr.enableDischargeSchedule(writecommand)
        elif command=="setBatteryPowerMode":
            writecommand['state']=str(message.payload.decode("utf-8"))
            wr.setBatteryPowerMode(writecommand)
        elif command=="enableDischarge":
            writecommand['state']=str(message.payload.decode("utf-8"))
            wr.enableDischarge(writecommand)
        elif command=="setChargeTarget":
            writecommand['chargeToPercent']=str(message.payload.decode("utf-8"))
            wr.setChargeTarget(writecommand)
        elif command=="setBatteryReserve":
            writecommand['reservePercent']=str(message.payload.decode("utf-8"))
            wr.setBatteryReserve(writecommand)
        elif command=="setBatteryCutoff":
            writecommand['dischargeToPercent']=str(message.payload.decode("utf-8"))
            wr.setBatteryCutoff(writecommand)
        elif command=="setBatteryMode":
            writecommand['mode']=str(message.payload.decode("utf-8"))
            wr.setBatteryMode(writecommand)
        elif command=="setDateTime":
            writecommand['dateTime']=str(message.payload.decode("utf-8"))
            wr.setDateTime(writecommand)
        elif command=="setShallowCharge":
            writecommand['val']=str(message.payload.decode("utf-8"))
            wr.setShallowCharge(writecommand)
        elif command=="setChargeStart1":
            #if exists(GivLUT.regcache):
                #with open(GivLUT.regcache, 'rb') as inp:
                #    regCacheStack= pickle.load(inp)
                #multi_output=regCacheStack[4]
                #finish=multi_output['Timeslots']['Charge_end_time_slot_1']
            payload['start']=message.payload.decode("utf-8")[:5]
                #payload['finish']=finish[:5]
            wr.setChargeSlotStart1(payload)
        elif command=="setChargeEnd1":
            #if exists(GivLUT.regcache):
            #    with open(GivLUT.regcache, 'rb') as inp:
            #        regCacheStack= pickle.load(inp)
            #    multi_output=regCacheStack[4]
            #    start=multi_output['Timeslots']['Charge_start_time_slot_1']
            payload['finish']=message.payload.decode("utf-8")[:5]
            #    payload['start']=start[:5]
            wr.setChargeSlotEnd1(payload)
        elif command=="setDischargeStart1":
            #if exists(GivLUT.regcache):
            #    with open(GivLUT.regcache, 'rb') as inp:
            #        regCacheStack= pickle.load(inp)
            #    multi_output=regCacheStack[4]
            #    finish=multi_output['Timeslots']['Discharge_end_time_slot_1']
            payload['start']=message.payload.decode("utf-8")[:5]
            #    payload['finish']=finish[:5]
            wr.setDischargeSlotStart1(payload)
        elif command=="setDischargeEnd1":
            #if exists(GivLUT.regcache):
            #    with open(GivLUT.regcache, 'rb') as inp:
            #        regCacheStack= pickle.load(inp)
            #    multi_output=regCacheStack[4]
            #    start=multi_output['Timeslots']['Discharge_start_time_slot_1']
            payload['finish']=message.payload.decode("utf-8")[:5]
            #    payload['start']=start[:5]
            wr.setDischargeSlotEnd1(payload)
        elif command=="setDischargeStart2":
            #if exists(GivLUT.regcache):
            #    with open(GivLUT.regcache, 'rb') as inp:
            #        regCacheStack= pickle.load(inp)
            #    multi_output=regCacheStack[4]
            #    finish=multi_output['Timeslots']['Discharge_end_time_slot_2']
            payload['start']=message.payload.decode("utf-8")[:5]
            #    payload['finish']=finish[:5]
            wr.setDischargeSlotStart2(payload)
        elif command=="setDischargeEnd2":
            #if exists(GivLUT.regcache):
            #    with open(GivLUT.regcache, 'rb') as inp:
            #        regCacheStack= pickle.load(inp)
            #    multi_output=regCacheStack[4]
            #    start=multi_output['Timeslots']['Discharge_start_time_slot_2']
            payload['finish']=message.payload.decode("utf-8")[:5]
            #    payload['start']=start[:5]
            wr.setDischargeSlotEnd2(payload)
        elif command=="tempPauseDischarge":
            if isfloat(message.payload.decode("utf-8")):
                writecommand=float(message.payload.decode("utf-8"))
                wr.tempPauseDischarge(writecommand)
            elif message.payload.decode("utf-8") == "Cancel":
                # Get the Job ID from the touchfile
                if exists(".tpdRunning"):
                    jobid= str(open(".tpdRunning","r").readline())
                    logger.debug("Retrieved jobID to cancel Temp Pause Discharge: "+ str(jobid))
                    result=wr.cancelJob(jobid)
                else:
                    logger.error("Temp Pause Charge is not currently running")
        elif command=="tempPauseCharge":
            if isfloat(message.payload.decode("utf-8")):
                writecommand=float(message.payload.decode("utf-8"))
                wr.tempPauseCharge(writecommand)
            elif message.payload.decode("utf-8") == "Cancel":
                # Get the Job ID from the touchfile
                if exists(".tpcRunning"):
                    jobid= str(open(".tpcRunning","r").readline())
                    logger.debug("Retrieved jobID to cancel Temp Pause Charge: "+ str(jobid))
                    result=wr.cancelJob(jobid)
                else:
                    logger.error("Temp Pause Charge is not currently running")
        elif command=="forceCharge":
            if isfloat(message.payload.decode("utf-8")):
                writecommand=float(message.payload.decode("utf-8"))
                wr.forceCharge(writecommand)
            elif message.payload.decode("utf-8") == "Cancel":
                # Get the Job ID from the touchfile
                if exists(".FCRunning"):
                    jobid= str(open(".FCRunning","r").readline())
                    logger.debug("Retrieved jobID to cancel Force Charge: "+ str(jobid))
                    result=wr.cancelJob(jobid)
                else:
                    logger.error("Force Charge is not currently running")
        elif command=="forceExport":
            if isfloat(message.payload.decode("utf-8")):
                writecommand=float(message.payload.decode("utf-8"))
                wr.forceExport(writecommand)
            elif message.payload.decode("utf-8") == "Cancel":
                # Get the Job ID from the touchfile
                if exists(".FERunning"):
                    jobid= str(open(".FERunning","r").readline())
                    logger.debug("Retrieved jobID to cancel Force Export: "+ str(jobid))
                    result=wr.cancelJob(jobid)
                else:
                    logger.error("Force Export is not currently running")
        elif command=="switchRate":
            writecommand=message.payload.decode("utf-8")
            wr.switchRate(writecommand)
    except:
        e = sys.exc_info()
        logger.error("MQTT.OnMessage Exception: "+str(e))
        return
    
    #Do something with the result??

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        logger.debug("connected OK Returned code="+str(rc))
        #Subscribe to the control topic for this invertor - relies on serial_number being present
        client.subscribe(MQTT_Topic+"/control/"+GiV_Settings.serial_number+"/#")
        logger.debug("Subscribing to "+MQTT_Topic+"/control/"+GiV_Settings.serial_number+"/#")
    else:
        logger.error("Bad connection Returned code= "+str(rc))


client=mqtt.Client("GivEnergy_GivTCP_"+str(GiV_Settings.givtcp_instance)+"_Control")
mqtt.Client.connected_flag=False        			#create flag in class
if MQTTCredentials:
    client.username_pw_set(MQTT_Username,MQTT_Password)
client.on_connect=on_connect     			        #bind call back function
client.on_message=on_message                        #bind call back function
#client.loop_start()

logger.debug ("Connecting to broker(sub): "+ MQTT_Address)
client.connect(MQTT_Address,port=MQTT_Port)
client.loop_forever()

# -*- coding: utf-8 -*-
# version 2022.01.31
import sys
import json
import logging
import datetime
from datetime import datetime, timedelta
from settings import GiV_Settings
import time
from os.path import exists
import pickle,os
from GivLUT import GivLUT, GivQueue
from givenergy_modbus.client import GivEnergyClient

#client= GivEnergyClient(host=GiV_Settings.invertorIP)

logging.getLogger("givenergy_modbus").setLevel(logging.CRITICAL)
client=GivEnergyClient(host=GiV_Settings.invertorIP)

logger = GivLUT.logger


def enableChargeTarget(payload):
    temp={}
    try:
        if payload['state']=="enable":
            logger.info("Enabling Charge Target")
            client.enable_charge_target()
        elif payload['state']=="disable":
            logger.info("Disabling Charge Target")
            client.disable_charge_target()
        temp['result']="Setting Charge Target was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Target failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def enableChargeSchedule(payload):
    temp={}
    try:
        if payload['state']=="enable":
            logger.info("Enabling Charge Schedule")
            client.enable_charge()
        elif payload['state']=="disable":
            logger.info("Disabling Charge Schedule")
            client.disable_charge()
        temp['result']="Setting Charge Enable was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def enableDischargeSchedule(payload):
    temp={}
    try:
        if payload['state']=="enable":
            logger.info("Enabling Disharge Schedule")
            client.enable_discharge()
        elif payload['state']=="disable":
            logger.info("Disabling Discharge Schedule")
            client.disable_discharge()
        temp['result']="Setting Charge Enable was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setShallowCharge(payload):
    temp={}
    try:
        logger.info("Setting Shallow Charge to: "+ str(payload['val']))
        client.set_shallow_charge(int(payload['val']))
        temp['result']="Setting Shallow Charge was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def enableDischarge(payload):
    temp={}
    saved_battery_reserve = getSavedBatteryReservePercentage()
    try:
        if payload['state']=="enable":
            logger.info("Enabling Discharge")
            client.set_shallow_charge(saved_battery_reserve)
        elif payload['state']=="disable":
            logger.info("Disabling Discharge")
            client.set_shallow_charge(100)
        temp['result']="Setting Discharge Enable was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeTarget(payload):
    logger.critical("Setting target SOC to: "+str(payload['chargeToPercent']))
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    target=int(payload['chargeToPercent'])
    try:
        logger.info("Setting Charge Target to: "+str(target))
        client.enable_charge_target(target)
        temp['result']="Setting Charge Target was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Target failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setBatteryReserve(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    #target=int(payload['dischargeToPercent'])
    target=int(payload['reservePercent'])
    #Only allow minimum of 4%
    if target<4: target=4
    logger.info ("Setting battery reserve target to: " + str(target))
    try:
        #client.set_battery_power_reserve(target)
        logger.info("Setting Battery Reserve to: "+str(target))
        client.set_shallow_charge(target)
        temp['result']="Setting Battery Reserve was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Battery Reserve failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setBatteryCutoff(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    target=int(payload['dischargeToPercent'])
    #Only allow minimum of 4%
    if target<4: target=4
    logger.info ("Setting battery cutoff target to: " + str(target))
    try:
        logger.info("Setting Battery Cutoff to: "+str(target))
        client.set_battery_power_reserve(target)
        temp['result']="Setting Battery Cutoff was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Battery Cutoff failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)


def setChargeRate(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    #Only allow max of 100% and if not 100% the scale to a third to get register value
    if int(payload['chargeRate'])>=100:
        target=50
    else:
        target=int(int(payload['chargeRate'])/3)
    logger.info ("Setting battery charge rate to: " + str(payload['chargeRate']))
    try:
        client.set_battery_charge_limit(target)
        temp['result']="Setting Charge Rate was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Rate failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)


def setDischargeRate(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    #Only allow max of 100% and if not 100% the scale to a third to get register value
    if int(payload['dischargeRate'])>=100:
        target=50
    else:
        target=int(int(payload['dischargeRate'])/3)
    logger.info ("Setting battery discharge rate to: " + str(payload['dischargeRate']))
    try:
        logger.info("Setting Discharge Rate to: "+str(payload['dischargeRate']))
        client.set_battery_discharge_limit(target)
        temp['result']="Setting Discharge Rate was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Rate failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)


def setChargeSlot1(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    if 'chargeToPercent' in payload.keys():
        targetresult=setChargeTarget(payload)
    try:
        logger.info("Setting Charge Slot 1 to: "+str(payload['start'])+" - "+str(payload['finish']))
        client.set_charge_slot_1((datetime.strptime(payload['start'],"%H:%M"),datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Charge Slot 1 was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot 1 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeSlot2(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    if 'chargeToPercent' in payload.keys():
        targetresult=setChargeTarget(payload)
    try:
        logger.info("Setting Charge Slot 2 to: "+str(payload['start'])+" - "+str(payload['finish']))
        client.set_charge_slot_2((datetime.strptime(payload['start'],"%H:%M"),datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Charge Slot 2 was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDischargeSlot1(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    if 'dischargeToPercent' in payload.keys():
        targetresult=setBatteryReserve(payload)
        time.sleep(1)
    try:
        strt=datetime.strptime(payload['start'],"%H:%M")
        fnsh=datetime.strptime(payload['finish'],"%H:%M")
        logger.info("Setting Discharge Slot 1 to: "+str(payload['start'])+" - "+str(payload['finish']))
        client.set_discharge_slot_1((strt,fnsh))
        temp['result']="Setting Discharge Slot 1 was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 1 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDischargeSlot2(payload):
    temp={}
    targetresult="Success"
    if type(payload) is not dict: payload=json.loads(payload)
    if 'dischargeToPercent' in payload.keys():
        targetresult=setBatteryReserve(payload)
        time.sleep(1)
    try:
        logger.info("Setting Discharge Slot 2 to: "+str(payload['start'])+" - "+str(payload['finish']))
        client.set_discharge_slot_2((datetime.strptime(payload['start'],"%H:%M"),datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Discharge Slot 2 was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def FEResume(revert):
    payload={}
    logger.info("Reverting Force Export settings:")
    payload['dischargeRate']=revert["dischargeRate"]
    result=setDischargeRate(payload)
    logger.debug("DischargeRate result is:" + str(result))
    time.sleep(1)
    payload={}
    payload['start']=revert["start_time"]
    payload['finish']=revert["end_time"]
    payload['dischargeToPercent']=revert["dischargeToPercent"]
    result=setDischargeSlot1(payload)
    logger.debug("Timeslot result is:" + str(result))
    time.sleep(1)
    payload={}
    payload["mode"]=revert["mode"]
    logger.debug("Reverting Mode")
    result=setBatteryMode(payload)
    logger.debug("Mode result is:" + str(result))
    os.remove(".FERunning")

def forceExport(exportTime):
    temp={}
    logger.info("Forcing Export for "+str(exportTime)+" minutes")
    try:
        exportTime=int(exportTime)
        result={}
        revert={}
        if exists(GivLUT.regcache):      # if there is a cache then grab it
            with open(GivLUT.regcache, 'rb') as inp:
                regCacheStack= pickle.load(inp)
            revert["dischargeRate"]=regCacheStack[4]["Control"]["Battery_Discharge_Rate"]
            revert["start_time"]=regCacheStack[4]["Timeslots"]["Discharge_start_time_slot_1"][:5]
            revert["end_time"]=regCacheStack[4]["Timeslots"]["Discharge_end_time_slot_1"][:5]
            revert["dischargeToPercent"]=regCacheStack[4]["Control"]["Battery_Power_Reserve"]
            revert["mode"]=regCacheStack[4]["Control"]["Mode"]
        
        #set slot2 to calc times and keep slot 1 as is
        slot1=(datetime.strptime(regCacheStack[4]["Timeslots"]["Discharge_start_time_slot_1"][:5],"%H:%M"),datetime.strptime(regCacheStack[4]["Timeslots"]["Discharge_end_time_slot_1"][:5],"%H:%M")) 
        slot2=(datetime.now(),datetime.now()+timedelta(minutes=exportTime))
        logger.debug("Setting export slot to: "+ slot2[0].strftime("%H:%M")+" - "+slot2[1].strftime("%H:%M"))
        result=client.set_mode_storage(slot1,slot2,export=True)
        logger.debug("Mode result is:" + str(result))
        
        time.sleep(1)

        payload={}
        payload['dischargeRate']=100
        result=setDischargeRate(payload)
        logger.debug("DischargeRate result is:" + str(result))
        
        if "success" in result:
            fejob=GivQueue.q.enqueue_in(timedelta(minutes=exportTime),FEResume,revert)
            f=open(".FCRunning", 'w')
            f.write(str(fejob.id))
            f.close()
            logger.info("Force Export revert jobid is: "+fejob.id)
            temp['result']="Export successfully forced for "+str(exportTime)+" minutes"
        else:
            temp['result']="Force Export failed"
    except:
        e = sys.exc_info()
        temp['result']="Force Export failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def FCResume(revert):
    payload={}
    logger.info("Reverting Force Charge Settings:")
    payload['chargeRate']=revert["chargeRate"]
    result=setChargeRate(payload)
    time.sleep(1)
    payload={}
    payload['state']=revert["chargeScheduleEnable"]
    enableChargeSchedule(payload)
    time.sleep(1)
    payload={}
    payload['start']=revert["start_time"]
    payload['finish']=revert["end_time"]
    payload['chargeToPercent']=revert["targetSOC"]
    setChargeSlot1(payload)
    os.remove(".FCRunning")

def cancelJob(jobid):
    if jobid in GivQueue.q.scheduled_job_registry:
        GivQueue.q.scheduled_job_registry.requeue(jobid, at_front=True)
        logger.info("Cancelling scheduled task as requested")
    else:
        logger.error("Job ID: " + str(jobid) + " not found in redis queue")


def forceCharge(chargeTime):
    temp={}
    logger.info("Forcing Charge for "+str(chargeTime)+" minutes")
    try:
        chargeTime=int(chargeTime)
        payload={}
        result={}
        revert={}
        if exists(GivLUT.regcache):      # if there is a cache then grab it
            with open(GivLUT.regcache, 'rb') as inp:
                regCacheStack= pickle.load(inp)
            revert["start_time"]=regCacheStack[4]["Timeslots"]["Charge_start_time_slot_1"][:5]
            revert["end_time"]=regCacheStack[4]["Timeslots"]["Charge_end_time_slot_1"][:5]
            revert["chargeRate"]=regCacheStack[4]["Control"]["Battery_Charge_Rate"]
            revert["targetSOC"]=regCacheStack[4]["Control"]["Target_SOC"]
            revert["chargeScheduleEnable"]=regCacheStack[4]["Control"]["Enable_Charge_Schedule"]
        
        payload['chargeRate']=100
        result=setChargeRate(payload)

        payload={}
        payload['state']="enable"
        result=enableChargeSchedule(payload)

        payload={}
        payload['start']=GivLUT.getTime(datetime.now())
        payload['finish']=GivLUT.getTime(datetime.now()+timedelta(minutes=chargeTime))
        payload['chargeToPercent']=100
        result=setChargeSlot1(payload)
        
        if "success" in result:
            fcjob=GivQueue.q.enqueue_in(timedelta(minutes=chargeTime),FCResume,revert)
            f=open(".FCRunning", 'w')
            f.write(str(fcjob.id))
            f.close()
            logger.info("Force Charge revert jobid is: "+fcjob.id)
            temp['result']="Charge successfully forced "+str(chargeTime)+" minutes"
        else:
            temp['result']="Force charge failed"
    except:
        e = sys.exc_info()
        temp['result']="Force charge failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def tmpPDResume(payload):
    result=setDischargeRate(payload)
    logger.info("Discharge Rate restored to: "+str(payload["dischargeRate"]))
    if exists(".tpdRunning"): os.remove(".tpdRunning")

def tempPauseDischarge(pauseTime):
    temp={}
    try:
        pauseTime=int(pauseTime)
        payload={}
        result={}
        payload['dischargeRate']=0
        result=setDischargeRate(payload)
        logger.info("Pausing Discharge for "+str(pauseTime)+" minutes")
        #Update read data via pickle
        if exists(GivLUT.regcache):      # if there is a cache then grab it
            with open(GivLUT.regcache, 'rb') as inp:
                regCacheStack= pickle.load(inp)
            revertRate=regCacheStack[4]["Control"]["Battery_Discharge_Rate"]
        
        if "success" in result:
            payload['dischargeRate']=revertRate
            delay=float(pauseTime*60)
            tpdjob=GivQueue.q.enqueue_in(timedelta(delay),tmpPDResume,payload)
            f=open(".tpdRunning", 'w')
            f.write(str(tpdjob.id))
            f.close()
            logger.info("Temp Pause Discharge revert jobid is: "+tpdjob.id)
            temp['result']="Discharge paused for "+str(delay)+" seconds"
        else:
            temp['result']="Pausing Discharge failed"
    except:
        e = sys.exc_info()
        temp['result']="Pausing Discharge failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def tmpPCResume(payload):
    result=setChargeRate(payload)
    logger.info("Charge Rate restored to: "+str(payload["chargeRate"]))
    if exists(".tpcRunning"): os.remove(".tpcRunning")

def tempPauseCharge(pauseTime):
    temp={}
    try:
        logger.info("Pausing Charge for "+str(pauseTime)+" minutes")
        payload={}
        result={}
        payload['chargeRate']=0
        result=setChargeRate(payload)
        logger.debug(result)
        #Update read data via pickle
        if exists(GivLUT.regcache):      # if there is a cache then grab it
            with open(GivLUT.regcache, 'rb') as inp:
                regCacheStack= pickle.load(inp)
        revertRate=regCacheStack[4]["Control"]["Battery_Charge_Rate"]
        
        if "success" in result:
            payload['chargeRate']=revertRate
            delay=float(pauseTime*60)
            tpcjob=GivQueue.q.enqueue_in(timedelta(delay),tmpPCResume,payload)
            f=open(".tpcRunning", 'w')
            f.write(str(tpcjob.id))
            f.close()
            logger.info("Temp Pause Charge revert jobid is: "+tpcjob.id)
            temp['result']="Charge paused for "+str(delay)+" seconds"
        else:
            temp['result']="Pausing Charge failed: "
        logger.debug("Result is: "+temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Pausing Charge failed: " + str(e)
        logger.error(temp['result'])
    return json.dumps(temp)

def setBatteryMode(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    logger.info("Setting Battery Mode to: "+str(payload['mode']))
    try:
        if payload['mode']=="Eco":
            client.set_mode_dynamic()
            time.sleep(1)
            client.set_shallow_charge(getSavedBatteryReservePercentage())
        elif payload['mode']=="Eco (Paused)":
            client.set_mode_dynamic()
            time.sleep(1)
            client.set_shallow_charge(100)
        elif payload['mode']=="Timed Demand":
            client.set_mode_storage()
            time.sleep(1)
            client.enable_discharge()
        elif payload['mode']=="Timed Export":
            client.set_mode_storage(export=True)
            time.sleep(1)
            client.enable_discharge()
        else:
            logger.error ("Invalid Mode requested: "+ payload['mode'])
            temp['result']="Invalid Mode requested"
            return json.dumps(temp)
        temp['result']="Setting Battery Mode was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Battery Mode failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDateTime(payload):
    temp={}
    targetresult="Success"
    if type(payload) is not dict: payload=json.loads(payload)
    #convert payload to dateTime components
    try:
        iDateTime=datetime.strptime(payload['dateTime'],"%d/%m/%Y %H:%M:%S")   #format '12/11/2021 09:15:32'
        logger.info("Setting Invertor time to: "+iDateTime)
        #Set Date and Time on Invertor
        client.set_datetime(iDateTime)
        temp['result']="Invertor time setting was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Battery Mode failed: " + str(e) 
        logger.error (temp['result'])
    return json.dumps(temp)

def switchRate(payload):
    temp={}
    if GiV_Settings.dynamic_tariff == False:     # Only allow this control if Dyanmic control is enabled
        temp['result']="External rate setting not allowed. Enale Dynamic Tariff in settings"
        logger.error(temp['result'])
        return json.dumps(temp)
    try:
        logger.info("Switching rate to: "+payload)
        if payload.lower()=="day":
            open(".dayRateRequest", 'w').close()
            logger.critical ("Setting dayRate via external trigger")
        else:
            open(".nightRateRequest", 'w').close()
            logger.critical ("Setting nightRate via external trigger")
    except:
        e = sys.exc_info()
        temp['result']="Setting Battery Mode failed: " + str(e) 
        logger.error (temp['result'])
    return json.dumps(temp)

def getSavedBatteryReservePercentage():
    saved_battery_reserve=4
    if exists(GivLUT.reservepkl):
        with open(GivLUT.reservepkl, 'rb') as inp:
            saved_battery_reserve= pickle.load(inp)
    return saved_battery_reserve

if __name__ == '__main__':
    if len(sys.argv)==2:
        globals()[sys.argv[1]]()
    elif len(sys.argv)==3:
        globals()[sys.argv[1]](sys.argv[2])

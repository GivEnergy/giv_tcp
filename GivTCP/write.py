# -*- coding: utf-8 -*-
# version 2022.01.31
import sys
import json
import logging
import datetime
from datetime import datetime, timedelta
from settings import GiV_Settings
import settings
import time
from os.path import exists
import pickle,os
from GivLUT import GivLUT, GivQueue
from givenergy_modbus.client import GivEnergyClient
from rq import Retry
from mqtt import GivMQTT
import requests
import importlib

logging.getLogger("givenergy_modbus").setLevel(logging.CRITICAL)
client=GivEnergyClient(host=GiV_Settings.invertorIP)

logger = GivLUT.logger

def updateControlMQTT(entity,value):
    # immediately update broker on success of control áction
    importlib.reload(settings)
    from settings import GiV_Settings
    if GiV_Settings.MQTT_Topic == "":
        GiV_Settings.MQTT_Topic = "GivEnergy"
    Topic=str(GiV_Settings.MQTT_Topic+"/"+GiV_Settings.serial_number+"/Control/")+str(entity)
    GivMQTT.single_MQTT_publish(Topic,str(value))
    return


def sct(target):
    temp={}
    try:
        client.enable_charge_target(target)
        updateControlMQTT("Target_SOC",target)
        temp['result']="Setting Charge Target "+str(target)+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Target "+str(target)+" failed: " + str(e)
    logger.info(temp['result'])
    return json.dumps(temp)
def sct2(target,slot):
    temp={}
    try:
        client.enable_charge_target_2(target,slot)
        updateControlMQTT("Charge_Target_SOC_"+str(slot),target)
        temp['result']="Setting Charge Target "+str(slot) + " was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Target "+str(slot) + " failed: " + str(e)
    logger.info(temp['result'])
    return json.dumps(temp)
def ect():
    temp={}
    try:
        client.enable_charge_target()
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def dct():
    temp={}
    try:
        client.disable_charge_target()
        updateControlMQTT("Target_SOC","100")
        temp['result']="Setting Discharge Disable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Disable failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def ed():
    temp={}
    try:
        client.enable_discharge()
        updateControlMQTT("Enable_Discharge_Schedule","enable")
        temp['result']="Enabling Discharge was a success"
    except:
        e = sys.exc_info()
        temp['result']="Enabling Discharge failed: " + str(e)
    logger.info(temp['result'])   
    return json.dumps(temp)
def dd():
    temp={}
    try:
        client.disable_discharge()
        updateControlMQTT("Enable_Discharge_Schedule","disable")
        temp['result']="Disabling discharge was a success"
    except:
        e = sys.exc_info()
        temp['result']="Disabling discharge failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def ec():
    temp={}
    try:
        client.enable_charge()
        updateControlMQTT("Enable_Charge_Schedule","enable")
        temp['result']="Setting Charge Enable was a success"
        
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def dc():
    temp={}
    try:
        client.disable_charge()
        updateControlMQTT("Enable_Charge_Schedule","disable")
        temp['result']="Disabling Charge was a success"
    except:
        e = sys.exc_info()
        temp['result']="Disabling Charge failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)

def slcm(val):
    temp={}
    try:
        client.set_local_control_mode(val)
        updateControlMQTT("Local_control_mode",str(GivLUT.local_control_mode[int(val)]))
        temp['result']="Setting Local Control Mode to " +str(GivLUT.local_control_mode[val])+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Local Control Mode to " +str(GivLUT.local_control_mode[val])+" failed: " + str(e)
    logger.info(temp['result'])
    return json.dumps(temp)

def sbpm(val):
    temp={}
    try:
        client.set_battery_pause_mode(val)
        updateControlMQTT("Battery_pause_mode",str(GivLUT.battery_pause_mode[int(val)]))
        temp['result']="Setting Battery Pause Mode to " +str(GivLUT.battery_pause_mode[val])+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Battery Pause Mode to " +str(GivLUT.battery_pause_mode[val])+" failed: " + str(e)
    logger.info(temp['result'])
    return json.dumps(temp)
    #return temp

def ssc(target):
    temp={}
    try:
        client.set_shallow_charge(target)
        updateControlMQTT("Battery_Power_Reserve",str(target))
        temp['result']="Setting shallow charge "+str(target)+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting shallow charge "+str(target)+" failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def sbpr(target):
    temp={}
    try:
        client.set_battery_power_reserve(target)
        updateControlMQTT("Battery_Power_Cutoff",str(target))
        temp['result']="Setting battery power reserve to "+str(target)+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting battery power reserve "+str(target)+" failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def ri():
    temp={}
    try:
        client.reboot_inverter()
        temp['result']="Rebooting Inverter was a success"
    except:
        e = sys.exc_info()
        temp['result']="Rebooting Inverter failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def sapr(target):
    temp={}
    try:
        client.set_active_power_rate(target)
        updateControlMQTT("Active_Power_Rate",str(target))
        temp['result']="Setting active power rate "+str(target)+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting active power rate "+str(target)+" failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def sbcl(target):
    temp={}
    try:
        client.set_battery_charge_limit(target)
        # Get cache and work out rate
        if exists(GivLUT.regcache):      # if there is a cache then grab it
            with open(GivLUT.regcache, 'rb') as inp:
                regCacheStack = pickle.load(inp)
                multi_output_old = regCacheStack[4]
                batteryCapacity=int(multi_output_old["Invertor_Details"]['Battery_Capacity_kWh'])*1000
                batmaxrate=int(multi_output_old["Invertor_Details"]['Invertor_Max_Bat_Rate'])
            val=int(min((target/100)*(batteryCapacity), batmaxrate))
            updateControlMQTT("Battery_Charge_Rate",str(val))
        temp['result']="Setting battery charge rate "+str(target)+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting battery charge rate "+str(target)+" failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def sbdl(target):
    temp={}
    try:
        client.set_battery_discharge_limit(target)
        # Get cache and work out rate
        if exists(GivLUT.regcache):      # if there is a cache then grab it
            with open(GivLUT.regcache, 'rb') as inp:
                regCacheStack = pickle.load(inp)
                multi_output_old = regCacheStack[4]
                batteryCapacity=int(multi_output_old["Invertor_Details"]['Battery_Capacity_kWh'])*1000
                batmaxrate=int(multi_output_old["Invertor_Details"]['Invertor_Max_Bat_Rate'])
            val=int(min((target/100)*(batteryCapacity), batmaxrate))
        temp['result']="Setting battery discharge limit "+str(target)+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting battery discharge limit "+str(target)+" failed: " + str(e)
    logger.info(temp['result'])   
    return json.dumps(temp)
def smd():
    temp={}
    try:
        client.set_mode_dynamic()
        #updateControlMQTT("Mode","Eco")
        temp['result']="Setting dynamic mode was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting dynamic mode failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def sms(target):
    temp={}
    try:
        client.set_mode_storage(target)
        temp['result']="Setting storage mode "+str(target)+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting storage mode "+str(target)+" failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def sbdmd():
    temp={}
    try:
        client.set_battery_discharge_mode_demand()
        #updateControlMQTT("Mode","Timed Demand")
        temp['result']="Setting demand mode was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting demand mode failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def sbdmmp():
    temp={}
    try:
        client.set_battery_discharge_mode_max_power()
        #updateControlMQTT("Mode","Timed Export")
        temp['result']="Setting export mode was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting export mode failed: " + str(e)
    logger.info(temp['result'])   
    return json.dumps(temp)

def spvim(val):
    temp={}
    try:
        client.set_pv_input_mode(val)
        updateControlMQTT("PV_input_mode",str(GivLUT.pv_input_mode[int(val)]))
        temp['result']="Setting PV Input mode to "+str(GivLUT.pv_input_mode[val])+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting PV Input mode to "+str(GivLUT.pv_input_mode[val])+" failed: " + str(e)
    logger.info(temp['result'])  
    return json.dumps(temp)

def sdt(idateTime):
    temp={}
    try:
        client.set_datetime(idateTime)
        temp['result']="Setting inverter time was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting inverter time failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def sds(payload):
    temp={}
    try:
        client.set_discharge_slot(int(payload['slot']),[datetime.strptime(payload['start'],"%H:%M"),datetime.strptime(payload['finish'],"%H:%M")])
        updateControlMQTT("Discharge_start_time_slot_"+str(payload['slot']),str(datetime.strptime(payload['start'],"%H:%M")))
        updateControlMQTT("Discharge_end_time_slot_"+str(payload['slot']),str(datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Discharge Slot "+str(payload['slot'])+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot "+str(payload['slot'])+" failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
def sdss(payload):
    temp={}
    try:
        client.set_discharge_slot_start(int(payload['slot']),datetime.strptime(payload['start'],"%H:%M"))
        updateControlMQTT("Discharge_start_time_slot_"+str(payload['slot']),str(datetime.strptime(payload['start'],"%H:%M")))
        temp['result']="Setting Discharge Slot Start "+str(payload['slot'])+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot Start "+str(payload['slot'])+" failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)

def sdse(payload):
    temp={}
    try:
        client.set_discharge_slot_end(int(payload['slot']),datetime.strptime(payload['finish'],"%H:%M"))
        updateControlMQTT("Discharge_end_time_slot_"+str(payload['slot']),str(datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Discharge Slot End "+str(payload['slot'])+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot End "+str(payload['slot'])+" failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)

def sps(payload):
    temp={}
    try:
        client.set_pause_slot_start(datetime.strptime(payload['start'],"%H:%M"))
        updateControlMQTT("Battery_pause_end_time_slot"+str(payload['slot']),str(datetime.strptime(payload['start'],"%H:%M")))
        temp['result']="Setting Pause Slot Start was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Pause Slot Start failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)

def spe(payload):
    temp={}
    try:
        client.set_pause_slot_end(datetime.strptime(payload['finish'],"%H:%M"))
        updateControlMQTT("Battery_pause_end_time_slot"+str(payload['slot']),str(datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Pause Slot End was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Pause Slot End failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)

def scs(payload):
    temp={}
    try:
        client.set_charge_slot(int(payload['slot']),[datetime.strptime(payload['start'],"%H:%M"),datetime.strptime(payload['finish'],"%H:%M")])
        updateControlMQTT("Charge_start_time_slot_"+str(payload['slot']),str(datetime.strptime(payload['start'],"%H:%M")))
        updateControlMQTT("Charge_end_time_slot_"+str(payload['slot']),str(datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Charge Slot "+str(payload['slot'])+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot "+str(payload['slot'])+" failed: " + str(e)
    logger.info(temp['result'])   
    return json.dumps(temp)
def scss(payload):
    temp={}
    try:
        client.set_charge_slot_start(int(payload['slot']),datetime.strptime(payload['start'],"%H:%M"))
        updateControlMQTT("Charge_start_time_slot_"+str(payload['slot']),str(datetime.strptime(payload['start'],"%H:%M")))
        temp['result']="Setting Charge Slot Start "+str(payload['slot'])+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot Start "+str(payload['slot'])+" failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)

def scse(payload):
    temp={}
    try:
        client.set_charge_slot_end(int(payload['slot']),datetime.strptime(payload['finish'],"%H:%M"))
        updateControlMQTT("Charge_end_time_slot_"+str(payload['slot']),str(datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Charge Slot End "+str(payload['slot'])+" was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot End "+str(payload['slot'])+" failed: " + str(e)
    logger.info(temp['result'])    
    return json.dumps(temp)
    
def enableChargeSchedule(payload):
    temp={}
    try:
        if payload['state']=="enable":
            logger.info("Enabling Charge Schedule")
            from write import ec
            result=GivQueue.q.enqueue(ec,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        elif payload['state']=="disable":
            logger.info("Disabling Charge Schedule")
            from write import dc
            result=GivQueue.q.enqueue(dc,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting charge schedule "+str(payload['state'])+" failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def enableChargeTarget(payload):
    temp={}
    try:
        if payload['state']=="enable":
            logger.info("Enabling Charge Target")
            from write import ect
            result=GivQueue.q.enqueue(ect,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        elif payload['state']=="disable":
            logger.info("Disabling Charge Target")
            from write import dct
            result=GivQueue.q.enqueue(dct,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Target failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def enableDischarge(payload):
    temp={}
    saved_battery_reserve = getSavedBatteryReservePercentage()
    try:
        if payload['state']=="enable":
            logger.info("Enabling Discharge")
            from write import ssc
            result=GivQueue.q.enqueue(ssc,saved_battery_reserve,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        elif payload['state']=="disable":
            logger.info("Disabling Discharge")
            from write import ssc
            result=GivQueue.q.enqueue(ssc,100,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def enableDischargeSchedule(payload):
    temp={}
    try:
        if payload['state']=="enable":
            logger.info("Enabling Disharge Schedule")
            from write import ed
            result=GivQueue.q.enqueue(ed,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        elif payload['state']=="disable":
            logger.info("Disabling Discharge Schedule")
            from write import dd
            result=GivQueue.q.enqueue(dd,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setShallowCharge(payload):
    temp={}
    try:
        logger.info("Setting Shallow Charge to: "+ str(payload['val']))
        from write import ssc
        result=GivQueue.q.enqueue(ssc,int(payload['val']),retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting shallow charge failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeTarget(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    target=int(payload['chargeToPercent'])
    try:
        logger.info("Setting Charge Target to: "+str(target))
        from write import sct
        result=GivQueue.q.enqueue(sct,target,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Target failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeTarget2(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    target=int(payload['chargeToPercent'])
    slot=int(payload['slot'])
    try:
        logger.info("Setting Charge Target "+str(slot) + " to: "+str(target))
        from write import sct2
        result=GivQueue.q.enqueue(sct2,target,slot,retry=Retry(max=GiV_Settings.queue_retries, interval=2))


    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Target "+str(slot) + " failed: " + str(e)
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
        from write import ssc
        result=GivQueue.q.enqueue(ssc,target,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
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
        from write import sbpr
        result=GivQueue.q.enqueue(sbpr,target,retry=Retry(max=GiV_Settings.queue_retries, interval=2))


    except:
        e = sys.exc_info()
        temp['result']="Setting Battery Cutoff failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def rebootinverter():
    temp={}
    try:
        logger.info("Rebooting inverter...")
        from write import ri
        result=GivQueue.q.enqueue(ri,retry=Retry(max=GiV_Settings.queue_retries, interval=2))


    except:
        e = sys.exc_info()
        temp['result']="Reboot inverter failed: " + str(e)
        logger.error (temp['result'])
        #raise Exception
    return json.dumps(temp)

def setActivePowerRate(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    target=int(payload['activePowerRate'])
    try:
        logger.info("Setting Active Power Rate to "+str(target))
        from write import sapr
        result=GivQueue.q.enqueue(sapr,target,retry=Retry(max=GiV_Settings.queue_retries, interval=2))


    except:
        e = sys.exc_info()
        temp['result']="Setting Active Power Rate failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeRate(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)

    # Get inverter max bat power
    if exists(GivLUT.regcache):      # if there is a cache then grab it
        with open(GivLUT.regcache, 'rb') as inp:
            regCacheStack = pickle.load(inp)
            multi_output_old = regCacheStack[4]
        invmaxrate=multi_output_old['Invertor_Details']['Invertor_Max_Bat_Rate']
        batcap=float(multi_output_old['Invertor_Details']['Battery_Capacity_kWh'])*1000

        if int(payload['chargeRate']) < int(invmaxrate):
            target=int(min((int(payload['chargeRate'])/(batcap/2))*50,50))
        else:
            target=50
        logger.info ("Setting battery charge rate to: " + str(payload['chargeRate'])+" ("+str(target)+")")
        try:
            from write import sbcl
            result=GivQueue.q.enqueue(sbcl,target,retry=Retry(max=GiV_Settings.queue_retries, interval=2))

        except:
            e = sys.exc_info()
            temp['result']="Setting Charge Rate failed: " + str(e)
            logger.error (temp['result'])
            #raise Exception
    else:
        temp['result']="Setting Charge Rate failed: No charge rate limit available"
        logger.error (temp['result'])
    return json.dumps(temp)

def setDischargeRate(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    # Get inverter max bat power
    if exists(GivLUT.regcache):      # if there is a cache then grab it
        with open(GivLUT.regcache, 'rb') as inp:
            regCacheStack = pickle.load(inp)
            multi_output_old = regCacheStack[4]
        invmaxrate=multi_output_old['Invertor_Details']['Invertor_Max_Bat_Rate']
        batcap=float(multi_output_old['Invertor_Details']['Battery_Capacity_kWh'])*1000

        if int(payload['dischargeRate']) < int(invmaxrate):
            target=int(min((int(payload['dischargeRate'])/(batcap/2))*50,50))
        else:
            target=50
        logger.info ("Setting battery discharge rate to: " + str(payload['dischargeRate'])+" ("+str(target)+")")
        try:
            from write import sbdl
            result=GivQueue.q.enqueue(sbdl,target,retry=Retry(max=GiV_Settings.queue_retries, interval=2))

        except:
            e = sys.exc_info()
            temp['result']="Setting Discharge Rate failed: " + str(e)
            logger.error (temp['result'])
    else:
        temp['result']="Setting Discharge Rate failed: No discharge rate limit available"
        logger.error (temp['result'])        
    return json.dumps(temp)

def setChargeSlot(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    if 'chargeToPercent' in payload.keys():
        target=int(payload['chargeToPercent'])
        from write import sct
        result=GivQueue.q.enqueue(sct,target,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    try:
        logger.info("Setting Charge Slot "+str(payload['slot'])+" to: "+str(payload['start'])+" - "+str(payload['finish']))
        from write import scs
        result=GivQueue.q.enqueue(scs,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot "+str(payload['slot'])+" failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeSlotStart(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Charge Slot "+str(payload['slot'])+" Start to: "+str(payload['start']))
        from write import scss
        result=GivQueue.q.enqueue(scss,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot "+str(payload['slot'])+" failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeSlotEnd(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Charge Slot End "+str(payload['slot'])+" to: "+str(payload['finish']))
        from write import scse
        result=GivQueue.q.enqueue(scse,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot "+str(payload['slot'])+" failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDischargeSlot(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    if 'dischargeToPercent' in payload.keys():
        result=setBatteryReserve(payload)
    try:
        strt=datetime.strptime(payload['start'],"%H:%M")
        fnsh=datetime.strptime(payload['finish'],"%H:%M")
        logger.info("Setting Discharge Slot "+str(payload['slot'])+" to: "+str(payload['start'])+" - "+str(payload['finish']))
        from write import sds
        result=GivQueue.q.enqueue(sds,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot "+str(payload['slot'])+" failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDischargeSlotStart(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Discharge Slot start "+str(payload['slot'])+" Start to: "+str(payload['start']))
        from write import sdss
        result=GivQueue.q.enqueue(sdss,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot start "+str(payload['slot'])+" failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDischargeSlotEnd(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Discharge Slot End "+str(payload['slot'])+" to: "+str(payload['finish']))
        from write import sdse
        result=GivQueue.q.enqueue(sdse,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot End "+str(payload['slot'])+" failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setPauseStart(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Pause Slot Start to: "+str(payload['start']))
        from write import sps
        result=GivQueue.q.enqueue(sps,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting Pause Slot Start failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setPauseEnd(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Pause Slot End to: "+str(payload['finish']))
        from write import spe
        result=GivQueue.q.enqueue(spe,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting Pause Slot End failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)



def FEResume(revert):
    temp={}
    try:
        payload={}
        logger.info("Reverting Force Export settings:")   
        payload['dischargeRate']=revert["dischargeRate"]
        result=setDischargeRate(payload)
        payload={}
        payload['start']=revert["start_time"]
        payload['finish']=revert["end_time"]
        payload['slot']=2
        result=setDischargeSlot(payload)
        payoad={}
        payload['state']=revert['discharge_schedule']
        result=enableDischargeSchedule(payload)
        payload={}
        payload['reservePercent']=revert["reservePercent"]
        result=setBatteryReserve(payload)
        payload={}
        payload["mode"]=revert["mode"]
        result=setBatteryMode(payload)
        os.remove(".FERunning")
        updateControlMQTT("Force_Export","Normal")
    except:
        e = sys.exc_info()
        temp['result']="Force Export Revert failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

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
            revert["start_time"]=regCacheStack[4]["Timeslots"]["Discharge_start_time_slot_2"][:5]
            revert["end_time"]=regCacheStack[4]["Timeslots"]["Discharge_end_time_slot_2"][:5]
            revert["reservePercent"]=regCacheStack[4]["Control"]["Battery_Power_Reserve"]
            revert["mode"]=regCacheStack[4]["Control"]["Mode"]
            revert['discharge_schedule']=regCacheStack[4]["Control"]["Enable_Discharge_Schedule"]
        maxDischargeRate=int(regCacheStack[4]["Invertor_Details"]["Invertor_Max_Bat_Rate"])
        
        #In case somebody has set a high reserve value set the reserve rate to the default value to allow the battery to discharge
        try:
            payload={}
            payload['reservePercent']=4
            result=setBatteryReserve(payload) 
        except:
            logger.debug("Error Setting Reserve to 4%")

        payload={}
        payload['state']="enable"
        result=enableDischargeSchedule(payload)
        payload={}
        payload['start']=GivLUT.getTime(datetime.now())
        payload['finish']=GivLUT.getTime(datetime.now()+timedelta(minutes=exportTime))
        payload['slot']=2
        result=setDischargeSlot(payload)
        payload={}
        payload['mode']="Timed Export"
        result=setBatteryMode(payload)
        payload={}
        logger.debug("Max discharge rate for inverter is: " + str(maxDischargeRate))
        payload['dischargeRate']=maxDischargeRate
        result=setDischargeRate(payload)
        if exists(".FERunning"):    # If a forcecharge is already running, change time of revert job to new end time
            logger.info("Force Export already running, changing end time")
            revert=getFEArgs()[0]   # set new revert object and cancel old revert job
            logger.critical("new revert= "+ str(revert))
        fejob=GivQueue.q.enqueue_in(timedelta(minutes=exportTime),FEResume,revert)
        f=open(".FERunning", 'w')
        f.write(str(fejob.id))
        f.close()
        logger.info("Force Export revert jobid is: "+fejob.id)
        temp['result']="Export successfully forced for "+str(exportTime)+" minutes"
        updateControlMQTT("Force_Export","Running")
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Force Export failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def FCResume(revert):
    payload={}
    logger.info("Reverting Force Charge Settings:")
    payload['chargeRate']=revert["chargeRate"]
    setChargeRate(payload)
    payload={}
    payload['state']=revert["chargeScheduleEnable"]
    enableChargeSchedule(payload)
    payload={}
    payload['start']=revert["start_time"]
    payload['finish']=revert["end_time"]
    payload['chargeToPercent']=revert["targetSOC"]
    payload['slot']=1
    setChargeSlot(payload)
    os.remove(".FCRunning")
    updateControlMQTT("Force_Charge","Normal")

def cancelJob(jobid):
    if jobid in GivQueue.q.scheduled_job_registry:
        GivQueue.q.scheduled_job_registry.requeue(jobid, at_front=True)
        logger.info("Cancelling scheduled task as requested")
    else:
        logger.error("Job ID: " + str(jobid) + " not found in redis queue")

def getFCArgs():
    from rq.job import Job
    # getjobid
    f=open(".FCRunning", 'r')
    jobid=f.readline()
    f.close()
    # get the revert details from the old job
    job=Job.fetch(jobid,GivQueue.redis_connection)
    details=job.args
    logger.debug("Previous args= "+str(details))
    GivQueue.q.scheduled_job_registry.remove(jobid) # Remove the job from the schedule
    return (details)

def getFEArgs():
    from rq.job import Job
    # getjobid
    f=open(".FERunning", 'r')
    jobid=f.readline()
    f.close()
    # get the revert details from the old job
    job=Job.fetch(jobid,GivQueue.redis_connection)
    details=job.args
    logger.debug("Previous args= "+str(details))
    GivQueue.q.scheduled_job_registry.remove(jobid) # Remove the job from the schedule
    return (details)

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
        maxChargeRate=int(regCacheStack[4]["Invertor_Details"]["Invertor_Max_Bat_Rate"])

        payload['chargeRate']=maxChargeRate
        result=setChargeRate(payload)
        payload={}
        payload['state']="enable"
        result=enableChargeSchedule(payload)
        payload={}
        payload['start']=GivLUT.getTime(datetime.now())
        payload['finish']=GivLUT.getTime(datetime.now()+timedelta(minutes=chargeTime))
        payload['chargeToPercent']=100
        payload['slot']=1
        result=setChargeSlot(payload)
        if exists(".FCRunning"):    # If a forcecharge is already running, change time of revert job to new end time
            logger.info("Force Charge already running, changing end time")
            revert=getFCArgs()[0]   # set new revert object and cancel old revert job
            logger.critical("new revert= "+ str(revert))
        fcjob=GivQueue.q.enqueue_in(timedelta(minutes=chargeTime),FCResume,revert)
        f=open(".FCRunning", 'w')
        f.write(str(fcjob.id))
        f.close()
        logger.info("Force Charge revert jobid is: "+fcjob.id)
        temp['result']="Charge successfully forced for "+str(chargeTime)+" minutes"
        updateControlMQTT("Force_Charge","Running")
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Force charge failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def tmpPDResume(payload):
    temp={}
    try:
        logger.info("Reverting Temp Pause Discharge")
        result=setDischargeRate(payload)
        if exists(".tpdRunning"): os.remove(".tpdRunning")
        temp['result']="Temp Pause Discharge Reverted"
        updateControlMQTT("Temp_Pause_Discharge","Normal")
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Temp Pause Discharge Resume failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def tempPauseDischarge(pauseTime):
    temp={}
    try:
        pauseTime=int(pauseTime)
        logger.info("Pausing Discharge for "+str(pauseTime)+" minutes")
        payload={}
        result={}
        payload['dischargeRate']=0
        result=setDischargeRate(payload)
        #Update read data via pickle
        if exists(GivLUT.regcache):      # if there is a cache then grab it
            with open(GivLUT.regcache, 'rb') as inp:
                regCacheStack= pickle.load(inp)
            revertRate=regCacheStack[4]["Control"]["Battery_Discharge_Rate"]
        else:

            revertRate=2600
        payload['dischargeRate']=revertRate
        delay=float(pauseTime*60)
        tpdjob=GivQueue.q.enqueue_in(timedelta(seconds=delay),tmpPDResume,payload)
        f=open(".tpdRunning", 'w')
        f.write(str(tpdjob.id))
        f.close()
        logger.info("Temp Pause Discharge revert jobid is: "+tpdjob.id)
        temp['result']="Discharge paused for "+str(delay)+" seconds"
        updateControlMQTT("Temp_Pause_Discharge","Running")
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Pausing Discharge failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def tmpPCResume(payload):
    temp={}
    try:
        logger.info("Reverting Temp Pause Charge...")
        result=setChargeRate(payload)
        if exists(".tpcRunning"): os.remove(".tpcRunning")
        temp['result']="Temp Pause Charge Reverted"
        updateControlMQTT("Temp_Pause_Charge","Normal")
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Temp Pause Charge Resume failed: " + str(e)
        logger.error (temp['result'])
    return json.dump(temp)

def tempPauseCharge(pauseTime):
    temp={}
    try:
        logger.info("Pausing Charge for "+str(pauseTime)+" minutes")
        payload={}
        result={}
        payload['chargeRate']=0
        result=setChargeRate(payload)
        #Update read data via pickle
        if exists(GivLUT.regcache):      # if there is a cache then grab it
            with open(GivLUT.regcache, 'rb') as inp:
                regCacheStack= pickle.load(inp)
            revertRate=regCacheStack[4]["Control"]["Battery_Charge_Rate"]
        else:
            revertRate=2600
        payload['chargeRate']=revertRate
        delay=float(pauseTime*60)
        tpcjob=GivQueue.q.enqueue_in(timedelta(seconds=delay),tmpPCResume,payload)
        f=open(".tpcRunning", 'w')
        f.write(str(tpcjob.id))
        f.close()
        logger.info("Temp Pause Charge revert jobid is: "+tpcjob.id)
        temp['result']="Charge paused for "+str(delay)+" seconds"
        updateControlMQTT("Temp_Pause_Charge","Running")
        logger.info(temp['result'])
        logger.debug("Result is: "+temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Pausing Charge failed: " + str(e)
        logger.error(temp['result'])
    return json.dumps(temp)

def setBatteryPowerMode(payload):
    temp={}
    logger.info("Setting Battery Power Mode to: "+str(payload['state']))
    if type(payload) is not dict: payload=json.loads(payload)
    if payload['state']=="enable":
        from write import sbdmd
        result=GivQueue.q.enqueue(sbdmd,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    else:
        from write import sbdmmp
        result=GivQueue.q.enqueue(sbdmmp,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    temp['result']="Setting Battery Power Mode to "+str(payload['state'])+" was a success"
    
    return json.dumps(temp)

def setBatteryPauseMode(payload):
    temp={}
    logger.info("Setting Battery Pause Mode to: "+str(payload['state']))
    if type(payload) is not dict: payload=json.loads(payload)
    if payload['state'] in GivLUT.battery_pause_mode:
        val=GivLUT.battery_pause_mode.index(payload['state'])
        from write import sbpm
        job=GivQueue.q.enqueue(sbpm,val,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        while job.result is None and job.exc_info is None:
            time.sleep(0.5)
        print (job)
    else:
        logger.error ("Invalid Mode requested: "+ payload['state'])
        temp['result']="Invalid Mode requested"
    return json.dumps(temp)

def setLocalControlMode(payload):
    temp={}
    logger.info("Setting Local Control Mode to: "+str(payload['state']))
    if type(payload) is not dict: payload=json.loads(payload)
    if payload['state'] in GivLUT.local_control_mode:
        val=GivLUT.local_control_mode.index(payload['state'])
        from write import slcm
        result=GivQueue.q.enqueue(slcm,val,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    else:
        logger.error ("Invalid Mode requested: "+ payload['state'])
        temp['result']="Invalid Mode requested"
    return json.dumps(temp)

def setBatteryMode(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    logger.info("Setting Battery Mode to: "+str(payload['mode']))
    #Update read data via pickle
    if exists(GivLUT.regcache):      # if there is a cache then grab it
        with open(GivLUT.regcache, 'rb') as inp:
            regCacheStack= pickle.load(inp)
    logger.debug("Current battery mode from pickle is: " + str(regCacheStack[4]["Control"]["Mode"] ))
    try:
        if payload['mode']=="Eco":
            from write import smd
            result=GivQueue.q.enqueue(smd,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            from write import ssc
            saved_battery_reserve = getSavedBatteryReservePercentage()
            result=GivQueue.q.enqueue(ssc,saved_battery_reserve,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        elif payload['mode']=="Eco (Paused)":
            from write import smd
            result=GivQueue.q.enqueue(smd,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            from write import ssc
            result=GivQueue.q.enqueue(ssc,100,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        elif payload['mode']=="Timed Demand":
            from write import sbdmd, ed
            result=GivQueue.q.enqueue(sbdmd,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            result=GivQueue.q.enqueue(ed,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        elif payload['mode']=="Timed Export":
            from write import sbdmmp,ed
            result=GivQueue.q.enqueue(sbdmmp,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            result=GivQueue.q.enqueue(ed,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
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

def setPVInputMode(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    logger.info("Setting PV Input mode to: "+ str(payload['state']))
    try:
        if payload['state'] in GivLUT.pv_input_mode:
            from write import spvim
            result=GivQueue.q.enqueue(spvim,GivLUT.pv_input_mode.index(payload['state']),retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        else:
            logger.error ("Invalid Mode requested: "+ payload['state'])
            temp['result']="Invalid Mode requested"
        temp['result']="Setting PV Input Mode was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting PV Input Mode failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDateTime(payload):
    temp={}
    targetresult="Success"
    if type(payload) is not dict: payload=json.loads(payload)
    #convert payload to dateTime components
    try:
        iDateTime=datetime.strptime(payload['dateTime'],"%d/%m/%Y %H:%M:%S")   #format '12/11/2021 09:15:32'
        logger.info("Setting inverter time to: "+iDateTime)
        #Set Date and Time on inverter
        from write import sdt
        result=GivQueue.q.enqueue(sdt,iDateTime,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    except:
        e = sys.exc_info()
        temp['result']="Setting inverter DateTime failed: " + str(e) 
        logger.error (temp['result'])
    return json.dumps(temp)

def switchRate(payload):
    temp={}
    if GiV_Settings.dynamic_tariff == False:     # Only allow this control if Dynamic control is enabled
        temp['result']="External rate setting not allowed. Enable Dynamic Tariff in settings"
        logger.error(temp['result'])
        return json.dumps(temp)
    try:
        if payload.lower()=="day":
            open(GivLUT.dayRateRequest, 'w').close()
            logger.info ("Setting dayRate via external trigger")
        else:
            open(GivLUT.nightRateRequest, 'w').close()
            logger.info ("Setting nightRate via external trigger")
    except:
        e = sys.exc_info()
        temp['result']="Setting Rate failed: " + str(e) 
        logger.error (temp['result'])
    return json.dumps(temp)

def rebootAddon():
    logger.critical("Restarting the GivTCP Addon in 5s...")
    time.sleep(5)
    access_token = os.getenv("SUPERVISOR_TOKEN")
    url="http://supervisor/addons/self/restart"
    result = requests.post(url,
          headers={'Content-Type':'application/json',
                   'Authorization': 'Bearer {}'.format(access_token)})

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

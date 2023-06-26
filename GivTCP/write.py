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
from rq import Retry
import requests

logging.getLogger("givenergy_modbus").setLevel(logging.CRITICAL)
client=GivEnergyClient(host=GiV_Settings.invertorIP)

logger = GivLUT.logger


def sct(target):
    temp={}
    try:
        client.enable_charge_target(target)
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def ect():
    temp={}
    try:
        client.enable_charge_target()
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def dct():
    temp={}
    try:
        client.disable_charge_target()
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def ed():
    temp={}
    try:
        client.enable_discharge()
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def dd():
    temp={}
    try:
        client.disable_discharge()
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def ec():
    temp={}
    try:
        client.enable_charge()
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def dc():
    temp={}
    try:
        client.disable_charge()
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def ssc(target):
    temp={}
    try:
        client.set_shallow_charge(target)
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def sbpr(target):
    temp={}
    try:
        client.set_battery_power_reserve(target)
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def ri():
    temp={}
    try:
        client.reboot_invertor()
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def sapr(target):
    temp={}
    try:
        client.set_active_power_rate(target)
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def sbcl(target):
    temp={}
    try:
        client.set_battery_charge_limit(target)
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def sbdl(target):
    temp={}
    try:
        client.set_battery_discharge_limit(target)
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def smd(target):
    temp={}
    try:
        client.set_mode_dynamic(target)
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def sms(target):
    temp={}
    try:
        client.set_mode_storage(target)
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def sbdmd():
    temp={}
    try:
        client.set_battery_discharge_mode_demand()
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def sbdmmp():
    temp={}
    try:
        client.set_battery_discharge_mode_max_power()
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def sdt(idateTime):
    temp={}
    try:
        client.set_datetime(idateTime)
        temp['result']="Setting Charge Enable was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def sds1(payload):
    temp={}
    try:
        client.set_discharge_slot_1((datetime.strptime(payload['start'],"%H:%M"),datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Discharge Slot 2 was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def sdss1(payload):
    temp={}
    try:
        client.set_discharge_slot_start_1((datetime.strptime(payload['start'],"%H:%M")))
        temp['result']="Setting Discharge Slot Start 1 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot Start 1 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def sdse1(payload):
    temp={}
    try:
        client.set_discharge_slot_end_1((datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Discharge Slot End 1 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot End 1 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def sdss2(payload):
    temp={}
    try:
        client.set_discharge_slot_start_2((datetime.strptime(payload['start'],"%H:%M")))
        temp['result']="Setting Discharge Slot Start 2 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot Start 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def sdse2(payload):
    temp={}
    try:
        client.set_discharge_slot_end_2((datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Discharge Slot End 2 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot End 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def sds2(payload):
    temp={}
    try:
        client.set_discharge_slot_2((datetime.strptime(payload['start'],"%H:%M"),datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Discharge Slot 2 was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def scs1(payload):
    temp={}
    try:
        client.set_charge_slot_1((datetime.strptime(payload['start'],"%H:%M"),datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Charge Slot 1 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot 1 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def scss1(payload):
    temp={}
    try:
        client.set_charge_slot_start_1((datetime.strptime(payload['start'],"%H:%M")))
        temp['result']="Setting Charge Slot Start 1 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot Start 1 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def scse1(payload):
    temp={}
    try:
        client.set_charge_slot_end_1((datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Charge Slot End 1 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot End 1 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def scs2(payload):
    temp={}
    try:
        client.set_charge_slot_2((datetime.strptime(payload['start'],"%H:%M"),datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Discharge Slot 2 was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
def scss2(payload):
    temp={}
    try:
        client.set_charge_slot_start_2((datetime.strptime(payload['start'],"%H:%M")))
        temp['result']="Setting Charge Slot Start 2 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot Start 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def scse2(payload):
    temp={}
    try:
        client.set_charge_slot_end_2((datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Charge Slot End 2 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot End 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)
    
def enableChargeSchedule(payload):
    temp={}
    try:
        if payload['state']=="enable":
            logger.info("Enabling Charge Schedule")
            from write import ec
            result=GivQueue.q.enqueue(ec,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            #client.enable_charge()
        elif payload['state']=="disable":
            logger.info("Disabling Charge Schedule")
            from write import dc
            result=GivQueue.q.enqueue(dc,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            #client.disable_charge()
        temp['result']="Setting Charge Enable was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def enableChargeTarget(payload):
    temp={}
    try:
        if payload['state']=="enable":
            logger.info("Enabling Charge Target")
            from write import ect
            result=GivQueue.q.enqueue(ect,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            #client.enable_charge_target()
        elif payload['state']=="disable":
            logger.info("Disabling Charge Target")
            from write import dct
            result=GivQueue.q.enqueue(dct,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            #client.disable_charge_target()
        temp['result']="Setting Charge Target was a success"

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
            #client.set_shallow_charge(saved_battery_reserve)
        elif payload['state']=="disable":
            logger.info("Disabling Discharge")
            from write import ssc
            result=GivQueue.q.enqueue(ssc,100,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        temp['result']="Setting Discharge Enable was a success"

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
            #client.enable_discharge()
        elif payload['state']=="disable":
            logger.info("Disabling Discharge Schedule")
            from write import dd
            result=GivQueue.q.enqueue(dd,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            #client.disable_discharge()
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
        from write import ssc
        result=GivQueue.q.enqueue(ssc,int(payload['val']),retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        #client.set_shallow_charge(int(payload['val']))
        temp['result']="Setting Shallow Charge was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
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
        #client.enable_charge_target(target)
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
        from write import ssc
        result=GivQueue.q.enqueue(ssc,target,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        #client.set_shallow_charge(target)
        logger.debug("Setting Battery Reserve to: "+str(target)+" was a success")        
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
        from write import sbpr
        result=GivQueue.q.enqueue(sbpr,target,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        #client.set_battery_power_reserve(target)
        temp['result']="Setting Battery Cutoff was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Battery Cutoff failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def rebootinvertor():
    temp={}
    try:
        logger.info("Rebooting Invertor...")
        from write import ri
        result=GivQueue.q.enqueue(ri,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        #client.reboot_invertor()
        temp['result']="Rebooting invertor was a success"
    except:
        e = sys.exc_info()
        temp['result']="Reboot Invertor failed: " + str(e)
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
        #client.set_active_power_rate(target)
        temp['result']="Setting Active Power Rate was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Active Power Rate failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeRate(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)

    # Get invertor max bat power
    if exists(GivLUT.regcache):      # if there is a cache then grab it
        with open(GivLUT.regcache, 'rb') as inp:
            regCacheStack = pickle.load(inp)
            multi_output_old = regCacheStack[4]
        invmaxrate=multi_output_old['Invertor_Details']['Invertor_Max_Rate']
        batcap=float(multi_output_old['Invertor_Details']['Battery_Capacity_kWh'])*1000

        if int(payload['chargeRate']) < int(invmaxrate):
            target=int(min((int(payload['chargeRate'])/(batcap/2))*50,50))
        else:
            target=50
        logger.info ("Setting battery charge rate to: " + str(payload['chargeRate'])+" ("+str(target)+")")
        try:
            from write import sbcl
            result=GivQueue.q.enqueue(sbcl,target,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            #client.set_battery_charge_limit(target)
            temp['result']="Setting Charge Rate was a success"

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
        invmaxrate=multi_output_old['Invertor_Details']['Invertor_Max_Rate']
        batcap=float(multi_output_old['Invertor_Details']['Battery_Capacity_kWh'])*1000

        if int(payload['dischargeRate']) < int(invmaxrate):
            target=int(min((int(payload['dischargeRate'])/(batcap/2))*50,50))
        else:
            target=50
        logger.info ("Setting battery discharge rate to: " + str(payload['dischargeRate'])+" ("+str(target)+")")
        try:
            from write import sbdl
            result=GivQueue.q.enqueue(sbdl,target,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            #client.set_battery_discharge_limit(target)
            temp['result']="Setting Discharge Rate was a success"
            logger.info(temp['result'])
        except:
            e = sys.exc_info()
            temp['result']="Setting Discharge Rate failed: " + str(e)
            logger.error (temp['result'])
    else:
        temp['result']="Setting Discharge Rate failed: No discharge rate limit available"
        logger.error (temp['result'])        
    return json.dumps(temp)

def setChargeSlot1(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    if 'chargeToPercent' in payload.keys():
        target=int(payload['chargeToPercent'])
        from write import sct
        result=GivQueue.q.enqueue(sct,target,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    try:
        logger.info("Setting Charge Slot 1 to: "+str(payload['start'])+" - "+str(payload['finish']))
        from write import scs1
        result=GivQueue.q.enqueue(scs1,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        temp['result']="Setting Charge Slot 1 was a success"
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot 1 failed: " + str(e)
        logger.error (temp['result'])
    
    return json.dumps(temp)

def setChargeSlotStart1(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Charge Slot 1 Start to: "+str(payload['start']))
        from write import scss1
        result=GivQueue.q.enqueue(scss1,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        temp['result']="Setting Charge Slot Start 1 was a success"
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot 1 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeSlotEnd1(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Charge Slot End 1 to: "+str(payload['finish']))
        from write import scse1
        result=GivQueue.q.enqueue(scse1,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        temp['result']="Setting Charge Slot End 1 was a success"
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot 1 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeSlot2(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    if 'chargeToPercent' in payload.keys():
        target=int(payload['chargeToPercent'])
        from write import sct
        result=GivQueue.q.enqueue(sct,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    try:
        logger.info("Setting Charge Slot 2 to: "+str(payload['start'])+" - "+str(payload['finish']))
        from write import scs2
        result=GivQueue.q.enqueue(scs2,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        temp['result']="Setting Charge Slot 2 was a success"
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeSlotStart2(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Charge Slot 2 Start to: "+str(payload['start']))
        from write import scss2
        result=GivQueue.q.enqueue(scss2,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        temp['result']="Setting Charge Slot Start 2 was a success"
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeSlotEnd2(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Charge Slot End 2 to: "+str(payload['finish']))
        from write import scse2
        result=GivQueue.q.enqueue(scse2,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        temp['result']="Setting Charge Slot End 2 was a success"
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDischargeSlot1(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    if 'dischargeToPercent' in payload.keys():
        #from write import writeHelpers
        #result=GivQueue.q.enqueue(setBatteryReserve,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        result=setBatteryReserve(payload)
    try:
        strt=datetime.strptime(payload['start'],"%H:%M")
        fnsh=datetime.strptime(payload['finish'],"%H:%M")
        logger.info("Setting Discharge Slot 1 to: "+str(payload['start'])+" - "+str(payload['finish']))
        from write import sds1
        result=GivQueue.q.enqueue(sds1,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        temp['result']="Setting Discharge Slot 1 was a success"
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 1 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDischargeSlotStart1(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Discharge Slot 1 Start to: "+str(payload['start']))
        from write import sdss1
        result=GivQueue.q.enqueue(sdss1,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        temp['result']="Setting Discharge Slot Start 1 was a success"
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 1 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDischargeSlotEnd1(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Discharge Slot End 1 to: "+str(payload['finish']))
        from write import sdse1
        result=GivQueue.q.enqueue(sdse1,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        temp['result']="Setting Discharge Slot End 1 was a success"
        logger.info(temp['result'])
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
        #from write import writeHelpers
        #result=GivQueue.q.enqueue(setBatteryReserve,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        result=setBatteryReserve(payload)
    try:
        logger.info("Setting Discharge Slot 2 to: "+str(payload['start'])+" - "+str(payload['finish']))
        from write import sds2
        result=GivQueue.q.enqueue(sds2,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        temp['result']="Setting Discharge Slot 2 was a success"
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDischargeSlotStart2(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Discharge Slot 2 Start to: "+str(payload['start']))
        from write import sdss2
        result=GivQueue.q.enqueue(sdss2,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        temp['result']="Setting Discharge Slot Start 2 was a success"
        logger.info(temp['result'])
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDischargeSlotEnd2(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        logger.info("Setting Discharge Slot End 2 to: "+str(payload['finish']))
        from write import sdse2
        result=GivQueue.q.enqueue(sdse2,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        temp['result']="Setting Discharge Slot End 2 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def FEResume(revert):
    payload={}
    logger.info("Reverting Force Export settings:")   
    payload['dischargeRate']=revert["dischargeRate"]
    #from write import setDischargeRate
    #GivQueue.q.enqueue(setDischargeRate,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    result=setDischargeRate(payload)
    payload={}
    payload['start']=revert["start_time"]
    payload['finish']=revert["end_time"]
    #from write import setDischargeSlot2
    #GivQueue.q.enqueue(setDischargeSlot2,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    result=setDischargeSlot2(payload)
    payoad={}
    payload['state']=revert['discharge_schedule']
    #from write import enableDischargeSchedule
    #GivQueue.q.enqueue(enableDischargeSchedule,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    result=enableDischargeSchedule(payload)
    payload={}
    payload['reservePercent']=revert["reservePercent"]
    #from write import setBatteryReserve
    #GivQueue.q.enqueue(setBatteryReserve,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    result=setBatteryReserve(payload)
    payload={}
    payload["mode"]=revert["mode"]
    #from write import setBatteryMode
    #GivQueue.q.enqueue(setBatteryMode,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    result=setBatteryMode(payload)
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
            revert["start_time"]=regCacheStack[4]["Timeslots"]["Discharge_start_time_slot_2"][:5]
            revert["end_time"]=regCacheStack[4]["Timeslots"]["Discharge_end_time_slot_2"][:5]
            revert["reservePercent"]=regCacheStack[4]["Control"]["Battery_Power_Reserve"]
            revert["mode"]=regCacheStack[4]["Control"]["Mode"]
            revert['discharge_schedule']=regCacheStack[4]["Control"]["Enable_Discharge_Schedule"]
        maxDischargeRate=int(regCacheStack[4]["Invertor_Details"]["Invertor_Max_Rate"])
        
        #In case somebody has set a high reserve value set the reserve rate to the default value to allow the battery to discharge
        try:
            payload={}
            payload['reservePercent']=4
            #from write import setBatteryReserve
            #result=GivQueue.q.enqueue(setBatteryReserve,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))    
            result=setBatteryReserve(payload) 
        except:
            logger.debug("Error Setting Reserve to 4%")

        #set slot2 to calc times and keep slot 1 as is
#        slot1=(datetime.strptime(regCacheStack[4]["Timeslots"]["Discharge_start_time_slot_1"][:5],"%H:%M"),datetime.strptime(regCacheStack[4]["Timeslots"]["Discharge_end_time_slot_1"][:5],"%H:%M")) 
        slot2=(datetime.now(),datetime.now()+timedelta(minutes=exportTime))
        logger.debug("Setting export slot to: "+ slot2[0].strftime("%H:%M")+" - "+slot2[1].strftime("%H:%M"))       
#        result= client.set_mode_storage(slot1,slot2,export=True)
        
        payload={}
        payload['start']=slot2[0].strftime("%H:%M")
        payload['finish']=slot2[1].strftime("%H:%M")
        #from write import setDischargeSlot2
        #result=GivQueue.q.enqueue(setDischargeSlot2,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        result=setDischargeSlot2(payload)
        payload={}
        payload['mode']="Timed Export"
        #from write import setBatteryMode
        #result=GivQueue.q.enqueue(setBatteryMode,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        result=setBatteryMode(payload)
        payload={}
        logger.debug("Max discharge rate for inverter is: " + str(maxDischargeRate))
        payload['dischargeRate']=maxDischargeRate
        #from write import setDischargeRate
        #result=GivQueue.q.enqueue(setDischargeRate,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        result=setDischargeRate(payload)
        payload={}
        payload['state']="enable"
        #from write import enableDischargeSchedule
        #result=GivQueue.q.enqueue(enableDischargeSchedule,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        result=enableDischargeSchedule(payload)
        if exists(".FERunning"):    # If a forcecharge is already running, change time of revert job to new end time
            logger.info("Force Export already running, changing end time")
            revert=getFEArgs()[0]   # set new revert object and cancel old revert job
        fejob=GivQueue.q.enqueue_in(timedelta(minutes=exportTime),FEResume,revert)
        f=open(".FERunning", 'w')
        f.write(str(fejob.id))
        f.close()
        logger.debug("Force Export revert jobid is: "+fejob.id)
        temp['result']="Export successfully forced for "+str(exportTime)+" minutes"
    except:
        e = sys.exc_info()
        temp['result']="Force Export failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def FCResume(revert):
    payload={}
    logger.info("Reverting Force Charge Settings:")
    payload['chargeRate']=revert["chargeRate"]
    #from write import setChargeRate
    #GivQueue.q.enqueue(setChargeRate,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    setChargeRate(payload)
    payload={}
    payload['state']=revert["chargeScheduleEnable"]
    #from write import enableChargeSchedule
    #GivQueue.q.enqueue(enableChargeSchedule,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    enableChargeSchedule(payload)
    payload={}
    payload['start']=revert["start_time"]
    payload['finish']=revert["end_time"]
    payload['chargeToPercent']=revert["targetSOC"]
    #from write import setChargeSlot1
    #GivQueue.q.enqueue(setChargeSlot1,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    setChargeSlot1(payload)
    os.remove(".FCRunning")

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
            maxChargeRate=int(regCacheStack[4]["Invertor_Details"]["Invertor_Max_Rate"])

        payload['chargeRate']=maxChargeRate
        #from write import setChargeRate
        #result=GivQueue.q.enqueue(setChargeRate,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        result=setChargeRate(payload)
        payload={}
        payload['state']="enable"
        #from write import enableChargeSchedule
        #result=GivQueue.q.enqueue(enableChargeSchedule,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        result=enableChargeSchedule(payload)
        payload={}
        payload['start']=GivLUT.getTime(datetime.now())
        payload['finish']=GivLUT.getTime(datetime.now()+timedelta(minutes=chargeTime))
        payload['chargeToPercent']=100
        #from write import setChargeSlot1
        #result=GivQueue.q.enqueue(setChargeSlot1,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        result=setChargeSlot1(payload)
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
    except:
        e = sys.exc_info()
        temp['result']="Force charge failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def tmpPDResume(payload):
    #from write import setDischargeRate
    #result=GivQueue.q.enqueue(setDischargeRate,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
    result=setDischargeRate(payload)
    #result=setDischargeRate(payload)
    logger.info("Discharge Rate restored to: "+str(payload["dischargeRate"]))
    if exists(".tpdRunning"): os.remove(".tpdRunning")

def tempPauseDischarge(pauseTime):
    temp={}
    try:
        pauseTime=int(pauseTime)
        payload={}
        result={}
        payload['dischargeRate']=0
        #from write import setDischargeRate
        #result=GivQueue.q.enqueue(setDischargeRate,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        result=setDischargeRate(payload)
        logger.info("Pausing Discharge for "+str(pauseTime)+" minutes")
        #Update read data via pickle
        if exists(GivLUT.regcache):      # if there is a cache then grab it
            with open(GivLUT.regcache, 'rb') as inp:
                regCacheStack= pickle.load(inp)
            revertRate=regCacheStack[4]["Control"]["Battery_Discharge_Rate"]

#### CHECK CHECK output from enqueue result
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
    #from write import setChargeRate
    #result=GivQueue.q.enqueue(setChargeRate,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
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
        #from write import setChargeRate
        #result=GivQueue.q.enqueue(setChargeRate,payload,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        result=setChargeRate(payload)
        logger.debug(result)
        #Update read data via pickle
        if exists(GivLUT.regcache):      # if there is a cache then grab it
            with open(GivLUT.regcache, 'rb') as inp:
                regCacheStack= pickle.load(inp)
        revertRate=regCacheStack[4]["Control"]["Battery_Charge_Rate"]

#### CHECK CHECK output from enqueue result
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
    #Update read data via pickle
    if exists(GivLUT.regcache):      # if there is a cache then grab it
        with open(GivLUT.regcache, 'rb') as inp:
            regCacheStack= pickle.load(inp)
    
    logger.debug("Current battery mode from pickle is: " + str(regCacheStack[4]["Control"]["Mode"] ))     
    
    try:
        if payload['mode']=="Eco":
            from write import smd
            result=GivQueue.q.enqueue(smd,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            #client.set_mode_dynamic()
            #time.sleep(1)
            from write import ssc
            saved_battery_reserve = getSavedBatteryReservePercentage()
            result=GivQueue.q.enqueue(ssc,saved_battery_reserve,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            #client.set_shallow_charge(getSavedBatteryReservePercentage())
        elif payload['mode']=="Eco (Paused)":
            from write import smd
            result=GivQueue.q.enqueue(smd,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            #client.set_mode_dynamic()
            #time.sleep(1)
            from write import ssc
            result=GivQueue.q.enqueue(ssc,100,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            #client.set_shallow_charge(100)
        elif payload['mode']=="Timed Demand":
            from write import sbdmd, ed
            result=GivQueue.q.enqueue(sbdmd,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            result=GivQueue.q.enqueue(ed,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            
            #client.set_battery_discharge_mode_demand()
            #client.enable_discharge()
#            if exists(GivLUT.regcache):      # if there is a cache then grab it
#                with open(GivLUT.regcache, 'rb') as inp:
#                    regCacheStack= pickle.load(inp)
#                    slot1=(datetime.strptime(regCacheStack[4]["Timeslots"]["Discharge_start_time_slot_1"][:5],"%H:%M"),datetime.strptime(regCacheStack[4]["Timeslots"]["Discharge_end_time_slot_1"][:5],"%H:%M")) 
#                    client.set_mode_storage(slot1)
#                    # If the invertor is AC then turn Enable Discharge on
#                    if "AC" in str(regCacheStack[4]["Invertor_Details"]["Invertor_Type"]):
#                        client.enable_discharge()
#            else:
#                client.set_mode_storage()
        elif payload['mode']=="Timed Export":
            from write import sbdmmp,ed
            result=GivQueue.q.enqueue(sbdmmp,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
            result=GivQueue.q.enqueue(ed,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
#            client.set_battery_discharge_mode_max_power()
#            client.enable_discharge()
#            if exists(GivLUT.regcache):      # if there is a cache then grab it
#                with open(GivLUT.regcache, 'rb') as inp:
#                    regCacheStack= pickle.load(inp)
#                    slot1=(datetime.strptime(regCacheStack[4]["Timeslots"]["Discharge_start_time_slot_1"][:5],"%H:%M"),datetime.strptime(regCacheStack[4]["Timeslots"]["Discharge_end_time_slot_1"][:5],"%H:%M")) 
#                    client.set_mode_storage(slot1,export=True)
#            else:
#                client.set_mode_storage(export=True)
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
        from write import sdt
        result=GivQueue.q.enqueue(sdt,iDateTime,retry=Retry(max=GiV_Settings.queue_retries, interval=2))
        #client.set_datetime(iDateTime)
        temp['result']="Invertor time setting was a success"

    except:
        e = sys.exc_info()
        temp['result']="Setting Invertor DateTime failed: " + str(e) 
        logger.error (temp['result'])
    return json.dumps(temp)

def switchRate(payload):
    temp={}
    if GiV_Settings.dynamic_tariff == False:     # Only allow this control if Dynamic control is enabled
        temp['result']="External rate setting not allowed. Enale Dynamic Tariff in settings"
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

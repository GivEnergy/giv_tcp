# -*- coding: utf-8 -*-
# version 2022.01.31
import sys
import json
import logging
from datetime import datetime
from settings import GiV_Settings
from givenergy_modbus.client import GivEnergyClient

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


def enableChargeTarget(payload):
    temp={}
    try:
        if payload['state']=="enable":
            GivEnergyClient(host=GiV_Settings.invertorIP).enable_charge_target()
        elif payload['state']=="disable":
            GivEnergyClient(host=GiV_Settings.invertorIP).disable_charge_target()
        temp['result']="Setting Charge Target was a success"
        open(".forceFullRefresh", 'w').close()
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Target failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def enableChargeSchedule(payload):
    temp={}
    try:
        if payload['state']=="enable":
            GivEnergyClient(host=GiV_Settings.invertorIP).enable_charge()
        elif payload['state']=="disable":
            GivEnergyClient(host=GiV_Settings.invertorIP).disable_charge()
        temp['result']="Setting Charge Enable was a success"
        open(".forceFullRefresh", 'w').close()
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def enableDischargeSchedule(payload):
    temp={}
    try:
        if payload['state']=="enable":
            GivEnergyClient(host=GiV_Settings.invertorIP).enable_discharge()
        elif payload['state']=="disable":
            GivEnergyClient(host=GiV_Settings.invertorIP).disable_discharge()
        temp['result']="Setting Charge Enable was a success"
        open(".forceFullRefresh", 'w').close()
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setShallowCharge(payload):
    temp={}
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).set_shallow_charge(int(payload['val']))
        temp['result']="Setting Charge Enable was a success"
        open(".forceFullRefresh", 'w').close()
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def enableDischarge(payload):
    temp={}
    try:
        if payload['state']=="enable":
            GivEnergyClient(host=GiV_Settings.invertorIP).set_shallow_charge(4)
        elif payload['state']=="disable":
            GivEnergyClient(host=GiV_Settings.invertorIP).set_shallow_charge(100)
        temp['result']="Setting Discharge Enable was a success"
        open(".forceFullRefresh", 'w').close()
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Enable failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeTarget(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    target=int(payload['chargeToPercent'])
    try:
        client=GivEnergyClient(host=GiV_Settings.invertorIP)
        client.enable_charge_target(target)
        temp['result']="Setting Charge Target was a success"
        open(".forceFullRefresh", 'w').close()
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Target failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setBatteryReserve(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    target=int(payload['dischargeToPercent'])
    #Only allow minimum of 4%
    if target<4: target=4
    logger.info ("Setting battery reserve target to: " + str(target))
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).set_battery_power_reserve(target)
        temp['result']="Setting Battery Reserve was a success"
        open(".forceFullRefresh", 'w').close()
    except:
        e = sys.exc_info()
        temp['result']="Setting Battery Reserve failed: " + str(e)
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
    logger.info ("Setting battery charge rate to: " + str(target))
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).set_battery_charge_limit(target)
        temp['result']="Setting Charge Rate was a success"
        open(".forceFullRefresh", 'w').close()
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
    logger.info ("Setting battery discharge rate to: " + str(target))
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).set_battery_discharge_limit(target)
        temp['result']="Setting Discharge Rate was a success"
        open(".forceFullRefresh", 'w').close()
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Rate failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)


def setChargeSlot1(payload):
    temp={}
    targetresult="Success"
    wintermoderesult="Success"
    if type(payload) is not dict: payload=json.loads(payload)
    if 'chargeToPercent' in payload.keys():
        targetresult=setChargeTarget(payload)
    client=GivEnergyClient(host=GiV_Settings.invertorIP)
    try:
        client.set_charge_slot_1((datetime.strptime(payload['start'],"%H:%M"),datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Charge Slot 1 was a success"
        open(".forceFullRefresh", 'w').close()
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot 1 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setChargeSlot2(payload):
    temp={}
    targetresult="Success"
    wintermoderesult="Success"
    if type(payload) is not dict: payload=json.loads(payload)
    if 'chargeToPercent' in payload.keys():
        targetresult=setChargeTarget(payload)
    client=GivEnergyClient(host=GiV_Settings.invertorIP)
    try:
        client.set_charge_slot_2((datetime.strptime(payload['start'],"%H:%M"),datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Charge Slot 2 was a success"
        open(".forceFullRefresh", 'w').close()
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDischargeSlot1(payload):
    temp={}
    targetresult="Success"
    wintermoderesult="Success"
    if type(payload) is not dict: payload=json.loads(payload)
    if 'dischargeToPercent' in payload.keys():
        targetresult=setBatteryReserve(payload)
    client=GivEnergyClient(host=GiV_Settings.invertorIP)
    try:
        client.set_discharge_slot_1((datetime.strptime(payload['start'],"%H:%M"),datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Discharge Slot 1 was a success"
        open(".forceFullRefresh", 'w').close()
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 1 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)

def setDischargeSlot2(payload):
    temp={}
    targetresult="Success"
    wintermoderesult="Success"
    if type(payload) is not dict: payload=json.loads(payload)
    if 'dischargeToPercent' in payload.keys():
        targetresult=setBatteryReserve(payload)
    client=GivEnergyClient(host=GiV_Settings.invertorIP)
    try:
        client.set_discharge_slot_2((datetime.strptime(payload['start'],"%H:%M"),datetime.strptime(payload['finish'],"%H:%M")))
        temp['result']="Setting Discharge Slot 2 was a success"
        open(".forceFullRefresh", 'w').close()
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 2 failed: " + str(e)
        logger.error (temp['result'])
    return json.dumps(temp)


def setBatteryMode(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    try:
        if payload['mode']=="Eco":
            client=GivEnergyClient(host=GiV_Settings.invertorIP).set_mode_dynamic()
        if payload['mode']=="Eco (Paused)":
            client=GivEnergyClient(host=GiV_Settings.invertorIP).set_mode_dynamic()
            client=GivEnergyClient(host=GiV_Settings.invertorIP).set_shallow_charge(100)
        
        elif payload['mode']=="Timed Demand":
            client=GivEnergyClient(host=GiV_Settings.invertorIP).set_mode_storage()
        elif payload['mode']=="Timed Export":
            client=GivEnergyClient(host=GiV_Settings.invertorIP).set_mode_storage(export=True)
        else:
            logger.info ("Invalid Mode requested: "+ payload['mode'])
            temp['result']="Invalid Mode requested"
            return json.dumps(temp)
        temp['result']="Setting Battery Mode was a success"
        open(".forceFullRefresh", 'w').close()
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
        #Set Date and Time on Invertor
        GivEnergyClient(host=GiV_Settings.invertorIP).set_datetime(iDateTime)
        temp['result']="Invertor time setting was a success"
        open(".forceFullRefresh", 'w').close()
    except:
        e = sys.exc_info()
        temp['result']="Setting Battery Mode failed: " + str(e) 
        logger.error (temp['result'])
    return json.dumps(temp)

if __name__ == '__main__':
    if len(sys.argv)==2:
        globals()[sys.argv[1]]()
    elif len(sys.argv)==3:
        globals()[sys.argv[1]](sys.argv[2])

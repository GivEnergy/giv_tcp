# -*- coding: utf-8 -*-
# version 2021.12.22
import sys
import json

from paho.mqtt.client import Client
from GivTCP import GivTCP
from datetime import datetime
from settings import GiV_Settings
from datetime import date
from givenergy_modbus.client import GivEnergyClient
from givenergy_modbus.model.register import HoldingRegister, InputRegister

def disableChargeTarget():
    temp={}
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).disable_charge_target
        temp['result']="Pausing Charge Schedule was a success"
    except:
        e = sys.exc_info()
        temp['result']="Pausing Charge Schedule failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def enableChargeTarget():
    temp={}
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).enable_charge_target
        temp['result']="Resuming Charge Schedule was a success"
    except:
        e = sys.exc_info()
        temp['result']="Pausing Charge Schedule failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def pauseChargeSchedule():
    temp={}
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).disable_charge
        temp['result']="Pausing Charge Schedule was a success"
    except:
        e = sys.exc_info()
        temp['result']="Pausing Charge Schedule failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def resumeChargeSchedule():
    temp={}
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).enable_charge
        temp['result']="Resuming Charge Schedule was a success"
    except:
        e = sys.exc_info()
        temp['result']="Resuming Charge Schedule failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def pauseDischargeSchedule():
    temp={}
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).enable_discharge
        temp['result']="Pausing Discharge Schedule was a success"
    except:
        e = sys.exc_info()
        temp['result']="Pausing Discharge Schedule failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def resumeDischargeSchedule():
    temp={}
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).disable_discharge
        temp['result']="Resuming Discharge Schedule was a success"
    except:
        e = sys.exc_info()
        temp['result']="Resuming Discharge Schedule failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def pauseBatteryCharge():
    temp={}
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).set_battery_charge_limit(0)
        temp['result']="Pausing Charge was a success"
    except:
        e = sys.exc_info()
        temp['result']="Pausing Charge failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def resumeBatteryCharge():
    temp={}
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).set_battery_charge_limit(50)
        temp['result']="Resuming Charge was a success"
    except:
        e = sys.exc_info()
        temp['result']="Resuming Charge failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def pauseBatteryDischarge():
    temp={}
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).set_battery_discharge_limit(0)
        temp['result']="Pausing Discharge was a success"
    except:
        e = sys.exc_info()
        temp['result']="Pausing Discharge failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def resumeBatteryDischarge():
    temp={}
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).set_battery_discharge_limit(50)
        temp['result']="Resuming Discharge was a success"
    except:
        e = sys.exc_info()
        temp['result']="Resuming Discharge failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def setChargeTarget(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    target=payload['chargeToPercent']
    try:
        client=GivEnergyClient(host=GiV_Settings.invertorIP)
        client.set_battery_target_soc(target)
        if target == 100:
            client.enable_charge_target
        else:
            client.disable_charge_target
        temp['result']="Setting Charge Target was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Target failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def setBatteryReserve(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    target=payload['dischargeToPercent']
    #Only allow minimum of 2%
    if int(target)<4: target="4"
    GivTCP.debug ("Setting battery reserve target to: " + target)
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).set_battery_power_reserve(target)
        temp['result']="Setting Battery Reserve was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Battery Reserve failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def setChargeRate(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    target=payload['chargeRate']
    #Only allow max of 100%
    target=int(target)/2
    if target>100: target="100"
    GivTCP.debug ("Setting battery charge rate to: " + str(target))
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).set_battery_charge_limit(target)
        temp['result']="Setting Charge Rate was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Rate failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)


def setDischargeRate(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    target=payload['dischargeRate']
    #Only allow max of 100%
    target=int(target)/2
    if target>100: target="100"
    GivTCP.debug ("Setting battery discharge rate to: " + str(target))
    try:
        GivEnergyClient(host=GiV_Settings.invertorIP).set_battery_discharge_limit(target)
        temp['result']="Setting Discharge Rate was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Rate failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)


def setChargeSlot1(payload):
    temp={}
    targetresult="Success"
    wintermoderesult="Success"
    if type(payload) is not dict: payload=json.loads(payload)
    start=payload['start']
    end=payload['finish']
    if 'chargeToPercent' in payload.keys():
        targetresult=setChargeTarget(payload)
    client=GivEnergyClient(host=GiV_Settings.invertorIP)
    try:
        client.enable_charge
        client.set_charge_slot_1(datetime.strptime(start,"%H:%M"),datetime.strptime(end,"%H:%M"))
        temp['result']="Setting Charge Slot 1 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot 1 failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def setChargeSlot2(payload):
    temp={}
    targetresult="Success"
    wintermoderesult="Success"
    if type(payload) is not dict: payload=json.loads(payload)
    start=payload['start']
    end=payload['finish']
    if 'chargeToPercent' in payload.keys():
        targetresult=setChargeTarget(payload)
    client=GivEnergyClient(host=GiV_Settings.invertorIP)
    try:
        client.enable_charge
        client.set_charge_slot_2(datetime.strptime(start,"%H:%M"),datetime.strptime(end,"%H:%M"))
        temp['result']="Setting Charge Slot 2 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Charge Slot 2 failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def setDischargeSlot1(payload):
    temp={}
    targetresult="Success"
    wintermoderesult="Success"
    if type(payload) is not dict: payload=json.loads(payload)
    start=payload['start']
    end=payload['finish']
    if 'dischargeToPercent' in payload.keys():
        targetresult=setBatteryReserve(payload)
    client=GivEnergyClient(host=GiV_Settings.invertorIP)
    try:
        client.set_discharge_slot_1(datetime.strptime(start,"%H:%M"),datetime.strptime(end,"%H:%M"))
        client.enable_discharge
        temp['result']="Setting Discharge Slot 1 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 1 failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

def setDischargeSlot2(payload):
    temp={}
    targetresult="Success"
    wintermoderesult="Success"
    if type(payload) is not dict: payload=json.loads(payload)
    start=payload['start']
    end=payload['finish']
    if 'dischargeToPercent' in payload.keys():
        targetresult=setBatteryReserve(payload)
    client=GivEnergyClient(host=GiV_Settings.invertorIP)
    try:
        client.set_discharge_slot_2(datetime.strptime(start,"%H:%M"),datetime.strptime(end,"%H:%M"))
        client.enable_discharge
        temp['result']="Setting Discharge Slot 2 was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Discharge Slot 2 failed: " + str(e)
    GivTCP.debug (temp['result'])
    return json.dumps(temp)


def setBatteryMode(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    mode=int(payload['mode'])
    try:
        if mode==1:
            client=GivEnergyClient(host=GiV_Settings.invertorIP).set_mode_dynamic
        elif mode==2:
            client=GivEnergyClient(host=GiV_Settings.invertorIP).set_mode_storage
        elif mode==3:
            client=GivEnergyClient(host=GiV_Settings.invertorIP).set_mode_storage(export=True)
        elif mode==4:
            client=GivEnergyClient(host=GiV_Settings.invertorIP).set_mode_storage(export=True)
        else:
            GivTCP.debug ("Invalid Mode requested: "+ mode)
            temp['result']="Invalid Mode requested"
            return json.dumps(temp)
        temp['result']="Setting Battery Mode was a success"
    except:
        e = sys.exc_info()
        temp['result']="Setting Battery Mode failed: " + str(e)
    GivTCP.debug (temp['result'])
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
    except:
        e = sys.exc_info()
        temp['result']="Setting Battery Mode failed: " + str(e) 
    GivTCP.debug (temp['result'])
    return json.dumps(temp)

if __name__ == '__main__':
    if len(sys.argv)==2:
        globals()[sys.argv[1]]()
    elif len(sys.argv)==3:
        globals()[sys.argv[1]](sys.argv[2])

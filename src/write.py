# -*- coding: utf-8 -*-
import sys
import json
from GivTCP import GivTCP
from GivLUT import GiV_Reg_LUT
from datetime import datetime
from settings import GiV_Settings

def writeReg(payload):
    params=json.loads(payload)
    register=params['register']
    value=params['value']
    result=GivTCP.write_single_register(register,value)
    GivTCP.debug ("Writing Register "+ str(register) + " was a: "+result)

def disableACCharge():
    temp={}
    result=GivTCP.write_single_register(20,0)
    GivTCP.debug ("Pausing Charge Schedule was a: "+result)
    temp['result']="Pausing Charge Schedule was a: "+result
    return json.dumps(temp)

def enableACCharge():
    temp={}
    result=GivTCP.write_single_register(20,1)
    GivTCP.debug ("Resuming Charge Schedule was a: "+ result)
    temp['result']="Resuming Charge Schedule was a: "+ result
    return json.dumps(temp)

def pauseChargeSchedule():
    temp={}
    result=GivTCP.write_single_register(96,0)
    GivTCP.debug ("Pausing Charge Schedule was a: "+result)
    temp['result']="Pausing Charge Schedule was a: "+result
    return json.dumps(temp)

def resumeChargeSchedule():
    temp={}
    result=GivTCP.write_single_register(96,1)
    GivTCP.debug ("Resuming Charge Schedule was a: "+ result)
    temp['result']="Resuming Charge Schedule was a: "+ result
    return json.dumps(temp)

def pauseDischargeSchedule():
    temp={}
    result=GivTCP.write_single_register(59,0)
    GivTCP.debug ("Pausing Discharge Schedule was a: " + result)
    temp['result']="Pausing Discharge Schedule was a: " + result
    return json.dumps(temp)

def resumeDischargeSchedule():
    temp={}
    result=GivTCP.write_single_register(59,1)
    GivTCP.debug ("Resuming Discharge Schedule was a: " + result)
    temp['result']="Resuming Discharge Schedule was a: " + result
    return json.dumps(temp)

def setChargeTarget(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    target=payload['chargeToPercent']
    targetresult=GivTCP.write_single_register(116,target)
    GivTCP.debug ("Setting charge target was a: " + targetresult)
    temp['result']="Setting charge target was a: " + targetresult
    return json.dumps(temp)

def setBatteryReserve(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    params=json.loads(payload)
    target=payload['dischargeToPercent']
    #Only allow minimum of 2%
    if int(target)<4: target="4"
    targetresult=GivTCP.write_single_register(114,target)
    GivTCP.debug ("Battery Reserve setting was a: " + targetresult)
    temp['result']="Battery Reserve setting was a: " + targetresult
    return json.dumps(temp)

def setChargeSlot1(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    start=payload['start']
    end=payload['finish']
    target=payload['chargeToPercent']
    startresult=GivTCP.write_single_register(94,start)
    endresult=GivTCP.write_single_register(95,end)
    targetresult=GivTCP.write_single_register(116,target)
    enableresult=GivTCP.write_single_register(96,1)     #enable charge flag automatically
    if startresult=="Success" and endresult=="Success" and targetresult=="Success" and enableresult=="Success":
        GivTCP.debug ("Charge Time successfully set")
        temp['result']="Charge Time successfully set"
    else:
        GivTCP.debug ("Error setting Charge time")
        temp['result']="Error setting Charge time"
    return json.dumps(temp)

def setChargeSlot2(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    start=payload['start']
    end=payload['finish']
    target=payload['chargeToPercent']
    startresult=GivTCP.write_single_register(31,start)
    endresult=GivTCP.write_single_register(32,end)
    targetresult=GivTCP.write_single_register(116,target)
    enableresult=GivTCP.write_single_register(96,1)     #enable charge flag automatically
    if startresult=="Success" and endresult=="Success" and targetresult=="Success" and enableresult=="Success":
        GivTCP.debug ("Charge Time successfully set")
        temp['result']="Charge Time successfully set"
    else:
        GivTCP.debug ("Error setting Charge time")
        temp['result']="Error setting Charge time"
    return json.dumps(temp)

def setDischargeSlot1(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    start=payload['start']
    end=payload['finish']
    target=payload['dischargeToPercent']
    startresult=GivTCP.write_single_register(56,start)
    endresult=GivTCP.write_single_register(57,end)
    targetresult=GivTCP.write_single_register(114,target)
    if startresult=="Success" and endresult=="Success" and targetresult=="Success":
        GivTCP.debug ("Disharge Time successfully set")
        temp['result']="Discharge Time successfully set"
    else:
        GivTCP.debug ("Error setting Discharge time")
        temp['result']="Error setting Discharge time"
    return json.dumps(temp)

def setDischargeSlot2(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    start=payload['start']
    end=payload['finish']
    target=payload['dischargeToPercent']
    startresult=GivTCP.write_single_register(44,start)
    endresult=GivTCP.write_single_register(45,end)
    targetresult=GivTCP.write_single_register(114,target)
    if startresult=="Success" and endresult=="Success" and targetresult=="Success":
        GivTCP.debug ("Disharge Time successfully set")
        temp['result']="Discharge Time successfully set"
    else:
        GivTCP.debug ("Error setting Discharge time")
        temp['result']="Error setting Discharge time"
    return json.dumps(temp)

def setBatteryMode(payload):
    temp={}
    if type(payload) is not dict: payload=json.loads(payload)
    mode=int(payload['mode'])
    if mode==1:
        shallowresult=GivTCP.write_single_register(110,4)
        dischargeresult=GivTCP.write_single_register(59,0)
        selfresult=GivTCP.write_single_register(27,1)
    elif mode==2:
        shallowresult=GivTCP.write_single_register(110,100)
        dischargeresult=GivTCP.write_single_register(59,1)
        selfresult=GivTCP.write_single_register(27,1)
        startresult=GivTCP.write_single_register(56,1600)
        endresult=GivTCP.write_single_register(57,700)
    elif mode==3:
        shallowresult=GivTCP.write_single_register(110,100)
        dischargeresult=GivTCP.write_single_register(59,1)
        selfresult=GivTCP.write_single_register(27,1)
    elif mode==4:
        shallowresult=GivTCP.write_single_register(110,4)
        dischargeresult=GivTCP.write_single_register(59,1)
        selfresult=GivTCP.write_single_register(27,0)
    else:
        GivTCP.debug ("Invalid Mode requested: "+ mode)
        temp['result']="Error setting Discharge time"
        return json.dumps(temp)
    #Calculate success
    if shallowresult=="Success" and dischargeresult=="Success" and selfresult=="Success":
        GivTCP.debug ("Control Mode successfully set")
        temp['result']="Control Mode successfully set"
    else:
        GivTCP.debug ("Error setting Control Mode")
        temp['result']="Error setting Control Mode"
    return json.dumps(temp)

if __name__ == '__main__':
    if len(sys.argv)==2:
        globals()[sys.argv[1]]()
    elif len(sys.argv)==3:
        globals()[sys.argv[1]](sys.argv[2])

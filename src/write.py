# -*- coding: utf-8 -*-
import sys
import json
from GivTCP import GivTCP
from GivLUT import GiV_Reg_LUT
from datetime import datetime
from settings import GiV_Settings
from read import giv_api


def writeReg(payload):
    params=json.loads(payload)
    register=params['register']
    value=params['value']
    result=GivTCP.write_single_register(register,value)
    GivTCP.debug ("Writing Register "+ str(register) + " was a: "+result)

@giv_api.route('/disableACCharge', methods=['GET'])
def disableACCharge():
    temp={}
    result=GivTCP.write_single_register(20,0)
    GivTCP.debug ("Pausing Charge Schedule was a: "+result)
    temp['result']="Pausing Charge Schedule was a: "+result
    return json.dumps(temp)

@giv_api.route('/enableACCharge', methods=['GET'])
def enableACCharge():
    temp={}
    result=GivTCP.write_single_register(20,1)
    GivTCP.debug ("Resuming Charge Schedule was a: "+ result)
    temp['result']="Resuming Charge Schedule was a: "+ result
    return json.dumps(temp)

@giv_api.route('/pauseChargeSchedule', methods=['GET'])
def pauseChargeSchedule():
    temp={}
    result=GivTCP.write_single_register(96,0)
    GivTCP.debug ("Pausing Charge Schedule was a: "+result)
    temp['result']="Pausing Charge Schedule was a: "+result
    return json.dumps(temp)

@giv_api.route('/resumeChargeSchedule', methods=['GET'])
def resumeChargeSchedule():
    temp={}
    result=GivTCP.write_single_register(96,1)
    GivTCP.debug ("Resuming Charge Schedule was a: "+ result)
    temp['result']="Resuming Charge Schedule was a: "+ result
    return json.dumps(temp)

@giv_api.route('/pauseDischargeSchedule', methods=['GET'])
def pauseDischargeSchedule():
    temp={}
    result=GivTCP.write_single_register(59,0)
    GivTCP.debug ("Pausing Discharge Schedule was a: " + result)
    temp['result']="Pausing Discharge Schedule was a: " + result
    return json.dumps(temp)

@giv_api.route('/resumeDischargeSchedule', methods=['GET'])
def resumeDischargeSchedule():
    temp={}
    result=GivTCP.write_single_register(59,1)
    GivTCP.debug ("Resuming Discharge Schedule was a: " + result)
    temp['result']="Resuming Discharge Schedule was a: " + result
    return json.dumps(temp)

@giv_api.route('/setChargeTarget', methods=['POST'])
def setChargeTarget():
    temp={}
    if payload=="":      #If no payload, assume its called via flask
        params = request.get_json(silent=True, force=True)
    else:
        params=json.loads(payload)
    target=params['chargeToPercent']
    targetresult=GivTCP.write_single_register(116,target)
    GivTCP.debug ("Setting charge target was a: " + targetresult)
    temp['result']="Setting charge target was a: " + targetresult
    return json.dumps(temp)

@giv_api.route('/setBatteryReserve/<payload>', methods=['GET'])
def setBatteryReserve(payload):
    temp={}
    params=request.get_json(force=True) 
    params=json.loads(payload)
    target=params['dischargeToPercent']
    #Only allow minimum of 2%
    if int(target)<4: target="4"
    targetresult=GivTCP.write_single_register(114,target)
    GivTCP.debug ("Battery Reserve setting was a: " + targetresult)
    temp['result']="Battery Reserve setting was a: " + targetresult
    return json.dumps(temp)

@giv_api.route('/setChargeSlot1/<payload>', methods=['GET'])
def setChargeSlot1(payload):
    temp={}
    params=json.loads(payload)
    start=params['start']
    end=params['finish']
    target=params['chargeToPercent']
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

@giv_api.route('/setChargeSlot2/<payload>', methods=['GET'])
def setChargeSlot2(payload):
    temp={}
    params=json.loads(payload)
    start=params['start']
    end=params['finish']
    target=params['chargeToPercent']
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

@giv_api.route('/setDischargeSlot1/<payload>', methods=['GET'])
def setDischargeSlot1(payload):
    temp={}
    params=json.loads(payload)
    start=params['start']
    end=params['finish']
    target=params['dischargeToPercent']
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

@giv_api.route('/setDischargeSlot2/<payload>', methods=['GET'])
def setDischargeSlot2(payload):
    temp={}
    params=json.loads(payload)
    start=params['start']
    end=params['finish']
    target=params['dischargeToPercent']
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

@giv_api.route('/setBatteryMode/<payload>', methods=['GET'])
def setBatteryMode(payload):
    temp={}
    params=json.loads(payload)
    mode=int(params['mode'])
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

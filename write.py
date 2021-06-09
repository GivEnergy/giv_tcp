# -*- coding: utf-8 -*-
import sys
import json
from GivTCP import GivTCP
from GivLUT import GiV_Reg_LUT
from datetime import datetime
from settings import GiV_Settings

Log_To_File=False
if GiV_Settings.Log_To_File=="True":          #if in debug mode write to log file
    Log_To_File=True
    f = open(GiV_Settings.Debug_File_Location + 'read_debug.log','a')
    sys.stdout = f

now = datetime.now()
print ("-----------------",now,"-----------------")

def pauseChargeSchedule():
    result=GivTCP.write_single_register(96,0)
    GivTCP.debug ("Pausing Charge Schedule was a: "+result)

def resumeChargeSchedule():
    result=GivTCP.write_single_register(96,1)
    GivTCP.debug ("Resuming Charge Schedule was a: "+ result)

def pauseDischargeSchedule():
    result=GivTCP.write_single_register(59,0)
    GivTCP.debug ("Pausing Discharge Schedule was a: " + result)

def resumeDischargeSchedule():
    result=GivTCP.write_single_register(59,1)
    GivTCP.debug ("Resuming Discharge Schedule was a: " + result)

def setChargeTarget(payload):
    params=json.loads(payload)
    target=params['chargeToPercent']
    targetresult=GivTCP.write_single_register(116,target)
    if targetresult=="Success":
        GivTCP.debug ("Charge Target successfully set")
    else:
        GivTCP.debug ("Error setting Charge Target")

def setBatteryReserve(payload):
    params=json.loads(payload)
    target=params['dischargeToPercent']
    targetresult=GivTCP.write_single_register(114,target)
    if targetresult=="Success":
        GivTCP.debug ("Battery Reserve successfully set")
    else:
        GivTCP.debug ("Error setting Battery Reserve")


def setChargeSlot1(payload):
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
    else:
        GivTCP.debug ("Error setting Charge time")

def setDischargeSlot1(payload):
    params=json.loads(payload)
    start=params['start']
    end=params['finish']
    target=params['dischargeToPercent']
    startresult=GivTCP.write_single_register(56,start)
    endresult=GivTCP.write_single_register(57,end)
    targetresult=GivTCP.write_single_register(114,target)
    if startresult=="Success" and endresult=="Success" and targetresult=="Success":
        GivTCP.debug ("Discharge Timeslot 1 successfully set")
    else:
        GivTCP.debug ("Error setting Discharge Timeslot 1")

def setDischargeSlot2(payload):
    params=json.loads(payload)
    start=params['start']
    end=params['finish']
    target=params['dischargeToPercent']
    startresult=GivTCP.write_single_register(44,start)
    endresult=GivTCP.write_single_register(45,end)
    targetresult=GivTCP.write_single_register(114,target)
    if startresult=="Success" and endresult=="Success" and targetresult=="Success":
        GivTCP.debug ("Disharge Timeslot 2 successfully set")
    else:
        GivTCP.debug ("Error setting Discharge Timeslot 2")

def setBatteryMode(payload):
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
        GivTCP.debug ("Invalid Mode: "+ mode)
        return
    #Calculate success
    if shallowresult=="Success" and dischargeresult=="Success" and selfresult=="Success":
        GivTCP.debug ("Control Mode successfully set")
    else:
        GivTCP.debug ("Error setting Control Mode")


if __name__ == '__main__':
    if len(sys.argv)==2:
        globals()[sys.argv[1]]()
    elif len(sys.argv)==3:
        globals()[sys.argv[1]](sys.argv[2])

# -*- coding: utf-8 -*-
import sys
import json
from GivTCP import GivTCP
from GivLUT import GiV_Reg_LUT

def setChargeEnable(payload):
    params=json.loads(payload)
    control=params['enable']
    if control=="False":
       val=0
    else:
       val=1
    result=GivTCP.write_single_register(96,val)
    print ("Setting Charge Enable to ",control," was: ",result)

def setDischargeEnable(payload):
    params=json.loads(payload)
    control=params['enable']
    if control=="False":
       val=0
    else:
       val=1
    result=GivTCP.write_single_register(59,val)
    print ("Setting Discharge Enable was: ",result)

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
        return ("Charge Time successfully set")
    else:
        return ("Error setting Charge time")

def setDishargeSlot1(payload):
    params=json.loads(payload)
    start=params['start']
    end=params['finish']
    target=params['dischargeToPercent']
    startresult=GivTCP.write_single_register(56,start)
    endresult=GivTCP.write_single_register(57,end)
    targetresult=GivTCP.write_single_register(114,target)
    if startresult=="Success" and endresult=="Success" and targetresult=="Success":
        return ("Charge enable successfully set")
    else:
        return ("Error setting Discharge Slot 1 times")

def setDishargeSlot2(payload):
    params=json.loads(payload)
    start=params['start']
    end=params['finish']
    target=params['dischargeToPercent']
    startresult=GivTCP.write_single_register(44,start)
    endresult=GivTCP.write_single_register(45,end)
    targetresult=GivTCP.write_single_register(114,end)
    if startresult=="Success" and endresult=="Success" and targetresult=="Success":
        return ("Disharge TImeslot 2 successfully set")
    else:
        return ("Error setting Discharge Slot 2 times")

def setBatteryMode(payload):
    params=json.loads(payload)
    mode=params['mode']
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
        print ("Invalid Mode: ",mode)
        return
    #Calculate success
    if shallowresult=="Success" and dischargeresult=="Success" and selfresult=="Success":
        print ("Control Mode successfully set")
    else:
        print ("Error setting Control Mode")


if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2])

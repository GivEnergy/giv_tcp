# -*- coding: utf-8 -*-
import socket
import sys
import codecs
from crccheck.crc import Crc16, CrcModbus
import subprocess
import re
import paho.mqtt.client as mqtt
import time
import json
from GivTCP import GivTCP
from GivLUT import GiV_Reg_LUT
# import schedule

def getTimeslots():
    timeslots={}

    #Grab Timeslots
    timeslots=GivTCP.read_register('44','03','02')
    timeslots.update(GivTCP.read_register('56','03','02'))
    timeslots.update(GivTCP.read_register('94','03','02'))
    if len(timeslots)!=0:
      GivTCP.publish_to_MQTT("Timeslots",timeslots)

def getCombinedStats():
    energy_output={}
    temp_output={}
    power_output={}
    PV_stats={}
    grid_power={}
    load_power={}
    battery_power={}
    SOC={}

    #Grab Energy data
    temp_output=GivTCP.read_register('0','04','60') #Get ALL input Registers

    if len(temp_output)==60:
        power_output['PV Power']= temp_output[GiV_Reg_LUT.input_register_LUT.get(18)[0]+"(18)"]+temp_output[GiV_Reg_LUT.input_register_LUT.get(20)[0]+"(20)"]

        temphex=str(temp_output[GiV_Reg_LUT.input_register_LUT.get(21)[0]+"(21)"])+str(temp_output[GiV_Reg_LUT.input_register_LUT.get(22)[0]+"(22)"])
        kwh_value=round(int(temphex,16) * GiV_Reg_LUT.input_register_LUT.get(21)[2],2)
        energy_output['Export Energy Total kwh']=kwh_value

        temphex=str(temp_output[GiV_Reg_LUT.input_register_LUT.get(27)[0]+"(27)"])+str(temp_output[GiV_Reg_LUT.input_register_LUT.get(28)[0]+"(28)"])
        kwh_value=round(int(temphex,16) * GiV_Reg_LUT.input_register_LUT.get(27)[2],2)
        energy_output['Load Energy Total kwh']=kwh_value

        temphex=str(temp_output[GiV_Reg_LUT.input_register_LUT.get(32)[0]+"(32)"])+str(temp_output[GiV_Reg_LUT.input_register_LUT.get(33)[0]+"(33)"])
        kwh_value=round(int(temphex,16) * GiV_Reg_LUT.input_register_LUT.get(32)[2],2)
        energy_output['Import Energy Total kwh']=kwh_value

        value= temp_output[GiV_Reg_LUT.input_register_LUT.get(30)[0]+"(30)"]
        if value<=0:
            import_power=abs(value)
            export_power=0
        elif value>=0:
            import_power=0
            export_power=abs(value)
        power_output['Grid Power']=value
        power_output['Import Power']=import_power
        power_output['Export Power']=export_power

        power_output['EPS Power']= temp_output[GiV_Reg_LUT.input_register_LUT.get(31)[0]+"(31)"]

        power_output['Load Power']= temp_output[GiV_Reg_LUT.input_register_LUT.get(42)[0]+"(42)"]
        temphex=str(temp_output[GiV_Reg_LUT.input_register_LUT.get(45)[0]+"(45)"])+str(temp_output[GiV_Reg_LUT.input_register_LUT.get(46)[0]+"(46)"])
        kwh_value=round(int(temphex,16) * GiV_Reg_LUT.input_register_LUT.get(45)[2],2)
        energy_output['INV OUT Energy Total kwh']=kwh_value

        value=temp_output[GiV_Reg_LUT.input_register_LUT.get(52)[0]+"(52)"]
        if value>=0:
            discharge_power=abs(value)
            charge_power=0
        elif value<=0:
            discharge_power=0
            charge_power=abs(value)
        power_output['Battery Power']=value
        power_output['Charge Power']=charge_power
        power_output['Discharge Power']=discharge_power

        power_output['SOC']=temp_output[GiV_Reg_LUT.input_register_LUT.get(59)[0]+"(59)"]
    if len(energy_output)!=0:
      GivTCP.publish_to_MQTT("Energy",energy_output)
    if len(power_output)!=0:
      GivTCP.publish_to_MQTT("Power",power_output)

def getModes():
    controls={}

    #Grab Modes
    shallow_charge=GivTCP.read_register('110','03','01')[GiV_Reg_LUT.holding_register_LUT.get(110)[0]+"(110)"]
    self_consumption=GivTCP.read_register('27','03','01')[GiV_Reg_LUT.holding_register_LUT.get(27)[0]+"(27)"]
    charge_enable=GivTCP.read_register('96','03','01')[GiV_Reg_LUT.holding_register_LUT.get(96)[0]+"(96)"]
    battery_reserve=GivTCP.read_register('114','03','01')[GiV_Reg_LUT.holding_register_LUT.get(114)[0]+"(114)"]
    target_soc=GivTCP.read_register('116','03','01')[GiV_Reg_LUT.holding_register_LUT.get(116)[0]+"(116)"]
    battery_capacity=GivTCP.read_register('55','03','01')[GiV_Reg_LUT.holding_register_LUT.get(55)[0]+"(55)"]
    discharge_enable=GivTCP.read_register('59','03','01')[GiV_Reg_LUT.holding_register_LUT.get(59)[0]+"(59)"]

    if shallow_charge==4 and self_consumption==True and discharge_enable==False:
        controlmode=1
    elif shallow_charge==100 and self_consumption==True and discharge_enable==True:
        controlmode=2&3
    elif shallow_charge==4 and self_consumption==False and discharge_enable==True:
        controlmode=4
    else:
        controlmode="unknown"

    controls['Mode']=controlmode
    controls['Battery Power Reserve']=battery_reserve
    controls['Target SOC']=target_soc
    controls['Battery Capacity']=round(((battery_capacity*51.2)/1000),2)
    controls['Smart Charge Enable']=charge_enable

    if len(controls)!=0:
      GivTCP.publish_to_MQTT("Control",controls)

def setTimeslot():
    result=GivTCP.write_single_register(95,1559)
    print (result,": Register 95 was set")

#Main Function...
getCombinedStats()
getModes()
#setTimeslot()
getTimeslots()

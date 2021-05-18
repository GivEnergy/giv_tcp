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
# import schedule

def getTimeslots():
    timeslots={}

    #Grab Timeslots
    timeslots=GivTCP.read_register('44','03','02')
    timeslots.update(GivTCP.read_register('56','03','02'))
    timeslots.update(GivTCP.read_register('94','03','02'))
    if len(timeslots)!=0:
      GivTCP.publish_to_MQTT("Timeslots",timeslots)

def getPowerData():
    power_output={}
    PV_stats={}
    grid_power={}
    load_power={}
    battery_power={}
    SOC={}

    #Grab power data
    PV_stats=GivTCP.read_register('18','04','3') #Get PV Power
    if len(PV_stats)==3:
        PVPower=PV_stats[GivTCP.input_register_LUT.get(18)[0]+"(18)"]+PV_stats[GivTCP.input_register_LUT.get(20)[0]+"(20)"]
        power_output['PV Power']=PVPower

    time.sleep(0.5)

    grid_power=GivTCP.read_register('30','04','1') #Get Grid Power
    #Calculate Import and Export
    if len(grid_power)!=0:
        value=grid_power[GivTCP.input_register_LUT.get(30)[0]+"(30)"]
        if value<=0:
            import_power=abs(value)
            export_power=0
        elif value>=0:
            import_power=0
            export_power=abs(value)
        power_output['Grid Power']=value
        power_output['Import Power']=import_power
        power_output['Export Power']=export_power

    time.sleep(0.5)

    load_power=GivTCP.read_register('42','04','1') #Get Load Power
    if len(load_power)!=0:
        power_output['Load Power']=load_power[GivTCP.input_register_LUT.get(42)[0]+"(42)"]

    time.sleep(0.5)

    eps_power=GivTCP.read_register('31','04','1') #Get Load Power
    if len(eps_power)!=0:
        power_output['EPS Power']=eps_power[GivTCP.input_register_LUT.get(31)[0]+"(31)"]

    time.sleep(0.5)

    battery_power=GivTCP.read_register('52','04','1') #Get Battery Power
    #Calculate Charge/Discharge
    if len(battery_power)!=0:
        value=battery_power[GivTCP.input_register_LUT.get(52)[0]+"(52)"]
        if value>=0:
            discharge_power=abs(value)
            charge_power=0
        elif value<=0:
            discharge_power=0
            charge_power=abs(value)
        power_output['Battery Power']=value
        power_output['Charge Power']=charge_power
        power_output['Discharge Power']=discharge_power

    time.sleep(0.5)

    SOC=GivTCP.read_register('59','04','1') #Get SOC
    if len(SOC)!=0:
        power_output['SOC']=SOC[GivTCP.input_register_LUT.get(59)[0]+"(59)"]

    if len(power_output)==10:		#Only publish if all values are there, otherwise values don't match up...
        GivTCP.publish_to_MQTT("Power",power_output)

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
        power_output['PV Power']= temp_output[GivTCP.input_register_LUT.get(18)[0]+"(18)"]+temp_output[GivTCP.input_register_LUT.get(20)[0]+"(20)"]

        temphex=str(temp_output[GivTCP.input_register_LUT.get(21)[0]+"(21)"])+str(temp_output[GivTCP.input_register_LUT.get(22)[0]+"(22)"])
        kwh_value=round(int(temphex,16) * GivTCP.input_register_LUT.get(21)[2],2)
        energy_output['Export Energy Total kwh']=kwh_value

        temphex=str(temp_output[GivTCP.input_register_LUT.get(27)[0]+"(27)"])+str(temp_output[GivTCP.input_register_LUT.get(28)[0]+"(28)"])
        kwh_value=round(int(temphex,16) * GivTCP.input_register_LUT.get(27)[2],2)
        energy_output['Load Energy Total kwh']=kwh_value

        temphex=str(temp_output[GivTCP.input_register_LUT.get(32)[0]+"(32)"])+str(temp_output[GivTCP.input_register_LUT.get(33)[0]+"(33)"])
        kwh_value=round(int(temphex,16) * GivTCP.input_register_LUT.get(32)[2],2)
        energy_output['Import Energy Total kwh']=kwh_value

        value= temp_output[GivTCP.input_register_LUT.get(30)[0]+"(30)"]
        if value<=0:
            import_power=abs(value)
            export_power=0
        elif value>=0:
            import_power=0
            export_power=abs(value)
        power_output['Grid Power']=value
        power_output['Import Power']=import_power
        power_output['Export Power']=export_power

        power_output['EPS Power']= temp_output[GivTCP.input_register_LUT.get(31)[0]+"(31)"]

        power_output['Load Power']= temp_output[GivTCP.input_register_LUT.get(42)[0]+"(42)"]
        temphex=str(temp_output[GivTCP.input_register_LUT.get(45)[0]+"(45)"])+str(temp_output[GivTCP.input_register_LUT.get(46)[0]+"(46)"])
        kwh_value=round(int(temphex,16) * GivTCP.input_register_LUT.get(45)[2],2)
        energy_output['INV OUT Energy Total kwh']=kwh_value

        value=temp_output[GivTCP.input_register_LUT.get(52)[0]+"(52)"]
        if value>=0:
            discharge_power=abs(value)
            charge_power=0
        elif value<=0:
            discharge_power=0
            charge_power=abs(value)
        power_output['Battery Power']=value
        power_output['Charge Power']=charge_power
        power_output['Discharge Power']=discharge_power

        power_output['SOC']=temp_output[GivTCP.input_register_LUT.get(59)[0]+"(59)"]
    if len(energy_output)!=0:
      GivTCP.publish_to_MQTT("Energy",energy_output)
    if len(power_output)!=0:
      GivTCP.publish_to_MQTT("Power",power_output)

#Main Function...
GivTCP.getTimeslots()
GivTCP.getCombinedStats()

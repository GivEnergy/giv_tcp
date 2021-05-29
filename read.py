# -*- coding: utf-8 -*-
import sys
from GivTCP import GivTCP
from GivLUT import GiV_Reg_LUT
from datetime import datetime
from settings import GiV_Settings

Log_To_File=False
if GiV_Settings.Log_To_File=="True":		#if in debug mode write to log file
    Log_To_File=True
    f = open('read_debug.log','a')
    sys.stdout = f

if GiV_Settings.Print_Raw_Registers=="True":
    Print_Raw=True

now = datetime.now()
print ("-----------------",now,"-----------------")

def getTimeslots():
    timeslots={}

    #Grab Timeslots
    timeslots=GivTCP.read_register('44','03','02')
    timeslots.update(GivTCP.read_register('56','03','02'))
    timeslots.update(GivTCP.read_register('94','03','02'))
    if len(timeslots)!=0:
      GivTCP.publish_to_MQTT("Timeslots",timeslots)

def getCombinedStats():
    energy_total_output={}
    energy_today_output={}
    temp_output={}
    extrareg={}
    power_output={}
    PV_stats={}
    grid_power={}
    load_power={}
    battery_power={}
    SOC={}
    sum=0
    emptycount=0

    #Grab Energy data
    temp_output=GivTCP.read_register('0','04','60') #Get ALL input Registers
    if Print_Raw:
        GivTCP.publish_to_MQTT("raw/input",temp_output)

    extrareg=GivTCP.read_register('180','04','4') #Get ALL input Registers
    if len(extrareg)==4:
        if extrareg[GiV_Reg_LUT.input_register_LUT.get(183)[0]+"(183)"]<100:	#Cap output at 100kWh in a single day
            energy_today_output['Battery Charge Energy Today kWh']=extrareg[GiV_Reg_LUT.input_register_LUT.get(183)[0]+"(183)"]
        if extrareg[GiV_Reg_LUT.input_register_LUT.get(182)[0]+"(182)"]<100:
            energy_today_output['Battery Discharge Energy Today kWh']=extrareg[GiV_Reg_LUT.input_register_LUT.get(182)[0]+"(182)"]
        energy_total_output['Battery Charge Energy Total kWh']=extrareg[GiV_Reg_LUT.input_register_LUT.get(181)[0]+"(181)"]
        energy_total_output['Battery Discharge Energy Total kWh']=extrareg[GiV_Reg_LUT.input_register_LUT.get(180)[0]+"(180)"]

    if Print_Raw:
        GivTCP.publish_to_MQTT("raw/input",extrareg)

    for key in temp_output:		#Check that not all registers are zero
        try:
            sum= sum+ int(temp_output[key])
            if int(temp_output[key])==0:
                emptycount+=1
        except:
            sum=sum
    print ("Sum of reg=",sum,"And there are",emptycount,"empty registers")

    if len(temp_output)==60 and emptycount<30:		#Only process and run if registers are all there and non-zero
        #Total Energy Figures
        temphex=str(temp_output[GiV_Reg_LUT.input_register_LUT.get(21)[0]+"(21)"])+str(temp_output[GiV_Reg_LUT.input_register_LUT.get(22)[0]+"(22)"])
        kwh_value=round(int(temphex,16) * GiV_Reg_LUT.input_register_LUT.get(21)[2],2)
        if kwh_value<100000:
            energy_total_output['Export Energy Total kWh']=kwh_value

        temphex=str(temp_output[GiV_Reg_LUT.input_register_LUT.get(6)[0]+"(6)"])+str(temp_output[GiV_Reg_LUT.input_register_LUT.get(7)[0]+"(7)"])
        kwh_value=round(int(temphex,16) * GiV_Reg_LUT.input_register_LUT.get(21)[2],2)
        if kwh_value<100000:
            energy_total_output['Battery Throughput Total kWh']=kwh_value

        temphex=str(temp_output[GiV_Reg_LUT.input_register_LUT.get(27)[0]+"(27)"])+str(temp_output[GiV_Reg_LUT.input_register_LUT.get(28)[0]+"(28)"])
        kwh_value=round(int(temphex,16) * GiV_Reg_LUT.input_register_LUT.get(27)[2],2)
        if kwh_value<100000:
            energy_total_output['Load Energy Total kWh']=kwh_value

        temphex=str(temp_output[GiV_Reg_LUT.input_register_LUT.get(32)[0]+"(32)"])+str(temp_output[GiV_Reg_LUT.input_register_LUT.get(33)[0]+"(33)"])
        kwh_value=round(int(temphex,16) * GiV_Reg_LUT.input_register_LUT.get(32)[2],2)
        if kwh_value<100000:
            energy_total_output['Import Energy Total kWh']=kwh_value

        temphex=str(temp_output[GiV_Reg_LUT.input_register_LUT.get(11)[0]+"(11)"])+str(temp_output[GiV_Reg_LUT.input_register_LUT.get(12)[0]+"(12)"])
        pv_kwh_value=round(int(temphex,16) * GiV_Reg_LUT.input_register_LUT.get(11)[2],2)
        if kwh_value<100000:
            energy_total_output['PV Energy Total kWh']=pv_kwh_value

        temphex=str(temp_output[GiV_Reg_LUT.input_register_LUT.get(45)[0]+"(45)"])+str(temp_output[GiV_Reg_LUT.input_register_LUT.get(46)[0]+"(46)"])
        invout_kwh_value=round(int(temphex,16) * GiV_Reg_LUT.input_register_LUT.get(45)[2],2)

        #Energy Today Fugures
        energy_today_output['Battery Throughput Today kWh']=temp_output[GiV_Reg_LUT.input_register_LUT.get(36)[0]+"(36)"]+temp_output[GiV_Reg_LUT.input_register_LUT.get(37)[0]+"(37)"]
        energy_today_output['PV Energy Today kWh']=round(temp_output[GiV_Reg_LUT.input_register_LUT.get(17)[0]+"(17)"]+temp_output[GiV_Reg_LUT.input_register_LUT.get(19)[0]+"(19)"],2)
        if temp_output[GiV_Reg_LUT.input_register_LUT.get(26)[0]+"(26)"]<100:
            energy_today_output['Import Energy Today kWh']=temp_output[GiV_Reg_LUT.input_register_LUT.get(26)[0]+"(26)"]
        if temp_output[GiV_Reg_LUT.input_register_LUT.get(25)[0]+"(25)"]<100:
            energy_today_output['Export Energy Today kWh']=temp_output[GiV_Reg_LUT.input_register_LUT.get(25)[0]+"(25)"]
        if temp_output[GiV_Reg_LUT.input_register_LUT.get(35)[0]+"(35)"]<100:
            energy_today_output['Load Energy Today kWh']=temp_output[GiV_Reg_LUT.input_register_LUT.get(35)[0]+"(35)"]

        #Instant Power figures
        temp_PV=temp_output[GiV_Reg_LUT.input_register_LUT.get(18)[0]+"(18)"]+temp_output[GiV_Reg_LUT.input_register_LUT.get(20)[0]+"(20)"]
        if temp_PV<15000:
            power_output['PV Power']= temp_PV
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
        temp_PInv=temp_output[GiV_Reg_LUT.input_register_LUT.get(24)[0]+"(24)"]
        if temp_PInv<15500:
            power_output['Invertor Power']= temp_PInv
        temp_Load=temp_output[GiV_Reg_LUT.input_register_LUT.get(42)[0]+"(42)"]
        if temp_Load<15500:
            power_output['Load Power']= temp_Load


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

        if len(energy_total_output)!=0:
          GivTCP.publish_to_MQTT("Energy/Total",energy_total_output)
        if len(energy_today_output)!=0:
          GivTCP.publish_to_MQTT("Energy/Today",energy_today_output)
        if len(power_output)!=0:
          GivTCP.publish_to_MQTT("Power",power_output)

def getModes():
    controls={}
    controlmode={}
    controls=GivTCP.read_register('0','03','60')
    controls.update(GivTCP.read_register('60','03','60'))
    if Print_Raw:
        GivTCP.publish_to_MQTT("raw/holding",controls)

    if len(controls)==120:
      shallow_charge=controls[GiV_Reg_LUT.holding_register_LUT.get(110)[0]+"(110)"]
      self_consumption=controls[GiV_Reg_LUT.holding_register_LUT.get(27)[0]+"(27)"]
      charge_enable=controls[GiV_Reg_LUT.holding_register_LUT.get(96)[0]+"(96)"]
      if charge_enable==True:
          charge_enable="Active"
      else:
          charge_enable="Paused"

      battery_reserve=controls[GiV_Reg_LUT.holding_register_LUT.get(114)[0]+"(114)"]
      target_soc=controls[GiV_Reg_LUT.holding_register_LUT.get(116)[0]+"(116)"]
      battery_capacity=controls[GiV_Reg_LUT.holding_register_LUT.get(55)[0]+"(55)"]
      discharge_enable=controls[GiV_Reg_LUT.holding_register_LUT.get(59)[0]+"(59)"]
      if discharge_enable==True:
          discharge_enable="Active"
      else:
          discharge_enable="Paused"

      print (shallow_charge,self_consumption,discharge_enable)

      if shallow_charge==4 and self_consumption==True and discharge_enable=="Paused":
          mode=1
      elif shallow_charge==100 and self_consumption==True and discharge_enable=="Active":
          mode=3
      elif shallow_charge==4 and self_consumption==False and discharge_enable=="Active":
          mode=4
      else:
          mode="unknown"

      controlmode['Mode']=mode
      controlmode['Battery Power Reserve']=battery_reserve
      controlmode['Target SOC']=target_soc
      controlmode['Battery Capacity']=round(((battery_capacity*51.2)/1000),2)
      controlmode['Charge Schedule State']=charge_enable
      controlmode['Discharge Schedule State']=discharge_enable

    if len(controlmode)!=0:
      GivTCP.publish_to_MQTT("Control",controlmode)

def runAll():
    getCombinedStats()
    getModes()
    getTimeslots()



if __name__ == '__main__':
    globals()[sys.argv[1]]()

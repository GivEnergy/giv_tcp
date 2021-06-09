# -*- coding: utf-8 -*-
import sys
import configparser
from GivTCP import GivTCP
from GivLUT import GiV_Reg_LUT
from datetime import datetime
from settings import GiV_Settings

def getTimeslots():
    timeslots={}
    GivTCP.debug("Getting TimeSlot data")
    #Grab Timeslots
    timeslots=GivTCP.read_register('44','03','02')
    timeslots.update(GivTCP.read_register('56','03','02'))
    timeslots.update(GivTCP.read_register('94','03','02'))
    if len(timeslots)!=0:
        GivTCP.debug("Publishing to Timeslot MQTT")
        GivTCP.publish_to_MQTT("Timeslots",timeslots)

def getCombinedStats():
    energy_total_output={}
    energy_today_output={}
    temp_output={}
    extrareg={}
    power_output={}
    power_flow_output={}
    sum=0
    emptycount=0

    GivTCP.debug("Getting All Input Registers Data")

    #Grab Energy data
    temp_output=GivTCP.read_register('0','04','60') #Get ALL input Registers
    if Print_Raw:
        GivTCP.publish_to_MQTT("raw/input",temp_output)

    extrareg=GivTCP.read_register('180','04','4') #Get v2.6 input Registers
    GivTCP.debug("Getting Extra Input Registers Data")
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
    GivTCP.debug("Sum of reg= "+str(sum)+" And there are " + str(emptycount) +" empty registers")

    if len(temp_output)==60 and emptycount<30:		#Only process and run if registers are all there and non-zero
#Total Energy Figures
        GivTCP.debug("Getting Total Energy Data")
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
            energy_total_output['AC Charge Energy Total kWh']=kwh_value

        temphex=str(temp_output[GiV_Reg_LUT.input_register_LUT.get(32)[0]+"(32)"])+str(temp_output[GiV_Reg_LUT.input_register_LUT.get(33)[0]+"(33)"])
        kwh_value=round(int(temphex,16) * GiV_Reg_LUT.input_register_LUT.get(32)[2],2)
        if kwh_value<100000:
            energy_total_output['Import Energy Total kWh']=kwh_value

        temphex=str(temp_output[GiV_Reg_LUT.input_register_LUT.get(45)[0]+"(45)"])+str(temp_output[GiV_Reg_LUT.input_register_LUT.get(46)[0]+"(46)"])
        inv_kwh_value=round(int(temphex,16) * GiV_Reg_LUT.input_register_LUT.get(45)[2],2)
        if kwh_value<100000:
            energy_total_output['Invertor Energy Total kWh']=inv_kwh_value

        temphex=str(temp_output[GiV_Reg_LUT.input_register_LUT.get(11)[0]+"(11)"])+str(temp_output[GiV_Reg_LUT.input_register_LUT.get(12)[0]+"(12)"])
        pv_kwh_value=round(int(temphex,16) * GiV_Reg_LUT.input_register_LUT.get(11)[2],2)
        if kwh_value<100000:
            energy_total_output['PV Energy Total kWh']=pv_kwh_value

        if GiV_Settings.Invertor_Type.lower()=="hybrid":
            energy_total_output['Load Energy Total kWh']=round((energy_total_output['Invertor Energy Total kWh']-energy_total_output['AC Charge Energy Total kWh'])-(energy_total_output['Export Energy Total kWh']-energy_total_output['Import Energy Total kWh']),3)
        else:
            energy_total_output['Load Energy Total kWh']=round((energy_total_output['Invertor Energy Total kWh']-energy_total_output['AC Charge Energy Total kWh'])-(energy_total_output['Export Energy Total kWh']-energy_total_output['Import Energy Total kWh'])+energy_total_output['PV Energy Total kWh'],3)
        
        energy_total_output['Self Consumption Energy Total kWh']=round(energy_total_output['PV Energy Total kWh']-energy_total_output['Export Energy Total kWh'],2)

#Energy Today Figures
        GivTCP.debug("Getting Today Energy Data")
        if round(temp_output[GiV_Reg_LUT.input_register_LUT.get(36)[0]+"(36)"]+temp_output[GiV_Reg_LUT.input_register_LUT.get(37)[0]+"(37)"],2)<100:
            energy_today_output['Battery Throughput Today kWh']=round(temp_output[GiV_Reg_LUT.input_register_LUT.get(36)[0]+"(36)"]+temp_output[GiV_Reg_LUT.input_register_LUT.get(37)[0]+"(37)"],2)
        if round(temp_output[GiV_Reg_LUT.input_register_LUT.get(17)[0]+"(17)"]+temp_output[GiV_Reg_LUT.input_register_LUT.get(19)[0]+"(19)"],2)<100:
            energy_today_output['PV Energy Today kWh']=round(temp_output[GiV_Reg_LUT.input_register_LUT.get(17)[0]+"(17)"]+temp_output[GiV_Reg_LUT.input_register_LUT.get(19)[0]+"(19)"],2)
        if temp_output[GiV_Reg_LUT.input_register_LUT.get(26)[0]+"(26)"]<100:
            energy_today_output['Import Energy Today kWh']=round(temp_output[GiV_Reg_LUT.input_register_LUT.get(26)[0]+"(26)"],2)
        if temp_output[GiV_Reg_LUT.input_register_LUT.get(25)[0]+"(25)"]<100:
            energy_today_output['Export Energy Today kWh']=round(temp_output[GiV_Reg_LUT.input_register_LUT.get(25)[0]+"(25)"],2)
        if temp_output[GiV_Reg_LUT.input_register_LUT.get(35)[0]+"(35)"]<100:
            energy_today_output['AC Charge Energy Today kWh']=round(temp_output[GiV_Reg_LUT.input_register_LUT.get(35)[0]+"(35)"],2)
        if temp_output[GiV_Reg_LUT.input_register_LUT.get(44)[0]+"(44)"]<100:
            energy_today_output['Invertor Energy Today kWh']=round(temp_output[GiV_Reg_LUT.input_register_LUT.get(44)[0]+"(44)"],2)


        if GiV_Settings.Invertor_Type.lower()=="hybrid":
            energy_today_output['Load Energy Today kWh']=round((energy_today_output['Invertor Energy Today kWh']-energy_today_output['AC Charge Energy Today kWh'])-(energy_today_output['Export Energy Today kWh']-energy_today_output['Import Energy Today kWh']),3)
        else:
            energy_today_output['Load Energy Today kWh']=round((energy_today_output['Invertor Energy Today kWh']-energy_today_output['AC Charge Energy Today kWh'])-(energy_today_output['Export Energy Today kWh']-energy_today_output['Import Energy Today kWh'])+energy_today_output['PV Energy Today kWh'],3)
        energy_today_output['Self Consumption Energy Today kWh']=round(energy_today_output['PV Energy Today kWh']-energy_today_output['Export Energy Today kWh'],2)

############  Core Power Stats    ############

    #PV Power
        GivTCP.debug("Getting PV Power")
        PV_power=temp_output[GiV_Reg_LUT.input_register_LUT.get(18)[0]+"(18)"]+temp_output[GiV_Reg_LUT.input_register_LUT.get(20)[0]+"(20)"]
        if PV_power<15000:
            power_output['PV Power']= PV_power

    #Grid Power
        GivTCP.debug("Getting Grid Power")
        grid_power= temp_output[GiV_Reg_LUT.input_register_LUT.get(30)[0]+"(30)"]
        if grid_power<0:
            import_power=abs(grid_power)
            export_power=0
        elif grid_power>0:
            import_power=0
            export_power=abs(grid_power)
        else:
            import_power=0
            export_power=0
        power_output['Grid Power']=grid_power
        power_output['Import Power']=import_power
        power_output['Export Power']=export_power

    #EPS Power
        GivTCP.debug("Getting EPS Power")
        power_output['EPS Power']= temp_output[GiV_Reg_LUT.input_register_LUT.get(31)[0]+"(31)"]

    #Invertor Power
        GivTCP.debug("Getting PInv Power")
        Invertor_power=temp_output[GiV_Reg_LUT.input_register_LUT.get(24)[0]+"(24)"]
        if -6000 <= Invertor_power <= 6000:
            power_output['Invertor Power']= Invertor_power
        if Invertor_power<0:
            power_output['AC Charge Power']= abs(Invertor_power)

#    #Calculated Load Power
#        GivTCP.debug("Calculating Load Power")
#        temp_Load_Calc=Invertor_power + PV_power - grid_power
#        if temp_Load_Calc<15500:
#            power_output['Load Power (calc)']= temp_Load_Calc

    #Load Power
        GivTCP.debug("Getting Load Power")
        Load_power=temp_output[GiV_Reg_LUT.input_register_LUT.get(42)[0]+"(42)"]
        if Load_power<15500:
            power_output['Load Power']=Load_power

    #Self Consumption
        GivTCP.debug("Getting Self Consumption Power")
        power_output['Self Consumption Power']=max(Load_power - import_power,0)

    #Battery Power
        Battery_power=temp_output[GiV_Reg_LUT.input_register_LUT.get(52)[0]+"(52)"]
        if Battery_power>=0:
            discharge_power=abs(Battery_power)
            charge_power=0
        elif Battery_power<=0:
            discharge_power=0
            charge_power=abs(Battery_power)
        power_output['Battery Power']=Battery_power
        power_output['Charge Power']=charge_power
        power_output['Discharge Power']=discharge_power

    #SOC
        GivTCP.debug("Getting SOC")
        if int(temp_output[GiV_Reg_LUT.input_register_LUT.get(59)[0]+"(59)"]) > 3:
            power_output['SOC']=temp_output[GiV_Reg_LUT.input_register_LUT.get(59)[0]+"(59)"]

############  Power Flow Stats    ############

    #Solar to H/B/G
        GivTCP.debug("Getting Solar to H/B/G Power Flows")
        if PV_power>0:
            S2H=min(PV_power,Load_power)
            power_flow_output['Solar to House']=S2H
            S2B=max((PV_power-S2H)-export_power,0)
            power_flow_output['Solar to Battery']=S2B
            power_flow_output['Solar to Grid']=max(PV_power - S2H - S2B,0)

        else:
            power_flow_output['Solar to House']=0
            power_flow_output['Solar to Battery']=0
            power_flow_output['Solar to Grid']=0

    #Battery to House
        GivTCP.debug("Getting Battery to House Power Flow")
        B2H=max(discharge_power-export_power,0)
        power_flow_output['Battery to House']=B2H

    #Grid to Battery/House Power
        GivTCP.debug("Getting Grid to Battery/House Power Flow")
        if import_power>0:
            power_flow_output['Grid to Battery']=charge_power-max(PV_power-Load_power,0)
            power_flow_output['Grid to House']=max(import_power-charge_power,0)

        else:
            power_flow_output['Grid to Battery']=0
            power_flow_output['Grid to House']=0

    #Battery to Grid Power
        GivTCP.debug("Getting Battery to Grid Power Flow")
        if export_power>0:
            power_flow_output['Battery to Grid']=max(discharge_power-B2H,0)
        else:
            power_flow_output['Battery to Grid']=0

    #Publish to MQTT
        GivTCP.debug("Publish all to MQTT")
        if len(energy_total_output)!=0:
            GivTCP.publish_to_MQTT("Energy/Total",energy_total_output)
        if len(energy_today_output)!=0:
            GivTCP.publish_to_MQTT("Energy/Today",energy_today_output)
        if len(power_output)!=0:
            GivTCP.publish_to_MQTT("Power",power_output)
        if len(power_flow_output)!=0:
            GivTCP.publish_to_MQTT("Power/Flows",power_flow_output)

def getModesandTimes():
    controls={}
    controlmode={}
    GivTCP.debug("Getting All Holding Registers")
    controls=GivTCP.read_register('0','03','60')
    controls.update(GivTCP.read_register('60','03','60'))
    if Print_Raw:
        GivTCP.publish_to_MQTT("raw/holding",controls)

    if len(controls)==120:
        GivTCP.debug("All holding registers retrieved")
        GivTCP.debug("Getting mode control figures")
# Get Control Mode registers
        shallow_charge=controls[GiV_Reg_LUT.holding_register_LUT.get(110)[0]+"(110)"]
        self_consumption=controls[GiV_Reg_LUT.holding_register_LUT.get(27)[0]+"(27)"]
        charge_enable=controls[GiV_Reg_LUT.holding_register_LUT.get(96)[0]+"(96)"]
        if charge_enable==True:
            charge_enable="Active"
        else:
            charge_enable="Paused"

#Get Battery Stat registers
        battery_reserve=controls[GiV_Reg_LUT.holding_register_LUT.get(114)[0]+"(114)"]
        target_soc=controls[GiV_Reg_LUT.holding_register_LUT.get(116)[0]+"(116)"]
        battery_capacity=controls[GiV_Reg_LUT.holding_register_LUT.get(55)[0]+"(55)"]
        discharge_enable=controls[GiV_Reg_LUT.holding_register_LUT.get(59)[0]+"(59)"]
        if discharge_enable==True:
            discharge_enable="Active"
        else:
            discharge_enable="Paused"

        GivTCP.debug("Shallow Charge= "+str(shallow_charge)+" Self Consumption= "+str(self_consumption)+" Discharge Enable= "+str(discharge_enable))

#Calculate Mode
        GivTCP.debug("Calculating Mode...")
        if shallow_charge==4 and self_consumption==True and discharge_enable=="Paused":
            mode=1
        elif shallow_charge==100 and self_consumption==True and discharge_enable=="Active":
            mode=3
        elif shallow_charge==4 and self_consumption==False and discharge_enable=="Active":
            mode=4
        else:
            mode="unknown"
        GivTCP.debug("Mode is: " + str(mode))
        controlmode['Mode']=mode
        controlmode['Battery Power Reserve']=battery_reserve
        controlmode['Target SOC']=target_soc
        controlmode['Battery Capacity']=round(((battery_capacity*51.2)/1000),2)
        controlmode['Charge Schedule State']=charge_enable
        controlmode['Discharge Schedule State']=discharge_enable

#Grab Timeslots
        timeslots={}
        GivTCP.debug("Getting TimeSlot data")
        timeslots['Discharge start time slot 1']=controls[GiV_Reg_LUT.holding_register_LUT.get(56)[0]+"(56)"]
        timeslots['Discharge end time slot 1']=controls[GiV_Reg_LUT.holding_register_LUT.get(57)[0]+"(57)"]
        timeslots['Discharge start time slot 2']=controls[GiV_Reg_LUT.holding_register_LUT.get(44)[0]+"(44)"]
        timeslots['Discharge end time slot 2']=controls[GiV_Reg_LUT.holding_register_LUT.get(45)[0]+"(45)"]
        timeslots['Charge start time slot 1']=controls[GiV_Reg_LUT.holding_register_LUT.get(94)[0]+"(94)"]
        timeslots['Charge end time slot 1']=controls[GiV_Reg_LUT.holding_register_LUT.get(95)[0]+"(95)"]


    if len(timeslots)==6:
        GivTCP.debug("Publishing to Timeslot MQTT")
        GivTCP.publish_to_MQTT("Timeslots",timeslots)

    if len(controlmode)==6:
        GivTCP.debug("Publishing to Control MQTT")
        GivTCP.publish_to_MQTT("Control",controlmode)

def extraRegCheck():
    extrareg={}
    energy_today_output={}
    energy_total_output={}
    extrareg=GivTCP.read_register('180','04','4') #Get v2.6 input Registers
    GivTCP.debug ("Extrareg is:" + str(extrareg))
    GivTCP.debug ("Extrareg is:" + str(len(extrareg))+" registers long")
    if len(extrareg)==4:
        if extrareg[GiV_Reg_LUT.input_register_LUT.get(183)[0]+"(183)"]<100:	#Cap output at 100kWh in a single day
            energy_today_output['Battery Charge Energy Today kWh']=extrareg[GiV_Reg_LUT.input_register_LUT.get(183)[0]+"(183)"]
        if extrareg[GiV_Reg_LUT.input_register_LUT.get(182)[0]+"(182)"]<100:
            energy_today_output['Battery Discharge Energy Today kWh']=extrareg[GiV_Reg_LUT.input_register_LUT.get(182)[0]+"(182)"]
        energy_total_output['Battery Charge Energy Total kWh']=extrareg[GiV_Reg_LUT.input_register_LUT.get(181)[0]+"(181)"]
        energy_total_output['Battery Discharge Energy Total kWh']=extrareg[GiV_Reg_LUT.input_register_LUT.get(180)[0]+"(180)"]

def getEMSData():
    EMSData={}
    EMSData=GivTCP.read_register('60','04','02') #Get v2.6 input Registers
    GivTCP.debug ("EMSData is:" + str(EMSData))
    GivTCP.debug ("EMSData is:" + str(len(EMSData))+" registers long")
    print ("EMSData: ",EMSData)


def runAll():
    starttime = datetime.now()
    GivTCP.debug("----------------------------Starting----------------------------")
    GivTCP.debug("Running getCombinedStats")
    getCombinedStats()
    GivTCP.debug("Running getModesandTimes")
    getModesandTimes()
    now = datetime.now()
    duration=now-starttime
    GivTCP.debug("----------------------------Ended taking "+str(duration)+" seconds------------")


if __name__ == '__main__':
    Log_To_File=False
    if GiV_Settings.Log_To_File.lower()=="true":		#if in debug mode write to log file
        Log_To_File=True
        f = open(GiV_Settings.Debug_File_Location + 'read_debug.log','a')
        sys.stdout = f

    Print_Raw=False
    if GiV_Settings.Print_Raw_Registers.lower()=="true":
        Print_Raw=True

    globals()[sys.argv[1]]()

# -*- coding: utf-8 -*-
# version 2022.01.31
import array
import sys
import json
import logging
import datetime
from HA_Discovery import HAMQTT
from settings import GiV_Settings
from givenergy_modbus.client import GivEnergyClient
from givenergy_modbus.model.inverter import Inverter, Model
from givenergy_modbus.model.battery import Battery
from givenergy_modbus.model.register_cache import RegisterCache

Print_Raw=False
if GiV_Settings.Print_Raw_Registers.lower()=="true":
    Print_Raw=True

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

def runAll():
    energy_total_output={}
    energy_today_output={}
    power_output={}
    controlmode={}
    power_flow_output={}
    invertor={}
    batteries = {}
    multi_output={}
    temp={}
    logger.info("----------------------------Starting----------------------------")
    logging.info("Getting All Registers")
    
    #Connect to Invertor and load data
    try:
    #    starttime=datetime.datetime.now()
    #    logger.error("Start time for library invertor call: "+ datetime.datetime.strftime(starttime,"%H:%M:%S"))
        client=GivEnergyClient(host=GiV_Settings.invertorIP)
        InvRegCache = RegisterCache()
        client.update_inverter_registers(InvRegCache)
        GEInv=Inverter.from_orm(InvRegCache)
        numBatteries=1
        try:
            numBatteries=int(GiV_Settings.numBatteries)
        except ValueError:
            logger.error("error parsing numbatteries defaulting to 1")

        for x in range(0, numBatteries):
            BatRegCache = RegisterCache()
            client.update_battery_registers(BatRegCache, battery_number=x)
            GEBat=Battery.from_orm(BatRegCache)
            batteries[GEBat.battery_serial_number]=GEBat.dict()
    #    endtime=datetime.datetime.now()
    #    logger.error("End time for library invertor call: "+ datetime.datetime.strftime(endtime,"%H:%M:%S"))
    #    logger.error("End time for library invertor call: "+ str(endtime-starttime))
        logger.info("Invertor connection successful, registers retrieved")
    except:
        e = sys.exc_info()
        logger.error("Error collecting registers: " + str(e))
        temp['result']="Error collecting registers: " + str(e)
        return json.dumps(temp)

    if Print_Raw:

        raw={}
        raw["invertor"]=GEInv.dict()
        raw["batteries"]=batteries
        multi_output['raw']=raw

    try:
    #Total Energy Figures
        logger.info("Getting Total Energy Data")
        energy_total_output['Export Energy Total kWh']=GEInv.e_grid_out_total
        energy_total_output['Battery Throughput Total kWh']=GEInv.e_battery_throughput_total
        energy_total_output['AC Charge Energy Total kWh']=GEInv.e_inverter_in_total
        energy_total_output['Import Energy Total kWh']=GEInv.e_grid_in_total
        energy_total_output['Invertor Energy Total kWh']=GEInv.e_inverter_out_total
        energy_total_output['PV Energy Total kWh']=GEInv.e_pv_total
        
        if  GEInv.inverter_model==Model.Hybrid:
            energy_total_output['Load Energy Total kWh']=(energy_total_output['Invertor Energy Total kWh']-energy_total_output['AC Charge Energy Total kWh'])-(energy_total_output['Export Energy Total kWh']-energy_total_output['Import Energy Total kWh'])
        else:
            energy_total_output['Load Energy Total kWh']=(energy_total_output['Invertor Energy Total kWh']-energy_total_output['AC Charge Energy Total kWh'])-(energy_total_output['Export Energy Total kWh']-energy_total_output['Import Energy Total kWh'])+energy_total_output['PV Energy Total kWh']

        if GEInv.e_battery_charge_total==0 and GEInv.e_battery_discharge_total==0:        #If no values in "nomal" registers then grab from battery
            energy_total_output['Battery Charge Energy Total kWh']=GEBat.e_battery_charge_total_2
            energy_total_output['Battery Discharge Energy Total kWh']=GEBat.e_battery_discharge_total_2
        else:
            energy_total_output['Battery Charge Energy Total kWh']=GEInv.e_battery_charge_total
            energy_total_output['Battery Discharge Energy Total kWh']=GEInv.e_battery_discharge_total

        energy_total_output['Self Consumption Energy Total kWh']=energy_total_output['PV Energy Total kWh']-energy_total_output['Export Energy Total kWh']

#Energy Today Figures
        logger.info("Getting Today Energy Data")
        energy_today_output['Battery Throughput Today kWh']=GEInv.e_battery_charge_day+GEInv.e_battery_discharge_day
        energy_today_output['PV Energy Today kWh']=GEInv.e_pv1_day+GEInv.e_pv2_day
        energy_today_output['Import Energy Today kWh']=GEInv.e_grid_in_day
        energy_today_output['Export Energy Today kWh']=GEInv.e_grid_out_day
        energy_today_output['AC Charge Energy Today kWh']=GEInv.e_inverter_in_day
        energy_today_output['Invertor Energy Today kWh']=GEInv.e_inverter_out_day
        energy_today_output['Battery Charge Energy Today kWh']=GEInv.e_battery_charge_day
        energy_today_output['Battery Discharge Energy Today kWh']=GEInv.e_battery_discharge_day
        energy_today_output['Self Consumption Energy Today kWh']=energy_today_output['PV Energy Today kWh']-energy_today_output['Export Energy Today kWh']
                
        if GEInv.inverter_model==Model.Hybrid: 
            energy_today_output['Load Energy Today kWh']=(energy_today_output['Invertor Energy Today kWh']-energy_today_output['AC Charge Energy Today kWh'])-(energy_today_output['Export Energy Today kWh']-energy_today_output['Import Energy Today kWh'])
        else:
            energy_today_output['Load Energy Today kWh']=(energy_today_output['Invertor Energy Today kWh']-energy_today_output['AC Charge Energy Today kWh'])-(energy_today_output['Export Energy Today kWh']-energy_today_output['Import Energy Today kWh'])+energy_today_output['PV Energy Today kWh']

        
############  Core Power Stats    ############

    #PV Power
        logger.info("Getting PV Power")
        PV_power_1=GEInv.p_pv1
        PV_power_2=GEInv.p_pv2
        PV_power=PV_power_1+PV_power_2
        if PV_power<15000:
            power_output['PV Power String 1']= PV_power_1
            power_output['PV Power String 2']= PV_power_2
            power_output['PV Power']= PV_power

    #Grid Power
        logger.info("Getting Grid Power")
        grid_power= GEInv.p_grid_out
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
        logger.info("Getting EPS Power")
        power_output['EPS Power']= GEInv.p_eps_backup

    #Invertor Power
        logger.info("Getting PInv Power")
        Invertor_power=GEInv.p_inverter_out
        if -6000 <= Invertor_power <= 6000:
            power_output['Invertor Power']= Invertor_power
        if Invertor_power<0:
            power_output['AC Charge Power']= abs(Invertor_power)

    #Load Power
        logger.info("Getting Load Power")
        Load_power=GEInv.p_load_demand 
        if Load_power<15500:
            power_output['Load Power']=Load_power

    #Self Consumption
        logger.info("Getting Self Consumption Power")
        power_output['Self Consumption Power']=max(Load_power - import_power,0)

    #Battery Power
        Battery_power=GEInv.p_battery 
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
        logger.info("Getting SOC")
        power_output['SOC']=GEInv.battery_percent

############  Power Flow Stats    ############

    #Solar to H/B/G
        logger.info("Getting Solar to H/B/G Power Flows")
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
        logger.info("Getting Battery to House Power Flow")
        B2H=max(discharge_power-export_power,0)
        power_flow_output['Battery to House']=B2H

    #Grid to Battery/House Power
        logger.info("Getting Grid to Battery/House Power Flow")
        if import_power>0:
            power_flow_output['Grid to Battery']=charge_power-max(PV_power-Load_power,0)
            power_flow_output['Grid to House']=max(import_power-charge_power,0)

        else:
            power_flow_output['Grid to Battery']=0
            power_flow_output['Grid to House']=0

    #Battery to Grid Power
        logger.info("Getting Battery to Grid Power Flow")
        if export_power>0:
            power_flow_output['Battery to Grid']=max(discharge_power-B2H,0)
        else:
            power_flow_output['Battery to Grid']=0

    #Get Invertor Temperature


    #Combine all outputs
        energy={}
        energy["Total"]=energy_total_output
        energy["Today"]=energy_today_output
        multi_output["Energy"]=energy
        power={}
        power["Power"]=power_output
        power["Flows"]=power_flow_output
        multi_output["Power"]=power
        multi_output["Invertor Details"]=invertor

    ################ Run Holding Reg now ###################
        logger.info("Getting mode control figures")
        # Get Control Mode registers
        shallow_charge=GEInv.battery_soc_reserve
        self_consumption=GEInv.battery_power_mode 
        charge_enable=GEInv.enable_charge
        if charge_enable==True:
            charge_enable="Active"
        else:
            charge_enable="Paused"

        #Get Battery Stat registers
        battery_reserve=GEInv.battery_discharge_min_power_reserve
        target_soc=GEInv.charge_target_soc
        discharge_enable=GEInv.enable_discharge
        if discharge_enable==True:
            discharge_enable="Active"
        else:
            discharge_enable="Paused"
        logger.info("Shallow Charge= "+str(shallow_charge)+" Self Consumption= "+str(self_consumption)+" Discharge Enable= "+str(discharge_enable))

        #Get Charge/Discharge Active status
        discharge_state=GEInv.battery_discharge_limit
        discharge_rate=discharge_state*3
        if discharge_rate>100: discharge_rate=100
        if discharge_state==0:
            discharge_state="Paused"
        else:
            discharge_state="Active"
        charge_state=GEInv.battery_charge_limit
        charge_rate=charge_state*3
        if charge_rate>100: charge_rate=100
        if charge_state==0:
            charge_state="Paused"
        else:
            charge_state="Active"


        #Calculate Mode
        logger.info("Calculating Mode...")
        mode=GEInv.system_mode
        logger.info("Mode is: " + str(mode))

        controlmode['Mode']=mode
        controlmode['Battery Power Reserve']=battery_reserve
        controlmode['Target SOC']=target_soc
        controlmode['Charge Schedule State']=charge_enable
        controlmode['Discharge Schedule State']=discharge_enable
        controlmode['Battery Charge State']=charge_state
        controlmode['Battery Discharge State']=discharge_state
        controlmode['Battery Charge Rate']=charge_rate
        controlmode['Battery Discharge Rate']=discharge_rate

        #Grab Timeslots
        timeslots={}
        logger.info("Getting TimeSlot data")
        timeslots['Discharge start time slot 1']=GEInv.discharge_slot_1[0]
        timeslots['Discharge end time slot 1']=GEInv.discharge_slot_1[1]
        timeslots['Discharge start time slot 2']=GEInv.discharge_slot_2[0]
        timeslots['Discharge end time slot 2']=GEInv.discharge_slot_2[1]
        timeslots['Charge start time slot 1']=GEInv.charge_slot_1[0]
        timeslots['Charge end time slot 1']=GEInv.charge_slot_1[1]
        timeslots['Charge start time slot 2']=GEInv.charge_slot_2[0]
        timeslots['Charge end time slot 2']=GEInv.charge_slot_2[1]

        #Get Invertor Details
        invertor={}
        logger.info("Getting Invertor Details")
        if GEInv.battery_type==1: batterytype="Lithium" 
        if GEInv.battery_type==0: batterytype="Lead Acid" 
        invertor['Battery Type']=batterytype
        invertor['Battery Capacity kWh']=((GEInv.battery_nominal_capacity*51.2)/1000)
        invertor['Invertor Serial Number']=GEInv.inverter_serial_number
        invertor['Battery Serial Number']=GEInv.first_battery_serial_number
        invertor['Modbus Version']=GEInv.modbus_version
        if GEInv.meter_type==1: metertype="EM115" 
        if GEInv.meter_type==0: metertype="EM418" 
        invertor['Meter Type']=metertype
        invertor['Invertor Type']= GEInv.inverter_model
        invertor['Invertor Temperature']=GEInv.temp_inverter_heatsink

        #Get Battery Details
        battery={}
        batteries2={}
        logger.info("Getting Battery Details")
        for b in batteries:
            logger.info("Building battery output: "+b)
            battery={}
            battery['Battery Serial Number']=batteries[b]['battery_serial_number']
            battery['Battery SOC']=batteries[b]['battery_soc']
            battery['Battery Capacity']=batteries[b]['battery_full_capacity']
            battery['Battery Design Capacity']=batteries[b]['battery_design_capacity']
            battery['Battery Remaining Capcity']=batteries[b]['battery_remaining_capacity']
            battery['Battery Firmware Version']=batteries[b]['bms_firmware_version']
            battery['Battery Cells']=batteries[b]['battery_num_cells']
            battery['Battery Cycles']=batteries[b]['battery_num_cycles']
            battery['Battery USB present']=batteries[b]['usb_inserted']
            battery['Battery Temperature']=batteries[b]['temp_bms_mos']
            battery['Battery Voltage']=batteries[b]['v_battery_cells_sum']

            battery['Battery Cell 1 Voltage'] = batteries[b]['v_battery_cell_01']
            battery['Battery Cell 2 Voltage'] = batteries[b]['v_battery_cell_02']
            battery['Battery Cell 3 Voltage'] = batteries[b]['v_battery_cell_03']
            battery['Battery Cell 4 Voltage'] = batteries[b]['v_battery_cell_04']
            battery['Battery Cell 5 Voltage'] = batteries[b]['v_battery_cell_05']
            battery['Battery Cell 6 Voltage'] = batteries[b]['v_battery_cell_06']
            battery['Battery Cell 7 Voltage'] = batteries[b]['v_battery_cell_07']
            battery['Battery Cell 8 Voltage'] = batteries[b]['v_battery_cell_08']
            battery['Battery Cell 9 Voltage'] = batteries[b]['v_battery_cell_09']
            battery['Battery Cell 10 Voltage'] = batteries[b]['v_battery_cell_10']
            battery['Battery Cell 11 Voltage'] = batteries[b]['v_battery_cell_11']
            battery['Battery Cell 12 Voltage'] = batteries[b]['v_battery_cell_12']
            battery['Battery Cell 13 Voltage'] = batteries[b]['v_battery_cell_13']
            battery['Battery Cell 14 Voltage'] = batteries[b]['v_battery_cell_14']
            battery['Battery Cell 15 Voltage'] = batteries[b]['v_battery_cell_15']
            battery['Battery Cell 16 Voltage'] = batteries[b]['v_battery_cell_16']

            battery['Battery Cell 1 Temperature'] = batteries[b]['temp_battery_cells_1']
            battery['Battery Cell 2 Temperature'] = batteries[b]['temp_battery_cells_2']
            battery['Battery Cell 3 Temperature'] = batteries[b]['temp_battery_cells_3']
            battery['Battery Cell 4 Temperature'] = batteries[b]['temp_battery_cells_4']
            batteries2[b]=battery
        #Create multioutput and publish
        multi_output["Timeslots"]=timeslots
        multi_output["Control"]=controlmode
        multi_output["Invertor Details"]=invertor
        multi_output["Battery Details"]=batteries2
        publishOutput(multi_output,GEInv.inverter_serial_number)
        
    except:
        e = sys.exc_info()
        logger.error("Error processing registers: " + str(e))
        temp['result']="Error processing registers: " + str(e)
        return json.dumps(temp)
    return json.dumps(multi_output, indent=4, sort_keys=True, default=str)

####### Addiitonal Publish options can be added here. 
####### A seperate file in the folder can be added with a new publish "plugin" 
####### then referenced here with any settings required added into settings.py

def publishOutput(array,SN):
    tempoutput={}
    tempoutput=iterate_dict(array)
    HAMQTT.publish_discovery(tempoutput,SN)
    if GiV_Settings.MQTT_Output.lower()=="true":
        from mqtt import GivMQTT
        logger.info("Publish all to MQTT")
        if GiV_Settings.MQTT_Topic=="":
            GiV_Settings.MQTT_Topic="GivEnergy"
        GivMQTT.multi_MQTT_publish(str(GiV_Settings.MQTT_Topic+"/"+SN+"/"), tempoutput)
    if GiV_Settings.JSON_Output.lower()=="true":
        from GivJson import GivJSON
        logger.info("Pushing JSON output")
        GivJSON.output_JSON(tempoutput)
    if GiV_Settings.Influx_Output.lower()=="true":
        from influx import GivInflux
        logger.info("Pushing output to Influx")
        GivInflux.publish(SN,tempoutput)

def iterate_dict(array):        # Create a publish safe version of the output (convert non string or int datapoints)
    safeoutput={}
    for p_load in array:
        output=array[p_load]
        if isinstance(output, dict):
            temp=iterate_dict(output)
            safeoutput[p_load]=temp
            logger.info('Dealt with '+p_load)
        elif isinstance(output, tuple):
            if "slot" in str(p_load):
                logger.info('Converting Timeslots to publish safe string')
                safeoutput[p_load+"_start"]=output[0].strftime("%H%M")
                safeoutput[p_load+"_end"]=output[1].strftime("%H%M")
            else:
                #Deal with other tuples _ Print each value
                for index, key in enumerate(output):
                    logger.info('Converting Tuple to multiple publish safe strings')
                    safeoutput[p_load+"_"+str(index)]=str(key)
        elif isinstance(output, datetime.datetime):
            logger.info('Converting datetime to publish safe string')
            safeoutput[p_load]=output.strftime("%d-%m-%Y %H:%M:%S")
        elif isinstance(output, datetime.time):
            logger.info('Converting time to publish safe string')
            safeoutput[p_load]=output.strftime("%H:%M")
        elif isinstance(output, Model):
            logger.info('Converting time to publish safe string')
            safeoutput[p_load]=output.name
        elif isinstance(output, float):
            safeoutput[p_load]=round(output,2)
        else:
            safeoutput[p_load]=output
    return(safeoutput)

if __name__ == '__main__':
    globals()[sys.argv[1]]()


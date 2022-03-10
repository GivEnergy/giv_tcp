# -*- coding: utf-8 -*-
# version 2022.01.31
import sys
sys.path.append('/app/GivTCP')
from pickletools import read_uint1
import json
import logging
import datetime
import pickle
import schedule
import time
from settings import GiV_Settings
from givenergy_modbus.client import GivEnergyClient
from givenergy_modbus.model.inverter import Model
from givenergy_modbus.model.battery import Battery
from givenergy_modbus.model.plant import Plant
from os.path import exists
import os


Print_Raw=False
if GiV_Settings.Print_Raw_Registers:
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
plant=Plant(number_batteries=GiV_Settings.numBatteries)

def getData(fullrefresh):      #Read from Invertor put in cache 
    energy_total_output={}
    energy_today_output={}
    power_output={}
    controlmode={}
    power_flow_output={}
    invertor={}
    batteries = {}
    multi_output={}
    result={}
    temp={}
    logger.info("----------------------------Starting----------------------------")
    logging.info("Getting All Registers")
    
    ### Only run if no lockfile present
    if exists(".lockfile"):
        logger.error("Lockfile set so aborting getData")
        result['result']="Error: Lockfile set so aborting getData"
        return json.dumps(result)

    #Connect to Invertor and load data
    try:
    #    starttime=datetime.datetime.now()
    #    logger.error("Start time for library invertor call: "+ datetime.datetime.strftime(starttime,"%H:%M:%S"))
        
        # SET Lockfile to prevent clashes
        logger.info(" setting lock file")
        open(".lockfile", 'w').close()
        

        client=GivEnergyClient(host=GiV_Settings.invertorIP)
        client.refresh_plant(plant,full_refresh=fullrefresh)
        GEInv=plant.inverter
        GEBat=plant.batteries

#        for x in range(0, numBatteries):
#            BatRegCache = RegisterCache()
#            client.update_battery_registers(BatRegCache, battery_number=x)
#            GEBat=Battery.from_orm(BatRegCache)
#            batteries[GEBat.battery_serial_number]=GEBat.dict()
            
        #Close Lockfile to allow access
        logger.info("Removing lock file")
        os.remove(".lockfile")

        multi_output['Last_Updated_Time']= datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()   
        #Get lastupdate from pickle if it exists
        if exists("lastUpdate.pkl"):
            with open('lastUpdate.pkl', 'rb') as inp:
                previousUpdate= pickle.load(inp)
            timediff=datetime.datetime.fromisoformat(multi_output['Last_Updated_Time'])-datetime.datetime.fromisoformat(previousUpdate)
            multi_output['Time_Since_Last_Update']=(((timediff.seconds*1000000)+timediff.microseconds)/1000000)
        
        #Save new time to pickle
        with open('lastUpdate.pkl', 'wb') as outp:
            pickle.dump(multi_output['Last_Updated_Time'], outp, pickle.HIGHEST_PROTOCOL)

    #    endtime=datetime.datetime.now()
    #    logger.error("End time for library invertor call: "+ datetime.datetime.strftime(endtime,"%H:%M:%S"))
    #    logger.error("End time for library invertor call: "+ str(endtime-starttime))
        multi_output['status']="online"
        
        logger.info("Invertor connection successful, registers retrieved")
    except:
        e = sys.exc_info()
        logger.error("Error collecting registers: " + str(e))
        temp['result']="Error collecting registers: " + str(e)
        #Close Lockfile to allow access in the event of an error
        logger.error("Removing lock file due to read error")
        os.remove(".lockfile")
        return json.dumps(temp)

    if Print_Raw:

        raw={}
        raw["invertor"]=GEInv.dict()
        raw["batteries"]=batteries
        multi_output['raw']=raw

    try:
    #Total Energy Figures
        logger.info("Getting Total Energy Data")
        energy_total_output['Export_Energy_Total_kWh']=GEInv.e_grid_out_total
        energy_total_output['Battery_Throughput_Total_kWh']=GEInv.e_battery_throughput_total
        energy_total_output['AC_Charge_Energy_Total_kWh']=GEInv.e_inverter_in_total
        energy_total_output['Import_Energy_Total_kWh']=GEInv.e_grid_in_total
        energy_total_output['Invertor_Energy_Total_kWh']=GEInv.e_inverter_out_total
        energy_total_output['PV_Energy_Total_kWh']=GEInv.e_pv_total
        
        if  GEInv.inverter_model==Model.Hybrid:
            energy_total_output['Load_Energy_Total_kWh']=(energy_total_output['Invertor_Energy_Total_kWh']-energy_total_output['AC_Charge_Energy_Total_kWh'])-(energy_total_output['Export_Energy_Total_kWh']-energy_total_output['Import_Energy_Total_kWh'])
        else:
            energy_total_output['Load_Energy_Total_kWh']=(energy_total_output['Invertor_Energy_Total_kWh']-energy_total_output['AC_Charge_Energy_Total_kWh'])-(energy_total_output['Export_Energy_Total_kWh']-energy_total_output['Import_Energy_Total_kWh'])+energy_total_output['PV_Energy_Total_kWh']
        if GEInv.e_battery_charge_total==0 and GEInv.e_battery_discharge_total==0:        #If no values in "nomal" registers then grab from back up registers - for some f/w versions
            energy_total_output['Battery_Charge_Energy_Total_kWh']=GEBat[0].e_battery_charge_total_2
            energy_total_output['Battery_Discharge_Energy_Total_kWh']=GEBat[0].e_battery_discharge_total_2
        else:
            energy_total_output['Battery_Charge_Energy_Total_kWh']=GEInv.e_battery_charge_total
            energy_total_output['Battery_Discharge_Energy_Total_kWh']=GEInv.e_battery_discharge_total

        energy_total_output['Self_Consumption_Energy_Total_kWh']=energy_total_output['PV_Energy_Total_kWh']-energy_total_output['Export_Energy_Total_kWh']

#Energy Today Figures
        logger.info("Getting Today Energy Data")
        energy_today_output['Battery_Throughput_Today_kWh']=GEInv.e_battery_charge_day+GEInv.e_battery_discharge_day
        energy_today_output['PV_Energy_Today_kWh']=GEInv.e_pv1_day+GEInv.e_pv2_day
        energy_today_output['Import_Energy_Today_kWh']=GEInv.e_grid_in_day
        energy_today_output['Export_Energy_Today_kWh']=GEInv.e_grid_out_day
        energy_today_output['AC_Charge_Energy_Today_kWh']=GEInv.e_inverter_in_day
        energy_today_output['Invertor_Energy_Today_kWh']=GEInv.e_inverter_out_day
        energy_today_output['Battery_Charge_Energy_Today_kWh']=GEInv.e_battery_charge_day
        energy_today_output['Battery_Discharge_Energy_Today_kWh']=GEInv.e_battery_discharge_day
        energy_today_output['Self_Consumption_Energy_Today_kWh']=energy_today_output['PV_Energy_Today_kWh']-energy_today_output['Export_Energy_Today_kWh']
                
        if GEInv.inverter_model==Model.Hybrid: 
            energy_today_output['Load_Energy_Today_kWh']=(energy_today_output['Invertor_Energy_Today_kWh']-energy_today_output['AC_Charge_Energy_Today_kWh'])-(energy_today_output['Export_Energy_Today_kWh']-energy_today_output['Import_Energy_Today_kWh'])
        else:
            energy_today_output['Load_Energy_Today_kWh']=(energy_today_output['Invertor_Energy_Today_kWh']-energy_today_output['AC_Charge_Energy_Today_kWh'])-(energy_today_output['Export_Energy_Today_kWh']-energy_today_output['Import_Energy_Today_kWh'])+energy_today_output['PV_Energy_Today_kWh']

        
############  Core Power Stats    ############

    #PV Power
        logger.info("Getting PV Power")
        PV_power_1=GEInv.p_pv1
        PV_power_2=GEInv.p_pv2
        PV_power=PV_power_1+PV_power_2
        if PV_power<15000:
            power_output['PV_Power_String_1']= PV_power_1
            power_output['PV_Power_String_2']= PV_power_2
            power_output['PV_Power']= PV_power
        power_output['PV_Voltage_String_1']=GEInv.v_pv1
        power_output['PV_Voltage_String_2']=GEInv.v_pv2

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
        power_output['Grid_Power']=grid_power
        power_output['Import_Power']=import_power
        power_output['Export_Power']=export_power

    #EPS Power
        logger.info("Getting EPS Power")
        power_output['EPS_Power']= GEInv.p_eps_backup

    #Invertor Power
        logger.info("Getting PInv Power")
        Invertor_power=GEInv.p_inverter_out
        if -6000 <= Invertor_power <= 6000:
            power_output['Invertor_Power']= Invertor_power
        if Invertor_power<0:
            power_output['AC_Charge_Power']= abs(Invertor_power)
        else:
            power_output['AC_Charge_Power']=0

    #Load Power
        logger.info("Getting Load Power")
        Load_power=GEInv.p_load_demand 
        if Load_power<15500:
            power_output['Load_Power']=Load_power

    #Self Consumption
        logger.info("Getting Self Consumption Power")
        power_output['Self_Consumption_Power']=max(Load_power - import_power,0)

    #Battery Power
        Battery_power=GEInv.p_battery 
        if Battery_power>=0:
            discharge_power=abs(Battery_power)
            charge_power=0
        elif Battery_power<=0:
            discharge_power=0
            charge_power=abs(Battery_power)
        power_output['Battery_Power']=Battery_power
        power_output['Charge_Power']=charge_power
        power_output['Discharge_Power']=discharge_power

    #SOC
        logger.info("Getting SOC")
        power_output['SOC']=GEInv.battery_percent

############  Power Flow Stats    ############

    #Solar to H/B/G
        logger.info("Getting Solar to H/B/G Power Flows")
        if PV_power>0:
            S2H=min(PV_power,Load_power)
            power_flow_output['Solar_to_House']=S2H
            S2B=max((PV_power-S2H)-export_power,0)
            power_flow_output['Solar_to_Battery']=S2B
            power_flow_output['Solar_to_Grid']=max(PV_power - S2H - S2B,0)

        else:
            power_flow_output['Solar_to_House']=0
            power_flow_output['Solar_to_Battery']=0
            power_flow_output['Solar_to_Grid']=0

    #Battery to House
        logger.info("Getting Battery to House Power Flow")
        B2H=max(discharge_power-export_power,0)
        power_flow_output['Battery_to_House']=B2H

    #Grid to Battery/House Power
        logger.info("Getting Grid to Battery/House Power Flow")
        if import_power>0:
            power_flow_output['Grid_to_Battery']=charge_power-max(PV_power-Load_power,0)
            power_flow_output['Grid_to_House']=max(import_power-charge_power,0)

        else:
            power_flow_output['Grid_to_Battery']=0
            power_flow_output['Grid_to_House']=0

    #Battery to Grid Power
        logger.info("Getting Battery to Grid Power Flow")
        if export_power>0:
            power_flow_output['Battery_to_Grid']=max(discharge_power-B2H,0)
        else:
            power_flow_output['Battery_to_Grid']=0

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
        multi_output["Invertor_Details"]=invertor

    ################ Run Holding Reg now ###################
        logger.info("Getting mode control figures")
        # Get Control Mode registers
        #shallow_charge=GEInv.battery_soc_reserve
        #self_consumption=GEInv.battery_power_mode 
        if GEInv.enable_charge==True:
            charge_schedule="enable"
        else:
            charge_schedule="disable"
        if GEInv.enable_discharge==True:
            discharge_schedule="enable"
        else:
            discharge_schedule="disable"
        #Get Battery Stat registers
        battery_reserve=GEInv.battery_discharge_min_power_reserve
        target_soc=GEInv.charge_target_soc
        if GEInv.battery_soc_reserve<=GEInv.battery_percent:
            discharge_enable="enable"
        else:
            discharge_enable="disable"
        #logger.info("Shallow Charge= "+str(shallow_charge)+" Self Consumption= "+str(self_consumption)+" Discharge Enable= "+str(discharge_enable))

        #Get Charge/Discharge Active status
        discharge_rate=GEInv.battery_discharge_limit*3
        if discharge_rate>100: discharge_rate=100
        
        charge_rate=GEInv.battery_charge_limit*3
        if charge_rate>100: charge_rate=100

        #Calculate Mode
        logger.info("Calculating Mode...")
        #Calc Mode
        
        if GEInv.battery_power_mode==1 and GEInv.enable_discharge==False and GEInv.battery_soc_reserve==4:
            #Dynamic r27=1 r110=4 r59=0
            mode="Eco"
        elif GEInv.battery_power_mode==1 and GEInv.enable_discharge==False and GEInv.battery_soc_reserve==100:
            #Dynamic r27=1 r110=4 r59=0
            mode="Eco (Paused)"
        elif GEInv.battery_power_mode==1 and GEInv.enable_discharge==True and GEInv.battery_soc_reserve==100:
            #Storage (demand) r27=1 r110=100 r59=1
            mode="Timed Demand"
        elif GEInv.battery_power_mode==0 and GEInv.enable_discharge==True and GEInv.battery_soc_reserve==100:
            #Storage (export) r27=0 r110=100 r59=1
            mode="Timed Export"
        else:
            mode="Unknown"
        
        logger.info("Mode is: " + str(mode))

        controlmode['Mode']=mode
        controlmode['Battery_Power_Reserve']=battery_reserve
        controlmode['Target_SOC']=target_soc
        controlmode['Enable_Charge_Schedule']=charge_schedule
        controlmode['Enable_Discharge_Schedule']=discharge_schedule
        controlmode['Enable_Discharge']=discharge_enable
        controlmode['Battery_Charge_Rate']=charge_rate
        controlmode['Battery_Discharge_Rate']=discharge_rate

        #Grab Timeslots
        timeslots={}
        logger.info("Getting TimeSlot data")
        timeslots['Discharge_start_time_slot_1']= GEInv.discharge_slot_1[0].isoformat()
        timeslots['Discharge_end_time_slot_1']=GEInv.discharge_slot_1[1].isoformat()
        timeslots['Discharge_start_time_slot_2']=GEInv.discharge_slot_2[0].isoformat()
        timeslots['Discharge_end_time_slot_2']=GEInv.discharge_slot_2[1].isoformat()
        timeslots['Charge_start_time_slot_1']=GEInv.charge_slot_1[0].isoformat()
        timeslots['Charge_end_time_slot_1']=GEInv.charge_slot_1[1].isoformat()
        timeslots['Charge_start_time_slot_2']=GEInv.charge_slot_2[0].isoformat()
        timeslots['Charge_end_time_slot_2']=GEInv.charge_slot_2[1].isoformat()

        #Get Invertor Details
        invertor={}
        logger.info("Getting Invertor Details")
        if GEInv.battery_type==1: batterytype="Lithium" 
        if GEInv.battery_type==0: batterytype="Lead Acid" 
        invertor['Battery_Type']=batterytype
        invertor['Battery_Capacity_kWh']=((GEInv.battery_nominal_capacity*51.2)/1000)
        invertor['Invertor_Serial_Number']=GEInv.inverter_serial_number
        invertor['Modbus_Version']=GEInv.modbus_version
        if GEInv.meter_type==1: metertype="EM115" 
        if GEInv.meter_type==0: metertype="EM418" 
        invertor['Meter_Type']=metertype
        invertor['Invertor_Type']= GEInv.inverter_model
        invertor['Invertor_Temperature']=GEInv.temp_inverter_heatsink

        #Get Battery Details
        battery={}
        batteries2={}
        logger.info("Getting Battery Details")
        for b in batteries:
            logger.info("Building battery output: "+b)
            battery={}
            battery['Battery_Serial_Number']=batteries[b]['battery_serial_number']
            battery['Battery_SOC']=batteries[b]['battery_soc']
            battery['Battery_Capacity']=batteries[b]['battery_full_capacity']
            battery['Battery_Design_Capacity']=batteries[b]['battery_design_capacity']
            battery['Battery_Remaining_Capcity']=batteries[b]['battery_remaining_capacity']
            battery['Battery_Firmware_Version']=batteries[b]['bms_firmware_version']
            battery['Battery_Cells']=batteries[b]['battery_num_cells']
            battery['Battery_Cycles']=batteries[b]['battery_num_cycles']
            battery['Battery_USB_present']=batteries[b]['usb_inserted']
            battery['Battery_Temperature']=batteries[b]['temp_bms_mos']
            battery['Battery_Voltage']=batteries[b]['v_battery_cells_sum']
            battery['Battery_Cell_1_Voltage'] = batteries[b]['v_battery_cell_01']
            battery['Battery_Cell_2_Voltage'] = batteries[b]['v_battery_cell_02']
            battery['Battery_Cell_3_Voltage'] = batteries[b]['v_battery_cell_03']
            battery['Battery_Cell_4_Voltage'] = batteries[b]['v_battery_cell_04']
            battery['Battery_Cell_5_Voltage'] = batteries[b]['v_battery_cell_05']
            battery['Battery_Cell_6_Voltage'] = batteries[b]['v_battery_cell_06']
            battery['Battery_Cell_7_Voltage'] = batteries[b]['v_battery_cell_07']
            battery['Battery_Cell_8_Voltage'] = batteries[b]['v_battery_cell_08']
            battery['Battery_Cell_9_Voltage'] = batteries[b]['v_battery_cell_09']
            battery['Battery_Cell_10_Voltage'] = batteries[b]['v_battery_cell_10']
            battery['Battery_Cell_11_Voltage'] = batteries[b]['v_battery_cell_11']
            battery['Battery_Cell_12_Voltage'] = batteries[b]['v_battery_cell_12']
            battery['Battery_Cell_13_Voltage'] = batteries[b]['v_battery_cell_13']
            battery['Battery_Cell_14_Voltage'] = batteries[b]['v_battery_cell_14']
            battery['Battery_Cell_15_Voltage'] = batteries[b]['v_battery_cell_15']
            battery['Battery_Cell_16_Voltage'] = batteries[b]['v_battery_cell_16']
            battery['Battery_Cell_1_Temperature'] = batteries[b]['temp_battery_cells_1']
            battery['Battery_Cell_2_Temperature'] = batteries[b]['temp_battery_cells_2']
            battery['Battery_Cell_3_Temperature'] = batteries[b]['temp_battery_cells_3']
            battery['Battery_Cell_4_Temperature'] = batteries[b]['temp_battery_cells_4']
            batteries2[b]=battery

        #Create multioutput and publish
        multi_output["Timeslots"]=timeslots
        multi_output["Control"]=controlmode
        multi_output["Invertor_Details"]=invertor
        multi_output["Battery_Details"]=batteries2

        with open('regCache.pkl', 'wb') as outp:
            pickle.dump(multi_output, outp, pickle.HIGHEST_PROTOCOL)
        result['result']="Success retrieving data"
    except:
        e = sys.exc_info()
        logger.error("Error processing registers: " + str(e))
        result['result']="Error processing registers: " + str(e)
        return json.dumps(result)
    return json.dumps(result, indent=4, sort_keys=True, default=str)

def runAll(full_refresh):       #Read from Invertor put in cache and publish
    #full_refresh=True
    result=getData(full_refresh)
    multi_output=pubFromPickle()
    return multi_output

def pubFromPickle():        #Publish last cached Invertor Data
    multi_output={}
    result="Success"
    if not exists("regCache.pkl"):      #if there is no cache, create it
        result=getData(True)
    if "Success" in result:
        with open('regCache.pkl', 'rb') as inp:
            multi_output= pickle.load(inp)
        SN=multi_output["Invertor_Details"]['Invertor_Serial_Number']
        publishOutput(multi_output,SN)
    else:
        multi_output['result']="Failure to find data cache"
    return json.dumps(multi_output, indent=4, sort_keys=True, default=str)

def self_run(loop_timer):
    quick_loop_timer=int(loop_timer[0])
    full_loop_timer=quick_loop_timer*3
    fullRefresh=True
    schedule.every(quick_loop_timer).seconds.do(runAll,True)
    #schedule.every(full_loop_timer).seconds.do(runAll(True))
    while True:
        schedule.run_pending()
        time.sleep(1)


####### Addiitonal Publish options can be added here. 
####### A seperate file in the folder can be added with a new publish "plugin" 
####### then referenced here with any settings required added into settings.py
def publishOutput(array,SN):
    tempoutput={}
    tempoutput=iterate_dict(array)
    if GiV_Settings.MQTT_Output:
        if GiV_Settings.first_run and GiV_Settings.HA_Auto_D:        # Home Assistant MQTT Discovery
            from HA_Discovery import HAMQTT
            HAMQTT.publish_discovery(tempoutput,SN)
            GiV_Settings.first_run=False
            updateFirstRun(SN)
        from mqtt import GivMQTT
        logger.info("Publish all to MQTT")
        if GiV_Settings.MQTT_Topic=="":
            GiV_Settings.MQTT_Topic="GivEnergy"
        GivMQTT.multi_MQTT_publish(str(GiV_Settings.MQTT_Topic+"/"+SN+"/"), tempoutput)
    if GiV_Settings.Influx_Output:
        from influx import GivInflux
        logger.info("Pushing output to Influx")
        GivInflux.publish(SN,tempoutput)

def updateFirstRun(SN):
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    rel_path = "settings.py"
    abs_file_path = os.path.join(script_dir, rel_path)
    with open(abs_file_path, "r") as f:
        lines = f.readlines()
    with open(abs_file_path, "w") as f:
        for line in lines:
            if line.strip("\n") == "    first_run = True":
                f.write("    first_run = False\n")
            else:
                f.write(line)
        f.writelines("    serial_number = \""+SN+"\"")

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
                safeoutput[p_load+"_start"]=output[0].strftime("%H:%M")
                safeoutput[p_load+"_end"]=output[1].strftime("%H:%M")
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
    globals()[sys.argv[1]]([sys.argv[2]])


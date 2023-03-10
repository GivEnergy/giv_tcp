# -*- coding: utf-8 -*-
# version 2022.08.01
from threading import Lock
from givenergy_modbus.model.plant import Plant, Inverter
#from givenergy_modbus.model.battery import Battery
from givenergy_modbus.model.inverter import Model
import sys
from pickletools import read_uint1
import json
import logging
import datetime
import pickle
import time
from GivLUT import GivLUT, GivQueue, GivClient, InvType
from settings import GiV_Settings
from os.path import exists
import os
import math
from rq import Retry

logging.getLogger("givenergy_modbus").setLevel(logging.CRITICAL)
logging.getLogger("rq.worker").setLevel(logging.CRITICAL)

sys.path.append(GiV_Settings.default_path)

givLUT = GivLUT.entity_type
logger = GivLUT.logger

cacheLock = Lock()

def invertorData(fullrefresh):
    temp={}
    try:
        plant = GivClient.getData(fullrefresh)
        Inv = plant.inverter
        Bat = plant.batteries
    except:
        return ("ERROR:-"+str(sys.exc_info()))
    return Inv,Bat

def getData(fullrefresh):  # Read from Invertor put in cache
    energy_total_output = {}
    energy_today_output = {}
    power_output = {}
    controlmode = {}
    power_flow_output = {}
    invertor = {}
    multi_output = {}
    result = {}
    temp = {}
    logger.debug("----------------------------Starting----------------------------")
    logger.debug("Getting All Registers")

    # Connect to Invertor and load data
    try:
        logger.debug("Connecting to: " + GiV_Settings.invertorIP)
        plant=GivQueue.q.enqueue(invertorData,fullrefresh,retry=Retry(max=2, interval=2))      
        while plant.result is None and plant.exc_info is None:
            time.sleep(0.5)

        # Check the ojects are not empty...
        if "ERROR" in plant.result:
            raise Exception ("Garbage or failed Invertor Response: "+ str(plant.result))

        GEInv=plant.result[0]
        GEBat=plant.result[1]
        
    except:
        e = sys.exc_info()
        consecFails(e)
        temp['result'] = "Error collecting registers: " + str(e)
        return json.dumps(temp)

    multi_output['Last_Updated_Time'] = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    multi_output['status'] = "online"
    multi_output['Time_Since_Last_Update'] = 0

    logger.debug("Invertor connection successful, registers retrieved")

    try:
        logger.debug("Beginning parsing of Inverter data")
        invertorModel= InvType
        # Determine Invertor Model and max charge rate first...

        genint=math.floor(int(GEInv.arm_firmware_version)/100)

        invertorModel.model=GEInv.inverter_model
        invertorModel.generation=GEInv.inverter_generation
        invertorModel.phase=GEInv.inverter_phases

        if GEInv.device_type_code[0] == "2":
            if GEInv.device_type_code[1:4] == "001":
                invertorModel.power = 5000
            elif GEInv.device_type_code[1:4] == "002":
                invertorModel.power = 4600
            elif GEInv.device_type_code[1:4] == "003":
                invertorModel.power = 3600
        elif GEInv.device_type_code[0] == "3":
            if GEInv.device_type_code[1:4] == "001":
                invertorModel.power = 3000
            elif GEInv.device_type_code[1:4] == "002":
                invertorModel.power = 3600
        elif GEInv.device_type_code[0] == "4":
            if GEInv.device_type_code[1:4] == "001":
                invertorModel.power = 6000
            elif GEInv.device_type_code[1:4] == "002":
                invertorModel.power = 8000
            elif GEInv.device_type_code[1:4] == "003":
                invertorModel.power = 10000
            elif GEInv.device_type_code[1:4] == "003":
                invertorModel.power = 11000
        elif GEInv.device_type_code[0] == "5":
            invertorModel.power=0
        elif GEInv.device_type_code[0] == "6":
            invertorModel.power=0
        elif GEInv.device_type_code[0] == "7":
            invertorModel.power=0
        elif GEInv.device_type_code[0] == "8":
            invertorModel.power=0

        if invertorModel.generation == 'Gen 1':
            if invertorModel.model == "AC":
                maxInvChargeRate=3000
            else:
                maxInvChargeRate=2600
        else:
            if invertorModel.model == "AC":
                maxInvChargeRate=5000
            else:
                maxInvChargeRate=3600

        # Calc max charge rate
        invertorModel.batmaxrate=min(maxInvChargeRate, (GEInv.battery_nominal_capacity*51.2)/2)


        # Total Energy Figures
        logger.debug("Getting Total Energy Data")
        energy_total_output['Export_Energy_Total_kWh'] = GEInv.e_grid_out_total
        energy_total_output['Import_Energy_Total_kWh'] = GEInv.e_grid_in_total
        energy_total_output['Invertor_Energy_Total_kWh'] = GEInv.e_inverter_out_total
        energy_total_output['PV_Energy_Total_kWh'] = GEInv.e_pv_total
        energy_total_output['AC_Charge_Energy_Total_kWh'] = GEInv.e_inverter_in_total

        if invertorModel.model == "Hybrid":
            energy_total_output['Load_Energy_Total_kWh'] = round((energy_total_output['Invertor_Energy_Total_kWh']-energy_total_output['AC_Charge_Energy_Total_kWh']) -
                                                                 (energy_total_output['Export_Energy_Total_kWh']-energy_total_output['Import_Energy_Total_kWh']), 2)
        else:
            energy_total_output['Load_Energy_Total_kWh'] = round((energy_total_output['Invertor_Energy_Total_kWh']-energy_total_output['AC_Charge_Energy_Total_kWh']) -
                                                                 (energy_total_output['Export_Energy_Total_kWh']-energy_total_output['Import_Energy_Total_kWh'])+energy_total_output['PV_Energy_Total_kWh'], 2)

        energy_total_output['Self_Consumption_Energy_Total_kWh'] = round(energy_total_output['PV_Energy_Total_kWh'], 2)-round(energy_total_output['Export_Energy_Total_kWh'], 2)


        # Energy Today Figures
        logger.debug("Getting Today Energy Data")
        energy_today_output['PV_Energy_Today_kWh'] = GEInv.e_pv1_day+GEInv.e_pv2_day
        energy_today_output['Import_Energy_Today_kWh'] = GEInv.e_grid_in_day
        energy_today_output['Export_Energy_Today_kWh'] = GEInv.e_grid_out_day
        energy_today_output['AC_Charge_Energy_Today_kWh'] = GEInv.e_inverter_in_day
        energy_today_output['Invertor_Energy_Today_kWh'] = GEInv.e_inverter_out_day
        energy_today_output['Self_Consumption_Energy_Today_kWh'] = round(energy_today_output['PV_Energy_Today_kWh'], 2)-round(energy_today_output['Export_Energy_Today_kWh'], 2)

        if invertorModel.model == "Hybrid":
            energy_today_output['Load_Energy_Today_kWh'] = round((energy_today_output['Invertor_Energy_Today_kWh']-energy_today_output['AC_Charge_Energy_Today_kWh']) -
                                                                 (energy_today_output['Export_Energy_Today_kWh']-energy_today_output['Import_Energy_Today_kWh']), 2)
        else:
            energy_today_output['Load_Energy_Today_kWh'] = round((energy_today_output['Invertor_Energy_Today_kWh']-energy_today_output['AC_Charge_Energy_Today_kWh']) -
                                                                 (energy_today_output['Export_Energy_Today_kWh']-energy_today_output['Import_Energy_Today_kWh'])+energy_today_output['PV_Energy_Today_kWh'], 2)

        checksum = 0
        for item in energy_today_output:
            checksum = checksum+energy_today_output[item]
        if checksum == 0 and GEInv.system_time.hour == 0 and GEInv.system_time.minute == 0:
            with cacheLock:
                if exists(GivLUT.regcache):
                    # remove regcache at midnight
                    logger.debug("Energy Today is Zero and its midnight so resetting regCache")
                    os.remove(GivLUT.regcache)


        ############  Core Power Stats    ############

        # PV Power
        logger.debug("Getting PV Power")
        PV_power_1 = GEInv.p_pv1
        PV_power_2 = GEInv.p_pv2
        PV_power = PV_power_1+PV_power_2
        if PV_power < 15000:
            power_output['PV_Power_String_1'] = PV_power_1
            power_output['PV_Power_String_2'] = PV_power_2
            power_output['PV_Power'] = PV_power
        power_output['PV_Voltage_String_1'] = GEInv.v_pv1
        power_output['PV_Voltage_String_2'] = GEInv.v_pv2
        power_output['PV_Current_String_1'] = GEInv.i_pv1*10
        power_output['PV_Current_String_2'] = GEInv.i_pv2*10
        power_output['Grid_Voltage'] = GEInv.v_ac1
        power_output['Grid_Current'] = GEInv.i_ac1 

        # Grid Power
        logger.debug("Getting Grid Power")
        grid_power = GEInv.p_grid_out
        if grid_power < 0:
            import_power = abs(grid_power)
            export_power = 0
        elif grid_power > 0:
            import_power = 0
            export_power = abs(grid_power)
        else:
            import_power = 0
            export_power = 0
        power_output['Grid_Power'] = grid_power
        power_output['Import_Power'] = import_power
        power_output['Export_Power'] = export_power

        # EPS Power
        logger.debug("Getting EPS Power")
        power_output['EPS_Power'] = GEInv.p_eps_backup

        # Invertor Power
        logger.debug("Getting PInv Power")
        Invertor_power = GEInv.p_inverter_out
        if -6000 <= Invertor_power <= 6000:
            power_output['Invertor_Power'] = Invertor_power
        if Invertor_power < 0:
            power_output['AC_Charge_Power'] = abs(Invertor_power)
        else:
            power_output['AC_Charge_Power'] = 0

        # Load Power
        logger.debug("Getting Load Power")
        Load_power = GEInv.p_load_demand
        if Load_power < 15500:
            power_output['Load_Power'] = Load_power

        # Self Consumption
        logger.debug("Getting Self Consumption Power")
        power_output['Self_Consumption_Power'] = max(Load_power - import_power, 0)


        ############  Power Flow Stats    ############

        # Solar to H/B/G
        logger.debug("Getting Solar to H/B/G Power Flows")
        if PV_power > 0:
            S2H = min(PV_power, Load_power)
            power_flow_output['Solar_to_House'] = S2H
            power_flow_output['Solar_to_Grid'] = export_power

        else:
            power_flow_output['Solar_to_House'] = 0
            power_flow_output['Solar_to_Grid'] = 0

        # Grid to Battery/House Power
        logger.debug("Getting Grid to Battery/House Power Flow")
        if import_power > 0:
            power_flow_output['Grid_to_House'] = import_power
        else:
            power_flow_output['Grid_to_House'] = 0

        ######## Grab output history to allow data smoothing ########

        # Grab previous data from Pickle and use it validate any outrageous changes
        with cacheLock:
            if exists(GivLUT.regcache):      # if there is a cache then grab it
                with open(GivLUT.regcache, 'rb') as inp:
                    regCacheStack = pickle.load(inp)
                    multi_output_old = regCacheStack[4]
            else:
                regCacheStack = [0, 0, 0, 0, 0]

        ######## Battery Stats only if there are batteries...  ########
        logger.debug("Getting SOC")
        if int(GiV_Settings.numBatteries) > 0:  # only do this if there are batteries
            if GEInv.battery_percent != 0:
                power_output['SOC'] = GEInv.battery_percent
            elif GEInv.battery_percent == 0 and 'multi_output_old' in locals():
                power_output['SOC'] = multi_output_old['Power']['Power']['SOC']
                logger.error("\"Battery SOC\" reported as: "+str(GEInv.battery_percent)+"% so using previous value")
            elif GEInv.battery_percent == 0 and not 'multi_output_old' in locals():
                power_output['SOC'] = 1
                logger.error("\"Battery SOC\" reported as: "+str(GEInv.battery_percent)+"% and no previou value so setting to 1%")
            power_output['SOC_kWh'] = (int(power_output['SOC'])*((GEInv.battery_nominal_capacity*51.2)/1000))/100

            # Energy Stats
            energy_today_output['Battery_Charge_Energy_Today_kWh'] = GEInv.e_battery_charge_day
            energy_today_output['Battery_Discharge_Energy_Today_kWh'] = GEInv.e_battery_discharge_day
            energy_today_output['Battery_Throughput_Today_kWh'] = GEInv.e_battery_charge_day+GEInv.e_battery_discharge_day
            energy_total_output['Battery_Throughput_Total_kWh'] = GEInv.e_battery_throughput_total
            if GEInv.e_battery_charge_total == 0 and GEInv.e_battery_discharge_total == 0:  # If no values in "nomal" registers then grab from back up registers - for some f/w versions
                energy_total_output['Battery_Charge_Energy_Total_kWh'] = GEBat[0].e_battery_charge_total_2
                energy_total_output['Battery_Discharge_Energy_Total_kWh'] = GEBat[0].e_battery_discharge_total_2
            else:
                energy_total_output['Battery_Charge_Energy_Total_kWh'] = GEInv.e_battery_charge_total
                energy_total_output['Battery_Discharge_Energy_Total_kWh'] = GEInv.e_battery_discharge_total

            # Battery Power
            Battery_power = GEInv.p_battery
            if Battery_power >= 0:
                discharge_power = abs(Battery_power)
                charge_power = 0
            elif Battery_power <= 0:
                discharge_power = 0
                charge_power = abs(Battery_power)
            power_output['Battery_Power'] = Battery_power
            power_output['Charge_Power'] = charge_power
            power_output['Discharge_Power'] = discharge_power

            # Power flows
            logger.debug("Getting Solar to H/B/G Power Flows")
            if PV_power > 0:
                S2H = min(PV_power, Load_power)
                power_flow_output['Solar_to_House'] = S2H
                S2B = max((PV_power-S2H)-export_power, 0)
                power_flow_output['Solar_to_Battery'] = S2B
                power_flow_output['Solar_to_Grid'] = max(PV_power - S2H - S2B, 0)

            else:
                power_flow_output['Solar_to_House'] = 0
                power_flow_output['Solar_to_Battery'] = 0
                power_flow_output['Solar_to_Grid'] = 0

            # Battery to House
            logger.debug("Getting Battery to House Power Flow")
            B2H = max(discharge_power-export_power, 0)
            power_flow_output['Battery_to_House'] = B2H

            # Grid to Battery/House Power
            logger.debug("Getting Grid to Battery/House Power Flow")
            if import_power > 0:
                power_flow_output['Grid_to_Battery'] = charge_power-max(PV_power-Load_power, 0)
                power_flow_output['Grid_to_House'] = max(import_power-charge_power, 0)

            else:
                power_flow_output['Grid_to_Battery'] = 0
                power_flow_output['Grid_to_House'] = 0

            # Battery to Grid Power
            logger.debug("Getting Battery to Grid Power Flow")
            if export_power > 0:
                power_flow_output['Battery_to_Grid'] = max(discharge_power-B2H, 0)
            else:
                power_flow_output['Battery_to_Grid'] = 0

        # Check for all zeros
        checksum = 0
        for item in energy_total_output:
            checksum = checksum+energy_total_output[item]
        if checksum == 0:
            raise ValueError("All zeros returned by Invertor, skipping update")


        ######## Get Control Data ########
        logger.debug("Getting mode control figures")
        # Get Control Mode registers
        if GEInv.enable_charge == True:
            charge_schedule = "enable"
        else:
            charge_schedule = "disable"
        if GEInv.enable_discharge == True:
            discharge_schedule = "enable"
        else:
            discharge_schedule = "disable"
        #Get Battery Stat registers
        #battery_reserve = GEInv.battery_discharge_min_power_reserve

        battery_reserve = GEInv.battery_soc_reserve

        # Save a non-100 battery_reserve value for use later in restoring after resuming Eco/Dynamic mode
        # Check to see if we have a saved value already...
        saved_battery_reserve = 0
        if exists(GivLUT.reservepkl):
            with open(GivLUT.reservepkl, 'rb') as inp:
                saved_battery_reserve = pickle.load(inp)

        # Has the saved value changed from the current value? Only carry on if it is different
        if saved_battery_reserve != battery_reserve:
            if battery_reserve < 100:
                try:
                    # Pickle the value to use later...
                    with open(GivLUT.reservepkl, 'wb') as outp:
                        pickle.dump(battery_reserve, outp, pickle.HIGHEST_PROTOCOL)
                    logger.debug ("Saving the battery reserve percentage for later: " + str(battery_reserve))
                except:
                    e = sys.exc_info()
                    temp['result'] = "Saving the battery reserve for later failed: " + str(e)
                    logger.error (temp['result'])
            else:
                # Value is 100, we don't want to save 100 because we need to restore to a value FROM 100...
                logger.debug ("Saving the battery reserve percentage for later: no need, it's currently at 100 and we don't want to save that.")

        battery_cutoff = GEInv.battery_discharge_min_power_reserve
        target_soc = GEInv.charge_target_soc
        if GEInv.battery_soc_reserve <= GEInv.battery_percent:
            discharge_enable = "enable"
        else:
            discharge_enable = "disable"

        # Get Charge/Discharge Active status
        discharge_rate = int(min((GEInv.battery_discharge_limit/100)*(GEInv.battery_nominal_capacity*51.2), invertorModel.batmaxrate))
        charge_rate = int(min((GEInv.battery_charge_limit/100)*(GEInv.battery_nominal_capacity*51.2), invertorModel.batmaxrate))

        # Calculate Mode
        logger.debug("Calculating Mode...")
        # Calc Mode

        if GEInv.battery_power_mode == 1 and GEInv.enable_discharge == False and GEInv.battery_soc_reserve != 100:
            # Dynamic r27=1 r110=4 r59=0
            mode = "Eco"
        elif GEInv.battery_power_mode == 1 and GEInv.enable_discharge == False and GEInv.battery_soc_reserve == 100:
            # Dynamic r27=1 r110=4 r59=0
            mode = "Eco (Paused)"
        elif GEInv.battery_power_mode == 1 and GEInv.enable_discharge == True and GEInv.battery_soc_reserve == 100:
            # Storage (demand) r27=1 r110=100 r59=1
            mode = "Timed Demand"
        elif GEInv.battery_power_mode == 0 and GEInv.enable_discharge == True and GEInv.battery_soc_reserve == 100:
            # Storage (export) r27=0 r110=100 r59=1
            mode = "Timed Export"
        else:
            mode = "Unknown"

        logger.debug("Mode is: " + str(mode))

        controlmode['Mode'] = mode
        controlmode['Battery_Power_Reserve'] = battery_reserve
        controlmode['Battery_Power_Cutoff'] = battery_cutoff
        controlmode['Target_SOC'] = target_soc
        controlmode['Enable_Charge_Schedule'] = charge_schedule
        controlmode['Enable_Discharge_Schedule'] = discharge_schedule
        controlmode['Enable_Discharge'] = discharge_enable
        controlmode['Battery_Charge_Rate'] = charge_rate
        controlmode['Battery_Discharge_Rate'] = discharge_rate
        if not isinstance(regCacheStack[4], int):
            if "Temp_Pause_Discharge" in regCacheStack[4]:
                controlmode['Temp_Pause_Discharge'] = regCacheStack[4]["Control"]["Temp_Pause_Discharge"]
            if "Temp_Pause_Charge" in regCacheStack[4]:
                controlmode['Temp_Pause_Charge'] = regCacheStack[4]["Control"]["Temp_Pause_Charge"]
        else:
            controlmode['Temp_Pause_Charge'] = "Normal"
            controlmode['Temp_Pause_Discharge'] = "Normal"

        if exists(".FCRunning"):
            logger.debug("Force Charge is Running")
            controlmode['Force_Charge'] = "Running"
        else:
            controlmode['Force_Charge'] = "Normal"
        if exists(".FERunning"):
            logger.debug("Force_Export is Running")
            controlmode['Force_Export'] = "Running"
        else:
            controlmode['Force_Export'] = "Normal"
        if exists(".tpcRunning"):
            logger.debug("Temp Pause Charge is Running")
            controlmode['Temp_Pause_Charge'] = "Running"
        else:
            controlmode['Temp_Pause_Charge'] = "Normal"
        if exists(".tpdRunning"):
            logger.debug("Temp_Pause_Discharge is Running")
            controlmode['Temp_Pause_Discharge'] = "Running"
        else:
            controlmode['Temp_Pause_Discharge'] = "Normal"

        ######## Grab Timeslots ########
        timeslots = {}
        logger.debug("Getting TimeSlot data")
        timeslots['Discharge_start_time_slot_1'] = GEInv.discharge_slot_1[0].isoformat()
        timeslots['Discharge_end_time_slot_1'] = GEInv.discharge_slot_1[1].isoformat()
        timeslots['Discharge_start_time_slot_2'] = GEInv.discharge_slot_2[0].isoformat()
        timeslots['Discharge_end_time_slot_2'] = GEInv.discharge_slot_2[1].isoformat()
        timeslots['Charge_start_time_slot_1'] = GEInv.charge_slot_1[0].isoformat()
        timeslots['Charge_end_time_slot_1'] = GEInv.charge_slot_1[1].isoformat()
        timeslots['Charge_start_time_slot_2'] = GEInv.charge_slot_2[0].isoformat()
        timeslots['Charge_end_time_slot_2'] = GEInv.charge_slot_2[1].isoformat()

        ######## Get Invertor Details ########
        invertor = {}
        logger.debug("Getting Invertor Details")
        if GEInv.battery_type == 1:
            batterytype = "Lithium"
        if GEInv.battery_type == 0:
            batterytype = "Lead Acid"
        invertor['Battery_Type'] = batterytype
        invertor['Battery_Capacity_kWh'] = ((GEInv.battery_nominal_capacity*51.2)/1000)
        invertor['Invertor_Serial_Number'] = GEInv.inverter_serial_number
        invertor['Modbus_Version'] = GEInv.modbus_version
        invertor['Invertor_Firmware'] = GEInv.arm_firmware_version
        invertor['Invertor_Time'] = GEInv.system_time
        if GEInv.meter_type == 1:
            metertype = "EM115"
        if GEInv.meter_type == 0:
            metertype = "EM418"
        invertor['Meter_Type'] = metertype
        invertor['Invertor_Type'] = invertorModel.generation + " " + invertorModel.model
        invertor['Invertor_Max_Rate'] = invertorModel.batmaxrate
        invertor['Invertor_Temperature'] = GEInv.temp_inverter_heatsink

        ######## Get Battery Details ########
        battery = {}
        batteries2 = {}
        logger.debug("Getting Battery Details")
        for b in GEBat:
            if b.battery_serial_number.upper().isupper():          # Check for empty battery object responses and only process if they are complete (have a serial number)
                logger.debug("Building battery output: ")
                battery = {}
                battery['Battery_Serial_Number'] = b.battery_serial_number
                if b.battery_soc != 0:
                    battery['Battery_SOC'] = b.battery_soc
                elif b.battery_soc == 0 and 'multi_output_old' in locals():
                    battery['Battery_SOC'] = multi_output_old['Battery_Details'][b.battery_serial_number]['Battery_SOC']
                elif b.battery_soc == 0 and not 'multi_output_old' in locals():
                    battery['Battery_SOC'] = 1
                battery['Battery_Capacity'] = b.battery_full_capacity
                battery['Battery_Design_Capacity'] = b.battery_design_capacity
                battery['Battery_Remaining_Capacity'] = b.battery_remaining_capacity
                battery['Battery_Firmware_Version'] = b.bms_firmware_version
                battery['Battery_Cells'] = b.battery_num_cells
                battery['Battery_Cycles'] = b.battery_num_cycles
                battery['Battery_USB_present'] = b.usb_inserted
                battery['Battery_Temperature'] = b.temp_bms_mos
                battery['Battery_Voltage'] = b.v_battery_cells_sum
                battery['Battery_Cell_1_Voltage'] = b.v_battery_cell_01
                battery['Battery_Cell_2_Voltage'] = b.v_battery_cell_02
                battery['Battery_Cell_3_Voltage'] = b.v_battery_cell_03
                battery['Battery_Cell_4_Voltage'] = b.v_battery_cell_04
                battery['Battery_Cell_5_Voltage'] = b.v_battery_cell_05
                battery['Battery_Cell_6_Voltage'] = b.v_battery_cell_06
                battery['Battery_Cell_7_Voltage'] = b.v_battery_cell_07
                battery['Battery_Cell_8_Voltage'] = b.v_battery_cell_08
                battery['Battery_Cell_9_Voltage'] = b.v_battery_cell_09
                battery['Battery_Cell_10_Voltage'] = b.v_battery_cell_10
                battery['Battery_Cell_11_Voltage'] = b.v_battery_cell_11
                battery['Battery_Cell_12_Voltage'] = b.v_battery_cell_12
                battery['Battery_Cell_13_Voltage'] = b.v_battery_cell_13
                battery['Battery_Cell_14_Voltage'] = b.v_battery_cell_14
                battery['Battery_Cell_15_Voltage'] = b.v_battery_cell_15
                battery['Battery_Cell_16_Voltage'] = b.v_battery_cell_16
                battery['Battery_Cell_1_Temperature'] = b.temp_battery_cells_1
                battery['Battery_Cell_2_Temperature'] = b.temp_battery_cells_2
                battery['Battery_Cell_3_Temperature'] = b.temp_battery_cells_3
                battery['Battery_Cell_4_Temperature'] = b.temp_battery_cells_4
                batteries2[b.battery_serial_number] = battery
                logger.debug("Battery "+str(b.battery_serial_number)+" added")
            else:
                logger.error("Battery Object empty so skipping")

        ######## Create multioutput and publish #########
        energy = {}
        energy["Today"] = energy_today_output
        energy["Total"] = energy_total_output
        power = {}
        power["Power"] = power_output
        power["Flows"] = power_flow_output
        multi_output["Power"] = power
        multi_output["Invertor_Details"] = invertor
        multi_output["Energy"] = energy
        multi_output["Timeslots"] = timeslots
        multi_output["Control"] = controlmode
        multi_output["Invertor_Details"] = invertor
        multi_output["Battery_Details"] = batteries2
        if GiV_Settings.Print_Raw_Registers:
            raw = {}
            raw["invertor"] = GEInv.dict()
            multi_output['raw'] = raw

        ######### Section where post processing of multi_ouput functions are called ###########

        # run ppkwh stats on firstrun and every half hour
        if 'multi_output_old' in locals():
            multi_output = ratecalcs(multi_output, multi_output_old)
        else:
            multi_output = ratecalcs(multi_output, multi_output)

        multi_output = calcBatteryValue(multi_output)

        if 'multi_output_old' in locals():
            multi_output = dataCleansing(multi_output, regCacheStack[4])
        # only update cache if its the same set of keys as previous (don't update if data missing)

        if 'multi_output_old' in locals():
            MOList = dicttoList(multi_output)
            MOOList = dicttoList(multi_output_old)
            dataDiff = set(MOOList) - set(MOList)
            if len(dataDiff) > 0:
                for key in dataDiff:
                    logger.error(str(key)+" is missing from new data, publishing all other data")

        # Add new data to the stack
        regCacheStack.pop(0)
        regCacheStack.append(multi_output)

        # Get lastupdate from pickle if it exists
        with cacheLock:
            if exists(GivLUT.lastupdate):
                with open(GivLUT.lastupdate, 'rb') as inp:
                    previousUpdate = pickle.load(inp)
                timediff = datetime.datetime.fromisoformat(multi_output['Last_Updated_Time'])-datetime.datetime.fromisoformat(previousUpdate)
                multi_output['Time_Since_Last_Update'] = (((timediff.seconds*1000000)+timediff.microseconds)/1000000)

            # Save new time to pickle
            with open(GivLUT.lastupdate, 'wb') as outp:
                pickle.dump(multi_output['Last_Updated_Time'], outp, pickle.HIGHEST_PROTOCOL)

            # Save new data to Pickle
            with open(GivLUT.regcache, 'wb') as outp:
                pickle.dump(regCacheStack, outp, pickle.HIGHEST_PROTOCOL)
                
            logger.debug("Successfully retrieved from: " + GiV_Settings.invertorIP)

            result['result'] = "Success retrieving data"

            # Success, so delete oldDataCount
            if exists(GivLUT.oldDataCount):
                os.remove(GivLUT.oldDataCount)

    except:
        e = sys.exc_info()
        consecFails(e)
        logger.error("Invertor Update failed so using last known good data from cache")
        result['result'] = "Error processing registers: " + str(e)
        return json.dumps(result)
    return json.dumps(result, indent=4, sort_keys=True, default=str)


def consecFails(e):
    with cacheLock:
        if exists(GivLUT.oldDataCount):
            with open(GivLUT.oldDataCount, 'rb') as inp:
                oldDataCount= pickle.load(inp)
            oldDataCount = oldDataCount + 1
            if oldDataCount > 2:
                logger.error("Consecutive failure count= "+str(oldDataCount) +" -- "+ str(e))
        else:
            oldDataCount = 1
        if oldDataCount>10:
            #10 error in a row so delete regCache data
            logger.error("10 failed invertor reads in a row so removing regCache to force update...")
            if exists(GivLUT.regcache):
                os.remove(GivLUT.regcache)
            if exists(GivLUT.batterypkl):
                os.remove(GivLUT.batterypkl)
            if exists(GivLUT.oldDataCount):
                os.remove(GivLUT.oldDataCount)
        else:
            with open(GivLUT.oldDataCount, 'wb') as outp:
                pickle.dump(oldDataCount, outp, pickle.HIGHEST_PROTOCOL)



def runAll(full_refresh):  # Read from Invertor put in cache and publish
    # full_refresh=True
    from read import getData
    result=getData(full_refresh)
    # Step here to validate data against previous pickle?
    multi_output = pubFromPickle()
    return multi_output


def pubFromJSON():
    temp = open('GivTCP\\testdata.json')
    data = json.load(temp)
    SN = data["Invertor_Details"]['Invertor_Serial_Number']
    publishOutput(data, SN)


def pubFromPickle():  # Publish last cached Invertor Data
    multi_output = {}
    result = "Success"
    if not exists(GivLUT.regcache):  # if there is no cache, create it
        result = "Please get data from Inverter first, either by calling runAll or waiting until the self-run has completed"
    if "Success" in result:
        with cacheLock:
            with open(GivLUT.regcache, 'rb') as inp:
                regCacheStack = pickle.load(inp)
                multi_output = regCacheStack[4]
        SN = multi_output["Invertor_Details"]['Invertor_Serial_Number']
        publishOutput(multi_output, SN)
    else:
        multi_output['result'] = result
    return json.dumps(multi_output, indent=4, sort_keys=True, default=str)

def getCache():     # Get latest cache data and return it (for use in REST)
    multi_output={}
    with open(GivLUT.regcache, 'rb') as inp:
        regCacheStack = pickle.load(inp)
        multi_output = regCacheStack[4]
    return multi_output

def self_run2():
    counter = 0
    runAll("True")
    while True:
        counter = counter+1
        if exists(GivLUT.forcefullrefresh):
            runAll("True")
            os.remove(GivLUT.forcefullrefresh)
            counter = 0
        elif counter == 20:
            counter = 0
            runAll("True")
        else:
            runAll("False")
        time.sleep(GiV_Settings.self_run_timer)


# Addiitonal Publish options can be added here.
# A seperate file in the folder can be added with a new publish "plugin"
# then referenced here with any settings required added into settings.py
def publishOutput(array, SN):
    tempoutput = {}
    tempoutput = iterate_dict(array)

    if GiV_Settings.MQTT_Output:
        if GiV_Settings.first_run and GiV_Settings.HA_Auto_D:        # Home Assistant MQTT Discovery
            logger.critical("Publishing Home Assistant Discovery messages")
            from HA_Discovery import HAMQTT
            HAMQTT.publish_discovery(tempoutput, SN)
            GiV_Settings.first_run = False
            updateFirstRun(SN)
        from mqtt import GivMQTT
        logger.debug("Publish all to MQTT")
        if GiV_Settings.MQTT_Topic == "":
            GiV_Settings.MQTT_Topic = "GivEnergy"
        GivMQTT.multi_MQTT_publish(str(GiV_Settings.MQTT_Topic+"/"+SN+"/"), tempoutput)
    if GiV_Settings.Influx_Output:
        from influx import GivInflux
        logger.debug("Pushing output to Influx")
        GivInflux.publish(SN, tempoutput)


def updateFirstRun(SN):
    isSN = False
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    rel_path = "settings.py"
    abs_file_path = os.path.join(script_dir, rel_path)
    with open(abs_file_path, "r") as f:
        lines = f.readlines()
    with open(abs_file_path, "w") as f:
        for line in lines:
            if line.strip("\n") == "    first_run= True":
                f.write("    first_run= False\n")
            else:
                f.write(line)
            if "serial_number" in line:
                isSN = True

        if not isSN:
            f.writelines("    serial_number = \""+SN+"\"\n")  # only add SN if its not there


def iterate_dict(array):        # Create a publish safe version of the output (convert non string or int datapoints)
    safeoutput = {}
    for p_load in array:
        output = array[p_load]
        if isinstance(output, dict):
            temp = iterate_dict(output)
            safeoutput[p_load] = temp
            logger.debug('Dealt with '+p_load)
        elif isinstance(output, tuple):
            if "slot" in str(p_load):
                logger.debug('Converting Timeslots to publish safe string')
                safeoutput[p_load+"_start"] = output[0].strftime("%H:%M")
                safeoutput[p_load+"_end"] = output[1].strftime("%H:%M")
            else:
                # Deal with other tuples _ Print each value
                for index, key in enumerate(output):
                    logger.debug('Converting Tuple to multiple publish safe strings')
                    safeoutput[p_load+"_"+str(index)] = str(key)
        elif isinstance(output, datetime.datetime):
            logger.debug('Converting datetime to publish safe string')
            safeoutput[p_load] = output.strftime("%d-%m-%Y %H:%M:%S")
        elif isinstance(output, datetime.time):
            logger.debug('Converting time to publish safe string')
            safeoutput[p_load] = output.strftime("%H:%M")
        elif isinstance(output, Model):
            logger.debug('Converting time to publish safe string')
            safeoutput[p_load] = output.name
        elif isinstance(output, float):
            safeoutput[p_load] = round(output, 3)
        else:
            safeoutput[p_load] = output
    return(safeoutput)


def ratecalcs(multi_output, multi_output_old):
    rate_data = {}
    dayRateStart = datetime.datetime.strptime(GiV_Settings.day_rate_start, '%H:%M')
    nightRateStart = datetime.datetime.strptime(GiV_Settings.night_rate_start, '%H:%M')
    night_start = datetime.datetime.combine(datetime.datetime.now(GivLUT.timezone).date(),nightRateStart.time()).replace(tzinfo=GivLUT.timezone)
    logger.debug("Night Start= "+datetime.datetime.strftime(night_start, '%c'))
    day_start = datetime.datetime.combine(datetime.datetime.now(GivLUT.timezone).date(),dayRateStart.time()).replace(tzinfo=GivLUT.timezone)
    logger.debug("Day Start= "+datetime.datetime.strftime(day_start, '%c'))
    # check if pickle data exists:
    if exists(GivLUT.ratedata):
        with open(GivLUT.ratedata, 'rb') as inp:
            rate_data = pickle.load(inp)
    else:
        logger.debug("No rate_data exists, so creating new baseline")

    import_energy = multi_output['Energy']['Total']['Import_Energy_Total_kWh']
    import_energy_old = multi_output_old['Energy']['Total']['Import_Energy_Total_kWh']

    # if midnight then reset costs
    if datetime.datetime.now(GivLUT.timezone).hour == 0 and datetime.datetime.now(GivLUT.timezone).minute == 0:
        logger.critical("Midnight, so resetting Day/Night stats...")
        rate_data['Night_Cost'] = 0.00
        rate_data['Day_Cost'] = 0.00
        rate_data['Night_Energy_kWh'] = 0.00
        rate_data['Day_Energy_kWh'] = 0.00
        rate_data['Day_Start_Energy_kWh'] = import_energy
        rate_data['Night_Start_Energy_kWh'] = import_energy

    if GiV_Settings.dynamic_tariff == False:     ## If we use externally triggered rates then don't do the time check but assume the rate files are set elsewhere (default to Day if not set)
        if dayRateStart.hour == datetime.datetime.now(GivLUT.timezone).hour and dayRateStart.minute == datetime.datetime.now(GivLUT.timezone).minute:
            #Save current Total stats as baseline
            logger.info("Saving current energy stats at start of day rate tariff")
            rate_data['Day_Start_Energy_kWh'] = import_energy
            open(GivLUT.dayRate, 'w').close()
            if exists(GivLUT.nightRate):
                logger.debug(".nightRate exists so deleting it")
                os.remove(GivLUT.nightRate)

        elif nightRateStart.hour == datetime.datetime.now(GivLUT.timezone).hour and nightRateStart.minute == datetime.datetime.now(GivLUT.timezone).minute:
            #Save current Total stats as baseline
            logger.info("Saving current energy stats at start of night rate tariff")
            rate_data['Night_Start_Energy_kWh'] = import_energy
            open(GivLUT.nightRate, 'w').close()
            if exists(GivLUT.dayRate):
                logger.debug(".dayRate exists so deleting it")
                os.remove(GivLUT.dayRate)  
    else:
        # Otherwise check to see if dynamic trigger has been recieved to change rate type
        if exists(GivLUT.nightRateRequest):
            os.remove(GivLUT.nightRateRequest)
            if not exists(GivLUT.nightRate):
                logger.info("Saving current energy stats at start of night rate tariff (Dynamic)")
                rate_data['Night_Start_Energy_kWh'] = import_energy
                open(GivLUT.nightRate, 'w').close()
                if exists(GivLUT.dayRate):
                    logger.debug(".dayRate exists so deleting it")
                    os.remove(GivLUT.dayRate)

        elif exists(GivLUT.dayRateRequest):
            os.remove(GivLUT.dayRateRequest)
            if not exists(GivLUT.dayRate):
                logger.info("Saving current energy stats at start of day rate tariff (Dynamic)")
                rate_data['Day_Start_Energy_kWh'] = import_energy
                open(GivLUT.dayRate, 'w').close()
                if exists(GivLUT.nightRate):
                    logger.debug(".nightRate exists so deleting it")
                    os.remove(GivLUT.nightRate)  

    if not exists(GivLUT.nightRate) and not exists(GivLUT.dayRate): #Default to Day if not previously set
        logger.info("No day/Night rate info so reverting to day")
        open(GivLUT.dayRate, 'w').close()

    if exists(GivLUT.dayRate):
        rate_data['Current_Rate_Type'] = "Day"
        rate_data['Current_Rate'] = GiV_Settings.day_rate
        logger.debug("Setting Rate to Day")
    else:
        rate_data['Current_Rate_Type'] = "Night"
        rate_data['Current_Rate'] = GiV_Settings.night_rate
        logger.debug("Setting Rate to Night")

#       If no data then just save current import as base data
    if not('Night_Start_Energy_kWh' in rate_data):
        logger.debug("No Night Start Energy so setting it to: "+str(import_energy))
        rate_data['Night_Start_Energy_kWh'] = import_energy
    if not('Day_Start_Energy_kWh' in rate_data):
        logger.debug("No Day Start Energy so setting it to: "+str(import_energy))
        rate_data['Day_Start_Energy_kWh'] = import_energy
    if not('Night_Energy_kWh' in rate_data):
        rate_data['Night_Energy_kWh'] = 0.00
    if not('Day_Energy_kWh' in rate_data):
        rate_data['Day_Energy_kWh'] = 0.00
    if not('Night_Cost' in rate_data):
        rate_data['Night_Cost'] = 0.00
    if not('Day_Cost' in rate_data):
        rate_data['Day_Cost'] = 0.00
    if not('Day_Rate' in rate_data):
        rate_data['Day_Rate'] = GiV_Settings.day_rate
    if not('Night_Rate' in rate_data):
        rate_data['Night_Rate'] = GiV_Settings.night_rate
    if not('Export_Rate' in rate_data):
        rate_data['Export_Rate'] = GiV_Settings.export_rate

    # now calc the difference for each value between the correct start pickle and now
    if import_energy>import_energy_old: # Only run if there has been more import
        logger.debug("Imported more energy so calculating current tariff costs: "+str(import_energy_old)+" -> "+str(import_energy))
    
#        if night_start <= datetime.datetime.now(GivLUT.timezone) < day_start:
        if exists(GivLUT.nightRate):
            logger.debug("Current Tariff is Night, calculating stats...")
            rate_data['Night_Energy_kWh'] = import_energy-rate_data['Night_Start_Energy_kWh']
            logger.debug("Night_Energy_kWh=" +str(import_energy)+" - "+str(rate_data['Night_Start_Energy_kWh']))
            rate_data['Night_Cost'] = float(rate_data['Night_Energy_kWh'])*float(GiV_Settings.night_rate)
            logger.debug("Night_Cost= "+str(rate_data['Night_Energy_kWh'])+"kWh x £"+str(float(GiV_Settings.night_rate))+"/kWh = £"+str(rate_data['Night_Cost']))
            rate_data['Current_Rate'] = GiV_Settings.night_rate
        else:
            logger.debug("Current Tariff is Day, calculating stats...")
            rate_data['Day_Energy_kWh'] = import_energy-rate_data['Day_Start_Energy_kWh']
            logger.debug("Day_Energy_kWh=" + str(import_energy)+" - "+str(rate_data['Day_Start_Energy_kWh']))
            rate_data['Day_Cost'] = float(rate_data['Day_Energy_kWh'])*float(GiV_Settings.day_rate)
            logger.debug("Day_Cost= "+str(rate_data['Day_Energy_kWh'])+"kWh x £"+str(float(GiV_Settings.day_rate))+"/kWh = £"+str(rate_data['Day_Cost']))
            rate_data['Current_Rate'] = GiV_Settings.day_rate

        if (multi_output['Energy']['Today']['Load_Energy_Today_kWh']) != 0:
            rate_data['Import_ppkwh_Today'] = round((rate_data['Day_Cost']+rate_data['Night_Cost'])/(multi_output['Energy']['Today']['Import_Energy_Today_kWh']), 3)
            logger.debug("Import_ppkwh_Today= (£"+str(rate_data['Day_Cost'])+" + £"+str(rate_data['Night_Cost'])+") \ "+str(multi_output['Energy']['Today']['Load_Energy_Today_kWh'])+"kWh = £"+str(rate_data['Import_ppkwh_Today'])+"/kWh")

    multi_output['Energy']['Rates'] = rate_data

    # dump current data to Pickle
    with open(GivLUT.ratedata, 'wb') as outp:
        pickle.dump(rate_data, outp, pickle.HIGHEST_PROTOCOL)

    return (multi_output)


def dataCleansing(data, regCacheStack):
    logger.debug("Running the data cleansing process")
    # iterate multi_output to get each end result dict.
    # Loop that dict to validate against
    new_multi_output = loop_dict(data, regCacheStack, data["Last_Updated_Time"])
    return(new_multi_output)


def dicttoList(array):
    safeoutput = []
    # finaloutput={}
    # arrayout={}
    for p_load in array:
        output = array[p_load]
        safeoutput.append(p_load)
        if isinstance(output, dict):
            safeoutput = safeoutput+dicttoList(output)
    return(safeoutput)


def loop_dict(array, regCacheStack, lastUpdate):
    safeoutput = {}
    # finaloutput={}
    # arrayout={}
    for p_load in array:
        output = array[p_load]
        if p_load == "raw":  # skip data cleansing for raw data
            safeoutput[p_load] = output
            continue
        if isinstance(output, dict):
            if p_load in regCacheStack:
                temp = loop_dict(output, regCacheStack[p_load], lastUpdate)
                safeoutput[p_load] = temp
                logger.debug('Data cleansed for: '+str(p_load))
            else:
                logger.debug(str(p_load)+" has no data in the cache so using new value.")
                safeoutput[p_load] = output
        else:
            # run datasmoother on the data item
            # only run if old data exists otherwise return the existing value
            if p_load in regCacheStack:
                safeoutput[p_load] = dataSmoother2([p_load, output], [p_load, regCacheStack[p_load]], lastUpdate)
            else:
                logger.debug(p_load+" has no data in the cache so using new value.")
                safeoutput[p_load] = output
    return(safeoutput)

def dataSmoother2(dataNew, dataOld, lastUpdate):
    # perform test to validate data and smooth out spikes
    newData = dataNew[1]
    oldData = dataOld[1]
    name = dataNew[0]
    lookup = givLUT[name]
    if GiV_Settings.data_smoother.lower() == "high":
        smoothRate = 0.25
    elif GiV_Settings.data_smoother.lower() == "medium":
        smoothRate = 0.35
    elif GiV_Settings.data_smoother.lower() == "none":
        return(newData)
    else:
        smoothRate = 0.50
    if isinstance(newData, int) or isinstance(newData, float):
        if oldData != 0:
            then = datetime.datetime.fromisoformat(lastUpdate)
            now = datetime.datetime.now(GivLUT.timezone)
    ### Run checks against the conditions in GivLUT ###
            if now.minute == 0 and now.hour == 0 and "Today" in name:  # Treat Today stats as a special case
                logger.debug("Midnight and "+str(name)+" so accepting value as is")
                return (dataNew)
            if newData < float(lookup.min) or newData > float(lookup.max):  # If outside min and max ranges
                logger.debug(str(name)+" is outside of allowable bounds so using old value: "+str(newData))
                return(oldData)
            if newData == 0 and not lookup.allowZero:  # if zero and not allowed to be
                logger.debug(str(name)+" is Zero so using old value")
                return(oldData)
            if lookup.smooth:     # apply smoothing if required
                if newData != oldData:  # Only if its not the same
                    timeDelta = (now-then).total_seconds()
                    dataDelta = abs(newData-oldData)/oldData
                    if dataDelta > smoothRate and timeDelta < 60:
                        logger.debug(str(name)+" jumped too far in a single read: "+str(oldData)+"->"+str(newData)+" so using previous value")
                        return(oldData)
            if lookup.onlyIncrease:  # if data can only increase then check
                if (oldData-newData) > 0.11:
                    logger.debug(str(name)+" has decreased so using old value")
                    return oldData
    return(newData)


def calcBatteryValue(multi_output):
    # get current data from read pickle
    batterystats = {}
    if exists(GivLUT.batterypkl):
        with open(GivLUT.batterypkl, 'rb') as inp:
            batterystats = pickle.load(inp)
    else:       # if no old AC charge, then set it to now and zero out value and ppkwh
        logger.critical("First time running so saving AC Charge status")
        batterystats['AC Charge last'] = float(multi_output['Energy']['Total']['AC_Charge_Energy_Total_kWh'])
        batterystats['Battery_Value'] = 0
        batterystats['Battery_ppkwh'] = 0
        batterystats['Battery_kWh_old'] = multi_output['Power']['Power']['SOC_kWh']

    if GiV_Settings.first_run or datetime.datetime.now(GivLUT.timezone).minute == 59 or datetime.datetime.now(GivLUT.timezone).minute == 29:
        if not exists(GivLUT.ppkwhtouch) and exists(GivLUT.batterypkl):      # only run this if there is no touchfile but there is a battery stat
            battery_kwh = multi_output['Power']['Power']['SOC_kWh']
            ac_charge = float(multi_output['Energy']['Total']['AC_Charge_Energy_Total_kWh'])-float(batterystats['AC Charge last'])
            logger.debug("Battery_kWh has gone from: "+str(batterystats['Battery_kWh_old'])+" -> "+str(battery_kwh))
            if float(battery_kwh) > float(batterystats['Battery_kWh_old']):
                logger.debug("Battery has been charged in the last 30mins so recalculating battery value and ppkwh: ")
                batVal = batterystats['Battery_Value']
                money_in = round(ac_charge*float(multi_output['Energy']['Rates']['Current_Rate']), 2)
                logger.debug("Money_in= "+str(round(ac_charge, 2))+"kWh * £"+str(float(multi_output['Energy']['Rates']['Current_Rate']))+"/kWh = £"+str(money_in))
                batterystats['Battery_Value'] = round(float(batterystats['Battery_Value']) + money_in, 3)
                logger.debug("Battery_Value= £"+str(float(batVal))+" + £"+str(money_in)+" = £"+str(batterystats['Battery_Value']))
                batterystats['Battery_ppkwh'] = round(batterystats['Battery_Value']/battery_kwh, 3)
                logger.debug("Battery_ppkWh= £"+str(batterystats['Battery_Value'])+" / "+str(battery_kwh)+"kWh = £"+str(batterystats['Battery_ppkwh'])+"/kWh")
            else:
                logger.debug("No battery charge in the last 30 mins so adjusting Battery Value")
                batterystats['Battery_Value'] = round(float(batterystats['Battery_ppkwh'])*battery_kwh, 3)
                logger.debug("Battery_Value= £"+str(round(float(batterystats['Battery_ppkwh']), 2))+"/kWh * "+str(round(battery_kwh, 2))+"kWh = £"+str(batterystats['Battery_Value']))
            # set the new "old" AC Charge stat to current AC Charge kwh
            batterystats['AC Charge last'] = float(multi_output['Energy']['Total']['AC_Charge_Energy_Total_kWh'])
            logger.debug("Updating battery_kWh_old to: "+str(battery_kwh))
            batterystats['Battery_kWh_old'] = battery_kwh
            open(GivLUT.ppkwhtouch, 'w').close()       # set touch file  to stop repeated triggers in the single minute

    else:       # remove the touchfile if it exists
        if exists(GivLUT.ppkwhtouch):
            os.remove(GivLUT.ppkwhtouch)

    # write data to pickle
    with open(GivLUT.batterypkl, 'wb') as outp:
        pickle.dump(batterystats, outp, pickle.HIGHEST_PROTOCOL)

    # remove non publishable stats
    del batterystats['AC Charge last']
    # add stats to multi_output
    multi_output['Energy']['Rates']['Battery_Value'] = batterystats['Battery_Value']
    multi_output['Energy']['Rates']['Battery_ppkwh'] = batterystats['Battery_ppkwh']
    return (multi_output)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        globals()[sys.argv[1]]()
    elif len(sys.argv) == 3:
        globals()[sys.argv[1]](sys.argv[2])

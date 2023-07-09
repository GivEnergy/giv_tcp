class GivClient:
    def getData(fullrefresh):
        from givenergy_modbus.client import GivEnergyClient
        from settings import GiV_Settings
        from givenergy_modbus.model.plant import Plant  
        client= GivEnergyClient(host=GiV_Settings.invertorIP)
        if GiV_Settings.isAIO:
            numbat=0
        else:
            numbat=GiV_Settings.numBatteries
        plant=Plant(number_batteries=numbat)
        client.refresh_plant(plant,GiV_Settings.isAIO,full_refresh=fullrefresh)
        return (plant)
        
class GivQueue:
    from redis import Redis
    from rq import Queue
    from settings import GiV_Settings
    redis_connection = Redis(host='127.0.0.1', port=6379, db=0)
    q = Queue("GivTCP_"+str(GiV_Settings.givtcp_instance),connection=redis_connection)
    
class GEType:
    def __init__(self,dT,sC,cF,mn,mx,aZ,sM,oI):
        self.devType = dT
        self.sensorClass=sC
        self.controlFunc=cF
        self.min=mn
        self.max=mx
        self.allowZero=aZ
        self.smooth=sM
        self.onlyIncrease=oI

class InvType:
    def __init__(self,ph,md,pw,mr,gn):
        self.phase=ph
        self.model=md
        self.power=pw
        self.batmaxrate=mr
        self.generation=gn

class GivLUT:
    #Logging config
    import logging, os, zoneinfo
    from settings import GiV_Settings
    from logging.handlers import TimedRotatingFileHandler
    logging.basicConfig(format='%(asctime)s - Inv'+ str(GiV_Settings.givtcp_instance)+' - %(module)-11s -  [%(levelname)-8s] - %(message)s')
    formatter = logging.Formatter(
        '%(asctime)s - %(module)s - [%(levelname)s] - %(message)s')
    fh = TimedRotatingFileHandler(GiV_Settings.Debug_File_Location, when='D', interval=1, backupCount=7)
    fh.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(fh)
    if str(os.getenv("LOG_LEVEL")).lower()=="debug":
        logger.setLevel(logging.DEBUG)
    elif str(os.getenv("LOG_LEVEL")).lower()=="info":
        logger.setLevel(logging.INFO)
    elif str(os.getenv("LOG_LEVEL")).lower()=="critical":
        logger.setLevel(logging.CRITICAL)
    elif str(os.getenv("LOG_LEVEL")).lower()=="warning":
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.ERROR)

    # File paths for use
    lockfile=".lockfile"
    regcache=GiV_Settings.cache_location+"/regCache_"+str(GiV_Settings.givtcp_instance)+".pkl"
    ratedata=GiV_Settings.cache_location+"/rateData_"+str(GiV_Settings.givtcp_instance)+".pkl"
    lastupdate=GiV_Settings.cache_location+"/lastUpdate_"+str(GiV_Settings.givtcp_instance)+".pkl"
    forcefullrefresh=GiV_Settings.cache_location+"/.forceFullRefresh_"+str(GiV_Settings.givtcp_instance)
    batterypkl=GiV_Settings.cache_location+"/battery_"+str(GiV_Settings.givtcp_instance)+".pkl"
    reservepkl=GiV_Settings.cache_location+"/reserve_"+str(GiV_Settings.givtcp_instance)+".pkl"
    ppkwhtouch=".ppkwhtouch"
    schedule=".schedule"
    oldDataCount=GiV_Settings.cache_location+"/oldDataCount_"+str(GiV_Settings.givtcp_instance)+".pkl"
    nightRate=GiV_Settings.cache_location+"/.nightRate"
    dayRate=GiV_Settings.cache_location+"/.dayRate"
    nightRateRequest=GiV_Settings.cache_location+"/.nightRateRequest"
    dayRateRequest=GiV_Settings.cache_location+"/.dayRateRequest"


    if "TZ" in os.environ:
        timezone=zoneinfo.ZoneInfo(key=os.getenv("TZ"))
    else:
        timezone=zoneinfo.ZoneInfo(key="Europe/London")

    # Standard values for devices
    maxInvPower=6000
    maxPower=20000
    maxBatPower=4000
    maxTemp=100
    maxCellVoltage=4
    maxTotalEnergy=100000000
    maxTodayEnergy=100000
    maxCost=100
    maxRate=2
    Last_Updated_Time=GEType("sensor","timestamp","","","",False,False,False)

    entity_type={
        "Last_Updated_Time":GEType("sensor","timestamp","","","",False,False,False),
        "Time_Since_Last_Update":GEType("sensor","","",0,10000,True,False,False),
        "status":GEType("sensor","string","","","",False,False,False),
        "Export_Energy_Total_kWh":GEType("sensor","energy","",0,maxTotalEnergy,False,True,True),
        "Battery_Throughput_Total_kWh":GEType("sensor","energy","",0,maxTotalEnergy,False,True,True),
        "AC_Charge_Energy_Total_kWh":GEType("sensor","energy","",0,maxTotalEnergy,False,True,True),
        "Import_Energy_Total_kWh":GEType("sensor","energy","",0,maxTotalEnergy,False,True,True),
        "Invertor_Energy_Total_kWh":GEType("sensor","energy","",0,maxTotalEnergy,False,True,True),
        "PV_Energy_Total_kWh":GEType("sensor","energy","",0,maxTotalEnergy,False,True,True),
        "Load_Energy_Total_kWh":GEType("sensor","energy","",0,maxTotalEnergy,False,True,True),
        "Battery_Charge_Energy_Total_kWh":GEType("sensor","energy","",0,maxTotalEnergy,False,True,True),
        "Battery_Discharge_Energy_Total_kWh":GEType("sensor","energy","",0,maxTotalEnergy,False,True,True),
        "Self_Consumption_Energy_Total_kWh":GEType("sensor","energy","",0,maxTotalEnergy,False,True,True),
        "Battery_Throughput_Today_kWh":GEType("sensor","energy","",0,maxTodayEnergy,True,False,False),
        "PV_Energy_Today_kWh":GEType("sensor","energy","",0,maxTodayEnergy,True,False,False),
        "Import_Energy_Today_kWh":GEType("sensor","energy","",0,maxTodayEnergy,True,False,False),
        "Export_Energy_Today_kWh":GEType("sensor","energy","",0,maxTodayEnergy,True,False,False),
        "AC_Charge_Energy_Today_kWh":GEType("sensor","energy","",0,maxTodayEnergy,True,False,False),
        "Invertor_Energy_Today_kWh":GEType("sensor","energy","",0,maxTodayEnergy,True,False,False),
        "Battery_Charge_Energy_Today_kWh":GEType("sensor","energy","",0,maxTodayEnergy,True,False,False),
        "Battery_Discharge_Energy_Today_kWh":GEType("sensor","energy","",0,maxTodayEnergy,True,False,False),
        "Self_Consumption_Energy_Today_kWh":GEType("sensor","energy","",0,maxTodayEnergy,True,False,False),
        "Load_Energy_Today_kWh":GEType("sensor","energy","",0,maxTodayEnergy,True,False,False),
        "PV_Power_String_1":GEType("sensor","power","",0,10000,True,False,False),
        "PV_Power_String_2":GEType("sensor","power","",0,10000,True,False,False),
        "PV_Power":GEType("sensor","power","",0,maxPower,True,False,False),
        "PV_Voltage_String_1":GEType("sensor","voltage","",0,550,True,False,False),
        "PV_Voltage_String_2":GEType("sensor","voltage","",0,550,True,False,False),
        "PV_Current_String_1":GEType("sensor","current","",0,20,True,False,False),
        "PV_Current_String_2":GEType("sensor","current","",0,20,True,False,False),
        "Grid_Power":GEType("sensor","power","",-maxPower,maxPower,True,False,False),
        "Grid_Current":GEType("sensor","current","",-120,120,False,False,False),
        "Grid_Voltage":GEType("sensor","voltage","",150,300,False,True,False),
        "Import_Power":GEType("sensor","power","",0,maxPower,True,False,False),
        "Export_Power":GEType("sensor","power","",0,maxInvPower,True,False,False),
        "EPS_Power":GEType("sensor","power","",0,10000,True,False,False),
        "Invertor_Power":GEType("sensor","power","",-maxInvPower,maxInvPower,True,False,False),
        "Load_Power":GEType("sensor","power","",0,maxPower,True,False,False),
        "AC_Charge_Power":GEType("sensor","power","",0,maxBatPower,True,False,False),
        "Self_Consumption_Power":GEType("sensor","power","",0,maxInvPower,True,False,False),
        "Battery_Power":GEType("sensor","power","",-maxBatPower,maxBatPower,True,False,False),
        "Charge_Power":GEType("sensor","power","",0,maxBatPower,True,False,False),
        "Discharge_Power":GEType("sensor","power","",0,maxBatPower,True,False,False),
        "SOC":GEType("sensor","battery","",0,100,False,False,False),
        "SOC_kWh":GEType("sensor","energy","",0,50,True,False,False),
        "Solar_to_House":GEType("sensor","power","",0,maxInvPower,True,False,False),
        "Solar_to_Battery":GEType("sensor","power","",0,maxInvPower,True,False,False),
        "Solar_to_Grid":GEType("sensor","power","",0,maxInvPower,True,False,False),
        "Battery_to_House":GEType("sensor","power","",0,maxBatPower,True,False,False),
        "Grid_to_Battery":GEType("sensor","power","",0,maxPower,True,False,False),
        "Grid_to_House":GEType("sensor","power","",0,maxPower,True,False,False),
        "Battery_to_Grid":GEType("sensor","power","",0,maxBatPower,True,False,False),
        "Battery_Type":GEType("sensor","string","","","",False,False,False),
        "Battery_Capacity_kWh":GEType("sensor","","",0,maxBatPower,True,True,False),
        "Invertor_Serial_Number":GEType("sensor","string","","","",False,False,False),
        "Invertor_Time":GEType("sensor","timestamp","","","",False,False,False),
        "Invertor_Max_Rate":GEType("sensor","","",0,maxBatPower,True,False,False),
        "Active_Power_Rate":GEType("number","","setActivePowerRate",0,100,True,False,False),
        "Invertor_Firmware":GEType("sensor","string","",0,10000,False,False,False),
        "Modbus_Version":GEType("sensor","","",1,10,False,True,False),
        "Meter_Type":GEType("sensor","string","","","",False,False,False),
        "Invertor_Type":GEType("sensor","string","","","",False,False,False),
        "Invertor_Temperature":GEType("sensor","temperature","",-maxTemp,maxTemp,True,True,False),
        "Discharge_start_time_slot_1":GEType("select","","setDischargeStart1","","",False,False,False),
        "Discharge_end_time_slot_1":GEType("select","","setDischargeEnd1","","",False,False,False),
        "Discharge_start_time_slot_2":GEType("select","","setDischargeStart2","","",False,False,False),
        "Discharge_end_time_slot_2":GEType("select","","setDischargeEnd2","","",False,False,False),
        "Charge_start_time_slot_1":GEType("select","","setChargeStart1","","",False,False,False),
        "Charge_end_time_slot_1":GEType("select","","setChargeEnd1","","",False,False,False),
        "Charge_start_time_slot_2":GEType("select","","setChargeStart2","","",False,False,False),
        "Charge_end_time_slot_2":GEType("select","","setChargeEnd2","","",False,False,False),
        "Battery_Serial_Number":GEType("sensor","string","","","",False,True,False),
        "Battery_SOC":GEType("sensor","battery","",0,100,False,False,False),
        "Battery_Capacity":GEType("sensor","","",0,250,False,True,False),
        "Battery_Design_Capacity":GEType("sensor","","",0,250,False,True,False),
        "Battery_Remaining_Capacity":GEType("sensor","","",0,250,True,True,False),
        "Battery_Firmware_Version":GEType("sensor","string","",500,5000,False,False,False),
        "Battery_Cells":GEType("sensor","","",0,24,False,True,False),
        "Battery_Cycles":GEType("sensor","","",0,5000,False,True,False),
        "Battery_USB_present":GEType("binary_sensor","","",0,2,True,False,False),
        "Battery_Temperature":GEType("sensor","temperature","",-maxTemp,maxTemp,True,True,False),
        "Battery_Voltage":GEType("sensor","voltage","",0,100,False,True,False),
        "Battery_Cell_1_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_2_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_3_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_4_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_5_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_6_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_7_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_8_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_9_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_10_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_11_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_12_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_13_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_14_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_15_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_16_Voltage":GEType("sensor","voltage","",0,maxCellVoltage,False,True,False),
        "Battery_Cell_1_Temperature":GEType("sensor","temperature","",-maxTemp,maxTemp,True,True,False),
        "Battery_Cell_2_Temperature":GEType("sensor","temperature","",-maxTemp,maxTemp,True,True,False),
        "Battery_Cell_3_Temperature":GEType("sensor","temperature","",-maxTemp,maxTemp,True,True,False),
        "Battery_Cell_4_Temperature":GEType("sensor","temperature","",-maxTemp,maxTemp,True,True,False),
        "Mode":GEType("select","","setBatteryMode","","",False,False,False),
        "Battery_Power_Reserve":GEType("number","","setBatteryReserve",4,100,False,False,False),
        "Battery_Power_Cutoff":GEType("number","","setBatteryCutoff",4,100,False,False,False),
        "Target_SOC":GEType("number","","setChargeTarget",4,100,False,False,False),
        "Enable_Charge_Schedule":GEType("switch","","enableChargeSchedule","","",False,False,False),
        "Enable_Discharge_Schedule":GEType("switch","","enableDishargeSchedule","","",False,False,False),
        "Enable_Discharge":GEType("switch","","enableDischarge","","",False,False,False),
        "Battery_Charge_Rate":GEType("number","","setChargeRate",0,10000,True,False,False),
        "Battery_Discharge_Rate":GEType("number","","setDischargeRate",0,10000,True,False,False),
        "Night_Start_Energy_kWh":GEType("sensor","energy","",0,maxTotalEnergy,False,False,False),
        "Night_Energy_kWh":GEType("sensor","energy","",0,maxTodayEnergy,False,False,False),
        "Night_Cost":GEType("sensor","money","",0,maxCost,True,False,False),
        "Night_Rate":GEType("sensor","money","",0,maxRate,True,False,False),
        "Day_Start_Energy_kWh":GEType("sensor","energy","",0,maxTotalEnergy,False,False,False),
        "Day_Energy_kWh":GEType("sensor","energy","",0,maxTodayEnergy,False,False,False),
        "Day_Cost":GEType("sensor","money","",0,maxCost,True,False,False),
        "Day_Rate":GEType("sensor","money","",0,maxRate,True,False,False),
        "Current_Rate":GEType("sensor","money","",0,maxRate,True,False,False),
        "Current_Rate_Type":GEType("select","","switchRate","","",True,False,False),
        "Export_Rate":GEType("sensor","money","",0,maxRate,True,False,False),
        "Import_ppkwh_Today":GEType("sensor","money","",0,maxRate,True,False,False),
        "Battery_Value":GEType("sensor","money","",0,maxCost,True,False,False),
        "Battery_ppkwh":GEType("sensor","money","",0,maxRate,True,False,False),
        "Temp_Pause_Discharge":GEType("select","","tempPauseDischarge","","",True,False,False),
        "Temp_Pause_Charge":GEType("select","","tempPauseCharge","","",True,False,False),
        "Force_Charge":GEType("select","","forceCharge","","",True,False,False),
        "Force_Export":GEType("select","","forceExport","","",True,False,False),
        "Reboot_Invertor":GEType("switch","","rebootInvertor","","",False,False,False),
        "Reboot_Addon":GEType("switch","","rebootAddon","","",False,False,False),
        "Discharge_Time_Remaining":GEType("sensor","","",0,1000,True,False,False),
        "Charge_Time_Remaining":GEType("sensor","","",0,1000,True,False,False),
        "Charge_Completion_Time":GEType("sensor","timestamp","","","",False,False,False),
        "Discharge_Completion_Time":GEType("sensor","timestamp","","","",False,False,False),
        "Battery_Power_Mode":GEType("switch","","setBatteryPowerMode","","",False,False,False),
        }
    time_slots=[
"00:00:00","00:01:00","00:02:00","00:03:00","00:04:00","00:05:00","00:06:00","00:07:00","00:08:00","00:09:00","00:10:00","00:11:00","00:12:00","00:13:00","00:14:00","00:15:00","00:16:00","00:17:00","00:18:00","00:19:00","00:20:00","00:21:00","00:22:00","00:23:00","00:24:00","00:25:00","00:26:00","00:27:00","00:28:00","00:29:00","00:30:00","00:31:00","00:32:00","00:33:00","00:34:00","00:35:00","00:36:00","00:37:00","00:38:00","00:39:00","00:40:00","00:41:00","00:42:00","00:43:00","00:44:00","00:45:00","00:46:00","00:47:00","00:48:00","00:49:00","00:50:00","00:51:00","00:52:00","00:53:00","00:54:00","00:55:00","00:56:00","00:57:00","00:58:00","00:59:00",
"01:00:00","01:01:00","01:02:00","01:03:00","01:04:00","01:05:00","01:06:00","01:07:00","01:08:00","01:09:00","01:10:00","01:11:00","01:12:00","01:13:00","01:14:00","01:15:00","01:16:00","01:17:00","01:18:00","01:19:00","01:20:00","01:21:00","01:22:00","01:23:00","01:24:00","01:25:00","01:26:00","01:27:00","01:28:00","01:29:00","01:30:00","01:31:00","01:32:00","01:33:00","01:34:00","01:35:00","01:36:00","01:37:00","01:38:00","01:39:00","01:40:00","01:41:00","01:42:00","01:43:00","01:44:00","01:45:00","01:46:00","01:47:00","01:48:00","01:49:00","01:50:00","01:51:00","01:52:00","01:53:00","01:54:00","01:55:00","01:56:00","01:57:00","01:58:00","01:59:00",
"02:00:00","02:01:00","02:02:00","02:03:00","02:04:00","02:05:00","02:06:00","02:07:00","02:08:00","02:09:00","02:10:00","02:11:00","02:12:00","02:13:00","02:14:00","02:15:00","02:16:00","02:17:00","02:18:00","02:19:00","02:20:00","02:21:00","02:22:00","02:23:00","02:24:00","02:25:00","02:26:00","02:27:00","02:28:00","02:29:00","02:30:00","02:31:00","02:32:00","02:33:00","02:34:00","02:35:00","02:36:00","02:37:00","02:38:00","02:39:00","02:40:00","02:41:00","02:42:00","02:43:00","02:44:00","02:45:00","02:46:00","02:47:00","02:48:00","02:49:00","02:50:00","02:51:00","02:52:00","02:53:00","02:54:00","02:55:00","02:56:00","02:57:00","02:58:00","02:59:00",
"03:00:00","03:01:00","03:02:00","03:03:00","03:04:00","03:05:00","03:06:00","03:07:00","03:08:00","03:09:00","03:10:00","03:11:00","03:12:00","03:13:00","03:14:00","03:15:00","03:16:00","03:17:00","03:18:00","03:19:00","03:20:00","03:21:00","03:22:00","03:23:00","03:24:00","03:25:00","03:26:00","03:27:00","03:28:00","03:29:00","03:30:00","03:31:00","03:32:00","03:33:00","03:34:00","03:35:00","03:36:00","03:37:00","03:38:00","03:39:00","03:40:00","03:41:00","03:42:00","03:43:00","03:44:00","03:45:00","03:46:00","03:47:00","03:48:00","03:49:00","03:50:00","03:51:00","03:52:00","03:53:00","03:54:00","03:55:00","03:56:00","03:57:00","03:58:00","03:59:00",
"04:00:00","04:01:00","04:02:00","04:03:00","04:04:00","04:05:00","04:06:00","04:07:00","04:08:00","04:09:00","04:10:00","04:11:00","04:12:00","04:13:00","04:14:00","04:15:00","04:16:00","04:17:00","04:18:00","04:19:00","04:20:00","04:21:00","04:22:00","04:23:00","04:24:00","04:25:00","04:26:00","04:27:00","04:28:00","04:29:00","04:30:00","04:31:00","04:32:00","04:33:00","04:34:00","04:35:00","04:36:00","04:37:00","04:38:00","04:39:00","04:40:00","04:41:00","04:42:00","04:43:00","04:44:00","04:45:00","04:46:00","04:47:00","04:48:00","04:49:00","04:50:00","04:51:00","04:52:00","04:53:00","04:54:00","04:55:00","04:56:00","04:57:00","04:58:00","04:59:00",
"05:00:00","05:01:00","05:02:00","05:03:00","05:04:00","05:05:00","05:06:00","05:07:00","05:08:00","05:09:00","05:10:00","05:11:00","05:12:00","05:13:00","05:14:00","05:15:00","05:16:00","05:17:00","05:18:00","05:19:00","05:20:00","05:21:00","05:22:00","05:23:00","05:24:00","05:25:00","05:26:00","05:27:00","05:28:00","05:29:00","05:30:00","05:31:00","05:32:00","05:33:00","05:34:00","05:35:00","05:36:00","05:37:00","05:38:00","05:39:00","05:40:00","05:41:00","05:42:00","05:43:00","05:44:00","05:45:00","05:46:00","05:47:00","05:48:00","05:49:00","05:50:00","05:51:00","05:52:00","05:53:00","05:54:00","05:55:00","05:56:00","05:57:00","05:58:00","05:59:00",
"06:00:00","06:01:00","06:02:00","06:03:00","06:04:00","06:05:00","06:06:00","06:07:00","06:08:00","06:09:00","06:10:00","06:11:00","06:12:00","06:13:00","06:14:00","06:15:00","06:16:00","06:17:00","06:18:00","06:19:00","06:20:00","06:21:00","06:22:00","06:23:00","06:24:00","06:25:00","06:26:00","06:27:00","06:28:00","06:29:00","06:30:00","06:31:00","06:32:00","06:33:00","06:34:00","06:35:00","06:36:00","06:37:00","06:38:00","06:39:00","06:40:00","06:41:00","06:42:00","06:43:00","06:44:00","06:45:00","06:46:00","06:47:00","06:48:00","06:49:00","06:50:00","06:51:00","06:52:00","06:53:00","06:54:00","06:55:00","06:56:00","06:57:00","06:58:00","06:59:00",
"07:00:00","07:01:00","07:02:00","07:03:00","07:04:00","07:05:00","07:06:00","07:07:00","07:08:00","07:09:00","07:10:00","07:11:00","07:12:00","07:13:00","07:14:00","07:15:00","07:16:00","07:17:00","07:18:00","07:19:00","07:20:00","07:21:00","07:22:00","07:23:00","07:24:00","07:25:00","07:26:00","07:27:00","07:28:00","07:29:00","07:30:00","07:31:00","07:32:00","07:33:00","07:34:00","07:35:00","07:36:00","07:37:00","07:38:00","07:39:00","07:40:00","07:41:00","07:42:00","07:43:00","07:44:00","07:45:00","07:46:00","07:47:00","07:48:00","07:49:00","07:50:00","07:51:00","07:52:00","07:53:00","07:54:00","07:55:00","07:56:00","07:57:00","07:58:00","07:59:00",
"08:00:00","08:01:00","08:02:00","08:03:00","08:04:00","08:05:00","08:06:00","08:07:00","08:08:00","08:09:00","08:10:00","08:11:00","08:12:00","08:13:00","08:14:00","08:15:00","08:16:00","08:17:00","08:18:00","08:19:00","08:20:00","08:21:00","08:22:00","08:23:00","08:24:00","08:25:00","08:26:00","08:27:00","08:28:00","08:29:00","08:30:00","08:31:00","08:32:00","08:33:00","08:34:00","08:35:00","08:36:00","08:37:00","08:38:00","08:39:00","08:40:00","08:41:00","08:42:00","08:43:00","08:44:00","08:45:00","08:46:00","08:47:00","08:48:00","08:49:00","08:50:00","08:51:00","08:52:00","08:53:00","08:54:00","08:55:00","08:56:00","08:57:00","08:58:00","08:59:00",
"09:00:00","09:01:00","09:02:00","09:03:00","09:04:00","09:05:00","09:06:00","09:07:00","09:08:00","09:09:00","09:10:00","09:11:00","09:12:00","09:13:00","09:14:00","09:15:00","09:16:00","09:17:00","09:18:00","09:19:00","09:20:00","09:21:00","09:22:00","09:23:00","09:24:00","09:25:00","09:26:00","09:27:00","09:28:00","09:29:00","09:30:00","09:31:00","09:32:00","09:33:00","09:34:00","09:35:00","09:36:00","09:37:00","09:38:00","09:39:00","09:40:00","09:41:00","09:42:00","09:43:00","09:44:00","09:45:00","09:46:00","09:47:00","09:48:00","09:49:00","09:50:00","09:51:00","09:52:00","09:53:00","09:54:00","09:55:00","09:56:00","09:57:00","09:58:00","09:59:00",
"10:00:00","10:01:00","10:02:00","10:03:00","10:04:00","10:05:00","10:06:00","10:07:00","10:08:00","10:09:00","10:10:00","10:11:00","10:12:00","10:13:00","10:14:00","10:15:00","10:16:00","10:17:00","10:18:00","10:19:00","10:20:00","10:21:00","10:22:00","10:23:00","10:24:00","10:25:00","10:26:00","10:27:00","10:28:00","10:29:00","10:30:00","10:31:00","10:32:00","10:33:00","10:34:00","10:35:00","10:36:00","10:37:00","10:38:00","10:39:00","10:40:00","10:41:00","10:42:00","10:43:00","10:44:00","10:45:00","10:46:00","10:47:00","10:48:00","10:49:00","10:50:00","10:51:00","10:52:00","10:53:00","10:54:00","10:55:00","10:56:00","10:57:00","10:58:00","10:59:00",
"11:00:00","11:01:00","11:02:00","11:03:00","11:04:00","11:05:00","11:06:00","11:07:00","11:08:00","11:09:00","11:10:00","11:11:00","11:12:00","11:13:00","11:14:00","11:15:00","11:16:00","11:17:00","11:18:00","11:19:00","11:20:00","11:21:00","11:22:00","11:23:00","11:24:00","11:25:00","11:26:00","11:27:00","11:28:00","11:29:00","11:30:00","11:31:00","11:32:00","11:33:00","11:34:00","11:35:00","11:36:00","11:37:00","11:38:00","11:39:00","11:40:00","11:41:00","11:42:00","11:43:00","11:44:00","11:45:00","11:46:00","11:47:00","11:48:00","11:49:00","11:50:00","11:51:00","11:52:00","11:53:00","11:54:00","11:55:00","11:56:00","11:57:00","11:58:00","11:59:00",
"12:00:00","12:01:00","12:02:00","12:03:00","12:04:00","12:05:00","12:06:00","12:07:00","12:08:00","12:09:00","12:10:00","12:11:00","12:12:00","12:13:00","12:14:00","12:15:00","12:16:00","12:17:00","12:18:00","12:19:00","12:20:00","12:21:00","12:22:00","12:23:00","12:24:00","12:25:00","12:26:00","12:27:00","12:28:00","12:29:00","12:30:00","12:31:00","12:32:00","12:33:00","12:34:00","12:35:00","12:36:00","12:37:00","12:38:00","12:39:00","12:40:00","12:41:00","12:42:00","12:43:00","12:44:00","12:45:00","12:46:00","12:47:00","12:48:00","12:49:00","12:50:00","12:51:00","12:52:00","12:53:00","12:54:00","12:55:00","12:56:00","12:57:00","12:58:00","12:59:00",
"13:00:00","13:01:00","13:02:00","13:03:00","13:04:00","13:05:00","13:06:00","13:07:00","13:08:00","13:09:00","13:10:00","13:11:00","13:12:00","13:13:00","13:14:00","13:15:00","13:16:00","13:17:00","13:18:00","13:19:00","13:20:00","13:21:00","13:22:00","13:23:00","13:24:00","13:25:00","13:26:00","13:27:00","13:28:00","13:29:00","13:30:00","13:31:00","13:32:00","13:33:00","13:34:00","13:35:00","13:36:00","13:37:00","13:38:00","13:39:00","13:40:00","13:41:00","13:42:00","13:43:00","13:44:00","13:45:00","13:46:00","13:47:00","13:48:00","13:49:00","13:50:00","13:51:00","13:52:00","13:53:00","13:54:00","13:55:00","13:56:00","13:57:00","13:58:00","13:59:00",
"14:00:00","14:01:00","14:02:00","14:03:00","14:04:00","14:05:00","14:06:00","14:07:00","14:08:00","14:09:00","14:10:00","14:11:00","14:12:00","14:13:00","14:14:00","14:15:00","14:16:00","14:17:00","14:18:00","14:19:00","14:20:00","14:21:00","14:22:00","14:23:00","14:24:00","14:25:00","14:26:00","14:27:00","14:28:00","14:29:00","14:30:00","14:31:00","14:32:00","14:33:00","14:34:00","14:35:00","14:36:00","14:37:00","14:38:00","14:39:00","14:40:00","14:41:00","14:42:00","14:43:00","14:44:00","14:45:00","14:46:00","14:47:00","14:48:00","14:49:00","14:50:00","14:51:00","14:52:00","14:53:00","14:54:00","14:55:00","14:56:00","14:57:00","14:58:00","14:59:00",
"15:00:00","15:01:00","15:02:00","15:03:00","15:04:00","15:05:00","15:06:00","15:07:00","15:08:00","15:09:00","15:10:00","15:11:00","15:12:00","15:13:00","15:14:00","15:15:00","15:16:00","15:17:00","15:18:00","15:19:00","15:20:00","15:21:00","15:22:00","15:23:00","15:24:00","15:25:00","15:26:00","15:27:00","15:28:00","15:29:00","15:30:00","15:31:00","15:32:00","15:33:00","15:34:00","15:35:00","15:36:00","15:37:00","15:38:00","15:39:00","15:40:00","15:41:00","15:42:00","15:43:00","15:44:00","15:45:00","15:46:00","15:47:00","15:48:00","15:49:00","15:50:00","15:51:00","15:52:00","15:53:00","15:54:00","15:55:00","15:56:00","15:57:00","15:58:00","15:59:00",
"16:00:00","16:01:00","16:02:00","16:03:00","16:04:00","16:05:00","16:06:00","16:07:00","16:08:00","16:09:00","16:10:00","16:11:00","16:12:00","16:13:00","16:14:00","16:15:00","16:16:00","16:17:00","16:18:00","16:19:00","16:20:00","16:21:00","16:22:00","16:23:00","16:24:00","16:25:00","16:26:00","16:27:00","16:28:00","16:29:00","16:30:00","16:31:00","16:32:00","16:33:00","16:34:00","16:35:00","16:36:00","16:37:00","16:38:00","16:39:00","16:40:00","16:41:00","16:42:00","16:43:00","16:44:00","16:45:00","16:46:00","16:47:00","16:48:00","16:49:00","16:50:00","16:51:00","16:52:00","16:53:00","16:54:00","16:55:00","16:56:00","16:57:00","16:58:00","16:59:00",
"17:00:00","17:01:00","17:02:00","17:03:00","17:04:00","17:05:00","17:06:00","17:07:00","17:08:00","17:09:00","17:10:00","17:11:00","17:12:00","17:13:00","17:14:00","17:15:00","17:16:00","17:17:00","17:18:00","17:19:00","17:20:00","17:21:00","17:22:00","17:23:00","17:24:00","17:25:00","17:26:00","17:27:00","17:28:00","17:29:00","17:30:00","17:31:00","17:32:00","17:33:00","17:34:00","17:35:00","17:36:00","17:37:00","17:38:00","17:39:00","17:40:00","17:41:00","17:42:00","17:43:00","17:44:00","17:45:00","17:46:00","17:47:00","17:48:00","17:49:00","17:50:00","17:51:00","17:52:00","17:53:00","17:54:00","17:55:00","17:56:00","17:57:00","17:58:00","17:59:00",
"18:00:00","18:01:00","18:02:00","18:03:00","18:04:00","18:05:00","18:06:00","18:07:00","18:08:00","18:09:00","18:10:00","18:11:00","18:12:00","18:13:00","18:14:00","18:15:00","18:16:00","18:17:00","18:18:00","18:19:00","18:20:00","18:21:00","18:22:00","18:23:00","18:24:00","18:25:00","18:26:00","18:27:00","18:28:00","18:29:00","18:30:00","18:31:00","18:32:00","18:33:00","18:34:00","18:35:00","18:36:00","18:37:00","18:38:00","18:39:00","18:40:00","18:41:00","18:42:00","18:43:00","18:44:00","18:45:00","18:46:00","18:47:00","18:48:00","18:49:00","18:50:00","18:51:00","18:52:00","18:53:00","18:54:00","18:55:00","18:56:00","18:57:00","18:58:00","18:59:00",
"19:00:00","19:01:00","19:02:00","19:03:00","19:04:00","19:05:00","19:06:00","19:07:00","19:08:00","19:09:00","19:10:00","19:11:00","19:12:00","19:13:00","19:14:00","19:15:00","19:16:00","19:17:00","19:18:00","19:19:00","19:20:00","19:21:00","19:22:00","19:23:00","19:24:00","19:25:00","19:26:00","19:27:00","19:28:00","19:29:00","19:30:00","19:31:00","19:32:00","19:33:00","19:34:00","19:35:00","19:36:00","19:37:00","19:38:00","19:39:00","19:40:00","19:41:00","19:42:00","19:43:00","19:44:00","19:45:00","19:46:00","19:47:00","19:48:00","19:49:00","19:50:00","19:51:00","19:52:00","19:53:00","19:54:00","19:55:00","19:56:00","19:57:00","19:58:00","19:59:00",
"20:00:00","20:01:00","20:02:00","20:03:00","20:04:00","20:05:00","20:06:00","20:07:00","20:08:00","20:09:00","20:10:00","20:11:00","20:12:00","20:13:00","20:14:00","20:15:00","20:16:00","20:17:00","20:18:00","20:19:00","20:20:00","20:21:00","20:22:00","20:23:00","20:24:00","20:25:00","20:26:00","20:27:00","20:28:00","20:29:00","20:30:00","20:31:00","20:32:00","20:33:00","20:34:00","20:35:00","20:36:00","20:37:00","20:38:00","20:39:00","20:40:00","20:41:00","20:42:00","20:43:00","20:44:00","20:45:00","20:46:00","20:47:00","20:48:00","20:49:00","20:50:00","20:51:00","20:52:00","20:53:00","20:54:00","20:55:00","20:56:00","20:57:00","20:58:00","20:59:00",
"21:00:00","21:01:00","21:02:00","21:03:00","21:04:00","21:05:00","21:06:00","21:07:00","21:08:00","21:09:00","21:10:00","21:11:00","21:12:00","21:13:00","21:14:00","21:15:00","21:16:00","21:17:00","21:18:00","21:19:00","21:20:00","21:21:00","21:22:00","21:23:00","21:24:00","21:25:00","21:26:00","21:27:00","21:28:00","21:29:00","21:30:00","21:31:00","21:32:00","21:33:00","21:34:00","21:35:00","21:36:00","21:37:00","21:38:00","21:39:00","21:40:00","21:41:00","21:42:00","21:43:00","21:44:00","21:45:00","21:46:00","21:47:00","21:48:00","21:49:00","21:50:00","21:51:00","21:52:00","21:53:00","21:54:00","21:55:00","21:56:00","21:57:00","21:58:00","21:59:00",
"22:00:00","22:01:00","22:02:00","22:03:00","22:04:00","22:05:00","22:06:00","22:07:00","22:08:00","22:09:00","22:10:00","22:11:00","22:12:00","22:13:00","22:14:00","22:15:00","22:16:00","22:17:00","22:18:00","22:19:00","22:20:00","22:21:00","22:22:00","22:23:00","22:24:00","22:25:00","22:26:00","22:27:00","22:28:00","22:29:00","22:30:00","22:31:00","22:32:00","22:33:00","22:34:00","22:35:00","22:36:00","22:37:00","22:38:00","22:39:00","22:40:00","22:41:00","22:42:00","22:43:00","22:44:00","22:45:00","22:46:00","22:47:00","22:48:00","22:49:00","22:50:00","22:51:00","22:52:00","22:53:00","22:54:00","22:55:00","22:56:00","22:57:00","22:58:00","22:59:00",
"23:00:00","23:01:00","23:02:00","23:03:00","23:04:00","23:05:00","23:06:00","23:07:00","23:08:00","23:09:00","23:10:00","23:11:00","23:12:00","23:13:00","23:14:00","23:15:00","23:16:00","23:17:00","23:18:00","23:19:00","23:20:00","23:21:00","23:22:00","23:23:00","23:24:00","23:25:00","23:26:00","23:27:00","23:28:00","23:29:00","23:30:00","23:31:00","23:32:00","23:33:00","23:34:00","23:35:00","23:36:00","23:37:00","23:38:00","23:39:00","23:40:00","23:41:00","23:42:00","23:43:00","23:44:00","23:45:00","23:46:00","23:47:00","23:48:00","23:49:00","23:50:00","23:51:00","23:52:00","23:53:00","23:54:00","23:55:00","23:56:00","23:57:00","23:58:00","23:59:00"
    ]
    
    delay_times=["Normal","Running","Cancel","2","15","30","45","60","90","120","150","180"]
    modes=["Eco","Eco (Paused)","Timed Demand","Timed Export","Unknown"]
    rates=["Day","Night"]

    def getTime(timestamp):
        timeslot=timestamp.strftime("%H:%M")
        return (timeslot)
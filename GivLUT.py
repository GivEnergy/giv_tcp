
class GiV_Reg_LUT:

  holding_register_LUT= {
    0:["Device Type Code","raw","1"],1:["Inverter Module (high)","raw","1"],2:["Inverter Module (low)","raw","1"],
    3:["Input tracker num and output phase num","raw","1"],4:["unknown","raw","1"],5:["unknown","raw","1"],6:["unknown","raw","1"],
    7:["unknown","raw","1"],8:["BAT Serial number 5","raw","1"],9:["BAT Serial number 4","raw","1"],10:["BAT Serial number 3","raw","1"],
    11:["BAT Serial number 2","raw","1"],12:["BAT Serial number 1","raw","1"],13:["INV Serial number 5","raw","1"],14:["INV Serial number 4","raw","1"],
    15:["INV Serial number 3","raw","1"],16:["INV Serial number 2","raw","1"],17:["INV Serial number 1","raw","1"],
    18:["unknown","raw","1"],19:["unknown","raw","1"],20:["Winter Mode On Off","raw","1"],21:["unknown","raw","1"],22:["Wifi or U disk ","raw","1"],
    23:["Selet dsp or ARM","raw","1"],24:["Set Variable address","raw","1"],25:["Set Variable Value","raw","1"],26:["GridPortMaxOutPutPower","raw","1"],
    27:["BatPowerMode","raw","1"],28:["FreMode","raw","1"],29:["SOC_ForceAdjust","raw","1"],30:["Communicate  address","raw","1"],31:["Slot 2 charge time start","time","1"],
    32:["Slot 2 charge time stop","time","1"],33:["User code","raw","1"],34:["Modbus Version","raw","1"],35:["System time-year","raw","1"],
    36:["System time- Month","raw","1"],37:["System time- Day","raw","1"],38:["System time- Hour","raw","1"],39:["System time- Min","raw","1"],
    40:["System time- Second","raw","1"],41:["DRM enable","raw","1"],42:["CT Adjust","raw","1"],43:["Chg and dischg Soc","raw","1"],
    44:["Discharge start time slot2","time","1"],45:["Discharge end time slot2","time","1"],46:["BMSVersion","raw","1"],47:[" bMeterType","raw","1"],
    48:["b115MeterDirect","raw","1"],49:["b418MeterDirect","raw","1"],50:["Active P rate","raw","1"],51:["Reactive P rate","raw","1"],
    52:["Power Factor","raw","1"],53:["Inverter State","raw","1"],54:["Battery type","raw","1"],55:["Battery norminal capacity","raw","1"],
    56:["Discharge start time slot1","time","1"],57:["Discharge end time slot1","time","1"],58:["AutoJudgeBatteryTypeEnable","raw","1"],59:["Dis_Time Enable flag ","boolean","1"],
    60:["Input start voltage ","raw","1"],61:["Start time","raw","1"],62:["RestartDelayTime","raw","1"],63:["Vac low OUT","raw","1"],
    64:["Vac high OUT","raw","1"],65:["Fac low OUT","raw","1"],66:["Fac high OUT","raw","1"],67:["Vac low OUT  time","raw","1"],
    68:["Vac high OUT  time","raw","1"],69:["Fac low OUT time","raw","1"],70:["Fac high OUT time","raw","1"],71:["Vac low IN","raw","1"],
    72:["Vac high IN","raw","1"],73:["Fac low IN","raw","1"],74:["Fac high IN","raw","1"],75:["Vac low IN time","raw","1"],76:["Vac high IN time","raw","1"],
    77:["Fac low time IN","raw","1"],78:["Fac high time IN","raw","1"],79:["Vac low C","raw","1"],80:["Vac high C","raw","1"],81:["Fac low C","raw","1"],
    82:["Fac high C","raw","1"],83:["U10min","raw","1"],84:["ISO1","raw","1"],85:["ISO2","raw","1"],86:["GFCI_I 1","raw","1"],87:["GFCI_time 1 ","raw","1"],
    88:["GFCI_I 2","raw","1"],89:["GFCI_time 2 ","raw","1"],90:["DCI_I 1","raw","1"],91:["DCI_time 1 ","raw","1"],92:["DCI_I 2","raw","1"],
    93:["DCI_time 2","raw","1"],94:["Charge start time slot1","time","1"],95:["Charge end time slot1","time","1"],96:["Charge enable flag","boolean","1"],
    97:["Discharger Low  limit","raw","1"],98:["Charger High limit","raw","1"],99:["Pv1 volt adjust","raw","1"],100:["Pv2 volt adjust","raw","1"],
    101:["Grid R volt adjust","raw","1"],102:["Grid S volt adjust","raw","1"],103:["Grid T volt adjust","raw","1"],104:["Grid Power adjust","raw","1"],
    105:["Bat volt adjust","raw","1"],106:["PV1 Power adjust","raw","1"],107:["PV2 Power adjust","raw","1"],108:["BatLowForceChgTime","raw","1"],
    109:["bBMSType","raw","1"],110:["bSocBase","raw","1"],111:["bBatChgLimit","raw","1"],112:["bBatDisLimit","raw","1"],113:["Buzzer_sw","raw","1"],
    114:["bDisMinSoc","raw","1"],115:["IsLanChkContiue","raw","1"],116:["WinterModeCutSoc","raw","1"],117:["Chg_soc stop2","raw","1"],
    118:["dischg_soc stop2","raw","1"],119:["Chg_soc stop","raw","1"],120:["dischg_soc stop","raw","1"]
    }

  input_register_LUT= {
    0:["Invertor Status","raw",1],1:["PV1 voltage","unsigned",0.1],2:["PV2 voltage","unsigned",0.1],3:["P Bus inside  Voltage","raw",1],
    4:["N Bus inside Voltage","raw",1],5:["single phase grid voltage","raw",1],6:["DwchgDis_EAllEE_H","raw",1],7:["DwchgDis_EAllEE_H","raw",1],
    8:["PV1 input current","unsigned",0.1],9:["PV2 input current","unsigned",0.1],10:["single phase grid output current","raw",1],11:["PV Total generating capacity_H","raw",1],
    12:["PV Total generating capacity_L","raw",1],13:["Grid frequency of Three-single Phase","raw",1],14:["Charge Status","raw",1],15:["HighBrighBUS_Volt","raw",1],
    16:["Inverter output PF now","raw",1],17:["PV1 Energy Today","raw",1],18:["PV1 input watt","raw",1],19:["PV2 Energy Today","raw",1],20:["PV2 input watt","raw",1],
    21:["Grid Energy Out totalH","hex",0.1],22:["Grid Energy Out totalL","hex",0.11],23:["PV mate","raw",1],24:["Three-single phase grid output watt (low)","raw",1],
    25:["Grid Energy Out Day","raw",0.1],26:["Grid Energy IN Day","raw",0.1],27:["INV Energy IN total H","hex",0.1],28:["INV Energy IN total L","hex",0.1],
    29:["YearDisChargeEnergyLow","raw",1],30:["Grid Output Power","signed",1],31:["PBackUp","unsigned",1],32:["Grid Energy IN totalH","hex",0.1],
    33:["Grid Energy IN totalL","hex",0.1],34:["Unknown","raw",1],35:["TotalLoad energy today","raw",0.1],36:["Charger energy today","raw",0.1],
    37:["Discharger energy today","raw",0.1],38:["wCountdown","raw",1],39:["fault Code High 16bits","raw",1],40:["fault Code Low 16bits","raw",1],
    41:["Inverter temperature","raw",0.1],42:["LoadTotal Power ","raw",1],43:["Pgrid_Apparent","raw",1],44:["Today generate energy today (low)","unsigned",0.1],
    45:["Total generate energy (high)","hex",0.1],46:["Total generate energy (low)","hex",0.1],47:["Work time total (high)","hex",1],48:["Work time total (low)","hex",1],
    49:["System Mode","raw",1],50:["Battery voltage","raw",0.01],51:["Battery current","signed",0.01],52:["Battery power","signed",1],
    53:["Output voltage","unsigned",0.1],54:["Output frequency","raw",1],55:["Charger temperature","raw",1],56:["Battery temperature","raw",1],
    57:["Charger Warning code","raw",1],58:["wGridPortCurr","raw",0.01],59:["Battery percent","raw",1]
    }

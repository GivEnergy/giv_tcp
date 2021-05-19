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
# import schedule

class GivTCP:

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


  invertorIP= sys.argv[1]
  dataloggerSN=sys.argv[2]
  MQTT_Address=sys.argv[3]
  if len(sys.argv)>4:
    MQTT_Username=sys.argv[4]
    MQTT_Password=sys.argv[5]

  def int_to_hex_string(value, bits):
      return "{0:0{1}X}".format(value & ((1<<bits) - 1), bits//4)

  def str_to_hex(s):
      return ''.join([('0'+hex(ord(c)).split('x')[1])[-2:] for c in s])

  def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print("connected OK Returned code=",rc)
        #client.subscribe(topic)
    else:
        print("Bad connection Returned code= ",rc)

  def publish_to_MQTT(topic,payload):
      mqtt.Client.connected_flag=False        #create flag in class
      client=mqtt.Client("GivEnergy_"+GivTCP.dataloggerSN)
      if len(sys.argv)>4:
          client.username_pw_set(GivTCP.MQTT_Username,GivTCP.MQTT_Password)
      client.on_connect=GivTCP.on_connect     #bind call back function
      client.loop_start()
      print("Connecting to broker ",GivTCP.MQTT_Address)
      client.connect(GivTCP.MQTT_Address)
      while not client.connected_flag:        #wait in loop
        print("In wait loop")
        time.sleep(0.5)
      print("in Main Loop")
      for reg in payload:
          print('Publishing: GivEnergy/'+GivTCP.dataloggerSN+'/'+topic+'/'+reg,payload[reg])
          client.publish('GivEnergy/'+GivTCP.dataloggerSN+'/'+topic+'/'+reg,payload[reg])
      client.loop_stop()                      #Stop loop 
      client.disconnect()
      return client

  def hex_to_signed(source):
    """Convert a string hex value to a signed hexidecimal value.
    hex_to_signed("F") should return -1.
    hex_to_signed("0F") should return 15.
    """
    if not isinstance(source, str):
        raise ValueError("string type required")
    if 0 == len(source):
        raise ValueError("string is empty")
    sign_bit_mask = 1 << (len(source)*4-1)
    other_bits_mask = sign_bit_mask - 1
    value = int(source, 16)
    return -(value & sign_bit_mask) | (value & other_bits_mask)

  def TCP_call(inputRegister,inputFunction,inputStep):
    #Constants
    HEAD = '5959'
    PROTOCOL_IDENTIFIER = '0001' #hex
    DEVICE_ADDRESS = '01' #hex
    DATALOGGER_FUNCTION_CODE = '02' #hex
    FILLER = '0000000000000008' #hex
    serial_number = GivTCP.str_to_hex(GivTCP.dataloggerSN) # datalogger sn hex

    # Connect the socket to the port where the server is listening
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (GivTCP.invertorIP, 8899)
    sock.connect(server_address)
    stepInt=int(inputStep)
    responseDataSize = 38 + stepInt*2
    inputFunctionHex =  GivTCP.int_to_hex_string(int(inputFunction),16)
    inputRegisterHex = GivTCP.int_to_hex_string(int(inputRegister),16)
    inputStepHex = GivTCP.int_to_hex_string(int(inputStep),16)

    crc = CrcModbus().process(bytearray.fromhex(inputFunctionHex + inputRegisterHex + inputStepHex)).finalhex()
    dataSize = GivTCP.int_to_hex_string(int(len( DEVICE_ADDRESS + DATALOGGER_FUNCTION_CODE + serial_number + FILLER + inputFunctionHex + inputRegisterHex + inputStepHex +crc)/2),16)
    command = HEAD + PROTOCOL_IDENTIFIER + dataSize + DEVICE_ADDRESS + DATALOGGER_FUNCTION_CODE + serial_number + FILLER + inputFunctionHex + inputRegisterHex + inputStepHex + crc
    sock.send(bytearray.fromhex(command))
    sock.settimeout(1)
    data=''
    # filtering  data package
    try:
        length = 0
        while length != responseDataSize  :
            data = sock.recv(164)
            length = data[5]
    except Exception as e:
        print('Error reading '+inputStep+' register(s) ' +inputRegister + ' from ' + inputFunction + ': ' +  str(e),file=sys.stderr)
        ### Do something here if socket timesout  ###
    sock.close()
    return(data)

  def read_register(inputRegister,inputFunction,inputStep):
    final_output={}
    data=''
    registerInt=int(inputRegister)
    stepInt=int(inputStep)
    n=0
    while data=='' and n<3:    #Try to get register data upto 3 times before giving up
      print ("TCP Call no: "+str(n+1))
      data=GivTCP.TCP_call(inputRegister,inputFunction,inputStep)
      n=n+1

    if data != '':
      rr = data.hex()[84:-4]
      print('Success reading '+inputStep+' register(s) ' +inputRegister + ' from ' + inputFunction + '--' + rr)
      registers=re.findall('....',rr)
      j=0
      for reg in registers:
          if inputFunction=='04':
              val=GivTCP.registerValueConvert(registerInt+j, reg, "input")
              key=GivTCP.input_register_LUT.get(registerInt+j)[0] + "(" + str(registerInt+j) + ")"
              final_output[key]=val
          elif inputFunction=='03':
              val=GivTCP.registerValueConvert(registerInt+j, reg, "holding")
              key=GivTCP.holding_register_LUT.get(registerInt+j)[0] + "(" + str(registerInt+j) + ")"
              final_output[key]=val
          j=j+1
          if j>=stepInt: break  #Handle cases where invertor send erroneous additional data

    return final_output

#Function to convert the raw rgister value to real output using LUT attributes
  def registerValueConvert(register,value,regType):
    if regType=="holding":
        dataformat=GivTCP.holding_register_LUT.get(register)[1]
        scaling=GivTCP.holding_register_LUT.get(register)[2]
    if regType=="input":
        dataformat=GivTCP.input_register_LUT.get(register)[1]
        scaling=GivTCP.input_register_LUT.get(register)[2]
    #format value
    if dataformat=="time":
       value=int(value,16)
       value=str(value).rjust(4,"0")
    elif dataformat=="signed":
       value=round(GivTCP.hex_to_signed(value) * scaling,2)
    elif dataformat=="unsigned":
       value=round(int(value,16) * scaling,2)
    elif dataformat=="boolean":
       value=bool(int(value,16))
    elif dataformat=="hex":
       value=value
    else:
       value=round(int(value,16) * int(scaling),2)
    return value

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

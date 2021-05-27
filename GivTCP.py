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
from GivLUT import GiV_Reg_LUT
from settings import GiV_Settings


# import schedule


class GivTCP:

  invertorIP= GiV_Settings.invertorIP
  dataloggerSN= GiV_Settings.dataloggerSN
  MQTT_Address=GiV_Settings.MQTT_Address
  if GiV_Settings.MQTT_Username=='':
     MQTTCredentials=False
  else:
     MQTTCredentials=True
     MQTT_Username=GiV_Settings.MQTT_Username
     MQTT_Password=GiV_Settings.MQTT_Password

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
      if GivTCP.MQTTCredentials:
          client.username_pw_set(GivTCP.MQTT_Username,GivTCP.MQTT_Password)
      client.on_connect=GivTCP.on_connect     #bind call back function
      client.loop_start()
      print ("Connecting to broker ",GivTCP.MQTT_Address)
      client.connect(GivTCP.MQTT_Address)
      while not client.connected_flag:        #wait in loop
        print ("In wait loop")
        time.sleep(0.5)
#      print ("in Main Loop")
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
    socketMax=0
    # Connect the socket to the port where the server is listening
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (GivTCP.invertorIP, 8899)
    sock.connect(server_address)
    stepInt=int(inputStep)
    if inputFunction=='06':
      responseDataSize=38
      socketMax=44
    else:
      responseDataSize = 38 + stepInt*2
      socketMax=164
    inputFunctionHex =  GivTCP.int_to_hex_string(int(inputFunction),16)
    inputRegisterHex = GivTCP.int_to_hex_string(int(inputRegister),16)
    inputStepHex = GivTCP.int_to_hex_string(int(inputStep),16)

    crc = CrcModbus().process(bytearray.fromhex(inputFunctionHex + inputRegisterHex + inputStepHex)).finalhex()
    dataSize = GivTCP.int_to_hex_string(int(len( DEVICE_ADDRESS + DATALOGGER_FUNCTION_CODE + serial_number + FILLER + inputFunctionHex + inputRegisterHex + inputStepHex +crc)/2),16)
    command = HEAD + PROTOCOL_IDENTIFIER + dataSize + DEVICE_ADDRESS + DATALOGGER_FUNCTION_CODE + serial_number + FILLER + inputFunctionHex + inputRegisterHex + inputStepHex + crc
    print ("Sending command: ",command)
    sock.send(bytearray.fromhex(command))
    sock.settimeout(1.5)
    data=''
    # filtering  data package
    try:
        length = 0
        while length != responseDataSize  :
            data = sock.recv(socketMax)
            length = data[5]
    except Exception as e:
        print ("Error: " + str(e))
        ### Do something here if socket timesout  ###
    sock.close()
    return(data)

  def write_single_register(register,value):
    response=''
    result="Failure"
    n=0
    while response=='' and n<3:    #Try to get register data upto 3 times before giving up
      print ("TCP Call no: ",str(n+1)," to write register",register)
      response=GivTCP.TCP_call(register,"06",value)
      n=n+1
    if response!='':
      rr = response.hex()[80:-4]
      if rr!='':
          val=GivTCP.registerValueConvert(register, rr, "holding")
          if int(val)==int(value):
            result="Success"
          else:
            result="Failure"
    else:
      result="Failure"
    return result

  def read_register(inputRegister,inputFunction,inputStep):
    final_output={}
    data=''
    registerInt=int(inputRegister)
    stepInt=int(inputStep)
    n=0
    while data=='' and n<3 and len(data)!= (stepInt*2)+44:    #Try to get register data upto 3 times before giving up
      print ("TCP Call no:",str(n+1),"to read register",inputRegister)
      data=GivTCP.TCP_call(inputRegister,inputFunction,inputStep)
      n=n+1
    if len(data)== (stepInt*2)+44:	#do not return if data length does not match
      rr = data.hex()[84:-4]
      if len(rr)==4 or int(rr,16)!=0:   #do not return if registers return all zeros unless its a single register
        print ('Success reading '+inputStep+' register(s) ' +inputRegister + ' from ' + inputFunction + '--' + rr)
        registers=re.findall('....',rr)
        j=0
        for reg in registers:
            if inputFunction=='04':
                val=GivTCP.registerValueConvert(registerInt+j, reg, "input")
                key=GiV_Reg_LUT.input_register_LUT.get(registerInt+j)[0] + "(" + str(registerInt+j) + ")"
                final_output[key]=val
            elif inputFunction=='03':
                val=GivTCP.registerValueConvert(registerInt+j, reg, "holding")
                key=GiV_Reg_LUT.holding_register_LUT.get(registerInt+j)[0] + "(" + str(registerInt+j) + ")"
                final_output[key]=val
            j=j+1
            if j>=stepInt: break  #Handle cases where invertor send erroneous additional data
    else:
      print('Error reading '+inputStep+' register(s) ' +inputRegister + ' from ' + inputFunction,file=sys.stderr)

    return final_output

#Function to convert the raw rgister value to real output using LUT attributes
  def registerValueConvert(register,value,regType):
    if regType=="holding":
        dataformat=GiV_Reg_LUT.holding_register_LUT.get(register)[1]
        scaling=GiV_Reg_LUT.holding_register_LUT.get(register)[2]
    if regType=="input":
        dataformat=GiV_Reg_LUT.input_register_LUT.get(register)[1]
        scaling=GiV_Reg_LUT.input_register_LUT.get(register)[2]
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

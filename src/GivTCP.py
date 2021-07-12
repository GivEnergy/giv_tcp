# -*- coding: utf-8 -*-
import socket
import sys
import codecs
from crccheck.crc import Crc16, CrcModbus
import subprocess
import re
import time
from datetime import datetime
from GivLUT import GiV_Reg_LUT
from settings import GiV_Settings

class GivTCP:
  Invertor_Type=""
  invertorIP= GiV_Settings.invertorIP
  dataloggerSN= "AB12345678"  #Dummy Serial number
  SN=""
      
  def debug(input):
    if GiV_Settings.debug.lower() == "true":
      sourceFile = open(GiV_Settings.Debug_File_Location + 'read_debug.log','a')
      print(str(datetime.now())+" - "+str(input), file = sourceFile)
      sourceFile.close()

  def int_to_hex_string(value, bits):
      return "{0:0{1}X}".format(value & ((1<<bits) - 1), bits//4)

  def str_to_hex(s):
      return ''.join([('0'+hex(ord(c)).split('x')[1])[-2:] for c in s])

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
    SLAVE_ADDRESS = '32' #hex
    serial_number = GivTCP.str_to_hex(GivTCP.dataloggerSN) # datalogger sn hex
    socketMax=0

    stepInt=int(inputStep)
    if inputFunction=='06':
      responseDataSize=38
      socketMax=44
    else:
      responseDataSize = 38 + stepInt*2
      socketMax=164
    inputFunctionHex =  GivTCP.int_to_hex_string(int(inputFunction),16)[-2:]
    GivTCP.debug("InputFunction hex=: "+ inputFunctionHex)
    inputRegisterHex = GivTCP.int_to_hex_string(int(inputRegister),16)
    inputStepHex = GivTCP.int_to_hex_string(int(inputStep),16)

    crc = CrcModbus().process(bytearray.fromhex(inputFunctionHex + inputRegisterHex + inputStepHex)).finalhex()
    dataSize = GivTCP.int_to_hex_string(int(len( DEVICE_ADDRESS + DATALOGGER_FUNCTION_CODE + serial_number + FILLER + inputFunctionHex + inputRegisterHex + inputStepHex +crc)/2),16)
    command = HEAD + PROTOCOL_IDENTIFIER + dataSize + DEVICE_ADDRESS + DATALOGGER_FUNCTION_CODE + serial_number + FILLER + SLAVE_ADDRESS + inputFunctionHex + inputRegisterHex + inputStepHex + crc
    try:
      # Connect the socket to the port where the server is listening
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      server_address = (GivTCP.invertorIP, 8899)
      GivTCP.debug("Connecting to Invertor on: "+str(server_address))
      sock.connect(server_address)
      GivTCP.debug("Connected to Invertor on: "+str(server_address))
    except socket.gaierror as e:
        GivTCP.debug ("Address-related error connecting to server:" + str(e))
        return()
    except socket.error as e:
        GivTCP.debug ("Connection error:" + str(e))
        return()
    except socket.timeout as e:
        GivTCP.debug ("Timeout error: " + str(e))
        return()
    except Exception as e:
        GivTCP.debug ("Unknown error: " + str(e))
    try:
      GivTCP.debug("Sending command: "+command)
      sock.send(bytearray.fromhex(command))
      sock.settimeout(1.5)
    except Exception as e:
      GivTCP.debug("Error sending data: "+str(e))
    data=''
    # filtering  data package
    try:
        length = 0
        while length != responseDataSize  :
            data = sock.recv(socketMax)
            length = data[5]
    except Exception as e:
        GivTCP.debug ("Error: " + str(e))
        ### Do something here if socket timesout  ###
    sock.close()
    return(data)

  def write_single_register(register,value):
    response=''
    result="Failure"
    n=0
    while response=='' and n<3:    #Try to get register data upto 3 times before giving up
      GivTCP.debug ("TCP Call no: "+str(n+1)+" to write register "+str(register))
      response=GivTCP.TCP_call(register,"06",value)
      n=n+1
    if response!='':
      rr = response.hex()[80:-4]
      if rr!='':
          val=GivTCP.registerValueConvert(register, rr, "03")
          if int(val)==int(value):
            GivTCP.debug('Register'+str(register) +'successfully set to '+str(val))
            result="Success"
          else:
            GivTCP.debug('Register'+str(register) +'failed to set to '+str(val))
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
      GivTCP.debug ("TCP Call no: "+str(n+1)+" to read "+str(stepInt)+" register(s) starting from reg: "+inputRegister)
      data=GivTCP.TCP_call(inputRegister,inputFunction,inputStep)
      n=n+1
    
    if len(data)== (stepInt*2)+44:	#do not return if data length does not match
      GivTCP.debug ('Returned Data is: '+data.hex())  
      #Get Invertor Type
      GivTCP.SN = data[28:38].decode()
      iType=GivTCP.SN[0:2]
      if iType=="CE":
        GivTCP.Invertor_Type="AC"
      elif iType=="ED":
        GivTCP.Invertor_Type="Gen 2"
      else:
        GivTCP.Invertor_Type="Hybrid"
      GivTCP.debug("Invertor Type is: "+ GivTCP.Invertor_Type)

      rr = data.hex()[84:-4]
      if len(rr)==4 or int(rr,16)!=0:   #do not return if registers return all zeros unless its a single register
        GivTCP.debug ('Success reading '+inputStep+' register(s) ' +inputRegister + ' from ' + inputFunction + '--' + rr)
        registers=re.findall('....',rr)
        j=0
        for reg in registers:
            if inputFunction=='04':
                val=GivTCP.registerValueConvert(registerInt+j, reg, "04")
                key=GiV_Reg_LUT.input_register_LUT.get(registerInt+j)[0] + "(" + str(registerInt+j) + ")"
                final_output[key]=val
            elif inputFunction=='03':
                val=GivTCP.registerValueConvert(registerInt+j, reg, "03")
                key=GiV_Reg_LUT.holding_register_LUT.get(registerInt+j)[0] + "(" + str(registerInt+j) + ")"
                final_output[key]=val
            j=j+1
            if j>=stepInt: break  #Handle cases where invertor send erroneous additional data
      else:
        GivTCP.debug('Error reading data. Invertor returned empty data')
    else:
      GivTCP.debug('Error reading '+inputStep+' register(s) ' +inputRegister + ' from ' + inputFunction)

    return final_output

#Function to convert the raw rgister value to real output using LUT attributes
  def registerValueConvert(register,value,regType):
    if regType=="03":
        dataformat=GiV_Reg_LUT.holding_register_LUT.get(register)[1]
        scaling=GiV_Reg_LUT.holding_register_LUT.get(register)[2]
    if regType=="04":
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
    elif dataformat=="ascii":
      try:
        value=bytearray.fromhex(value).decode()
      except:
        value=value
    else:
      value=round(int(value,16) * int(scaling),2)
    return value

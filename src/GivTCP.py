# -*- coding: utf-8 -*-
# version 1.0
import sys
from datetime import datetime
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
        print(str(datetime.now())+" - "+str(input), file=sys.stderr)
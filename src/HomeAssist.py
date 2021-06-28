import json
import sys
from homeassistant_api import Client
from GivTCP import GivTCP
from settings import GiV_Settings

class GivHA():
    def push(data):
        url=GiV_Settings.HA_url
        token=GiV_Settings.HA_token
        client = Client(url, token)
        power_output = data['Power']
        GivTCP.debug("Creating Power entities for HA")
        for key in power_output:
            print("inside loop")
            entityid="sensor.givtcp_"+key.replace(" ","_")
            payload='{"state":"'+str(power_output[key])+'"}'
            print("sending",str(power_output[key]), "to", entityid.lower()) 
            result=client.set_entity(entity_id='sensor.givtcp_test', state='test')
            print (result)
import json
import sys
from homeassistant_api import Client
from settings import GiV_Settings

url=GiV_Settings.HA_url
token=GiV_Settings.HA_token
client = Client(url, token)
result=client.set_entity('sensor.givenergy_load_power', state='9999')
print (result)
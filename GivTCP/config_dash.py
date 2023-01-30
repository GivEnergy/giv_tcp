# -*- coding: utf-8 -*-
# version 2022.01.31
import sys, os, logging
import pickle
from os.path import exists
from GivLUT import GivLUT, GivQueue, GivClient
from datetime import datetime, timedelta
from settings import GiV_Settings

def get_config():
    if exists(GivLUT.regcache):      # if there is a cache then grab it
        with open(GivLUT.regcache, 'rb') as inp:
            regCacheStack= pickle.load(inp)
            multi_output_old=regCacheStack[4]
        serial_number=multi_output_old["Invertor_Details"]['Invertor_Serial_Number']
    else:
        serial_number="Unknown"

    head=f'''
            <html>
            <body>
                <p>GivTCP Config for Invertor: {serial_number}</p>'''
    form=f'''
                <form method="post" action="/config">'''
    for attribute in vars(GiV_Settings):
        if not attribute.startswith('__'):
            form=form+f'''
            <p><label for="{attribute}">{attribute}: </label>
            <input name="{attribute}" id="{attribute}" value="{vars(GiV_Settings)[attribute]}"/></p>'''
    form=form+'''
        <p><input type="submit" value="Save Config" /></p>
        </form>'''

    footer=f'''
            </body>
        </html>'''
    html=head+form+footer
    return html

def set_config(formdata):
    #Accept input
    
    inv=formdata["givtcp_instance"]
#update the ENV
    os.environ["INVERTOR_IP_"+str(inv)]= formdata["invertorIP"]
    os.environ["NUMBATTERIES_"+str(inv)]= formdata["numBatteries"]
    os.environ["PRINT_RAW"]= formdata["Print_Raw_Registers"]
    os.environ["MQTT_OUTPUT"]= formdata["MQTT_Output"]
    os.environ["MQTT_ADDRESS"]= formdata["MQTT_Address"]
    os.environ["MQTT_USERNAME"]= formdata["MQTT_Username"]
    os.environ["MQTT_PASSWORD"]= formdata["MQTT_Password"]
    os.environ["MQTT_TOPIC"]= formdata["MQTT_Topic"]
    os.environ["MQTT_PORT"]= formdata["MQTT_Port"]
    os.environ["LOG_LEVEL"]= formdata["Log_Level"]
    os.environ["INFLUX_OUTPUT"]= formdata["Influx_Output"]
    os.environ["INFLUX_URL"]= formdata["influxURL"]
    os.environ["INFLUX_TOKEN"]= formdata["influxToken"]
    os.environ["INFLUX_BUCKET"]= formdata["influxBucket"]
    os.environ["INFLUX_ORG"]= formdata["influxOrg"]
    os.environ["HA_AUTO_D"]= formdata["HA_Auto_D"]
    os.environ["SELF_RUN_LOOP_TIMER"]= formdata["self_run_timer"]
    os.environ["PATH"]= formdata["default_path"]
    os.environ["DAYRATE"]= formdata["day_rate"]
    os.environ["NIGHTRATE"]= formdata["night_rate"]
    os.environ["EXPORTRATE"]= formdata["export_rate"]
    os.environ["DAYRATESTART"]= formdata["day_rate_start"]
    os.environ["NIGHTRATESTART"]= formdata["night_rate_start"]
    os.environ["HADEVICEPREFIX"]= formdata["ha_device_prefix"]
    os.environ["DATASMOOTHER"]= formdata["data_smoother"]
    os.environ["CACHELOCATION"]= formdata["cache_location"]

#restart GivTCP (kill PID 1)
    open('/app/.reboot', 'w').close()
#reload page (GET)
    return "Settings Updated, rebooting GivTCP"
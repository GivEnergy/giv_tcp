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
    PATH= "/app/GivTCP_"+str(inv)

    with open(PATH+"/settings.py", 'w') as outp:
        outp.write("class GiV_Settings:\n")
        outp.write("    invertorIP=\""+formdata["invertorIP"]+"\"\n")
        outp.write("    numBatteries=\""+formdata["numBatteries"]+"\"\n")
        outp.write("    Print_Raw_Registers="+formdata["Print_Raw_Registers"]+"\n")
        outp.write("    MQTT_Output="+formdata["MQTT_Output"]+"\n")
        outp.write("    MQTT_Address=\""+formdata["MQTT_Address"]+"\"\n")
        outp.write("    MQTT_Username=\""+formdata["MQTT_Username"]+"\"\n")
        outp.write("    MQTT_Password=\""+formdata["MQTT_Password"]+"\"\n")
        outp.write("    MQTT_Topic=\""+formdata["MQTT_Topic"]+"\"\n")
        outp.write("    MQTT_Port="+formdata["MQTT_Port"]+"\n")
        outp.write("    Log_Level=\""+formdata["Log_Level"]+"\"\n")
        outp.write("    Influx_Output="+formdata["Influx_Output"]+"\n")
        outp.write("    influxURL=\""+formdata["influxURL"]+"\"\n")
        outp.write("    influxToken=\""+formdata["influxToken"]+"\"\n")
        outp.write("    influxBucket=\""+formdata["influxBucket"]+"\"\n")
        outp.write("    influxOrg=\""+formdata["influxOrg"]+"\"\n")
        outp.write("    HA_Auto_D=\""+formdata["HA_Auto_D"]+"\"\n")
        outp.write("    first_run= True\n")
        outp.write("    self_run_timer="+formdata["self_run_timer"]+"\n")
        outp.write("    givtcp_instance="+str(inv)+"\n")
        outp.write("    default_path=\""+formdata["default_path"]+"\"\n")
        outp.write("    dynamic_tariff="+formdata["Dynamic_Tariff"]+"\n")
        outp.write("    day_rate="+formdata["day_rate"]+"\n")
        outp.write("    night_rate="+formdata["night_rate"]+"\n")
        outp.write("    export_rate="+formdata["export_rate"]+"\n")
        outp.write("    day_rate_start=\""+formdata["day_rate_start"]+"\"\n")
        outp.write("    night_rate_start=\""+formdata["night_rate_start"]+"\"\n")
        outp.write("    ha_device_prefix=\""+formdata["ha_device_prefix"]+"\"\n")
        outp.write("    data_smoother=\""+formdata["data_smoother"]+"\"\n")
        if str(os.getenv("CACHELOCATION"))=="":
            outp.write("    cache_location=\"/config/GivTCP\"\n")
            outp.write("    Debug_File_Location=\"/config/GivTCP/log_inv_"+str(inv)+".log\"\n")
        else:
            outp.write("    cache_location=\""+formdata["cache_location"]+"\"\n")
            outp.write("    Debug_File_Location=\""+formdata["cache_location"]+"/log_inv_"+str(inv)+".log\"\n")

    import startup_2 as startup
    # If its already running then stop current processes
    startup.restart(inv)
    # else startup
    startup.startup(inv)
#reload page (GET)
    return "Settings Updated, reloading GivTCP"
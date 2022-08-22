from asyncio import subprocess
from genericpath import exists
import os
import subprocess
from time import sleep
import logging
import shutil, shlex

logger = logging.getLogger("GivTCP_MAIN")
selfRun={}
mqttClient={}
gunicorn={}
webDash={}
for inv in range(1,int(os.getenv('NUMINVERTORS'))+1):
    logger.critical ("Instance is inv: "+str(inv)+"/"+str(os.getenv('NUMINVERTORS')))
    PATH= "/app/GivTCP_"+str(inv)
    PATH2= "/app/GivEnergy-Smart-Home-Display-givtcp_"+str(inv)

    # Create folder per instance
    if not exists(PATH):
        shutil.copytree("/app/GivTCP", PATH)
        shutil.copytree("/app/GivEnergy-Smart-Home-Display-givtcp", PATH2)
    # Remove old settings file
    if exists(PATH+"/settings.py"):
        os.remove(PATH+"/settings.py")
    
    # create settings file
    logger.critical ("Recreating settings.py for invertor "+str(inv))
    with open(PATH+"/settings.py", 'w') as outp:
        outp.write("class GiV_Settings:\n")
        outp.write("    invertorIP=\""+str(os.getenv("INVERTOR_IP_"+str(inv)))+"\"\n")
        outp.write("    numBatteries=\""+str(os.getenv("NUMBATTERIES_"+str(inv))+"\"\n"))
        outp.write("    Print_Raw_Registers=\""+str(os.getenv("PRINT_RAW"))+"\"\n")
        outp.write("    MQTT_Output="+str(os.getenv("MQTT_OUTPUT")+"\n"))
        outp.write("    MQTT_Address=\""+str(os.getenv("MQTT_ADDRESS")+"\"\n"))
        outp.write("    MQTT_Username=\""+str(os.getenv("MQTT_USERNAME")+"\"\n"))
        outp.write("    MQTT_Password=\""+str(os.getenv("MQTT_PASSWORD")+"\"\n"))
        outp.write("    MQTT_Topic=\""+str(os.getenv("MQTT_TOPIC")+"\"\n"))
        outp.write("    MQTT_Port="+str(os.getenv("MQTT_PORT")+"\n"))
        outp.write("    Log_Level=\""+str(os.getenv("LOG_LEVEL")+"\"\n"))
        outp.write("    Debug_File_Location=\""+str(os.getenv("DEBUG_FILE_LOCATION")+"\"\n"))
        outp.write("    Influx_Output="+str(os.getenv("INFLUX_OUTPUT"))+"\n")
        outp.write("    influxURL=\""+str(os.getenv("INFLUX_URL")+"\"\n"))
        outp.write("    influxToken=\""+str(os.getenv("INFLUX_TOKEN")+"\"\n"))
        outp.write("    influxBucket=\""+str(os.getenv("INFLUX_BUCKET")+"\"\n"))
        outp.write("    influxOrg=\""+str(os.getenv("INFLUX_ORG")+"\"\n"))
        outp.write("    HA_Auto_D="+str(os.getenv("HA_AUTO_D"))+"\n")
        outp.write("    first_run= True\n")
        outp.write("    self_run_timer="+str(os.getenv("SELF_RUN_LOOP_TIMER"))+"\n")
        outp.write("    givtcp_instance="+str(inv)+"\n")
        outp.write("    default_path=\""+str(os.getenv("PATH")+"\"\n"))
        outp.write("    day_rate=\""+str(os.getenv("DAYRATE")+"\"\n"))
        outp.write("    night_rate=\""+str(os.getenv("NIGHTRATE")+"\"\n"))
        outp.write("    day_rate_start=\""+str(os.getenv("DAYRATESTART")+"\"\n"))
        outp.write("    night_rate_start=\""+str(os.getenv("NIGHTRATESTART")+"\"\n"))
        outp.write("    ha_device_prefix=\""+str(os.getenv("HADEVICEPREFIX")+"\"\n"))

    # replicate the startup script here:

    if exists(PATH+"/regCache.pkl"):
        os.remove(PATH+"/regCache.pkl")
    if exists(PATH+"/.lockfile"):
        os.remove(PATH+"/.lockfile")
    
    logger.critical ("GivTCP Instance is "+str(inv))

    os.chdir(PATH)
    if os.getenv('SELF_RUN')=="True":
        logger.critical ("Running Invertor read loop every "+str(os.getenv('SELF_RUN_LOOP_TIMER')))
        selfRun[inv]=subprocess.Popen(["/usr/local/bin/python3",PATH+"/read.py", "self_run2"])
    if os.getenv('MQTT_OUTPUT')=="True":
        logger.critical ("Subscribing Mosquitto on port "+str(os.getenv('MQTT_PORT')))
        mqttClient[inv]=subprocess.Popen(["/usr/local/bin/python3",PATH+"/mqtt_client.py"])
    
    GUPORT=6344+inv
    logger.critical ("Starting Gunicorn on port "+str(GUPORT))
    command=shlex.split("/usr/local/bin/gunicorn -w 3 -b :"+str(GUPORT)+" REST:giv_api")
    gunicorn[inv]=subprocess.Popen(command)
    
    os.chdir(PATH2)
    if os.getenv('WEB_DASH')=="True":
        # Create app.json
        logger.critical ("Creating web dashbaord config")
        with open(PATH2+"/app.json", 'w') as outp:
            outp.write("{\n")
            outp.write("\"givTcpHostname\": \""+os.getenv('HOSTIP')+":6345\",")
            outp.write("\"solarRate\": "+os.getenv('DAYRATE')+",")
            outp.write("\"exportRate\": "+os.getenv('EXPORTRATE')+"")
            outp.write("}")
        WDPORT=int(os.getenv('WEB_DASH_PORT'))+inv
        logger.critical ("Serving Web Dashboard from port "+str(WDPORT))
        command=shlex.split("/usr/bin/node /usr/local/bin/serve -p "+ str(WDPORT))
        webDash[inv]=subprocess.Popen(command)

if os.getenv('MQTT_ADDRESS')=="127.0.0.1" and os.getenv('MQTT_OUTPUT')=="True":
    logger.critical ("Starting Mosquitto on port "+str(os.getenv('MQTT_PORT')))
    mqttBroker=subprocess.Popen(["/usr/sbin/mosquitto", "-c",PATH+"/mqtt.conf"])
    
# Loop round checking all processes are running
while True:
    for inv in range(1,int(os.getenv('NUMINVERTORS'))+1):
        PATH= "/app/GivTCP_"+str(inv)
        if os.getenv('SELF_RUN') and not selfRun[inv].poll()==None:
            logger.error("Self Run loop process died. restarting...")
            os.chdir(PATH)
            logger.critical ("Running Invertor read loop every "+str(os.getenv('SELF_RUN_LOOP_TIMER')))
            selfRun[inv]=subprocess.Popen(["/usr/local/bin/python3",PATH+"/read.py", "self_run2"])
        elif os.getenv('MQTT_OUTPUT') and not mqttClient[inv].poll()==None:
            logger.error("MQTT Client process died. Restarting...")
            os.chdir(PATH)
            logger.critical ("Subscribing Mosquitto on port "+str(os.getenv('MQTT_PORT')))
            mqttClient[inv]=subprocess.Popen(["/usr/local/bin/python3",PATH+"/mqtt_client.py"])
        elif os.getenv('WEB_DASH') and not webDash[inv].poll()==None:
            logger.error("Web Dashboard process died. Restarting...")
            os.chdir(PATH2)
            WDPORT=int(os.getenv('WEB_DASH_PORT'))+inv
            logger.critical ("Serving Web Dashboard from port "+str(WDPORT))
            command=shlex.split("/usr/bin/node /usr/local/bin/serve -p "+ str(WDPORT))
            webDash[inv]=subprocess.Popen(command)
        elif not gunicorn[inv].poll()==None:
            logger.error("REST API process died. Restarting...")
            os.chdir(PATH)
            GUPORT=6344+inv
            logger.critical ("Starting Gunicorn on port "+str(GUPORT))
            command=shlex.split("/usr/local/bin/gunicorn -w 3 -b :"+str(GUPORT)+" REST:giv_api")
            gunicorn[inv]=subprocess.Popen(command)
    if os.getenv('MQTT_ADDRESS')=="127.0.0.1" and not mqttBroker.poll()==None:
        logger.error("MQTT Broker process died. Restarting...")
        os.chdir(PATH)
        logger.critical ("Starting Mosquitto on port "+str(os.getenv('MQTT_PORT')))
        mqttBroker=subprocess.Popen(["/usr/sbin/mosquitto", "-c",PATH+"/mqtt.conf"])
    sleep (60)
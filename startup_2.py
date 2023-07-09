from datetime import datetime, timedelta
from genericpath import exists
import os, pickle, subprocess, logging,shutil, shlex, schedule
from time import sleep
import rq_dashboard
import zoneinfo
import requests
from GivTCP.findInvertor import findInvertor

selfRun={}
mqttClient={}
gunicorn={}
webDash={}
rqWorker={}
redis={}

logger = logging.getLogger("startup")
logging.basicConfig(format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')

if os.getenv("LOG_LEVEL").lower=="debug":
    logger.setLevel(logging.DEBUG)
elif os.getenv("LOG_LEVEL").lower()=="info":
    logger.setLevel(logging.INFO)
elif os.getenv("LOG_LEVEL").lower()=="critical":
    logger.setLevel(logging.CRITICAL)
elif os.getenv("LOG_LEVEL").lower()=="warning":
    logger.setLevel(logging.WARNING)
else:
    logger.setLevel(logging.ERROR)

# Check if config directory exists and creates it if not

def palm_job():
    subprocess.Popen(["/usr/local/bin/python3","/app/GivTCP_1/palm_soc.py"])

numInv=0
try:
    logger.debug("SUPERVISOR_TOKEN is: "+ os.getenv("SUPERVISOR_TOKEN"))
    isAddon=True
    access_token = os.getenv("SUPERVISOR_TOKEN")
except:
    logger.critical("SUPERVISOR TOKEN does not exist")
    isAddon=False
    hasMQTT=False

if isAddon:
    #Get MQTT Details    
    url="http://supervisor/services/mqtt"
    result = requests.get(url,
        headers={'Content-Type':'application/json',
                'Authorization': 'Bearer {}'.format(access_token)})
    mqttDetails=result.json()
    if mqttDetails['result']=="ok":
        logger.critical ("HA MQTT Service has been found at "+str(mqttDetails['data']['host']))
        mqtt_host=mqttDetails['data']['host']
        mqtt_username=mqttDetails['data']['username']
        mqtt_password=mqttDetails['data']['password']
        mqtt_port=mqttDetails['data']['port']
        hasMQTT=True
    else:
        hasMQTT=False
        logger.critical("No HA MQTT service has been found")

    #Get Host Details    
    url="http://supervisor/network/info"
    result = requests.get(url,
        headers={'Content-Type':'application/json',
                'Authorization': 'Bearer {}'.format(access_token)})
    hostDetails=result.json()
    
    if hostDetails['result']=="ok":
    # For each interface scan for inverters
        try:
            for interface in hostDetails['data']['interfaces']:
                subnet=interface['ipv4']['gateway']
                invList=findInvertor(subnet)
                logger.critical ("We have found the following invertors: "+str(invList))
            numInv=len(invList)
        except:
            logger.error("Error scanning for Inverters")
    
logger.critical("GivTCP isAddon: "+str(isAddon)+" and we have found "+str(numInv)+" inverters on the network")


if not os.path.exists(str(os.getenv("CACHELOCATION"))):
    os.makedirs(str(os.getenv("CACHELOCATION")))
    logger.critical("No config directory exists, so creating it...")
else:
    logger.critical("Config directory already exists")

redis=subprocess.Popen(["/usr/bin/redis-server","/app/redis.conf"])
logger.critical("Running Redis")

rqdash=subprocess.Popen(["/usr/local/bin/rq-dashboard"])
logger.critical("Running RQ Dashboard on port 9181")

for inv in range(1,numInv+1):
    logger.critical ("Setting up invertor: "+str(inv)+" of "+str(os.getenv('NUMINVERTORS')))
    PATH= "/app/GivTCP_"+str(inv)
    PATH2= "/app/GivEnergy-Smart-Home-Display-givtcp_"+str(inv)

    # Create folder per instance
    if not exists(PATH):
        shutil.copytree("/app/GivTCP", PATH)
        shutil.copytree("/app/GivEnergy-Smart-Home-Display-givtcp", PATH2)
    # Remove old settings file
    if exists(PATH+"/settings.py"):
        os.remove(PATH+"/settings.py")
    FILENAME=""
    # create settings file
    logger.critical ("Recreating settings.py for invertor "+str(inv))
    with open(PATH+"/settings.py", 'w') as outp:
        outp.write("class GiV_Settings:\n")
        outp.write("    invertorIP=\""+str(invList[inv+1])+"\"\n")
        outp.write("    numBatteries=\""+str(os.getenv("NUMBATTERIES_"+str(inv),"")+"\"\n"))
        outp.write("    Print_Raw_Registers="+str(os.getenv("PRINT_RAW",""))+"\n")
        outp.write("    MQTT_Output="+str(os.getenv("MQTT_OUTPUT","")+"\n"))
        if hasMQTT:
            outp.write("    MQTT_Address=\""+str(mqtt_host)+"\"\n")
            outp.write("    MQTT_Username=\""+str(mqtt_username)+"\"\n")
            outp.write("    MQTT_Password=\""+str(mqtt_password)+"\"\n")
            outp.write("    MQTT_Port="+str(mqtt_port)+"\n")
        else:
            outp.write("    MQTT_Address=\""+str(os.getenv("MQTT_ADDRESS","")+"\"\n"))
            outp.write("    MQTT_Username=\""+str(os.getenv("MQTT_USERNAME","")+"\"\n"))
            outp.write("    MQTT_Password=\""+str(os.getenv("MQTT_PASSWORD","")+"\"\n"))
            outp.write("    MQTT_Port="+str(os.getenv("MQTT_PORT","")+"\n"))
        if isAddon:
            outp.write("    HA_Auto_D=True\n")
        else:
            outp.write("    HA_Auto_D="+str(os.getenv("HA_AUTO_D",""))+"\n")
        if inv==1:
            outp.write("    MQTT_Topic=\""+str(os.getenv("MQTT_TOPIC","")+"\"\n"))
        else:
            outp.write("    MQTT_Topic=\""+str(os.getenv("MQTT_TOPIC_"+str(inv),"")+"\"\n"))

        outp.write("    Log_Level=\""+str(os.getenv("LOG_LEVEL","")+"\"\n"))
        #setup debug filename for each inv
        outp.write("    Influx_Output="+str(os.getenv("INFLUX_OUTPUT",""))+"\n")
        outp.write("    influxURL=\""+str(os.getenv("INFLUX_URL","")+"\"\n"))
        outp.write("    influxToken=\""+str(os.getenv("INFLUX_TOKEN","")+"\"\n"))
        outp.write("    influxBucket=\""+str(os.getenv("INFLUX_BUCKET","")+"\"\n"))
        outp.write("    influxOrg=\""+str(os.getenv("INFLUX_ORG","")+"\"\n"))
        outp.write("    first_run= True\n")
        outp.write("    self_run_timer="+str(os.getenv("SELF_RUN_LOOP_TIMER","5"))+"\n")
        outp.write("    queue_retries="+str(os.getenv("QUEUE_RETRIES","2"))+"\n")    
        outp.write("    givtcp_instance="+str(inv)+"\n")
        outp.write("    default_path=\""+str(os.getenv("PATH","")+"\"\n"))
        outp.write("    dynamic_tariff="+str(os.getenv("DYNAMICTARIFF","")+"\n"))
        outp.write("    day_rate="+str(os.getenv("DAYRATE","")+"\n"))
        outp.write("    night_rate="+str(os.getenv("NIGHTRATE","")+"\n"))
        outp.write("    export_rate="+str(os.getenv("EXPORTRATE","")+"\n"))
        outp.write("    day_rate_start=\""+str(os.getenv("DAYRATESTART","")+"\"\n"))
        outp.write("    night_rate_start=\""+str(os.getenv("NIGHTRATESTART","")+"\"\n"))
        if inv==1:
            outp.write("    ha_device_prefix=\""+str(os.getenv("HADEVICEPREFIX","")+"\"\n"))
        else:
            outp.write("    ha_device_prefix=\""+str(os.getenv("HADEVICEPREFIX_"+str(inv),"")+"\"\n"))
        outp.write("    data_smoother=\""+str(os.getenv("DATASMOOTHER","")+"\"\n"))
        if str(os.getenv("CACHELOCATION"))=="":
            outp.write("    cache_location=\"/config/GivTCP\"\n")
            outp.write("    Debug_File_Location=\"/config/GivTCP/log_inv_"+str(inv)+".log\"\n")
        else:
            outp.write("    cache_location=\""+str(os.getenv("CACHELOCATION")+"\"\n"))
            outp.write("    Debug_File_Location=\""+os.getenv("CACHELOCATION")+"/log_inv_"+str(inv)+".log\"\n")

    # replicate the startup script here:

    if exists(os.getenv("CACHELOCATION")+"/regCache_"+str(inv)+".pkl"):
        logger.critical("Removing old invertor data cache")
        os.remove(str(os.getenv("CACHELOCATION"))+"/regCache_"+str(inv)+".pkl")
    if exists(PATH+"/.lockfile"):
        logger.critical("Removing old .lockfile")
        os.remove(PATH+"/.lockfile")
    if exists(PATH+"/.FCRunning"):
        logger.critical("Removing old .FCRunning")
        os.remove(PATH+"/.FCRunning")
    if exists(PATH+"/.FERunning"):
        logger.critical("Removing old .FERunning")
        os.remove(PATH+"/.FERunning")
    if exists(os.getenv("CACHELOCATION")+"/battery_"+str(inv)+".pkl"):
        logger.critical("Removing old battery data cache")
        os.remove(str(os.getenv("CACHELOCATION"))+"/battery_"+str(inv)+".pkl")
    if exists(os.getenv("CACHELOCATION")+"/rateData_"+str(inv)+".pkl"):
        if "TZ" in os.environ:
            timezone=zoneinfo.ZoneInfo(key=os.getenv("TZ"))
        else:
            timezone=zoneinfo.ZoneInfo(key="Europe/London")
        modDay= datetime.fromtimestamp(os.path.getmtime(os.getenv("CACHELOCATION")+"/rateData_"+str(inv)+".pkl")).date()
        if modDay<datetime.now(timezone).date():
            logger.critical("Old rate data cache not updated today, so deleting")
            os.remove(str(os.getenv("CACHELOCATION"))+"/rateData_"+str(inv)+".pkl")
        else:
            logger.critical("Rate Data exisits but is from today so keeping it")

########### Run the various processes needed #############
    os.chdir(PATH)

    rqWorker[inv]=subprocess.Popen(["/usr/local/bin/python3",PATH+"/worker.py"])
    logger.critical("Running RQ worker to queue and process givernergy-modbus calls")

    if not hasMQTT and os.getenv('MQTT_ADDRESS')=="127.0.0.1" and os.getenv('MQTT_OUTPUT')=="True":
        logger.critical ("Starting Mosquitto on port "+str(os.getenv('MQTT_PORT')))
        mqttBroker=subprocess.Popen(["/usr/sbin/mosquitto", "-c",PATH+"/mqtt.conf"])

    if os.getenv('SELF_RUN')=="True" or isAddon:
        logger.critical ("Running Invertor read loop every "+str(os.getenv('SELF_RUN_LOOP_TIMER'))+"s")
        selfRun[inv]=subprocess.Popen(["/usr/local/bin/python3",PATH+"/read.py", "self_run2"])
    if os.getenv('MQTT_OUTPUT')=="True" or isAddon:
        logger.critical ("Subscribing MQTT Broker for control")
        mqttClient[inv]=subprocess.Popen(["/usr/local/bin/python3",PATH+"/mqtt_client.py"])
    
    GUPORT=6344+inv
    logger.critical ("Starting Gunicorn on port "+str(GUPORT))
    command=shlex.split("/usr/local/bin/gunicorn -w 3 -b :"+str(GUPORT)+" REST:giv_api")
    gunicorn[inv]=subprocess.Popen(command)
    
    os.chdir(PATH2)
    if os.getenv('WEB_DASH')=="True":
        # Create app.json
        logger.critical ("Creating web dashboard config")
        with open(PATH2+"/app.json", 'w') as outp:
            outp.write("{\n")
            outp.write("\"givTcpHostname\": \""+os.getenv('HOSTIP')+":6345\",")
            outp.write("\"solarRate\": "+os.getenv('DAYRATE')+",")
            outp.write("\"exportRate\": "+os.getenv('EXPORTRATE')+"")
            outp.write("}")
        WDPORT=int(os.getenv('WEB_DASH_PORT'))-1+inv
        logger.critical ("Serving Web Dashboard from port "+str(WDPORT))
        command=shlex.split("/usr/bin/node /usr/local/bin/serve -p "+ str(WDPORT))
        webDash[inv]=subprocess.Popen(command)

if str(os.getenv('SMARTTARGET'))=="True":
    starttime= datetime.strftime(datetime.strptime(os.getenv('NIGHTRATESTART'),'%H:%M') - timedelta(hours=0, minutes=10),'%H:%M')
    logger.critical("Setting daily charge target forecast job to run at: "+starttime)
    schedule.every().day.at(starttime).do(palm_job)

# Loop round checking all processes are running
while True:
    for inv in range(1,int(os.getenv('NUMINVERTORS'))+1):
        PATH= "/app/GivTCP_"+str(inv)
        if os.getenv('SELF_RUN')==True and not selfRun[inv].poll()==None:
            logger.error("Self Run loop process died. restarting...")
            os.chdir(PATH)
            logger.critical ("Restarting Invertor read loop every "+str(os.getenv('SELF_RUN_LOOP_TIMER'))+"s")
            selfRun[inv]=subprocess.Popen(["/usr/local/bin/python3",PATH+"/read.py", "self_run2"])
        elif os.getenv('MQTT_OUTPUT')==True and not mqttClient[inv].poll()==None:
            logger.error("MQTT Client process died. Restarting...")
            os.chdir(PATH)
            logger.critical ("Resubscribing Mosquitto for control on port "+str(os.getenv('MQTT_PORT')))
            mqttClient[inv]=subprocess.Popen(["/usr/local/bin/python3",PATH+"/mqtt_client.py"])
        elif os.getenv('WEB_DASH')==True and not webDash[inv].poll()==None:
            logger.error("Web Dashboard process died. Restarting...")
            os.chdir(PATH2)
            WDPORT=int(os.getenv('WEB_DASH_PORT'))+inv-1
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

    #Run jobs for smart target
    schedule.run_pending()
    if exists ("/app/.reboot"):
        logger.critical("Reboot requested... rebooting now")
        os.remove("/app/.reboot")
        exit()
    sleep (60)
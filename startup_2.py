from datetime import datetime, timedelta
from genericpath import exists
import os, pickle, subprocess, logging,shutil, shlex, schedule
from time import sleep
import rq_dashboard
import importlib

selfRun={}
mqttClient={}
gunicorn={}
webDash={}
rqWorker={}
redis={}

logger = logging.getLogger("startup")
logging.basicConfig(format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')

logger.setLevel(logging.INFO)

# Check if config directory exists and creates it if not

def palm_job():
    subprocess.Popen(["/usr/local/bin/python3","/app/GivTCP_1/palm_soc.py"])

def clearCache(inv):
    PATH= "/app/GivTCP_"+str(inv)
    if exists(PATH+"/regCache_"+str(inv)+".pkl"):
        logger.critical("Removing old invertor data cache")
        os.remove(PATH+"/regCache_"+str(inv)+".pkl")
    if exists(PATH+"/.lockfile"):
        logger.critical("Removing old .lockfile")
        os.remove(PATH+"/.lockfile")
    if exists(PATH+"/.FCRunning"):
        logger.critical("Removing old .FCRunning")
        os.remove(PATH+"/.FCRunning")
    if exists(PATH+"/.FERunning"):
        logger.critical("Removing old .FERunning")
        os.remove(PATH+"/.FERunning")
    if exists(PATH+"/battery_"+str(inv)+".pkl"):
        logger.critical("Removing old battery data cache")
        os.remove(PATH+"/battery_"+str(inv)+".pkl")
    if exists(PATH+"/rateData_"+str(inv)+".pkl"):
        logger.critical("Removing old rate data cache")
        os.remove(PATH+"/rateData_"+str(inv)+".pkl")

########### Run the various processes needed #############

def startup(inv):
    #from GivTCP.settings import GiV_Settings

    importlib.import_module('.settings.GiV_Settings', package='GivTCP_'+str(inv))

    PATH= "/app/GivTCP_"+str(inv)
    PATH2= "/app/GivEnergy-Smart-Home-Display-givtcp_"+str(inv)
    pidfile=PATH+"/pidfile_"+inv
    os.chdir(PATH)

    rqWorker=subprocess.Popen(["/usr/local/bin/python3",PATH+"/worker.py"])
    logger.critical("Running RQ worker to queue and process givernergy-modbus calls")

    if GiV_Settings.self_run:
        logger.critical ("Running Invertor read loop every "+str(GiV_Settings.self_run_timer)+"s")
        selfRun=subprocess.Popen(["/usr/local/bin/python3",PATH+"/read.py", "self_run2"])

    if GiV_Settings.MQTT_Output:
        logger.critical ("Subscribing Mosquitto on port "+GiV_Settings.MQTT_Port)
        mqttClient=subprocess.Popen(["/usr/local/bin/python3",PATH+"/mqtt_client.py"])
    
    os.chdir(PATH2)
    if GiV_Settings.Web_Dash:
        # Create app.json
        logger.critical ("Creating web dashboard config")
        with open(PATH2+"/app.json", 'w') as outp:
            outp.write("{\n")
            outp.write("\"givTcpHostname\": \""+os.getenv('HOSTIP')+":6345\",")
            outp.write("\"solarRate\": "+os.getenv('DAYRATE')+",")
            outp.write("\"exportRate\": "+os.getenv('EXPORTRATE')+"")
            outp.write("}")
        WDPORT=int(GiV_Settings.Web_Dash_Port)-1+inv
        logger.critical ("Serving Web Dashboard from port "+str(WDPORT))
        command=shlex.split("/usr/bin/node /usr/local/bin/serve -p "+ str(WDPORT))
        webDash=subprocess.Popen(command)

    with open(pidfile, 'w') as pidf:
        pidf.writelines("self_run="+selfRun.pid,"mqttClient="+mqttClient.pid,"rqWorker="+rqWorker.pid,"webDash="+webDash.pid)

    if GiV_Settings.Smart_Target:
        starttime= datetime.strftime(datetime.strptime(GiV_Settings.night_rate_start,'%H:%M') - timedelta(hours=0, minutes=10),'%H:%M')
        logger.critical("Setting daily charge target forecast job to run at: "+starttime)
        schedule.every().day.at(starttime).do(palm_job)
        #GivQueue.q.enqueue_at(starttime,palm_job)
        schedule.run_pending()

def watchdog():
# Loop round checking all processes are running
# Do we need to get PIDs from earlier?
    while True:
    # Check to see if anythign is due to be running, if not then just wait
        for inv in range(1,int(os.getenv('NUMINVERTORS'))+1):
            GS = importlib.import_module('.settings.GiV_Settings', package='GivTCP_'+str(inv))
            PATH= "/app/GivTCP_"+str(inv)
            if GiV_Settings.self_run==True and not selfRun[inv].poll()==None:
                logger.error("Self Run loop process died. restarting...")
                os.chdir(PATH)
                logger.critical ("Restarting Invertor read loop every "+str(os.getenv('SELF_RUN_LOOP_TIMER'))+"s")
                selfRun[inv]=subprocess.Popen(["/usr/local/bin/python3",PATH+"/read.py", "self_run2"])
            elif GiV_Settings.MQTT_Output==True and not mqttClient[inv].poll()==None:
                logger.error("MQTT Client process died. Restarting...")
                os.chdir(PATH)
                logger.critical ("Resubscribing Mosquitto for control on port "+str(os.getenv('MQTT_PORT')))
                mqttClient[inv]=subprocess.Popen(["/usr/local/bin/python3",PATH+"/mqtt_client.py"])
            elif GiV_Settings.Web_Dash==True and not webDash[inv].poll()==None:
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
            if os.getenv('MQTT_INTERNAL')=="True" and not mqttBroker.poll()==None:
                logger.error("MQTT Broker process died. Restarting...")
                os.chdir(PATH)
                logger.critical ("Starting Mosquitto on port "+str(os.getenv('MQTT_PORT')))
                mqttBroker=subprocess.Popen(["/usr/sbin/mosquitto", "-c",PATH+"/mqtt.conf"])
        
        schedule.run_pending()  # Run Smart Target jobs if set
        sleep (60)

def restart(inv):
    # Do something to close all processes and restart
    clearCache(inv) # Clear down the cache
    return



redis=subprocess.Popen(["/usr/bin/redis-server","/app/redis.conf"])
logger.critical("Running Redis")

rqdash=subprocess.Popen(["/usr/local/bin/rq-dashboard"])
logger.critical("Running RQ Dashboard on port 9181")

if str(os.getenv("MQTT_INTERNAL"))=="True":
    # Run internal MQTT Broker
    mqtt=subprocess.Popen(["/usr/sbin/mosquitto","/app/GivTCP/mqtt.conf"])
    logger.critical("Running Mosquitto")

for inv in range(1,int(os.getenv('NUMINVERTORS'))+1):
    logger.critical ("Setting up invertor: "+str(inv)+" of "+str(os.getenv('NUMINVERTORS')))
    PATH= "/app/GivTCP_"+str(inv)
    PATH2= "/app/GivEnergy-Smart-Home-Display-givtcp_"+str(inv)

    # Create folder per instance
    if not exists(PATH):
        shutil.copytree("/app/GivTCP", PATH)
        shutil.copytree("/app/GivEnergy-Smart-Home-Display-givtcp", PATH2)
    # Remove old settings file
    if not exists(PATH+"/settings.py"):
        # if it doesn't exist then create a blank settings file
        logger.critical ("Recreating settings.py for invertor "+str(inv))
        with open(PATH+"/settings.py", 'w') as outp:
            outp.write("class GiV_Settings:\n")
            outp.write("    invertorIP=\"\"\n")
            outp.write("    numBatteries=\"\"\n")
            outp.write("    Print_Raw_Registers=True\n")
            outp.write("    MQTT_Output=True\n")
            outp.write("    MQTT_Address=\"\"\n")
            outp.write("    MQTT_Username=\"\"\n")
            outp.write("    MQTT_Password=\"\"\n")
            outp.write("    MQTT_Topic=\"\"\n")
            outp.write("    MQTT_Port=\"\"\n")
            outp.write("    Log_Level=\"\"\n")
            #setup debug filename for each inv
            outp.write("    Influx_Output=False\n")
            outp.write("    influxURL=\"\"\n")
            outp.write("    influxToken=\"\"\n")
            outp.write("    influxBucket=\"\"\n")
            outp.write("    influxOrg=\"\"\n")
            outp.write("    HA_Auto_D=True\n")
            outp.write("    Web_Dash=False\n")
            outp.write("    first_run= True\n\n")
            outp.write("    self_run=True\n")
            outp.write("    self_run_timer=\"\"\n")
            outp.write("    givtcp_instance=\""+str(inv)+"\"\n")
            outp.write("    default_path=\"\"\n")
            outp.write("    dynamic_tariff=True\n")
            outp.write("    day_rate=\"\"\n")
            outp.write("    night_rate=\"\"\n")
            outp.write("    export_rate=\"\"\n")
            outp.write("    day_rate_start=\"\"\n")
            outp.write("    night_rate_start=\"\"\n")
            outp.write("    ha_device_prefix=\"\"\n")
            outp.write("    data_smoother=\"\"\n")
            outp.write("    cache_location=\"/config/GivTCP\"\n")
            outp.write("    Debug_File_Location=\"/config/GivTCP/log_inv_"+str(inv)+".log\"\n")
            outp.write("    Smart_Target=False\n")
            outp.write("    GE_API=\"\"\n")
            outp.write("    Solcast_API=\"\"\n")
            outp.write("    Solcast_SiteID=\"\"\n")
            outp.write("    Solcast_SiteID2=\"\"\n")

    # Run the REST service so we can have config dash running

        if not os.path.exists('/config/GivTCP'):
            os.makedirs('/config/GivTCP')
            logger.critical("No config directory exists, so creating it...")
        else:
            logger.critical("Config directory already exists")

        os.chdir(PATH)
        GUPORT=6344+inv
        logger.critical ("Starting Gunicorn on port "+str(GUPORT))
        command=shlex.split("/usr/local/bin/gunicorn -w 3 -b :"+str(GUPORT)+" REST:giv_api")
        gunicorn[inv]=subprocess.Popen(command)
        pidfile=PATH+"/pidfile_"+str(inv)
        with open(pidfile, 'w') as pidf:
            pidf.writelines("gunicorn="+str(gunicorn[inv].pid))
        # Now run watchdog
        # watchdog()
        while True:
            sleep(60)
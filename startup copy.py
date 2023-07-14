from datetime import datetime, timedelta
from genericpath import exists
import os, pickle, subprocess, logging,shutil, shlex, schedule
from time import sleep
import rq_dashboard
from GivTCP.GivLUT import GivLUT
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

redis=subprocess.Popen(["/usr/bin/redis-server","/app/redis.conf"])
logger.critical("Running Redis")

rqdash=subprocess.Popen(["/usr/local/bin/rq-dashboard"])
logger.critical("Running RQ Dashboard on port 9181")

########### Run the various processes needed #############
os.chdir(PATH)

rqWorker=subprocess.Popen(["/usr/local/bin/python3",PATH+"/worker.py"])
logger.critical("Running RQ worker to queue and process givernergy-modbus calls")

while True:
    #Run jobs for smart target
    sleep (60)
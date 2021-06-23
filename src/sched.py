#Script to periodically execute the runALL function every 10s, to be used with MQTT for unattended publishing
import schedule
import time
from read import runAll

schedule.every(10).seconds.do(runAll)

while True:
    schedule.run_pending()
    time.sleep(1)
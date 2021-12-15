#Script to periodically execute the runALL function every 10s, to be used with MQTT for unattended publishing
# version 1.0
import schedule
import time
import sys
from read import runAll

loop_timer=int(sys.argv[1])
schedule.every(loop_timer).seconds.do(runAll)

while True:
    schedule.run_pending()
    time.sleep(1)
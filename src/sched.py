#Script to periodically execute the runALL function every 10s, to be used with MQTT for unattended publishing
# version 1.0
import schedule
import time
import sys
import read as rd

quick_loop_timer=int(sys.argv[1])
full_loop_timer=quick_loop_timer*3

schedule.every(quick_loop_timer).seconds.do(rd.runAll())
#schedule.every(full_loop_timer).seconds.do(runAll(fullrefresh=True))


while True:
    schedule.run_pending()
    time.sleep(1)
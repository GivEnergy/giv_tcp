#!/bin/sh
#Only used for Docker Deployment
# version 1.0

find -type f -name '*pkl*' -delete     #Remove any legacy pickle files
find -type f -name '*lockfile*' -delete     #Remove any legacy lockfiles

if [ "$SELF_RUN" = "True" ]                         #Only run Schedule if requested
then
    echo Running Invertor read loop every "$SELF_RUN_LOOP_TIMER"s...
    python3 /app/GivTCP/read.py self_run2  &       #Use to run periodically and push to MQTT
fi

if [ "$MQTT_ADDRESS" = "127.0.0.1" ] && [ "$MQTT_OUTPUT" = "True" ]                #Only run Mosquitto if its using local broker
then
    echo Starting Mosquitto on port "$MQTT_PORT"
    /usr/sbin/mosquitto -c /app/GivTCP/mqtt.conf &           #Run local MQTT broker as default
fi

if [ "$MQTT_OUTPUT" = "True" ]                      #If we are running MQTT then start up the listener for control
then
    echo subscribing Mosquitto on port "$MQTT_PORT"
    python3 /app/GivTCP/mqtt_client.py &
fi
echo instance is "$i"
GUPORT=$(($NUMINVERTORS+6344))
echo Starting Gunicorn on port "$GUPORT"
gunicorn -w 3 -b :"$GUPORT" GivTCP.REST:giv_api             #Use for on-demand read and control

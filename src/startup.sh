#!/bin/sh
#Only used for Docker Deployment

rm settings.py	# remove settings.py in case it exists

printf "class GiV_Settings:\n" >> settings.py
if [ -z "$INVERTOR_IP" ]
then
    for i in 1 2 3
    do
        echo 'IP not set in ENV, scanning network...'
        outputString=`python3 findInvertor.py`
        if [ ! -z "$outputString" ]
        then
            break
    done

    if [ -z "$outputString" ]
    then
        echo 'No invertor found... Please add into ENV manually'
        exit 1
    else
        echo Invertor found at "$outputString"
        printf "    invertorIP=\"$outputString\"\n" >> settings.py
    fi
else
    printf "    invertorIP=\"$INVERTOR_IP\"\n" >> settings.py
fi
printf "    Print_Raw_Registers=\"$PRINT_RAW\"\n" >> settings.py
printf "    MQTT_Address=\"$MQTT_ADDRESS\"\n" >> settings.py
printf "    MQTT_Username=\"$MQTT_USERNAME\"\n" >> settings.py
printf "    MQTT_Password=\"$MQTT_PASSWORD\"\n" >> settings.py
printf "    MQTT_Topic=\"$MQTT_TOPIC\"\n" >> settings.py
printf "    MQTT_Port=\"$MQTT_PORT\"\n" >> settings.py
printf "    output=\"$OUTPUT\"\n" >> settings.py
printf "    debug=\"$DEBUG\"\n" >> settings.py
printf "    Debug_File_Location=\"$DEBUG_FILE_LOCATION\"\n" >> settings.py

echo Starting Gunicorn on port 6345
gunicorn -w 3 -b :6345 REST:giv_api &     #Use for on-demand read and control

if [ "$MQTT_ADDRESS" = "127.0.0.1" ]        #Only run Mosquitto if its using local broker
then
    echo Starting Mosquitto on port "$MQTT_PORT"
    /usr/sbin/mosquitto -p "$MQTT_PORT" &        #Run local MQTT brker as default
fi

echo 'Running Invertor read loop every 10s...'
python3 sched.py       #Use to run periodically and push to MQTT
#!/bin/sh
#Only used for Docker Deployment
# version 1.0

FILE=/app/GivTCP/settings.py
if [ -f "$FILE" ]
then
    echo "$FILE exists, deleting and re-creating."
    rm settings.py    #delete file and re-create
else
    echo "$FILE does not exist, creating."
fi
FILE2=/app/lastUpdate.pkl
if [ -f "$FILE2" ]
then
    echo "$FILE2 exists, deleting."
    rm $FILE2    #delete file and re-create
fi
FILE3=/app/.lockfile
if [ -f "$FILE3" ]
then
    echo "$FILE3 exists, deleting."
    rm $FILE3    #delete file and re-create
fi

if [ -z "$INVERTOR_IP" ]; then
    echo 'IP not set in ENV'
    for i in 1 2 3
    do
        echo 'IP not set in ENV, scanning network attempt ' "$i"
        outputString=`python3 findInvertor.py`
        if [ ! -z "$outputString" ]
        then
            break
        fi
    done

    if [ -z "$outputString" ]
    then
        echo 'No invertor found... Please add into ENV manually'
        exit 1
    else
        echo Invertor found at "$outputString"
        printf "class GiV_Settings:\n" >> settings.py
        printf "    invertorIP=\"$outputString\"\n" >> settings.py
    fi
else
        printf "class GiV_Settings:\n" >> settings.py
        printf "    invertorIP=\"$INVERTOR_IP\"\n" >> settings.py
fi
printf "    numBatteries=$NUM_BATTERIES\n" >> settings.py
printf "    Print_Raw_Registers=$PRINT_RAW\n" >> settings.py
printf "    MQTT_Output=$MQTT_OUTPUT\n" >> settings.py
printf "    MQTT_Address=\"$MQTT_ADDRESS\"\n" >> settings.py
printf "    MQTT_Username=\"$MQTT_USERNAME\"\n" >> settings.py
printf "    MQTT_Password=\"$MQTT_PASSWORD\"\n" >> settings.py
printf "    MQTT_Topic=\"$MQTT_TOPIC\"\n" >> settings.py
printf "    MQTT_Port=$MQTT_PORT\n" >> settings.py
printf "    Log_Level=\"$LOG_LEVEL\"\n" >> settings.py
printf "    Debug_File_Location=\"$DEBUG_FILE_LOCATION\"\n" >> settings.py
printf "    Influx_Output=$INFLUX_OUTPUT\n" >> settings.py
printf "    influxURL=\"$INFLUX_URL\"\n" >> settings.py
printf "    influxToken=\"$INFLUX_TOKEN\"\n" >> settings.py
printf "    influxBucket=\"$INFLUX_BUCKET\"\n" >> settings.py
printf "    influxOrg=\"$INFLUX_ORG\"\n" >> settings.py
printf "    HA_Auto_D=$HA_AUTO_D\n" >> settings.py 
printf "    first_run= True\n" >> settings.py

#TODO Update givTCP if a newer release is available

if [ "$SELF_RUN" = "True" ]                         #Only run Schedule if requested
then
    echo Running Invertor read loop every "$SELF_RUN_LOOP_TIMER"s...
    python3 -m GivTCP.read.self_run "$SELF_RUN_LOOP_TIMER" &       #Use to run periodically and push to MQTT
fi

if [ "$MQTT_ADDRESS" = "127.0.0.1" ]                #Only run Mosquitto if its using local broker
then
    echo Starting Mosquitto on port "$MQTT_PORT"
    /usr/sbin/mosquitto -p "$MQTT_PORT" &           #Run local MQTT broker as default
fi

if [ "$MQTT_OUTPUT" = "True" ]                      #If we are running MQTT then start up the listener for control
then
    echo subscribing Mosquitto on port "$MQTT_PORT"
    python3 -m GivTCP.services.mqtt_client &
fi

GUPORT=$(($GIVTCPINSTANCE+6344))
echo Starting Gunicorn on port "$GUPORT"
gunicorn -w 3 -b :"$GUPORT" GivTCP.REST:giv_api            #Use for on-demand read and control



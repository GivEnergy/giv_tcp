#!/bin/sh
#Only used for Docker Deployment
# version 1.0

# If only 1 inertor then just launch startup.sh in the standard folder!

for i in $(seq 1 $NUMINVERTORS)
do
    # Set path to new folder
    PATH=/app/GivTCP_"${i}"

    # Copy the GivTCP folder across
    if [ ! -d "$PATH" ]; then
        echo Creating "$PATH" folder
        echo cp -r /app/GivTCP "$PATH"
        /bin/cp -r /app/GivTCP "$PATH"
    fi
    
    # create settings.py file in the directory
    FILE=${PATH}/settings.py
    FILE2=${PATH}/startup.sh
    FILE3=/app/GivEnergy-Smart-Home-Display/app.json

    #Remove settings file if its already there
    if [ -f "$FILE" ]
    then
        echo "$FILE exists, deleting and re-creating."
        /bin/rm "$FILE"    #delete file and re-create
    else
        echo "$FILE does not exist, creating."
    fi

    #Remove startup file if its already there
    if [ -f "$FILE2" ]
    then
        echo "$FILE2 exists, deleting and re-creating."
        /bin/rm "$FILE2"    #delete file and re-create
    else
        echo "$FILE2 does not exist, creating."
    fi



    if [ $WEB_DASH = "True" ]
    then
        if [ -f "$FILE3" ]
        then
            echo "$FILE3 exists, deleting and re-creating."
            /bin/rm "$FILE3"    #delete file and re-create
        else
            echo "$FILE3 does not exist, creating."
        fi
        echo "Creating web dashboard config file"
        printf "{\n" >> $FILE3
        printf "\"givTcpHostname\": \"${HOSTIP}:6345\",\n" >> $FILE3
        printf "\"solarRate\": ${DAYRATE},\n" >> $FILE3
        printf "\"exportRate\": ${EXPORTRATE}\n" >> $FILE3
        printf "}" >> $FILE3
    fi

    ############################
    ### Create Settings File ###
    ############################
    echo "Creating settings.py for Invertor ${i}"

    printf "class GiV_Settings:\n" >> "$FILE"
    if [ "$i" = 1 ]; then
        printf "    invertorIP=\"$INVERTOR_IP_1\"\n" >> "$FILE"
        printf "    numBatteries=\"$NUMBATTERIES_1\"\n" >> "$FILE"
    elif [ "$i" = 2 ]; then
        printf "    invertorIP=\"$INVERTOR_IP_2\"\n" >> "$FILE"
        printf "    numBatteries=\"$NUMBATTERIES_2\"\n" >> "$FILE"
    elif [ "$i" = 3 ]; then
        printf "    invertorIP=\"$INVERTOR_IP_3\"\n" >> "$FILE"
        printf "    numBatteries=\"$NUMBATTERIES_3\"\n" >> "$FILE"
    elif [ "$i" = 4 ]; then
        printf "    invertorIP=\"$INVERTOR_IP_4\"\n" >> "$FILE"
        printf "    numBatteries=\"$NUMBATTERIES_4\"\n" >> "$FILE"
    fi 
    printf "    Print_Raw_Registers=$PRINT_RAW\n" >> "$FILE"
    printf "    MQTT_Output=$MQTT_OUTPUT\n" >> "$FILE"
    printf "    MQTT_Address=\"$MQTT_ADDRESS\"\n" >> "$FILE"
    printf "    MQTT_Username=\"$MQTT_USERNAME\"\n" >> "$FILE"
    printf "    MQTT_Password=\"$MQTT_PASSWORD\"\n" >> "$FILE"
    printf "    MQTT_Topic=\"$MQTT_TOPIC\"\n" >> "$FILE"
    printf "    MQTT_Port=$MQTT_PORT\n" >> "$FILE"
    printf "    Log_Level=\"$LOG_LEVEL\"\n" >> "$FILE"
    printf "    Debug_File_Location=\"$DEBUG_FILE_LOCATION\"\n" >> "$FILE"
    printf "    Influx_Output=$INFLUX_OUTPUT\n" >> "$FILE"
    printf "    influxURL=\"$INFLUX_URL\"\n" >> "$FILE"
    printf "    influxToken=\"$INFLUX_TOKEN\"\n" >> "$FILE"
    printf "    influxBucket=\"$INFLUX_BUCKET\"\n" >> "$FILE"
    printf "    influxOrg=\"$INFLUX_ORG\"\n" >> "$FILE"
    printf "    HA_Auto_D=$HA_AUTO_D\n" >> "$FILE" 
    printf "    first_run= True\n" >> "$FILE"
    printf "    self_run_timer= $SELF_RUN_LOOP_TIMER\n" >> "$FILE"
    printf "    givtcp_instance= $i\n" >> "$FILE"
    printf "    default_path= \"$PATH\"\n"  >> "$FILE"
    printf "    day_rate= \"$DAYRATE\"\n"  >> "$FILE"
    printf "    night_rate= \"$NIGHTRATE\"\n"  >> "$FILE"
    printf "    day_rate_start= \"$DAYRATESTART\"\n"  >> "$FILE"
    printf "    night_rate_start= \"$NIGHTRATESTART\"\n"  >> "$FILE"
    printf "    ha_device_prefix= \"$HADEVICEPREFIX\"\n"  >> "$FILE"
    
    
    #############################
    ### Create Startup Script ###
    #############################
    echo "Creating startup.sh file for Invertor ${i}"

    printf "#!/bin/sh\n" >> "$FILE2"
    printf "#Only used for Docker Deployment\n" >> "$FILE2"
    printf "# version 1.0\n" >> "$FILE2"
    printf "/usr/bin/find -type f -name 'regCache.pkl' -delete     #Remove any legacy pickle files\n" >> "$FILE2"
    printf "/usr/bin/find -type f -name '*lockfile*' -delete     #Remove any legacy lockfiles\n" >> "$FILE2"
    printf "echo GivTCP instance is \"$i\"\n" >> "$FILE2"
    ### Run main invertor read loop ###
    printf "if [ \"\$SELF_RUN\" = \"True\" ]                         #Only run Schedule if requested\n" >> "$FILE2"
    printf "then\n" >> "$FILE2"
    printf "    echo Running Invertor read loop every \"\$SELF_RUN_LOOP_TIMER\"s...\n" >> "$FILE2"
    printf "    /usr/local/bin/python3 ${PATH}/read.py self_run2  &       #Use to run periodically and push to MQTT\n" >> "$FILE2"
    printf "fi\n" >> "$FILE2"
    ### Run MQTT Broker if requested ###
    printf "if [ \"\$MQTT_ADDRESS\" = \"127.0.0.1\" ] && [ \"\$MQTT_OUTPUT\" = \"True\" ]                #Only run Mosquitto if its using local broker\n" >> "$FILE2"
    printf "then\n" >> "$FILE2"
    printf "    echo Starting Mosquitto on port \"\$MQTT_PORT\"\n" >> "$FILE2"
    printf "    /usr/sbin/mosquitto -c ${PATH}/mqtt.conf &           #Run local MQTT broker as default\n" >> "$FILE2"
    printf "fi\n" >> "$FILE2"
    ### Run MQTT client to listen for MQTT control commands ###
    printf "if [ \"\$MQTT_OUTPUT\" = \"True\" ]                      #If we are running MQTT then start up the listener for control\n" >> "$FILE2"
    printf "then\n" >> "$FILE2"
    printf "    echo subscribing Mosquitto on port \"\$MQTT_PORT\"\n" >> "$FILE2"
    printf "    /usr/local/bin/python3 ${PATH}/mqtt_client.py &\n" >> "$FILE2"
    printf "fi\n" >> "$FILE2"
    ### Run Web Dashboard ###
    printf "if [ \"\$WEB_DASH\" = \"True\" ]\n" >> "$FILE2"
    printf "then\n" >> "$FILE2"
    printf "    (cd /app/GivEnergy-Smart-Home-Display; /usr/bin/node /usr/local/bin/serve -p ${WEB_DASH_PORT}&)\n">> "$FILE2"
    printf "fi\n" >> "$FILE2"
    ### Run REST API ###
    printf "GUPORT=$((${i}+6344))\n" >> "$FILE2"
    printf "echo Starting Gunicorn on port \"\$GUPORT\"\n" >> "$FILE2"
    printf "(cd \$PATH; /usr/local/bin/gunicorn -w 3 -b :\"\$GUPORT\" REST:giv_api)" >> "$FILE2"

    if [ "$i" = "$NUMINVERTORS" ]
    then
        (cd $PATH; /bin/sh startup.sh)   #Launch the individual startup script and hold for completion
    else
        (cd $PATH; /bin/sh startup.sh &)   #Launch the individual startup script and carry on executing
    fi
done

/bin/sh
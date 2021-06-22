#!/bin/sh
#Only used for Docker Deployment

rm settings.py	# remove settings.py in case it exists

printf "class GiV_Settings:\n" >> settings.py
#if [$INVERTOR_IP=""]
#then
#outputString=$(python3 findInvertor.py)
printf "    invertorIP=\"$outputString\"\n" >> settings.py
#else
printf "    invertorIP=\"$INVERTOR_IP\"\n" >> settings.py
#fi
printf "    dataloggerSN=\"$SERIAL_NUMBER\"\n" >> settings.py
printf "    Print_Raw_Registers=\"$PRINT_RAW\"\n" >> settings.py
printf "    MQTT_Address=\"$MQTT_ADDRESS\"\n" >> settings.py
printf "    MQTT_Username=\"$MQTT_USERNAME\"\n" >> settings.py
printf "    MQTT_Password=\"$MQTT_PASSWORD\"\n" >> settings.py
printf "    MQTT_Topic=\"$MQTT_TOPIC\"\n" >> settings.py
printf "    output=\"$OUTPUT\"\n" >> settings.py
printf "    debug=\"$DEBUG\"\n" >> settings.py
printf "    Debug_File_Location=\"$DEBUG_FILE_LOCATION\"\n" >> settings.py

gunicorn -w 3 -b :6345 REST:giv_api

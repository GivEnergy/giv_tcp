# Starting Guide

This page will shows you how to use the script, if you are unsure where to start, just following on this page!

## Set Up
You will need set up your dongle and have your device connected to dongle.
( If you are connecting to your main Wifi and your dongle serves extention, you need to change some the configuration, see below for more)

## Methodology
- VS code

### VS code
<img src="/images/giv_tcp_tutorial_1.png"/>

1. Press the code button at the top right of the github page

2. Download the zip file

3. Extract the zip file and open the extracted file on VS code

<img src="/images/giv_tcp_tutorial_2.png"/>

4. Go to Terminal and run the code 

```python3 GivTCP.py {{invertorIP}} {{wifiSN}} {{MQTTIP}} {{MQTTusername}} {{MQTTpassword}}```

where the invertorIP (if directly connected to dongle) is 10.10.100.254

MQTTIP is your MQTT address, if you dont have a MQTT preference, or you just want to make a test, you can choose `public.mqtthq.com` 
from https://mqtthq.com/

The last two parameters are optional, if you have an MQTT account, you can type the parameter to save your data into your own MQTT account

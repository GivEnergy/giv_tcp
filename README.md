# GivTCP
TCP Modbus connection to MQTT for Givenergy Battery/PV Invertors

I've been plugging away at getting a script running locally that connects to the invertor and can read register data and push it straight to an MQTT server. This is allowing me to get real-time (10-15s) data feed without having to use the cloud. Its very alpha at the moment and isn't particularly robust, but I'm keen to share it to get some feedback.

In essence the script connects to a Modbus TCP server which runs on the wifi dongle, so all you need is somewhere to run the script on the same network. You will need the following to make it work:
* MQTT server running on the network and know its IP address
* MQTT login credentials (optional)
* IP address of the invertor
* Serial Number of the wifi/gps dongle (not the invertor) - which can be found on the portal: https://www.givenergy.cloud/GivManage/setting/deviceMenu/inverterList
* Machine running Python which has following modules installed:
  * crccheck
  * paho-mqtt

Currently the script will write timeslots and power stats to the MQTT queue, but can be made to publish any register.


script is called with arguments as below:

`python3 GivTCP.py {{invertorIP}} {{wifiSN}} {{MQTTIP}} {{MQTTusername}} {{MQTTpassword}}`

[Some API Documentation](/documentation/APIDocumentation)


Control is also possible, but hasn't been implemented yet.

Health Warning:
* I'm seeing pretty frequent timeouts on the Modbus TCP connection, so its not super reliable, but it will keep on calling and hopefully get data next time round
* You will need a way of running the script contuinually, I'm using node-red and an exec-node
![image](https://user-images.githubusercontent.com/69121158/118310510-a219a700-b4e6-11eb-9979-e3094aa7e776.png)
* Not even beta test ready yet, but open for all to share in the effort of making this work.

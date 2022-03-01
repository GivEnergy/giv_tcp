# set base image (host OS)
FROM python:rc-alpine

RUN apk --no-cache add mosquitto
RUN apk add --no-cache bash

# set the working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY src/ .
COPY givenergy_modbus/ /usr/local/lib/python3.10/site-packages/givenergy_modbus

ENV INVERTOR_IP=""
ENV NUM_BATTERIES="1"
ENV MQTT_OUTPUT="True"
ENV MQTT_ADDRESS="127.0.0.1"
ENV MQTT_USERNAME=""
ENV MQTT_PASSWORD=""
ENV MQTT_TOPIC=""
ENV MQTT_PORT="1883"
ENV LOG_LEVEL="Error"
ENV DEBUG_FILE_LOCATION=""
ENV PRINT_RAW="True"
ENV SELF_RUN="True"
ENV SELF_RUN_LOOP_TIMER="10"
ENV INFLUX_OUTPUT="False"
ENV INFLUX_URL=""
ENV INFLUX_TOKEN=""
ENV INFLUX_BUCKET=""
ENV INFLUX_ORG=""
ENV HA_AUTO_D="False"
ENV GIVTCPINSTANCE=1

EXPOSE 6345 1883

ENTRYPOINT ["sh", "/app/startup.sh"]

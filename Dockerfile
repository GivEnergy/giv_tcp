# set base image (host OS)
FROM python:rc-alpine

RUN apk --no-cache add mosquitto

# set the working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY src/ .

ENV INVERTOR_IP=""
ENV MQTT_OUTPUT="True"
ENV MQTT_ADDRESS="127.0.0.1"
ENV MQTT_USERNAME=""
ENV MQTT_PASSWORD=""
ENV MQTT_TOPIC=""
ENV MQTT_PORT="1883"
ENV JSON_OUTPUT="False"
ENV LOG_LEVEL="Error"
ENV DEBUG_FILE_LOCATION=""
ENV PRINT_RAW="False"
ENV SELF_RUN="True"
ENV SELF_RUN_LOOP_TIMER="10"
ENV INFLUX_OUTPUT="False"
ENV INFLUX_URL=""
ENV INFLUX_TOKEN=""
ENV INFLUX_BUCKET=""
ENV INFLUX_ORG=""

EXPOSE 6345 1883

ENTRYPOINT ["sh", "/app/startup.sh"]

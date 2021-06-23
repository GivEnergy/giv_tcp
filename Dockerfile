# set base image (host OS)
FROM python:rc-alpine

RUN apk --no-cache add mosquitto mosquitto-clients

# set the working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY src/ .

ENV INVERTOR_IP=""
ENV PRINT_RAW="False"
ENV MQTT_ADDRESS="127.0.0.1"
ENV MQTT_USERNAME=""
ENV MQTT_PASSWORD=""
ENV MQTT_TOPIC=""
ENV MQTT_PORT="1883"
ENV OUTPUT="MQTT"
ENV DEBUG="False"
ENV DEBUG_FILE_LOCATION=""

EXPOSE 6345 1883

ENTRYPOINT ["sh", "/app/startup.sh"]

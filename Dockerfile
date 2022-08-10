# set base image (host OS)
FROM python:rc-alpine

RUN apk --no-cache add mosquitto
RUN apk add curl
# Install nodejs for the dashboard
#RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apk add --update npm
RUN npm install -g serve
RUN apk add git
RUN apk add tzdata

# set the working directory in the container
WORKDIR /app

RUN git clone --branch givtcp https://github.com/DanielGallo/GivEnergy-Smart-Home-Display.git

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY GivTCP/ ./GivTCP

COPY setup.sh setup.sh
#COPY givenergy_modbus/ /usr/local/lib/python3.10/site-packages/givenergy_modbus

ENV NUMINVERTORS="1"
ENV INVERTOR_IP_1=""
ENV NUMBATTERIES_1="1"
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
ENV SELF_RUN_LOOP_TIMER="5"
ENV INFLUX_OUTPUT="False"
ENV INFLUX_URL=""
ENV INFLUX_TOKEN=""
ENV INFLUX_BUCKET=""
ENV INFLUX_ORG=""
ENV HA_AUTO_D="True"
ENV HADEVICEPREFIX="GivTCP"
ENV PYTHONPATH="/app"
ENV DAYRATE=0.155
ENV NIGHTRATE=0.055
ENV HOSTIP="192.168.2.10"
ENV DAYRATESTART="04:30"
ENV NIGHTRATESTART="00:00"
ENV TZ="Europe/London"


EXPOSE 6345 1883 3000

CMD ["sh", "/app/setup.sh"]

## Critical to update
NUMINVERTORS=1                       # Set this to the number of Inverters in your setup, then replicate the next two lines for each inverter (changing the last number of the ENV)
INVERTOR_IP_1=''                     # Set this to the IP address of your Inverter on your local network
NUMBATTERIES_1=1                     # Number of battery modules installed and connected to the above inverter
MQTT_OUTPUT=True                     # "True" if you want to publish your data to MQTT, "False" otherwise
MQTT_ADDRESS=''                      # IP address of an existing MQTT broker, or leave as "127.0.0.1" to use the internal broker
MQTT_USERNAME=''                     # Username of your existing broker, if needed. Not required for internal broker
MQTT_PASSWORD=''                     # Password of your existing broker, if needed. Not required for internal broker
HOSTIP=''                            # External IP address of the docker host (needed for web dashboard)
CACHELOCATION='/config/GivTCP'       # Location of cache data, this folder can be mapped to a persistence storage outside the container
TZ='Europe/London'                   # Set to your Timezone
## Optional
MQTT_TOPIC=''                        # Root topic to publish data to for Inverter 1. If left blank it will default to GivEnergy/<invertor_serial_number>
MQTT_TOPIC_2=''                      # Root topic to publish data to for Inverter 2. If left blank it will default to GivEnergy/<invertor_serial_number>
MQTT_TOPIC_3=''                      # Root topic to publish data to for Inverter 3. If left blank it will default to GivEnergy/<invertor_serial_number>
MQTT_PORT=1883                       # Port of your existing broker, leave as "1883" for internal broker

LOG_LEVEL='Info'                     # Level of logs to be reported: "Error", "Info" or "Debug"
PRINT_RAW=True                       # If True this will publish all inverter data unprocessed as well as standard data
SELF_RUN=True                        # If True the container will self-run and connect and publish data. If "False" the you will need to trigger externally via REST
SELF_RUN_LOOP_TIMER=15               # Wait time between every read command to the inverter
QUEUE_RETRIES=2                      # The number of calls to the inverter when trying to set a register. A higher number improves the chance of inverter writes succeeding

INFLUX_OUTPUT=False                  # "True" if you want to publish your data to InfluxDB, "False" otherwise
INFLUX_URL=''                        # URL of an external Influx instance
INFLUX_TOKEN=''                      # Access Token for your Influx instance
INFLUX_BUCKET=''                     # Data Bucket of your Influx instance you want data sent to
INFLUX_ORG=''                        # Influx instance Organisation
HA_AUTO_D=True                       # If True (and if MQTT_OUTPUT is True) this will publish Home Assistant Auto Discovery messages to the broker
HADEVICEPREFIX='GivTCP'              # Defines the prefix for all entities in Home Assistant for inverter 1
HADEVICEPREFIX_2='GivTCP2'           # Defines the prefix for all entities in Home Assistant for inverter 2
HADEVICEPREFIX_3='GivTCP3'           # Defines the prefix for all entities in Home Assistant for inverter 3
PYTHONPATH='/app'       
DYNAMICTARIFF=False                  # When set to true DAYRATESTART and NIGHTRATESTART times are ignored and tariff rates are changed by a dedicated entity/function
DAYRATE=0.395                        # Price in £/$ for your daytime electricity per kWh
NIGHTRATE=0.155                      # Price in £/$ for your night time electricity per kWh
EXPORTRATE=0.04                      # Price in £/$ for your export electricity per kWh
DAYRATESTART='05:30'                 # Time in HH:MM when your day time\expensive tariff kicks in
NIGHTRATESTART='23:30'               # Time in HH:MM when your night time\cheap tariff kicks in
WEB_DASH=False                       # Enable the web dashboard
WEB_DASH_PORT=3000                   # Port to serve the web dashboard on. Should be the same as the private port (above), not the container port
SMARTTARGET=False                    # Enables the PALM capability, requires the three ENV below to be set
GEAPI=''                             # API Key for the GivEnergy Cloud
SOLCASTAPI=''                        # API key for Solcast
SOLCASTSITEID=''                     # SiteID for Solcast site (first array)
SOLCASTSITEID2=''                    # SiteID for Solcast site (second array)
DATASMOOTHER='medium'                # Set the data smoothing to most aggressive setting (High, medium, low, none)
PALM_WINTER='01,02,03,10,11,12'      # Comma delimited list of the winter months (01=January, etc)
PALM_SHOULDER='04,05,09'             # Comma delimited list of months in which consumption can vary so SOC calculation should be more cautious
PALM_MIN_SOC_TARGET=25               # Lower limit for state of charge (summertime)
PALM_MAX_SOC_TARGET=45               # Lower limit for SoC limit in shoulder months
PALM_BATT_RESERVE=4                  # Battery reserve for power cuts (minimum of 4%)
PALM_BATT_UTILISATION=0.85           # Usable proportion of battery (100% less reserve and any charge limit) on a scale of 0-1
PALM_WEIGHT=35                       # Weighting used for final target soc
LOAD_HIST_WEIGHT=1                   # Load History Weighting
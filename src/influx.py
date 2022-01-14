# version 1.0
import sys
import atexit
import rx
import json
from influxdb_client import InfluxDBClient, WriteApi, WriteOptions
from datetime import timedelta
from rx import operators as ops
from GivTCP import GivTCP
from datetime import datetime
from settings import GiV_Settings

class GivInflux():

    def line_protocol(readings):
        return '{},tagKey={} {}'.format(GivTCP.SN,'GivReal', readings) 

    def make_influx_string(datastr):
        new_str=datastr.replace(" ","_")
        new_str=new_str.lower()
        return new_str

    def publish(data):
        output_str=""
        power_output = data['Power']
        for key in power_output:
            GivTCP.debug("Creating Power string for InfluxDB")
            output_str=output_str+str(GivInflux.make_influx_string(key))+'='+str(power_output[key])+','

        energy_today = data['Energy/Today']
        for key in energy_today:
            GivTCP.debug("Creating Energy/Today string for InfluxDB")
            output_str=output_str+str(GivInflux.make_influx_string(key))+'='+str(energy_today[key])+','

        energy_total = data['Energy/Total']
        for key in energy_total:
            GivTCP.debug("Creating Energy/Total string for InfluxDB")
            output_str=output_str+str(GivInflux.make_influx_string(key))+'='+str(energy_total[key])+','

        GivTCP.debug("Data sent to Influx is: "+ output_str[:-1])
        data1=GivInflux.line_protocol(output_str[:-1])
        
        _db_client = InfluxDBClient(url=GiV_Settings.influxURL, token=GiV_Settings.influxToken, org=GiV_Settings.influxOrg, debug=True)
        _write_api = _db_client.write_api(write_options=WriteOptions(batch_size=1))
        _write_api.write(bucket=GiV_Settings.influxBucket, record=data1)

        write_api.close()
        db_client.close()

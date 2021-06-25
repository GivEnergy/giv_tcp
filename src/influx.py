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

    def giv_stats(multi_output):
        """
        Calls runAll and returns a string suitable to populate Influx
        """
        power_output_str=""
        key = 'Power'

        if key in multi_output.keys():
            GivTCP.debug("Received good JSON")
            multi_output2 = multi_output['Power']
            power_output_str='pv_power='+str(multi_output2['PV Power'])+',grid_power='+str(multi_output2['Grid Power'])+',import_power='+str(multi_output2['Import Power'])+',export_power='+str(multi_output2['Export Power'])+',eps_power='+str(multi_output2['EPS Power'])+',invertor_power='+str(multi_output2['Export Power'])+',load_power='+str(multi_output2['Load Power'])+',self_consumption_power='+str(multi_output2['Self Consumption Power'])+',battery_power='+str(multi_output2['Battery Power'])+',charge_power='+str(multi_output2['Charge Power'])+',discharge_power='+str(multi_output2['Discharge Power'])+',battery_soc='+str(multi_output2['SOC'])
            GivTCP.debug("InfluxDB feed is " + power_output_str )        
            print (power_output_str)

        return (power_output_str)
    
    def on_exit(db_client: InfluxDBClient, write_api: WriteApi):
        """Close clients after terminate a script.

        :param db_client: InfluxDB client
        :param write_api: WriteApi
        :return: nothing
        """
        write_api.close()
        db_client.close()

    def line_protocol(readings):
        """Create a InfluxDB line protocol with structure:

            'inverterStats,tagKey=GivReal pv_power=1370,pv_power_east=138,pv_power_west=1232,grid_power=48,import_power=0,export_power=48,eps_power=0,invertor_power=1344,load_power=1295,self_consumption_power=1295,battery_power=0,charge_power=0,discharge_power=0,battery_soc=100'

        :return: Line protocol to write into InfluxDB
        """
        return 'inverterStats,tagKey={} {}'.format('GivReal', readings) 

    def publish(data):
        data1 = rx\
            .interval(period=timedelta(seconds=8))\
            .pipe(ops.map(lambda t: giv_stats(data)),
                ops.map(lambda readings: line_protocol(readings)))
        _db_client = InfluxDBClient(url=GiV_Settings.influxURL, token=GiV_Settings.influxToken, org=GiV_Settings.influxOrg, debug=True)

        """
        Create client that writes data into InfluxDB
        """
        _write_api = _db_client.write_api(write_options=WriteOptions(batch_size=1))
        _write_api.write(bucket=GiV_Settings.influxBucket, record=data1)

        """
        Call after terminate a script
        """
        atexit.register(on_exit, _db_client, _write_api)
        input()


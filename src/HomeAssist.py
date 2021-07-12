from GivTCP import GivTCP
from settings import GiV_Settings
from requests import post

class GivHA:
    def publish(data,type):
        headers = {
        'Authorization': 'Bearer '+GiV_Settings.HA_token,
        'content-type': 'application/json',
        }
        if type=="Power":
            attributes = '"attributes":{"unit_of_measurement":"W","icon":"mdi:battery-charging","device_class":"power"}'
        elif type=="Energy":
            attributes = '"attributes":{"unit_of_measurement":"kWh","icon":"mdi:battery-charging","device_class":"power"}'

        for key in data:
            entityid="sensor.givtcp_"+key.replace(" ","_")
            url = GiV_Settings.HA_url+'/api/states/'+entityid
            payload='{"state":"'+str(data[key])+'",'+attributes+'}'
            GivTCP.debug("Publishing "+str(entityid)+": "+str(payload))
            response = post(url, headers=headers, data=payload)
            GivTCP.debug("Result is: "+str(response.text))

    def push(data):
        if 'Power' in data.keys():
            power_output = data['Power']
            GivTCP.debug("Creating Power entities for HA")
            GivHA.publish(power_output,"Power")
        
        if 'Energy/Today' in data.keys():
            energy_today_output = data['Energy/Today']
            GivTCP.debug("Creating Today Energy entities for HA")
            GivHA.publish(energy_today_output,"Energy")

        if 'Energy/Today' in data.keys():
            energy_total_output = data['Energy/Total']
            GivTCP.debug("Creating Total Energy entities for HA")
            GivHA.publish(energy_total_output,"Energy")

if __name__ == '__main__':
    globals()[sys.argv[1]]()
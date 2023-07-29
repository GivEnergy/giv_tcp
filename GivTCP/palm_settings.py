# version 2023.06.21
# Settings file for use with palm.py: 30-minute calculations (v0.9.0) and weightings for daily historical consumption (v0.10.0)

from settings import GiV_Settings
from GivLUT import GivLUT
import pickle
from os.path import exists
import os

# User settings for GivEnergy inverter API
class GE:
    enable = True
    # Modify url with system name in place of CExxxxxx and paste API key generated on GivEnergy web portal in place of xxxx
    url = "https://api.givenergy.cloud/v1/inverter/"+GiV_Settings.serial_number+"/"
    key = str(os.getenv('GEAPI'))
    
    # Most users will not need to touch that many of the pre-configured settings below
    
    # Disable SoC calculation in the winter months as consumption >> generation
    # winter = ["01", "02", "11", "12"]
    winter = os.getenv('PALM_WINTER').split(',')

    # Throttle SoC calculation in shoulder months as consumption can vary with heating coming on, etc
    # shoulder = ["03", "04", "09", "10"]
    shoulder = os.getenv('PALM_SHOULDER').split(',')

    # Lower limit for state of charge (summertime)
    #min_soc_target = 25
    min_soc_target = int(os.getenv('PALM_MIN_SOC_TARGET'))

    # Lower limit for SoC limit in shoulder months
    #max_soc_target = 45
    max_soc_target = int(os.getenv('PALM_MAX_SOC_TARGET'))

    # Battery reserve for power cuts (minmum of 4%)
    #batt_reserve = 4
    batt_reserve = int(os.getenv('PALM_BATT_RESERVE'))

    # Nominal battery capacity
    #batt_capacity = 10.4
    #batt_capacity = float(os.getenv('PALM_BATT_CAPACITY')) 

    # Usable proportion of battery (100% less reserve and any charge limit)
    #batt_utilisation = 0.85
    batt_utilisation = float(os.getenv('PALM_BATT_UTILISATION'))

    #batt_max_charge = batt_capacity * batt_utilisation

    # Inverter charge/discharge rate in kW, INVERTER_MAX_BAT_RATE is in Watts
    #charge_rate = 2.5
    #charge_rate = float(os.getenv('INVERTER_MAX_BAT_RATE') / 1000)
    if exists(GivLUT.regcache):      # if there is a cache then grab it
        with open(GivLUT.regcache, 'rb') as inp:
            regCacheStack = pickle.load(inp)
            multi_output_old = regCacheStack[4]
        charge_rate=float(multi_output_old['Invertor_Details']['Invertor_Max_Bat_Rate'])/1000
    else:
        charge_rate=2.5

  
    # Default data for base load. Overwritten by actual data if available
    base_load = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, \
                 0.2, 0.2, 0.2, 0.3, 0.2, 0.2, 0.1, 0.3, 0.3, 0.2, 0.3, 0.8, 0.6, 0.3, 0.3, 0.2, \
                 0.2, 0.2, 0.2, 0.6, 0.6, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]

    # Load history is a weighted average of actual load from previous days.
    # Uncomment required settings or make your own using positive integers only. Examples:
    # Most recent day only
    load_hist_weight = [1] # Need to declare this even if using environment variables, just to instantiate the property
    # 3-day average
    # load_hist_weight = [1, 1, 1]
    # 7-day average
    # load_hist_weight = [1, 1, 1, 1, 1, 1, 1]
    # Same day last week - useful if, say, Monday is always wash-day
    # load_hist_weight = [0, 0, 0, 0, 0, 0, 1]
    # Weighted average (a more extreme example)
    # load_hist_weight = [4, 2, 2, 1, 1, 1, 1]

    # Pull in load history weighting from environment variables.
    tmp_load_hist_weight = str(os.getenv('LOAD_HIST_WEIGHT'))
    load_hist_weight = [int(elem) for elem in tmp_load_hist_weight.split(',') if elem.strip().isnumeric()]

    # Start time for Overnight Charge
    start_time = os.getenv('NIGHTRATESTART')

    # End time for Overnight Charge
    end_time = os.getenv('DAYRATESTART')


# SolCast PV forecast generator. Up to two arrays are supported with a forecast for each
class Solcast:
    def isBlank (myString):
        return not (myString and myString.strip())
    
    enable = True
    key = str(os.getenv('SOLCASTAPI'))
    url_se = "https://api.solcast.com.au/rooftop_sites/"+str(os.getenv('SOLCASTSITEID'))
    
    # For single array installation uncomment the line below and comment out the subsequent line
    #url_sw = ""
    if not isBlank(str(os.getenv('SOLCASTSITEID2'))):
        url_sw = "https://api.solcast.com.au/rooftop_sites/"+str(os.getenv('SOLCASTSITEID2'))
    else:
        url_sw = ""

    weight = int(os.getenv('PALM_WEIGHT'))  # Confidence factor for forecast (range 10 to 90)

    cmd = "/forecasts?format=json"

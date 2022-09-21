# version 2022.08.05
# palm_settings.py file for use with palm.py and palm_soc.py
#
# IMPORTANT
# For palm_soc.py only enter parameters in the first part of the file and ignore the entries below the horizontal line
from settings import GiV_Settings
import os

# User settings for GivEnergy inverter API
class GE:
    enable = True
    # Modify url with system name in place of CExxxxxx and paste API key generated on GivEnergy web portal in place of xxxx
    url = "https://api.givenergy.cloud/v1/inverter/"+GiV_Settings.serial_number+"/"
    key = str(os.getenv('GEAPI'))

    # Most users will not need to touch that many of the pre-configured settings below
    
    # Disable SoC calculation in the winter months as consumption >> generation
    winter = ["01", "02", "03", "10", "11", "12"]

    # Throttle SoC calculation in shoulder months as consumption can vary with heating coming on, etc
    shoulder = ["04", "05", "09"]

    # Lower limit for state of charge (summertime)
    min_soc_target = 25

    # Lower limit for SoC limit in shoulder months
    max_soc_target = 45

    # Battery reserve for power cuts (minmum of 4%)
    batt_reserve = 4

    # Nominal battery capacity
    batt_capacity = 10.4

    # Usable proportion of battery (100% less reserve and any charge limit)
    batt_utilisation = 0.85

    batt_max_charge = batt_capacity * batt_utilisation

    # Inverter charge/discharge rate in kW
    charge_rate = 2.5

    # Default data for base load. Overwritten by actual data if available
    base_load = [0.3, 2, 0.3, 0.3, 0.3, 0.5, 1.7, 1.8, 2.6, 1.5, 0.5, 2.5,\
        1.3, 1, 1.5, 0.5, 0.3, 1, 1.5, 1, 0.6, 0.5, 0.5, 0.3]

    # Start time for Overnight Charge
    start_time = "00:30"

    # End time for Overnight Charge
    end_time = "04:30"


# SolCast PV forecast generator. Up to two arrays are supported with a forecast for each
class Solcast:
    enable = True
    key = str(os.getenv('SOLCASTAPI'))
    url_se = "https://api.solcast.com.au/rooftop_sites/"+str(os.getenv('SOLCASTSITEID'))
   
    # For single array installation uncomment the line below and comment out the subsequent line
    url_sw = ""
    #url_sw = "https://api.solcast.com.au/rooftop_sites/xxxx"
    cmd = "/forecasts?format=json"
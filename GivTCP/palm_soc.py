#!/usr/bin/env python3
"""PALM - PV Active Load Manager."""

import sys
import time
import json
from datetime import datetime, timedelta
from typing import Tuple, List
import requests
import palm_settings as stgs
import write as wr
from GivLUT import GivLUT, GivQueue
from os.path import exists
import pickle
logger = GivLUT.logger

# This software in any form is covered by the following Open Source BSD license:
#
# Copyright 2023, Steve Lewis
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted
# provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions
# and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or other materials provided
# with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

###########################################
# This code sets overnight charge point, based on SolCast forecast & actual usage
#
###########################################

# Changelog:
# v0.8.3aSoC   28/Jul/22 Branch from palm - SoC only
# v0.8.3bSoC   05/Aug/22 Improved commenting, removed legacy code
# v0.8.4bSoC   31/Dec/22 Re-merge with Palm 0.8.4b, add example for second charge period
# v0.8.4cSoC   01/Jan/23 General tidy up
# v0.8.4dSoC   09/Jan/23 Updated GivEnergyObj to download & validate inverter commands
# v0.8.5SoC    04/May/23 Fixed midnight rollover issue in SoC calculation timing
# v0.9.0       01/Jun/23 30-minute SoC time-slices, auto-correct GMT/BST in Solcast data
# v0.9.1       03/Jun/23 Added logging functionality
# v0.9.2SoC    09/Jun/23 Merge with palm.py, including fallback inverter writes via API
# v0.9.3       18/Jun/23 Fixed significant bug in SoC calculation introduced in v0.9.2
# v0.10.0      21/Jun/23 Added multi-day averaging for usage calcs
# v1.0.0       28/Jul/23 Align with palm v1.0.0: 48-hour forecast, minor bugfixes

PALM_VERSION = "v1.0.0SoC"
# -*- coding: utf-8 -*-

class GivEnergyObj:
    """Class for GivEnergy inverter"""

    def __init__(self):
        sys_item = {'time': '',
                    'solar': {'power': 0, 'arrays':
                                  [{'array': 1, 'voltage': 0, 'current': 0, 'power': 0},
                                   {'array': 2, 'voltage': 0, 'current': 0, 'power': 0}]},
                    'grid': {'voltage': 0, 'current': 0, 'power': 0, 'frequency': 0},
                    'battery': {'percent': 0, 'power': 0, 'temperature': 0},
                    'inverter': {'temperature': 0, 'power': 0, 'output_voltage': 0, \
                        'output_frequency': 0, 'eps_power': 0},
                    'consumption': 0}
        self.sys_status: List[str] = [sys_item] * 5

        meter_item = {'time': '',
                      'today': {'solar': 0, 'grid': {'import': 0, 'export': 0},
                                'battery': {'charge': 0, 'discharge': 0}, 'consumption': 0},
                      'total': {'solar': 0, 'grid': {'import': 0, 'export': 0},
                                'battery': {'charge': 0, 'discharge': 0}, 'consumption': 0}}
        self.meter_status: List[str] = [meter_item] * 5

        self.read_time_mins: int = -100
        self.line_voltage: float = 0
        self.grid_power: int = 0
        self.grid_energy: int = 0
        self.pv_power: int = 0
        self.pv_energy: int = 0
        self.batt_power: int = 0
        self.consumption: int = 0
        self.soc: int = 0
        self.base_load = stgs.GE.base_load
        self.tgt_soc = 100

        #Grab most recent data from invertor and store useful attributes
        if exists(GivLUT.regcache):      # if there is a cache then grab it
            with open(GivLUT.regcache, 'rb') as inp:
                regCacheStack = pickle.load(inp)
                multi_output_old = regCacheStack[4]
            self.invmaxrate=float(multi_output_old['Invertor_Details']['Invertor_Max_Bat_Rate']) / 1000
            self.batcap=float(multi_output_old['Invertor_Details']['Battery_Capacity_kWh'])

        # v0.9.2: Removed routine to download valid inverter commands from GE API - not used
        # in this version and superseded in palm.py to avoid errors if network is unreachable
        # on initialisation

    def get_latest_data(self):
        """Download latest data from GivEnergy."""

        utc_timenow_mins = t_to_mins(time.strftime("%H:%M:%S", time.gmtime()))
        if (utc_timenow_mins > self.read_time_mins + 5 or
            utc_timenow_mins < self.read_time_mins):  # Update every 5 minutes plus day rollover

            url = stgs.GE.url + "system-data/latest"
            key = stgs.GE.key
            headers = {
                'Authorization': 'Bearer  ' + key,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            try:
                resp = requests.request('GET', url, headers=headers)
            except requests.exceptions.RequestException as error:
                logger.error(error)
                return

            if len(resp.content) > 100:
                for index in range(4, -1, -1):  # Right shift old data
                    if index > 0:
                        self.sys_status[index] = self.sys_status[index - 1]
                    else:
                        try:
                            self.sys_status[index] = \
                                json.loads(resp.content.decode('utf-8'))['data']
                        except Exception:
                            logger.error("Error reading GivEnergy system status "+ T_NOW_VAR)
                            logger.error(resp.content)
                            self.sys_status[index] = self.sys_status[index + 1]
                if LOOP_COUNTER_VAR == 0:  # Pack array on startup
                    i = 1
                    while i < 5:
                        self.sys_status[i] = self.sys_status[0]
                        i += 1
                self.read_time_mins = t_to_mins(self.sys_status[0]['time'][11:])
                self.line_voltage = float(self.sys_status[0]['grid']['voltage'])
                self.grid_power = -1 * int(self.sys_status[0]['grid']['power'])  # -ve = export
                self.pv_power = int(self.sys_status[0]['solar']['power'])
                self.batt_power = int(self.sys_status[0]['battery']['power'])  # -ve = charging
                self.consumption = int(self.sys_status[0]['consumption'])
                self.soc = int(self.sys_status[0]['battery']['percent'])

            url = stgs.GE.url + "meter-data/latest"
            try:
                resp = requests.request('GET', url, headers=headers)
            except requests.exceptions.RequestException as error:
                logger.error(error)
                return

            if len(resp.content) > 100:
                for i in range(4, -1, -1):  # Right shift old data
                    if i > 0:
                        self.meter_status[i] = self.meter_status[i - 1]
                    else:
                        try:
                            self.meter_status[i] = \
                                json.loads(resp.content.decode('utf-8'))['data']
                        except Exception:
                            logger.error("Error reading GivEnergy meter status "+ T_NOW_VAR)
                            logger.error(resp.content)
                            self.meter_status[i] = self.meter_status[i + 1]
                if LOOP_COUNTER_VAR == 0:  # Pack array on startup
                    i = 1
                    while i < 5:
                        self.meter_status[i] = self.meter_status[0]
                        i += 1

                self.pv_energy = int(self.meter_status[0]['today']['solar'] * 1000)

                # Daily grid energy must be >=0 for PVOutput.org (battery charge >= midnight value)
                self.grid_energy = max(int(self.meter_status[0]['today']['consumption'] * 1000), 0)

    def get_load_hist(self):
        """Download historical consumption data from GivEnergy and pack array for next SoC calc"""

        def get_load_hist_day(offset: int):
            """Get load history for a single day"""

            load_array = [0] * 48
            day_delta = 0 if (T_NOW_MINS_VAR > 1260) else 1  # Use latest day if after 2100 hrs
            day_delta += offset
            day = datetime.strftime(datetime.now() - timedelta(day_delta), '%Y-%m-%d')
            url = stgs.GE.url + "data-points/"+ day
            key = stgs.GE.key
            headers = {
                'Authorization': 'Bearer  ' + key,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            params = {
                'page': '1',
                'pageSize': '2000'
            }

            try:
                resp = requests.request('GET', url, headers=headers, params=params)
            except requests.exceptions.RequestException as error:
                logger.error(error)
                return load_array
            if resp.status_code != 200:
                logger.error("Invalid response: "+ str(resp.status_code))
                return load_array

            if len(resp.content) > 100:
                history = json.loads(resp.content.decode('utf-8'))
                i = 6
                counter = 0
                current_energy = prev_energy = 0
                while i < 290:
                    try:
                        current_energy = float(history['data'][i]['today']['consumption'])
                    except Exception:
                        break
                    if counter == 0:
                        load_array[counter] = round(current_energy, 1)
                    else:
                        load_array[counter] = round(current_energy - prev_energy, 1)
                    counter += 1
                    prev_energy = current_energy
                    i += 6
            return load_array

        load_hist_array = [0] * 48
        acc_load = [0] * 48
        total_weight: int = 0

        i: int = 0
        while i < len(stgs.GE.load_hist_weight):
            if stgs.GE.load_hist_weight[i] > 0:
                logger.info("Processing load history for day -"+ str(i + 1))
                load_hist_array = get_load_hist_day(i)
                j = 0
                while j < 48:
                    acc_load[j] += load_hist_array[j] * stgs.GE.load_hist_weight[i]
                    acc_load[j] = round(acc_load[j], 2)
                    j += 1
                total_weight += stgs.GE.load_hist_weight[i]
                logger.debug(str(acc_load)+ " total weight: "+ str(total_weight))
            else:
                logger.info("Skipping load history for day -"+ str(i + 1)+ " (weight = 0)")
            i += 1

        # Calculate averages and write results
        i = 0
        while i < 48:
            self.base_load[i] = round(acc_load[i]/total_weight, 1)
            i += 1

        logger.info("Load Calc Summary: "+ str(self.base_load))

    def set_mode(self, cmd: str, *arg: str):
        """Configures inverter operating mode"""

        def set_inverter_register(register: str, value: str):
            """Exactly as it says"""

            # Validate command against list in settings
            cmd_name = ""
            #valid_cmd = False
            #for line in self.cmd_list:
                #if line['id'] == int(register):
                    #cmd_name = line['name']
                    #valid_cmd = True
                    #break

            #if valid_cmd is False:
                #logger.critical("write attempt to invalid inverter register: "+ str(register))
                #return

            url = stgs.GE.url + "settings/"+ register + "/write"
            key = stgs.GE.key
            headers = {
                'Authorization': 'Bearer  ' + key,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            payload = {
                'value': value
            }
            resp = "TEST"
            if not TEST_MODE:
                try:
                    resp = requests.request('POST', url, headers=headers, json=payload)
                except requests.exceptions.RequestException as error:
                    logger.error(error)
                    return
                if resp.status_code != 201:
                    logger.info("Invalid response: "+ str(resp.status_code))
                    return

            logger.info("Setting Register "+ str(register)+ " ("+ str(cmd_name) + ") to "+
                        str(value)+ "   Response: "+ str(resp))

            time.sleep(3)

            # Readback check
            url = stgs.GE.url + "settings/"+ register + "/read"
            key = stgs.GE.key
            headers = {
                'Authorization': 'Bearer  ' + key,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            payload = {}

            try:
                resp = requests.request('POST', url, headers=headers, json=payload)
            except resp.exceptions.RequestException as error:
                logger.error(error)
                return
            if resp.status_code != 201:
                logger.error("Invalid response: "+ resp.status_code)
                return

            returned_cmd = json.loads(resp.content.decode('utf-8'))['data']['value']
            if str(returned_cmd) == str(value):
                logger.info("Successful register read: "+ str(register)+ " = "+ str(returned_cmd))
            else:
                logger.error("Readback failed on GivEnergy API... Expected " +
                    str(value) + ", Read: "+ str(returned_cmd))

        if cmd == "set_soc":  # Sets target SoC to value
            try:
                result={}
                logger.debug("Setting Charge Target to: "+ str(arg[0])+ "%")
                payload={}
                payload['chargeToPercent']= arg[0]
                result=GivQueue.q.enqueue(wr.setChargeTarget,payload)
                logger.debug(result)
            except:
                set_inverter_register("77", arg[0])
                set_inverter_register("64", stgs.GE.start_time)
                set_inverter_register("65", stgs.GE.end_time)

        elif cmd == "set_soc_winter":  # Restore default overnight charge params
            try:
                result={}
                logger.debug("Setting Charge Target to: "+ str(100)+ "%")
                payload={}
                payload['chargeToPercent']= 100
                result=GivQueue.q.enqueue(wr.setChargeTarget,payload)
                logger.debug(result)
            except:
                set_inverter_register("77", "100")
                set_inverter_register("64", stgs.GE.start_time)
                set_inverter_register("65", stgs.GE.end_time_winter)

        elif cmd == "charge_now":
            set_inverter_register("77", "100")
            set_inverter_register("64", "00:30")
            set_inverter_register("65", "23:59")

        elif cmd == "pause":
            try:
                result={}
                logger.debug("Setting Charge rate to: 0W")
                payload={}
                payload['chargeRate']= 0
                result=GivQueue.q.enqueue(wr.setChargeRate,payload)
                logger.debug(result)
                result={}
                logger.debug("Setting Discharge rate to: 0W")
                payload={}
                payload['dischargeRate']= 0
                result=GivQueue.q.enqueue(wr.setDischargeRate,payload)
                logger.debug(result)
            except:
                set_inverter_register("72", "0")
                set_inverter_register("73", "0")
        elif cmd == "resume":
            try:
                result={}
                logger.debug("Setting Charge rate to: "+str(self.invmaxrate)+"W")
                payload={}
                payload['chargeRate']= self.invmaxrate
                result=GivQueue.q.enqueue(wr.setChargeRate,payload)
                logger.debug(result)
                result={}
                logger.debug("Setting Discharge rate to: "+str(self.invmaxrate)+"W")
                payload={}
                payload['dischargeRate']= self.invmaxrate
                result=GivQueue.q.enqueue(wr.setDischargeRate,payload)
                logger.debug(result)
            except:
                set_inverter_register("72", "3000")
                set_inverter_register("73", "3000")

        else:
            logger.error("unknown inverter command: "+ cmd)

    def compute_tgt_soc(self, gen_fcast, weight: int, commit: bool):
        """Compute overnight SoC target"""

        # Winter months = 100%
        if MNTH_VAR in stgs.GE.winter and commit:  # No need for sums...
            logger.info("winter month, SoC set to 100")
            self.set_mode("set_soc_winter")
            return

        # Quick check for valid generation data
        if gen_fcast.pv_est50_day[0] == 0:
            logger.error("Missing generation data, SoC set to 100")
            self.set_mode("set_soc")
            return

        # Solcast provides 3 estimates (P10, P50 and P90). Compute individual weighting
        # factors for each of the 3 estimates from the weight input parameter, using a
        # triangular approximation for simplicity

        weight = min(max(weight,10),90)  # Range check
        wgt_10 = max(0, 50 - weight)
        if weight > 50:
            wgt_50 = 90 - weight
        else:
            wgt_50 = weight - 10
        wgt_90 = max(0, weight - 50)

        logger.info("")
        logger.info("{:<20} {:>10} {:>10} {:>10} {:>10}  {:>10} {:>10}".format("SoC Calc;",
            "Day", "Hour", "Charge", "Cons", "Gen", "SoC"))

        if stgs.GE.end_time != "":
            end_charge_period = int(stgs.GE.end_time[0:2]) * 2
        else:
            end_charge_period = 8

        batt_max_charge: float = stgs.GE.batt_max_charge
        batt_charge: float = [0] * 98
        reserve_energy = batt_max_charge * stgs.GE.batt_reserve / 100
        max_charge_pcnt = [0] * 2
        min_charge_pcnt = [0] * 2

        # The clever bit:
        # Start with battery at reserve %. For each 30-minute slot of the coming day, calculate
        # the battery charge based on forecast generation and historical usage. Capture values
        # for maximum charge and also the minimum charge value at any time before the maximum.

        day = 0
        while day < 2:  # Repeat for tomorrow and next day
            batt_charge[0] = max_charge = min_charge = reserve_energy
            est_gen = 0
            i = 0
            while i < 48:
                if i <= end_charge_period:  # Battery is in AC Charge mode
                    total_load = 0
                    batt_charge[i] = batt_charge[0]
                else:
                    total_load = ge.base_load[i]
                    est_gen = (gen_fcast.pv_est10_30[day*48 + i] * wgt_10 +
                        gen_fcast.pv_est50_30[day*48 + i] * wgt_50 +
                        gen_fcast.pv_est90_30[day*48 + i] * wgt_90) / (wgt_10 + wgt_50 + wgt_90)
                    batt_charge[i] = (batt_charge[i - 1] +
                        max(-1 * stgs.GE.charge_rate,
                        min(stgs.GE.charge_rate, (est_gen - total_load))))

                # Capture min charge on lowest point on down-slope before charge reaches 100%
                # or max charge if on an up slope after overnight charge
                if (batt_charge[i] <= batt_charge[i - 1] and
                    max_charge < batt_max_charge):
                    min_charge = min(min_charge, batt_charge[i])
                elif i > end_charge_period:  # Charging after overnight boost
                    max_charge = max(max_charge, batt_charge[i])

                logger.info("{:<20} {:>10} {:>10} {:>10} {:>10}  {:>10} {:>10}".format("SoC Calc;",
                    day, t_to_hrs(i * 30), round(batt_charge[i], 2), round(total_load, 2),
                    round(est_gen, 2), int(100 * batt_charge[i] / batt_max_charge)))
                i += 1

            max_charge_pcnt[day] = int(100 * max_charge / batt_max_charge)
            min_charge_pcnt[day] = int(100 * min_charge / batt_max_charge)

            day += 1

        # low_soc is the minimum SoC target. Provide more buffer capacity in shoulder months
        # when load is likely to be more variable, e.g. heating
        if MNTH_VAR in stgs.GE.shoulder:
            low_soc = stgs.GE.max_soc_target
        else:
            low_soc = stgs.GE.min_soc_target

        # So we now have the four values of max & min charge for tomorrow & overmorrow
        # Check if overmorrow is better than tomorrow and there is opportunity to reduce target
        # to avoid residual charge at the end of the day in anticipation of a sunny day
        if max_charge_pcnt[1] > 100 - low_soc > max_charge_pcnt[0]:
            logger.info("Overmorrow correction applied")
            max_charge_pc = max_charge_pcnt[0] + (max_charge_pcnt[1] - 100) / 2
        else:
            logger.info("Overmorrow correction not needed/applied")
            max_charge_pc = max_charge_pcnt[0]
        min_charge_pc = min_charge_pcnt[0]

        print("Min & max", min_charge_pc, max_charge_pc)
        # The really clever bit: reduce the target SoC to the greater of:
        #     The surplus above 100% for max_charge_pcnt
        #     The value needed to achieve the stated spare capacity at minimum charge point
        #     The preset minimum value
        tgt_soc = max(100 - max_charge_pc, (low_soc - min_charge_pc), low_soc)
        # Range check the resulting value
        tgt_soc = int(min(tgt_soc, 100))  # Limit range to 100%

        # Produce SoC plots (y1 = baseline, y2 = adjusted)

        logger.info("{:<25} {:>10} {:>10} {:>10} {:>10} {:>10}".format("SoC Calc Summary;",
            "Max Charge", "Min Charge", "Max %", "Min %", "Target SoC"))
        logger.info("{:<25} {:>10} {:>10} {:>10} {:>10} {:>10}".format("SoC Calc Summary;",
            round(max_charge, 2), round(min_charge, 2),
            max_charge_pc, min_charge_pc, tgt_soc))
        logger.info("{:<25} {:>10} {:>10} {:>10} {:>10} {:>10}".format("SoC (Adjusted);",
            round(max_charge, 2), round(min_charge, 2),
            max_charge_pc + tgt_soc, min_charge_pc + tgt_soc, "\n"))

        if commit:
            logger.critical("Sending calculated SoC to inverter: "+ str(tgt_soc))
            self.set_mode("set_soc", str(tgt_soc))
            self.tgt_soc = tgt_soc

# End of GivEnergyObj() class definition

class SolcastObj:
    """Stores and manipulates daily Solcast forecast."""

    def __init__(self):
        # Skeleton solcast summary array
        self.pv_est10_day: [int] = [0] * 7
        self.pv_est50_day: [int] = [0] *  7
        self.pv_est90_day: [int] = [0] * 7

        self.pv_est10_30: [int] = [0] * 96
        self.pv_est50_30: [int] = [0] * 96
        self.pv_est90_30: [int] = [0] * 96

    def update(self):
        """Updates forecast generation from Solcast server."""

        def get_solcast(url) -> Tuple[bool, str]:
            """Download latest Solcast forecast."""

            solcast_url = url + stgs.Solcast.cmd + "&api_key=" + stgs.Solcast.key
            try:
                resp = requests.get(solcast_url, timeout=5)
                resp.raise_for_status()
            except requests.exceptions.RequestException as error:
                logger.error(error)
                return False, ""
            if resp.status_code != 200:
                logger.error("Invalid response: "+ str(resp.status_code))
                return False, ""

            if len(resp.content) < 50:
                logger.warning("Warning: Solcast data missing/short")
                logger.warning(resp.content)
                return False, ""

            solcast_data = json.loads(resp.content.decode('utf-8'))
            logger.debug(str(solcast_data))

            return True, solcast_data
        #  End of get_solcast()

        # Download latest data for each array, abort if unsuccessful
        result, solcast_data_1 = get_solcast(stgs.Solcast.url_se)
        if not result:
            logger.warning("Error; Problem reading Solcast data, using previous values (if any)")
            return

        if stgs.Solcast.url_sw != "":  # Two arrays are specified
            logger.info("url_sw = '"+str(stgs.Solcast.url_sw)+"'")
            result, solcast_data_2 = get_solcast(stgs.Solcast.url_sw)
            if not result:
                logger.warning("Error; Problem reading Solcast data, using previous values (if any)")
                return
        else:
            logger.info("No second array")

        logger.info("Successful Solcast download.")

        # Combine forecast for PV arrays & align data with day boundaries
        pv_est10 = [0] * 10080
        pv_est50 = [0] * 10080
        pv_est90 = [0] * 10080

        if stgs.Solcast.url_sw != "":  # Two arrays are specified
            forecast_lines = min(len(solcast_data_1['forecasts']), len(solcast_data_2['forecasts']))
        else:
            forecast_lines = len(solcast_data_1['forecasts'])
        interval = int(solcast_data_1['forecasts'][0]['period'][2:4])
        solcast_offset = (60 * int(solcast_data_1['forecasts'][0]['period_end'][11:13]) +
            int(solcast_data_1['forecasts'][0]['period_end'][14:16]) - interval - 60)

        # Check for BST and convert to local time
        if time.strftime("%z", time.localtime()) == "+0100":
            logger.info("Applying BST offset to Solcast data")
            solcast_offset += 60

        i = solcast_offset
        cntr = 0
        while i < solcast_offset + forecast_lines * interval:
            if stgs.Solcast.url_sw != "":  # Two arrays are specified
                pv_est10[i] = (int(solcast_data_1['forecasts'][cntr]['pv_estimate10'] * 1000) +
                    int(solcast_data_2['forecasts'][cntr]['pv_estimate10'] * 1000))
                pv_est50[i] = (int(solcast_data_1['forecasts'][cntr]['pv_estimate'] * 1000) +
                    int(solcast_data_2['forecasts'][cntr]['pv_estimate'] * 1000))
                pv_est90[i] = (int(solcast_data_1['forecasts'][cntr]['pv_estimate90'] * 1000) +
                    int(solcast_data_2['forecasts'][cntr]['pv_estimate90'] * 1000))
            else:
                pv_est10[i] = int(solcast_data_1['forecasts'][cntr]['pv_estimate10'] * 1000)
                pv_est50[i] = int(solcast_data_1['forecasts'][cntr]['pv_estimate'] * 1000)
                pv_est90[i] = int(solcast_data_1['forecasts'][cntr]['pv_estimate90'] * 1000)

            if i > 1 and i % interval == 0:
                cntr += 1
            i += 1

        if solcast_offset > 720:  # Forget about current day
            offset = 1440 - 90
        else:
            offset = 0

        i = 0
        while i < 7:  # Summarise daily forecasts
            start = i * 1440 + offset + 1
            end = start + 1439
            self.pv_est10_day[i] = round(sum(pv_est10[start:end]) / 60000, 3)
            self.pv_est50_day[i] = round(sum(pv_est50[start:end]) / 60000, 3)
            self.pv_est90_day[i] = round(sum(pv_est90[start:end]) / 60000, 3)
            i += 1

        i = 0
        while i < 96:  # Calculate half-hourly generation
            start = i * 30 + offset + 1
            end = start + 29
            self.pv_est10_30[i] = round(sum(pv_est10[start:end])/60000, 3)
            self.pv_est50_30[i] = round(sum(pv_est50[start:end])/60000, 3)
            self.pv_est90_30[i] = round(sum(pv_est90[start:end])/60000, 3)
            i += 1

        timestamp = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
        logger.debug("PV Estimate 10% (hrly, 7 days) / kWh; "+ timestamp+ "; "+
            str(self.pv_est10_30[0:47])+ str(self.pv_est10_day[0:6]))
        logger.debug("PV Estimate 50% (hrly, 7 days) / kWh; "+ timestamp+ "; "+
            str(self.pv_est50_30[0:47])+ str(self.pv_est50_day[0:6]))
        logger.debug("PV Estimate 90% (hrly, 7 days) / kWh; "+ timestamp+ "; "+
            str(self.pv_est90_30[0:47])+ str(self.pv_est90_day[0:6]))

# End of SolcastObj() class definition

def t_to_mins(time_in_hrs: str) -> int:
    """Convert times from HH:MM format to mins after midnight."""

    try:
        time_in_mins = 60 * int(time_in_hrs[0:2]) + int(time_in_hrs[3:5])
        return time_in_mins
    except Exception:
        return 0

#  End of t_to_mins()

def t_to_hrs(time_in: int) -> str:
    """Convert times from mins after midnight format to HH:MM."""

    try:
        hours = int(time_in // 60)
        mins = int(time_in - hours * 60)
        time_in_hrs = '{:02d}{}{:02d}'.format(hours, ":", mins)
        return time_in_hrs
    except Exception:
        return "00:00"

#  End of t_to_hrs()

if __name__ == '__main__':

    LOOP_COUNTER_VAR = 0
    TEST_MODE: bool = False
    DEBUG_MODE: bool = False
    LONG_T_NOW_VAR: str = time.strftime("%d-%m-%Y %H:%M:%S %z", time.localtime())
    MNTH_VAR: str = LONG_T_NOW_VAR[3:5]
    T_NOW_VAR: str = LONG_T_NOW_VAR[11:]
    T_NOW_MINS_VAR: int = t_to_mins(T_NOW_VAR)

    logger.info("PALM... PV Automated Load Manager Version:"+ str(PALM_VERSION))

    # GivEnergy power object initialisation
    ge: GivEnergyObj = GivEnergyObj()

    if exists(ge.batcap):
        logger.info("Battery Capacity: "+ str(ge.batcap))
    
    # Solcast PV prediction object initialisation
    solcast: SolcastObj = SolcastObj()
    solcast.update()

    try:
        ge.get_load_hist()
        logger.debug("10% forecast...")
        ge.compute_tgt_soc(solcast, 10, False)
        logger.debug("50% forecast...")
        ge.compute_tgt_soc(solcast, 50, False)
        logger.debug("90% forecast...")
        ge.compute_tgt_soc(solcast, 90, False)
    except Exception:
        logger.critical("Unable to set SoC")

    # Write final SoC target to GivEnergy register
    # Change weighting in command according to desired risk/reward profile
    logger.info("Forecast weighting: "+ str(stgs.Solcast.weight))
    ge.compute_tgt_soc(solcast, stgs.Solcast.weight, True)

# End of main

# -*- coding: utf-8 -*-
# version 2021.11.15
import sys
import json
from flask import Flask, json, request
import read as rd       #grab passthrough functions from main read file
import write as wr      #grab passthrough functions from main write file

#set-up Flask details
giv_api = Flask(__name__)

#Proxy Read Functions
@giv_api.route('/getTimeslots', methods=['GET'])
def getTimes():
    return rd.getTimeslots()

@giv_api.route('/getCombinedStats', methods=['GET'])
def getStats():
    return rd.getCombinedStats()

@giv_api.route('/getModesandTimes', methods=['GET'])
def getcontrols():
    return rd.getModesandTimes()

@giv_api.route('/runAll', methods=['GET'])
def getAll():
    return rd.runAll()

#Proxy Write Functions
@giv_api.route('/disableChargeTarget', methods=['POST'])
def disChargeTrgt():
    return wr.disableChargeTarget()

@giv_api.route('/enableChargeTarget', methods=['POST'])
def enChargeTrgt():
    return wr.enableChargeTarget()

@giv_api.route('/pauseChargeSchedule', methods=['POST'])
def pauseChrgSchedule():
    return wr.pauseChargeSchedule()

@giv_api.route('/resumeChargeSchedule', methods=['POST'])
def resumeChrgSchedule():
    return wr.resumeChargeSchedule()

@giv_api.route('/pauseDischargeSchedule', methods=['POST'])
def pauseDischrgSchedule():
    return wr.pauseDischargeSchedule()

@giv_api.route('/resumeDischargeSchedule', methods=['POST'])
def resumeDischrgSchedule():
    return wr.resumeDischargeSchedule()

@giv_api.route('/pauseBatteryCharge', methods=['POST'])
def pauseBatCharge():
    return wr.pauseBatteryCharge()

@giv_api.route('/resumeBatteryCharge', methods=['POST'])
def resumeBatCharge():
    return wr.resumeBatteryCharge()

@giv_api.route('/pauseBatteryDischarge', methods=['POST'])
def pauseBatDisharge():
    return wr.pauseBatteryDischarge()

@giv_api.route('/resumeBatteryDischarge', methods=['POST'])
def resumeBatDisharge():
    return wr.resumeBatteryDischarge()

@giv_api.route('/setChargeTarget', methods=['POST'])
def setChrgTarget():
    payload = request.get_json(silent=True, force=True)
    return wr.setChargeTarget(payload)

@giv_api.route('/setBatteryReserve', methods=['POST'])
def setBattReserve():
    payload = request.get_json(silent=True, force=True)
    return wr.setBatteryReserve(payload)

@giv_api.route('/setChargeRate', methods=['POST'])
def setChrgeRate():
    payload = request.get_json(silent=True, force=True)
    return wr.setChargeRate(payload)

@giv_api.route('/setDischargeRate', methods=['POST'])
def setDischrgeRate():
    payload = request.get_json(silent=True, force=True)
    return wr.setDischargeRate(payload)

@giv_api.route('/setChargeSlot1', methods=['POST'])
def setChrgSlot1():
    payload = request.get_json(silent=True, force=True)
    return wr.setChargeSlot1(payload)

@giv_api.route('/setChargeSlot2', methods=['POST'])
def setChrgSlot2():
    payload = request.get_json(silent=True, force=True)
    return wr.setChargeSlot2(payload)

@giv_api.route('/setDischargeSlot1', methods=['POST'])
def setDischrgSlot1():
    payload = request.get_json(silent=True, force=True)
    return wr.setDischargeSlot1(payload)

@giv_api.route('/setDischargeSlot2', methods=['POST'])
def setDischrgSlot2():
    payload = request.get_json(silent=True, force=True)
    return wr.setDischargeSlot2(payload)

@giv_api.route('/setBatteryMode', methods=['POST'])
def setBattMode():
    payload = request.get_json(silent=True, force=True)
    return wr.setBatteryMode(payload)

@giv_api.route('/setDateTime', methods=['POST'])
def setDate():
    payload = request.get_json(silent=True, force=True)
    return wr.setDateTime(payload)
# -*- coding: utf-8 -*-
import sys
import json
from read import giv_api
from flask import Flask, json, request

from write import *     #grab passthrough functions from main write file

@giv_api.route('/disableACCharge', methods=['POST'])
def disACCharge():
    return disableACCharge

@giv_api.route('/enableACCharge', methods=['POST'])
def enACCharge():
    return enableACCharge    

@giv_api.route('/pauseChargeSchedule', methods=['POST'])
def pauseChrgSchedule():
    return pauseChargeSchedule

@giv_api.route('/resumeChargeSchedule', methods=['POST'])
def resumeChrgSchedule():
    return resumeChargeSchedule

@giv_api.route('/pauseDischargeSchedule', methods=['POST'])
def pauseDischrgSchedule():
    return pauseDischargeSchedule

@giv_api.route('/resumeDischargeSchedule', methods=['POST'])
def resumeDischrgSchedule():
    return resumeDischargeSchedule

@giv_api.route('/setChargeTarget', methods=['POST'])
def setChrgTarget():
    payload = request.get_json(silent=True, force=True)
    print (payload)
    return setChargeTarget(payload)

@giv_api.route('/setBatteryReserve', methods=['POST'])
def setBattReserve():
    payload = request.get_json(silent=True, force=True)
    return setBatteryReserve(payload)

@giv_api.route('/setChargeSlot1', methods=['POST'])
def setChrgSlot1():
    payload = request.get_json(silent=True, force=True)
    return setChargeSlot1(payload)

@giv_api.route('/setChargeSlot2', methods=['POST'])
def setChrgSlot2():
    payload = request.get_json(silent=True, force=True)
    return setChargeSlot2(payload)

@giv_api.route('/setDischargeSlot1', methods=['POST'])
def setDischrgSlot1():
    payload = request.get_json(silent=True, force=True)
    return setDischargeSlot1(payload)

@giv_api.route('/setDischargeSlot2', methods=['POST'])
def setDischrgSlot2():
    payload = request.get_json(silent=True, force=True)
    return setDischargeSlot2(payload)

@giv_api.route('/setBatteryMode', methods=['POST'])
def setBattMode():
    payload = request.get_json(silent=True, force=True)
    return setBatteryMode(payload)

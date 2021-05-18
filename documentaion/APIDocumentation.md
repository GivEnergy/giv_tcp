# API Documentation

## GivTCP class

### Methods

- getTimeslots()

- getCombinedStats()


#### getTimeslots()
Returns the following values:

Name |Value|MQTT topic
--------------|-------------|--------------
Discharge Start 1| 0 to 2359 | GivEnergy/`datalloggerSN`/timeslots/dischargeStart1
Discharge End 1| 0 to 2359 | GivEnergy/`datalloggerSN`/timeslots/dischargeEnd1
Discharge Start 2| 0 to 2359 | GivEnergy/`datalloggerSN`/timeslots/dischargeStart2
Discharge End 2| 0 to 2359 | GivEnergy/`datalloggerSN`/timeslots/dischargeEnd2
Charge Start 1| 0 to 2359 | GivEnergy/`datalloggerSN`/timeslots/chargeStart1
Charge Start 1| 0 to 2359 | GivEnergy/`datalloggerSN`/timeslots/chargeEnd1

#### getCombinedStats()

Returns the following values:

Name |Unit|MQTT topic
--------------|-------------|--------------
PV Power| W | GivEnergy/`datalloggerSN`/power/pvPower
Grid Power| W | GivEnergy/`datalloggerSN`/power/gridPower
Import Power| W | GivEnergy/`datalloggerSN`/power/importPower
Export Power| W | GivEnergy/`datalloggerSN`/power/exportPower
EPS Power| W | GivEnergy/`datalloggerSN`/power/epsPower
Load Power| W | GivEnergy/`datalloggerSN`/power/loadPower
EPS Power| W | GivEnergy/`datalloggerSN`/power/batteryPower
Charge Power| W | GivEnergy/`datalloggerSN`/power/chargePower
Discharge Power| W | GivEnergy/`datalloggerSN`/power/dischargePower
SOC| percent | GivEnergy/`datalloggerSN`/power/SOC
Total Grid Export Energy| kWh | GivEnergy/`datalloggerSN`/energy/totalGridExportEnergy
Total Load Energy| kWh | GivEnergy/`datalloggerSN`/energy/totalLoadEnergy
Total Grid Import Energy| kWh | GivEnergy/`datalloggerSN`/totalGridImportEnergy

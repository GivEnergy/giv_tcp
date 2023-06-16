
# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.1.16] - 2023-06-12
### Fixed
- Type error in MQTT publishing handled gracefully
- Grid Current scaling factor corrected (x10)
### Added
- Updated SmartTarget to PALM 0.9.2 (Thanks Steve Lewis)
- Charge and Discharge time remaining entities (mins till full charge/discharge at current power rate)
- Gen 3 invertors now recognised
- MQTT Auto recognition. If using the Mosquitto addon in HA it will now auto connect, removing need for MQTT configuration
  
## [2.1.15] - 2023-06-08
### Fixed
- Fixed SmartTarget error for solcast calls with a single array

## [2.1.14] - 2023-06-05
### Fixed
- REST /getCache endpoint fixed (incorrect json format)
- Minor updates to README.md documentation
- Refactored Force Export to use queuing for more reliable revert
### Added
- Updated SmartTarget to PALM 0.8.5 (Thanks Stephen Lewis)

## [2.1.13] - 2023-05-13
### Fixed
- REST /getCache endpoint fixed (incorrect json format)
- Minor updates to README.md documentation
- Refactored Force Export to use queing for more reliable revert
### Added
- Updated SmartTarget to PALM 0.8.5 (Thanks Stephen Lewis)

## [2.1.13] - 2023-05-13
### Fixed
- Reverting entity naming to include serial number for compatability
### Added
- Reboot Invertor function

## [2.1.12] - 2023-05-13
### Fixed
- HA Invertor time device_class error removed
- Fixed Timed Export & Revert Export Settings (Thanks @Ed-M72)
- Timed Discharge and Force Export no longer set soc_reserve to 100 (which stopped discharge)

## [2.1.11] - 2023-05-07
### Fixed
- HA discovery message error fixed for string variables (Thanks @metalblue)
- Restructure config variables for ease of use (thanks @S0ckhamster)
- Improved handling of Timed Demand mode handing (Thanks @Ed-M72)

## [2.1.10] - 2023-04-30
### Fixed
- HADEVICEPREFIX config variables added for second and third invertors for HA Addon deployment

## [2.1.9] - 2023-04-30
### Fixed
- Updated max mppt pv voltage to match datasheet (550v)
- Remove Data Smoothing from SOC to prevent getting stuck on values below 4%
- Set Rate data points to GBP/kWh
- Dual site IDs now working for Solcast/PALM (Thanks to s0ckhamster)

### Added
- HA Device Prefix per Invertor (use the "_X" suffix )
- Retain Rate Data across reboots/updates (if data is from today)
- PALM settings now handled via ENV (Thanks to s0ckhamster)
- Entity Friendly names no longer use Serial Number

## [2.1.7] - 2023-03-10
### Fixed
- Updated max mppt pv voltage to match datasheet (550v)

## [2.1.3] - 2023-03-04
### Fixed
- modified givenergy-modbus library to calulate inverter type from registers, not from serial number
- Fixed day/Night rate stability in dynamic mode

## [2.1.3] - 2023-02-12
### Fixed
- Fixed error on garbage invertor output
- Fixed Force Charge/Export power rate setting from 100(%) to maxInvertorRate

### Added
- Per Invertor MQTT Topic now available
- Overlapping ForceCharge\Export now handled gracefully. You can extend a current Force action byt recalling it with a new duration and it will set a new Force end time

## [2.1.2] - 2023-02-09

### Added
- Charge and Discharge rates now use absolute power values (2600W) not percentage (100%) to align with Cloud portal and to give correct operation
- Prevented the REST readData call (pubFromPickle) from triggering another read 
 
### Fixed
- Worked on race conditions by using critical sections to replace file locks
- Fix select entities error when setting to a non-float value

### Added
- Changed logging levels so that Info now just shows which operations are called and everything else is Debug
- Force Charge, Force Export and Temp Pause controls now allow you to Cancel, reverting to preious settings immediately
- Updated Battery Reserve and Cut-off entities to correctly reflect invertor behaviour
- Updated Redis scheduling for control lockout
- Added "None" as a smoothing option
- Added invertor firmware to output
- Allow dynamic Day/Night energy slots as well as fixed time (Go vs Intelligent) New "select" entity created to allow external automations to change rate (DYNAMICTARIFF ENV can be set to true to ignore day/night ENV and change rates based on the value of the Select entity)
- Ability to accept dual array installations for Solcast Smart Target (new ENV) 


## [2.0.1] - 2022-09-18
 
Update to GivLUT to allow battery max power to go up to 4000w to account for Gen2 invertors

## [2.0.0rc2] - 2022-09-17
 
Major update including various stability fixes and new features
 
### Added
- Force Export boost function (and restore)
- Force Charge boost function (and restore)
- Temporary charge and discharge pause (and restore)
- Change timeslot start and end
- All new control functions are avalable via:
  - Select devices (Home assistant)
  - MQTT Topic
  - REST

- Smart target charge using Solcast forecast and load energy stats. Thanks to [Stephen Lewis](https://github.com/salewis38/palm)
  - Only avaiable in docker container or Home Assistant Addon

- User defined port for web dashboard. Thanks to [Dan Gallo](https://github.com/DanielGallo/GivEnergy-Smart-Home-Display/tree/givtcp)
  - Only avaiable in docker container or Home Assistant Addon

- Data smoothing across energy and battery data (not power)
- log to file by default
- Cache data stored in user defined folder. Useful to delete in the event of problems 

#### New ENV
- CACHELOCATION="/config/GivTCP" - if using Home assistant addon, make sure this starts with /config
- DATASMOOTHER="High" - High, medium or low. Level of aggression on smoothing large jumps in data
- SMARTTARGET=True - If True, then the three below ENV must be set. This will update your Target SOC 20mins before it is due to start charging
- GEAPI="" - API key from your GE account
- SOLCASTAPI="" - Solcast API key 
- SOLCASTSITEID="" - Solcast site ID
- DEBUG_FILE_LOCATION - has been removed

### Changed
- Re-structred the lookup tables into single class
- Data structure for all data points using new class type
- Logging to file now uses a rotating file handler and will keep 7 days of logs
- Underlying [givenergy-modbus](https://github.com/dewet22/givenergy-modbus) errors supressed in logging
- Mode control now automatically updates (dis)charge schedule as appropriate
### Fixed
- Obey Print Raw ENV
- Midnight data sticking for Energy Today stats
- many more...

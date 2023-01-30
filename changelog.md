
# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [2.1.0] - 2023-01-28

- Added "None" as a smoothing option
- Worked on race conditions by using critical sections to replace file locks
- Changed logging levels so that Info now just shows which operations are called and everything else is Debug
- Prevented the readData call (pubFromPickle) from triggering another read (this is a change in behaviour)

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
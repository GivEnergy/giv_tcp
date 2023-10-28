import { defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'

export const useTcpStore = defineStore('givtcp-form', {
  state: () => ({
    inverter: useStorage('inverter', {
      NUMINVERTORS: 1,
      INVERTOR_IP: null,
      NUMBATTERIES: 1
    }),
    mqtt: useStorage('mqtt', {
      MQTT_OUTPUT: false,
      MQTT_ADDRESS: null,
      MQTT_USERNAME: null,
      MQTT_PASSWORD: null,
      //optional
      MQTT_TOPIC: [],
      MQTT_PORT: 1833
    }),
    influx: useStorage('influx', {
      INFLUX_OUTPUT: false,
      INFLUX_URL: null,
      INFLUX_TOKEN: null,
      INFLUX_BUCKET: null,
      INFLUX_ORG: null
    }),
    homeAssistant: useStorage('homeAssistant', {
      HADEVICEPREFIX: [],
      PYTHONPATH: '/app',
      HA_AUTO_D: true
    }),
    tariffs: useStorage('tariffs', {
      DYNAMICTARIFF: false,
      EXPORTRATE: 0.04,
      DAYRATE:0.395,
      DAYRATESTART: "05: 30",
      NIGHTRATE: 0.155,
      NIGHTRATESTART: "23: 30",
          }),
    miscellaneous: useStorage('miscellaneous', {
      HOSTIP: null,
      CACHELOCATION: '/config/GivTCP',
      TZ: 'Europe/London',
      PRINT_RAW: true,
      LOG_LEVEL: "Info",
      SELF_RUN: true,
      SELF_RUN_LOOP_TIMER: 15,
      QUEUE_RETRIES: 2,
      SMARTTARGET: false,
    }),
    web: useStorage('web', {
      WEB_DASH: false,
      WEB_DASH_PORT: 3000
    }),
    keys: useStorage('keys', {
      GEAPI: null,
      SOLCASTAPI:null,
      SOLCASTSITEID:null,
      SOLCASTSITEID2:null,
    }),
    palm: useStorage('palm', {
      DATASMOOTHER: "medium",
      PALM_WINTER: "01,02,03,10,11,12",
      PALM_SHOULDER: "04,05,09",
      PALM_MIN_SOC_TARGET: 25,
      PALM_MAX_SOC_TARGET: 45,
      PALM_BATT_RESERVE: 4,
      PALM_BATT_UTILISATION: 0.85,
      PALM_WEIGHT: 35,
      LOAD_HIST_WEIGHT: 1

    }),
    restart: useStorage('restart',{
      restart:false,
      hasRestarted:null
    })
  })
})

export const useStep = defineStore('step', {
  state: () => ({
    step: useStorage('step', -1),
    isNew: useStorage('isNew', true)
  })
})

export const useCard = defineStore('card', {
  state: () => ({
    inverter: {
      title: 'Inverter',
      subtitle: 'Setup your inverter configurations',
      fields: [
        {
          type: 'select',
          options: {
            label: 'Number Of Inverters',
            items: [1, 2, 3],
            parent: 'inverter',
            key: 'NUMINVERTORS'
          }
        },
        {
          type: 'select',
          options: {
            label: 'Number Of Batteries',
            items: [1, 2, 3],
            parent: 'inverter',
            key: ' NUMBATTERIES'
          }
        },
        {
          type: 'text',
          options: {
            label: 'IP Address',
            parent: 'inverter',
            key: 'INVERTOR_IP'
          }
        }
      ]
    },
    mqtt: {
      title: 'MQTT',
      subtitle: 'Setup the MQTT broker that stores information about your incoming inverter data',
      fields: [
        {
          type: 'text',
          options: {
            label: 'IP Address',
            parent: 'mqtt',
            key: 'MQTT_ADDRESS'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Username',
            parent: 'mqtt',
            key: 'MQTT_USERNAME'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Password',
            parent: 'mqtt',
            key: 'MQTT_PASSWORD'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Topic',
            parent: 'mqtt',
            key: 'MQTT_TOPIC'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Port',
            parent: 'mqtt',
            key: 'MQTT_PORT'
          }
        },
        {
          type: 'checkbox',
          options: {
            label: 'Output',
            parent: 'mqtt',
            key: 'MQTT_OUTPUT'
          }
        }
      ]
    },
    influx: {
      title: 'InfluxDB',
      subtitle: 'Setup your InfluxDB instance',
      fields: [
        {
          type: 'text',
          options: {
            label: 'URL',
            parent: 'influx',
            key: 'INFLUX_URL'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Token',
            parent: 'influx',
            key: 'INFLUX_TOKEN'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Bucket',
            parent: 'influx',
            key: 'INFLUX_BUCKET'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Org',
            parent: 'influx',
            key: 'INFLUX_ORG'
          }
        },
        {
          type: 'checkbox',
          options: {
            label: 'Output',
            parent: 'influx',
            key: 'INFLUX_OUTPUT'
          }
        }
      ]
    },
    homeAssistant: {
      title: 'Home Assistant',
      subtitle: 'Setup your Home Assistant instance',
      fields: [
        {
          type: 'text',
          options: {
            label: 'Device Prefix',
            parent: 'homeAssistant',
            key: 'HADEVICEPREFIX'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Python Path',
            parent: 'homeAssistant',
            key: 'PYTHONPATH'
          }
        },
        {
          type: 'checkbox',
          options: {
            label: 'Auto Discovery',
            parent: 'homeAssistant',
            key: 'HA_AUTO_D'
          }
        }
      ]
    },
    tariffs: {
      title: 'Tariffs',
      subtitle: 'Setup your Tariffs',
      fields: [
        {
          type: 'text',
          options: {
            label: 'Export Rate',
            parent: 'tariffs',
            key: 'EXPORTRATE'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Day Rate',
            parent: 'tariffs',
            key: 'DAYRATE'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Day Start',
            parent: 'tariffs',
            key: 'DAYRATESTART'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Night Rate',
            parent: 'tariffs',
            key: 'NIGHTRATE'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Night Start',
            parent: 'tariffs',
            key: 'NIGHTRATESTART'
          }
        },
        {
          type: 'checkbox',
          options: {
            label: 'Dynamic',
            parent: 'tariffs',
            key: 'DYNAMICTARIFF'
          }
        }
      ]
    },
    miscellaneous: {
      title: 'Miscellaneous',
      subtitle: 'Setup Any Miscellaneous variables',
      fields: [
        {
          type: 'text',
          options: {
            label: 'Host IP',
            parent: 'miscellaneous',
            key: 'HOSTIP'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Cache Location',
            parent: 'miscellaneous',
            key: 'CACHELOCATION'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Timezone',
            parent: 'miscellaneous',
            key: 'TZ'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Log Level',
            parent: 'miscellaneous',
            key: 'LOG_LEVEL'
          }
        },
        {
          type: 'checkbox',
          options: {
            label: 'Print Raw',
            parent: 'miscellaneous',
            key: 'PRINT_RAW'
          }
        },{
          type: 'checkbox',
          options: {
            label: 'Self Run',
            parent: 'miscellaneous',
            key: 'SELF_RUN'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Self Run Loop Timer',
            parent: 'miscellaneous',
            key: 'SELF_RUN_LOOP_TIMER'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Queue Retries',
            parent: 'miscellaneous',
            key: 'QUEUE_RETRIES'
          }
        },{
          type: 'checkbox',
          options: {
            label: 'Smart Target',
            parent: 'miscellaneous',
            key: 'SMARTTARGET'
          }
        },
      ]
    },
    web: {
      title: 'Web',
      subtitle: 'Setup Any Web variables',
      fields: [
        {
          type: 'checkbox',
          options: {
            label: 'Dashboard',
            parent: 'web',
            key: 'WEB_DASH'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Port',
            parent: 'web',
            key: 'WEB_DASH_PORT'
          }
        }
      ]
    },
    keys: {
      title: 'Keys',
      subtitle: 'Setup Any Keys',
      fields: [
        {
          type: 'text',
          options: {
            label: 'GivEnergy',
            parent: 'keys',
            key: 'GEAPI'
          }
        },
        {
          type: 'text',
          options: {
            label: 'SolCast API Key',
            parent: 'keys',
            key: 'SOLCASTAPI'
          }
        },
        {
          type: 'text',
          options: {
            label: 'SolCast Site ID 1',
            parent: 'keys',
            key: 'SOLCASTSITEID'
          }
        },
        {
          type: 'text',
          options: {
            label: 'SolCast Site ID 2',
            parent: 'keys',
            key: 'SOLCASTSITEID2'
          }
        }
      ]
    },
    palm: {
      title: 'Palm',
      subtitle: 'Setup your Palm variables',
      fields: [
        {
          type: 'text',
          options: {
            label: 'Smoothing',
            parent: 'palm',
            key: 'DATASMOOTHER'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Winter',
            parent: 'palm',
            key: 'PALM_WINTER'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Shoulder',
            parent: 'palm',
            key: 'PALM_SHOULDER'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Minimum SoC Target',
            parent: 'palm',
            key: 'PALM_MIN_SOC_TARGET'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Maximum SoC Target',
            parent: 'palm',
            key: 'PALM_MAX_SOC_TARGET'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Battery Reserve',
            parent: 'palm',
            key: 'PALM_BATT_RESERVE'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Battery Utilisation',
            parent: 'palm',
            key: 'PALM_BATT_UTILISATION'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Weight',
            parent: 'palm',
            key: 'PALM_WEIGHT'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Historical Weight',
            parent: 'palm',
            key: 'LOAD_HIST_WEIGHT'
          }
        }
      ]
    },
    restart:{
      title:"Finished Setup",
      subtitle:"Restart Container to apply changes",
      fields:[
        {
          type: 'button',
          options: {
            label: 'Restart Container',
            parent: 'restart',
            key: 'restart',
            message:useTcpStore().restart.hasRestarted != null ? useTcpStore().restart.hasRestarted ? "Container Restarted Successfully" : "Container Failed to Restart. Try Restarting Manually" : '',
            onClick:async ()=>{
              const store = useTcpStore()
              try{
              const res = await fetch("http://127.0.0.1:6345/restart")
              if(res.ok){
                store.restart.hasRestarted = true
              }else{
                store.restart.hasRestarted = false
              }
            } catch(e){
              store.restart.hasRestarted = false
            }
            }
          }
        },
      ]
    }
  })
})

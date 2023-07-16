import { defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'

export const useTcpStore = defineStore('givtcp-form', {
  state: () => ({
    inverter: useStorage('inverter', {
      numberOfInverters: 1,
      inverterIpAddress: null,
      numberOfBatteries: 1
    }),
    mqtt: useStorage('mqtt', {
      output: false,
      address: null,
      username: null,
      password: null,
      //optional
      topic: [],
      port: 1833
    }),
    influx: useStorage('influx', {
      output: false,
      url: null,
      token: null,
      bucket: null,
      org: null
    }),
    homeAssistant: useStorage('homeAssistant', {
      devicePrefix: [],
      pythonPath: '/app'
    }),
    tariffs: useStorage('tariffs', {
      dynamic: false,
      exportRate: 0.04,
      day: {
        rate: 0.395,
        start: '05:30'
      },
      night: {
        rate: 0.155,
        start: '23:30'
      }
    }),
    miscellaneous: useStorage('miscellaneous', {
      hostIp: null,
      cacheLocation: '/config/GivTCP',
      timezone: 'Europe/London',
      printRaw: true,
      haAutoD: true
    }),
    web: useStorage('web', {
      dashboard: false,
      port: 3000
    }),
    keys: useStorage('keys', {
      givenergy: null,
      solcast: {
        apiKey: null,
        siteIdOne: null,
        siteIdTwo: null
      }
    }),
    palm: useStorage('palm', {
      smoothing: 'medium',
      settings: {
        winter: '01,02,03,10,11,12',
        shoulder: '04,05,09',
        minSocTarget: 25,
        maxSocTarget: 45,
        batteryReserve: 4,
        batteryUtilisation: 0.85,
        weight: 35,
        historicalWeight: 1
      }
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
            key: 'numberOfInverters'
          }
        },
        {
          type: 'select',
          options: {
            label: 'Number Of Batteries',
            items: [1, 2, 3],
            parent: 'inverter',
            key: 'numberOfBatteries'
          }
        },
        {
          type: 'text',
          options: {
            label: 'IP Address',
            parent: 'inverter',
            key: 'inverterIpAddress'
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
            key: 'address'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Username',
            parent: 'mqtt',
            key: 'username'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Password',
            parent: 'mqtt',
            key: 'password'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Topic',
            parent: 'mqtt',
            key: 'topic'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Port',
            parent: 'mqtt',
            key: 'port'
          }
        },
        {
          type: 'checkbox',
          options: {
            label: 'Output',
            parent: 'mqtt',
            key: 'output'
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
            key: 'url'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Token',
            parent: 'influx',
            key: 'token'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Bucket',
            parent: 'influx',
            key: 'bucket'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Org',
            parent: 'influx',
            key: 'org'
          }
        },
        {
          type: 'checkbox',
          options: {
            label: 'Output',
            parent: 'influx',
            key: 'output'
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
            key: 'devicePrefix'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Python Path',
            parent: 'homeAssistant',
            key: 'pythonPath'
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
            key: 'exportRate'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Day Rate',
            parent: 'tariffs',
            key: 'day.rate'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Day Start',
            parent: 'tariffs',
            key: 'day.start'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Night Rate',
            parent: 'tariffs',
            key: 'night.rate'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Night Start',
            parent: 'tariffs',
            key: 'night.start'
          }
        },
        {
          type: 'checkbox',
          options: {
            label: 'Dynamic',
            parent: 'tariffs',
            key: 'dynamic'
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
            key: 'hostIp'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Cache Location',
            parent: 'miscellaneous',
            key: 'cacheLocation'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Timezone',
            parent: 'miscellaneous',
            key: 'timezone'
          }
        },
        {
          type: 'checkbox',
          options: {
            label: 'Print Raw',
            parent: 'miscellaneous',
            key: 'printRaw'
          }
        },
        {
          type: 'checkbox',
          options: {
            label: 'HA Auto Discovery',
            parent: 'miscellaneous',
            key: ' haAutoD'
          }
        }
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
            key: 'dashboard'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Port',
            parent: 'web',
            key: 'port'
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
            key: 'givenergy'
          }
        },
        {
          type: 'text',
          options: {
            label: 'SolCast API Key',
            parent: 'keys',
            key: 'solcast.apiKey'
          }
        },
        {
          type: 'text',
          options: {
            label: 'SolCast Site ID 1',
            parent: 'keys',
            key: 'solcast.siteIdOne'
          }
        },
        {
          type: 'text',
          options: {
            label: 'SolCast Site ID 2',
            parent: 'keys',
            key: 'solcast.siteIdTwo'
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
            key: 'smoothing'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Winter',
            parent: 'palm',
            key: 'settings.winter'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Shoulder',
            parent: 'palm',
            key: 'settings.shoulder'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Minimum SoC Target',
            parent: 'palm',
            key: 'settings.minSocTarget'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Maximum SoC Target',
            parent: 'palm',
            key: 'settings.maxSocTarget'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Battery Reserve',
            parent: 'palm',
            key: 'settings.batteryReserve'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Battery Utilisation',
            parent: 'palm',
            key: 'settings.batteryUtilisation'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Weight',
            parent: 'palm',
            key: 'settings.weight'
          }
        },
        {
          type: 'text',
          options: {
            label: 'Historical Weight',
            parent: 'palm',
            key: 'settings.historicalWeight'
          }
        }
      ]
    }
  })
})

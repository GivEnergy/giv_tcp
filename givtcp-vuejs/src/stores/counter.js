import {defineStore} from 'pinia'

export const useTcpStore = defineStore('givtcp-form', {
    state: () => ({
        inverter: {
            numberOfInverters: 1,
            inverterIpAddress: null,
            numberOfBatteries: 1,
        },
        mqtt: {
            output: false,
            address: null,
            username: null,
            password: null,
            //optional
            topic: [],
            port: 1833
        },
        influx: {
            output: false,
            url: null,
            token: null,
            bucket: null,
            org: null,
        },
        homeAssistant: {
            devicePrefix: [],
            pythonPath: '/app'
        },
        tariffs: {
            dynamic: false,
            exportRate: 0.04,
            day: {
                rate: 0.395,
                start: '05:30'
            },
            night: {
                rate: 0.155,
                start: '23:30'
            },
        },
        miscellaneous: {
            hostIp: null,
            cacheLocation: '/config/GivTCP',
            timezone: 'Europe/London',
            printRaw: true,
            haAutoD: true
        },
        web: {
            dashboard: false,
            port: 3000,
        },
        keys: {
            givenergy: null,
            solcast: {
                apiKey: null,
                siteIdOne: null,
                siteIdTwo: null,
            },
        },
        palm: {
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
        }
    }),

    actions: {
        get(property) {
            console.log(this[property]);
            return this[property];
        },
        set(property, value){
           this[property] = value;
        }
    },

    getters: {},
})

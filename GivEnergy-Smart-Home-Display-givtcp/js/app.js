import { SensorType } from './enums.js';
import { Sensors } from './sensors.js';
import { Helpers } from './helpers.js';
import { Formatters } from './formatters.js';
import { Converters } from './converters.js';

class App {
    constructor() {
        const me = this;

        me.givTcpHostname = null;
        me.solarRate = null;
        me.exportRate = null;

        // Fetch the settings from `app.json`
        fetch("./app.json")
            .then(response => {
                return response.json();
            })
            .then(data => {
                me.givTcpHostname = data.givTcpHostname;
                me.solarRate = data.solarRate;
                me.exportRate = data.exportRate;

                if (me.givTcpHostname != null && me.solarRate != null && me.exportRate != null) {
                    me.launch();
                }
            });
    }

    /**
     * Fetch the initial set of data and setup a routine to fetch the data every 10 seconds
     */
    launch() {
        const me = this;

        // Get the initial set of data
        me.fetchData();

        // Repopulate the data every 10 seconds
        setInterval(me.fetchData.bind(me), 10000);
    }

    /**
     * Fetch the latest values from GivTCP
     */
    fetchData() {
        const me = this;

        fetch(`http://${me.givTcpHostname}/readData`, {
            mode: 'cors',
            headers: {
                'Access-Control-Allow-Origin': 'localhost:63342'
            }
        }).then(response => {
            return response.json();
        }).then(data => {
            me.onResponse(data)
        });
    }

    /**
     * Successful response from GivTCP
     * @param data
     */
    onResponse(data) {
        const me = this;

        me.updateTimeStamp();

        for (let i in Sensors) {
            let sensor = Sensors[i];
            let node = null;
            let value = null;

            if (sensor.mapping) {
                value = Helpers.getPropertyValueFromMapping(data, sensor.mapping);
            }

            // Some sensors require calculation of the values
            if (sensor.id === 'Battery_State') {
                let chargeRate = data.Power.Power.Charge_Power;
                let dischargeRate = data.Power.Power.Discharge_Power;

                if (dischargeRate > 0) {
                    value = "Discharging";
                } else if (chargeRate > 0) {
                    value = "Charging";
                } else {
                    value = "Idle";
                }
            } else if (sensor.id === 'Solar_Income' || sensor.id === 'Export_Income') {
                let income = value * me.solarRate;

                value = Converters.numberToCurrency(income);
            }

            if (value) {
                me.processItem({
                    sensor: sensor,
                    value: value
                });
            }
        }
    }

    /**
     * This takes an individual sensor data object and based on its type (power usage, power flow, summary), and
     * renders it within the appropriate point in the user interface
     * @param sensorData An individual sensor data object
     */
    processItem(sensorData) {
        const entityId = sensorData.sensor.id;
        const sensor = sensorData.sensor;

        let value = sensorData.value;
        let element = null;
        let group = null;
        let line = null;
        let arrow = null;

        if (sensor.type === SensorType.Summary) {
            element = $(`#${sensor.textElementId}`);
        } else if (sensor.type === SensorType.Power) {
            element = $(`#${sensor.textElementId}`);
        } else if (sensor.type === SensorType.Flow) {
            element = $(`#${sensor.flowElementId}`);
        }

        if (sensor.type === SensorType.Flow) {
            group = element;

            if (group.children('path').length > 0) {
                // Arc flow
                arrow = 'arc-arrow';

                if (entityId === 'Grid_to_Battery' || entityId === 'Solar_to_Grid') {
                    arrow = 'arc-arrow-opposite';
                }

                line = group.children('path')[0];
            } else {
                // Line flow
                arrow = 'line-arrow';
                line = group.children('line')[0];
            }
        } else if (sensor.type === SensorType.Power) {
            arrow = 'line-arrow';
            group = element.parent().parent();
            element.text(Formatters.sensorValue(value, sensor));

            if (group.children('line').length > 0) {
                line = group.children('line')[0];
            }
        } else if (sensor.type === SensorType.Summary) {
            element.text(Formatters.sensorValue(value, sensor));
        }

        if (sensor.type === SensorType.Power || sensor.type === SensorType.Flow) {
            if (parseFloat(value) < 0.01) {
                // If value is less than 0.01 kW, mark the line/group as Idle
                if (line) {
                    line.setAttribute("marker-end", "");
                }

                group.removeClass('active');
                group.addClass('idle');
            } else {
                // Active
                if (line) {
                    line.setAttribute("marker-end", `url(#${arrow})`);
                }

                group.removeClass('idle');
                group.addClass('active');
            }
        }
    }

    /**
     * Updates the time in the UI to let the user know when the data was last refreshed
     */
    updateTimeStamp() {
        const clock = $('#clock');
        const date = new Date();
        let hours = date.getHours();
        let minutes = date.getMinutes();

        if (minutes < 10) {
            minutes = '0' + minutes;
        }

        let suffix = 'am';

        if (hours > 12) {
            hours -= 12;
            suffix = 'pm';
        } else if (hours === 0) {
            hours = 12;
        }

        clock.text(`${hours}:${minutes}${suffix}`);
    }
}

export { App };
window.App = new App();
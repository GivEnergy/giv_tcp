class Formatters {
    /**
     * Formats a value based on the properties defined on the sensor
     * @param value The value to format
     * @param sensor The sensor object
     * @returns {string} Formatted value
     */
    static sensorValue(value, sensor) {
        const me = this;
        let text = value;

        // Format the value if a converter function has been set
        if (sensor.converter) {
            text = sensor.converter.call(me, text);
        }

        // If the value requires other special formatting
        if (sensor.formatter) {
            text = sensor.formatter.call(me, text);
        }

        // Add any prefix
        if (sensor.prefix) {
            text = `${sensor.prefix}${text}`;
        }

        // Add any suffix
        if (sensor.suffix) {
            text = `${text}${sensor.suffix}`;
        }

        return text;
    }

    static roundToOneDecimalPlace(value) {
        return value.toFixed(1);
    }
}

export { Formatters };
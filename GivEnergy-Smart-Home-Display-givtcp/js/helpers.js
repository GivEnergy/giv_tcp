class Helpers {
    /**
     * Traverses a nested object by processing a dot-delimited string
     * @param obj The object to traverse
     * @param mapping The mapping (a dot-delimited string)
     * @returns {*} The value of the nested object
     */
    static getPropertyValueFromMapping(obj, mapping) {
        let properties = mapping.split('.');

        for (let i in properties) {
            obj = obj[properties[i]];
        }

        return obj;
    }
}

export { Helpers };
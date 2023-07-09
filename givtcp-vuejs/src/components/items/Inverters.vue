<template>
    <v-card>
        <v-card-title>
            Inverters
        </v-card-title>
        <v-card-subtitle>
            Setup your inverter configurations
        </v-card-subtitle>
        <v-card-text>
            <v-form v-model="valid" @update:model-value="$emit('input', valid)">
                <v-select label="Number Of Inverters" v-model="form.numberOfInverters" :items="[1, 2, 3]"/>

                <v-select label="Number Of Batteries" v-model="form.numberOfBatteries" :items="[1, 2, 3]"/>

                <v-text-field label="IP Address" v-model="form.inverterIpAddress"/>
            </v-form>
        </v-card-text>
    </v-card>
</template>

<script>

import {useTcpStore} from "@/stores/counter";

export default {
    name: "Inverters",
    props: ['form', 'storeKey'],
    data() {
        return {
            valid: false,
        }
    },

    watch: {
        //need to implement a mixin that stores the update values
        form: {
            deep: true,
            handler(val) {
                useTcpStore().set(this.storeKey, val);
            }
        },
    }
}
</script>

<style scoped>

</style>
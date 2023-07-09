<template>
    <v-card>
        <v-card-title>
            MQTT
        </v-card-title>
        <v-card-subtitle>
            Setup the MQTT broker that stores information about your incoming inverter data
        </v-card-subtitle>
        <v-card-text>
            <v-form v-model="valid">
                <v-checkbox v-model="form.output"/>
                <v-text-field label="IP Address" v-model="form.address"/>
                <v-text-field label="Username" v-model="form.username"/>
                <v-text-field label="Password" v-model="form.password"/>

            </v-form>
        </v-card-text>
    </v-card>
</template>

<script>
import {useTcpStore} from "@/stores/counter";

export default {
    name: "Mqtt",
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
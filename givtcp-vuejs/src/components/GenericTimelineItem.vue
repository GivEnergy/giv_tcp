<template>
    <v-timeline-item>
        <component :is="component" v-model="valid" :form="form" :store-key="storeKey"/>
    </v-timeline-item>
</template>

<script>
import {useTcpStore} from "@/stores/counter";
import Inverters from "@/components/items/Inverters.vue";
import Mqtt from "@/components/items/Mqtt.vue";

export default {
    name: "GenericTimelineItem",
    components: {
        Inverters,
        Mqtt
    },

    props: {
        storeKey: {
            required: true,
            type: String
        },
        component: {
            required: true,
            type: String,
        }
    },

    data() {
        return {
            store: useTcpStore(),
            form: useTcpStore().get(this.storeKey),
            valid: false,
        }
    },
    watch: {
        form: {
            deep: true,
            handler(val) {
                this.store.set(this.storeKey, val);
            }
        },
    }
}
</script>

<style scoped>

</style>
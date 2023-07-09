<template>
    <v-container>
        <span> Welcome to the GivTCP environment setup page, </span>
        <!-- v stepper is currently unavailable so components for the time being are coded to card components -->

        <v-timeline align="start">
            <generic-timeline-item component="inverters" store-key="inverter"/>
            <generic-timeline-item component="mqtt" store-key="mqtt" />
        </v-timeline>

    </v-container>
</template>

<script>

import GenericTimelineItem from "@/components/GenericTimelineItem.vue";

export default {
    name: "Setup",
    components: {GenericTimelineItem},
    data() {
        return {
            step: 0,
        }
    }
}
</script>

<style scoped>

</style>
<template>
  <div>
    <v-timeline direction="horizontal" align="start" side="end">
      <v-timeline-item
        v-for="(timeline, i) in timelineList"
        :key="i"
        :dot-color="i <= storeStep.step ? '#4fbba9' : '#000'"
        size="small"
      >
        <div
          :style="{
            textTransform: timeline === 'mqtt' ? 'uppercase' : 'capitalize'
          }"
        >
          {{ timeline === 'homeAssistant' ? 'home Assistant' : timeline }}
        </div>
      </v-timeline-item>
    </v-timeline>
    <v-container>
      <h1 class="text-center" v-if="storeStep.step === -1">
        Welcome to the GivTCP environment setup page
      </h1>
      <FormCard v-if="storeStep.step >= 0" :card="storeCard[timelineList[storeStep.step]]" />
      <div class="d-flex flex-1-1-100 justify-center ma-5">
        <StepButton />
      </div>
    </v-container>
  </div>
</template>

<script>
import FormCard from '@/components/FormCard.vue'
import StepButton from '@/components/StepButton.vue'
import { useTcpStore, useStep, useCard } from '@/stores/counter'

export default {
  name: 'Setup',
  components: {
    FormCard,
    StepButton
  },
  data() {
    return {
      storeStep: useStep(),
      storeTCP: useTcpStore(),
      storeCard: useCard()
    }
  },
  computed: {
    timelineList() {
      return Object.keys(this.storeTCP).filter(
        (v) => !v.includes('$') && !v.includes('_') && v !== 'set' && v !== 'get'
      )
    }
  }
}
</script>

<style scoped></style>

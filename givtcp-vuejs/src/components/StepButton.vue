<template>
  <div>
    <v-btn v-if="storeStep.step > -1" @click="storeStep.step = storeStep.step - 1">
      Previous
    </v-btn>
    <v-btn v-if="storeStep.step < 10" @click="storeStep.step = storeStep.step + 1"> Next </v-btn>
  </div>
</template>

<script>
import { useTcpStore, useStep } from '@/stores/counter'

export default {
  name: 'Setup',
  data() {
    return {
      storeStep: useStep(),
      storeTCP: useTcpStore()
    }
  }
}
</script>

<style scoped></style>

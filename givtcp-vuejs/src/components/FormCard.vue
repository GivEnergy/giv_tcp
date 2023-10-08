<template>
  <div>
    <v-card>
      <v-card-title> {{ card?.title }} </v-card-title>
      <v-card-subtitle> {{ card?.subtitle }} </v-card-subtitle>
      <v-card-text>
        <div v-for="(input, i) in card?.fields" :key="i">
          <v-select
            v-if="input?.type === 'select'"
            :label="input?.options?.label"
            :items="input?.options?.items"
            v-model="storeTCP[input?.options?.parent][input?.options?.key]"
          />
          <v-text-field
            v-else-if="input?.type === 'text'"
            v-model="storeTCP[input?.options?.parent][input?.options?.key]"
            :label="input?.options?.label"
          />
          <v-switch
            v-else-if="input?.type === 'checkbox'"
            v-model="storeTCP[input?.options?.parent][input?.options?.key]"
            :label="input?.options?.label"
            color='#4fbba9'
          />
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { useTcpStore } from '@/stores/counter'

export default {
  name: 'FormCard',

  props: {
    card: {
      required: true,
      type: Object
    }
  },

  data() {
    return {
      storeTCP: useTcpStore()
    }
  }
}
</script>

<style scoped></style>

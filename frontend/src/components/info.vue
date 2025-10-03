<script>
import {defineComponent} from "vue";

export default defineComponent({
  emits: ['click'],
  props: {
    text: {
      type: String
    },
    icon: {
      type: String,
      default: 'mdi-help-circle-outline'
    },
    color: {
      type: String,
      default: 'blue-darken-4'
    },
    class: {
      type: String,
      default: 'cursor-help'
    }
  },
})
</script>
<template>
  <v-tooltip bottom>
    <template v-slot:activator="{ props }">
      <v-icon v-bind="props" :icon="icon" :color="color" :class="class" @click="$emit('click')"/>
    </template>
    <slot>
      {{ text }}
    </slot>
  </v-tooltip>
</template>

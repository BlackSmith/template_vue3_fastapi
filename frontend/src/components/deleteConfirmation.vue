<script>
import {defineComponent} from "vue";

export default defineComponent({
  emits: ['delete', 'update:modelValue'],
  props: {
    modelValue: {
      type: Boolean,
      required: true
    },
    name: {
      type: String,
      default: null
    },
    maxWidth: {
      type: Number,
      default: 500
    },
    objectName: {
      type: String,
      default: 'item'
    }
  },
  data() {
    return {}
  },
  computed: {
    getName() {
      return this.name ? `"${this.name}" ` : ''
    },
    iModelValue: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      }
    }
  },
  methods: {
    doDelete() {
      this.$emit('delete')
      this.$emit('update:modelValue', false);
    }
  }
})
//
</script>

<template>
  <v-dialog v-model="iModelValue" :max-width="maxWidth">
    <v-card prepend-icon="mdi-trash-can-outline">
      <template v-slot:text>
        <slot name="text">
          Are you sure that you want to delete this {{ objectName }}?
        </slot>
      </template>
      <template v-slot:title>Delete {{getName}}{{ objectName }}?</template>
      <template v-slot:actions>
        <v-spacer></v-spacer>
        <v-btn @click="$emit('update:modelValue', false)">Cancel</v-btn>
        <v-btn @click="doDelete" color="red-darken-4">Delete</v-btn>
      </template>
    </v-card>
  </v-dialog>
</template>

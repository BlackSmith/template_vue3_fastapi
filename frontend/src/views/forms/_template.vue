<script>
import {defineComponent} from "vue";
import Notification from "@/components/notification.vue";
import DeleteConfirmation from "@/components/deleteConfirmation.vue";

export default defineComponent({
  components: {DeleteConfirmation, Notification},
  emits: ['canceled', 'deleted', 'created', 'updated'],
  props: {
    selected: {
      type: Object
    }
  },
  data() {
    return {
      deleteConfirmationOpen: false,
      selectedBackup: {...this.selected},
      notify: null,
      isFormValid: null,
    }
  },
  computed: {},
  methods: {
    doCancel() {
      Object.assign(this.selected, this.selectedBackup)
      this.$emit('canceled', this.selectedBackup)
    },
    async doDelete() {
      const result = await this.$apiStore.delete('UserGroup', this.selected)
      this.notify = result.notification;
      if (this.notify?.status !== 'error') {
        this.$emit('deleted', this.selected)
      }
    },
    async doSubmit() {
      if (this.$refs.userForm.validate()) {
        const result = await this.$apiStore.submit('Network', this.selected)
        this.notify = result.notification;
        if (this.notify?.status !== 'error') {
          if (result?.created) {
            Object.assign(this.selected, result.updated)
            this.$emit('created', result.created)

          } else {
            Object.assign(this.selected, result.updated)
            this.$emit('updated', result.updated)
          }
        }
      }
    }
  }
})
</script>

<template>
  <v-card flat color="transparent" v-if="selected !== null"
          :prepend-icon="$router.currentRoute._value.meta.icon"
          :title="selected.name"
  >
    <v-card-text>
      <v-form ref="userForm" v-model="isFormValid" lazy-validation>


      </v-form>
    </v-card-text>
    <v-card-actions class="d-flex justify-space-between">
      <div>
        <v-btn
            text="Save"
            class="ml-3 my-1"
            color="primary"
            :disabled="!isFormValid"
            @click="doSubmit"/>
        <v-btn
            class="ml-3 my-1"
            @click="doCancel">Cancel
        </v-btn>
      </div>
      <div>
        <v-btn
            v-if="!selected.is_admin && !selected.is_default && selected.id"
            class="mr-3 my-1"
            @click="deleteConfirmationOpen=true"
            prepend-icon="mdi-trash-can-outline"
            color="red-darken-4">Delete
        </v-btn>
      </div>
    </v-card-actions>
  </v-card>

  <delete-confirmation
      v-model="deleteConfirmationOpen"
      objectName="network"
      :name="selected?.name"
      @delete="doDelete"
  />
  <notification :notify-obj="notify"/>
</template>

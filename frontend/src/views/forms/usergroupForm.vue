<script>
import {defineComponent} from "vue";
import Info from "@/components/info.vue";
import Notification from "@/components/notification.vue";
import DeleteConfirmation from "@/components/deleteConfirmation.vue";

export default defineComponent({
  components: {DeleteConfirmation, Notification, Info},
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
        const result = await this.$apiStore.submit('UserGroup', this.selected)
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

        <v-text-field
            v-model="selected.name"
            label="Name"
            :rules="[v => !!v || 'Name is required']"
            :counter="$apiStore.getMaxLength('UserGroupUpdate', 'name')"
        >
          <template #append-inner>
            <v-icon icon="mdi-asterisk" color="red-darken-4" size="x-small"></v-icon>
          </template>
        </v-text-field>

        <v-textarea
            v-model="selected.description"
            label="Description"
            row-height="15"
            rows="1"
            max-rows="10"
            :counter="$apiStore.getMaxLength('UserGroupUpdate', 'description')"
            auto-grow
        ></v-textarea>

        <v-text-field
            v-model="selected.realm_role"
            prepend-icon="mdi-cloud-key-outline"
            label="Keycloak Role"
            :counter="$apiStore.getMaxLength('UserGroupUpdate', 'realm_role')"
            v-if="!selected.is_default"
            :disabled="selected.is_admin"
        >
          <template #append-inner>
            <info>If a user' keycloak role match with this value,<br/>
                  the user will be assigned to this user group dynamically.</info>
          </template>
        </v-text-field>

        <v-card v-else
                title="Info"
                text="This is the default user group. Each user of this system is automatically assigned to this group."
        >
          <template v-slot:prepend>
            <v-icon icon="mdi-information-outline" color="blue-darken-2" size="large"></v-icon>
          </template>
        </v-card>

        <v-card v-if="selected.is_admin"
                title="Warnig"
        >
          <template v-slot:prepend>
            <v-icon icon="mdi-shield-alert-outline" color="orange-darken-2" size="large"></v-icon>
          </template>
          <template v-slot:text>
            <p>This is the admin user group. Users are assigned only by keycloak role.</p>
            <p>Only members of this group can manage user, user's&nbsp;groups and networks.</p>
          </template>
        </v-card>

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

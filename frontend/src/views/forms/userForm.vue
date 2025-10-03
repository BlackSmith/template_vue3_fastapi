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
      allUserGroups: []
    }
  },
  mounted() {
    this.$api.get('/api/users-groups/').then((data) => {
      this.allUserGroups = data.data
    })
  },
  computed: {
    assignabledUserGroups() {
      return this.allUserGroups.filter((it) => it.is_assignable)
    }
  },
  methods: {
    doCancel() {
      Object.assign(this.selected, this.selectedBackup)
      this.$emit('canceled', this.selectedBackup)
    },
    async doDelete() {
      const result = await this.$apiStore.delete('User', this.selected)
      this.notify = result.notification;
      if (this.notify?.status !== 'error') {
          this.$emit('deleted', this.selected)
      }
    },
    async doSubmit() {
      if (this.$refs.userForm.validate()) {
        const result = await this.$apiStore.submit('User', this.selected)
        this.notify = result.notification;
        if (this.notify?.status !== 'error') {
          if (result?.updated) {
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
            :counter="$apiStore.getMaxLength('UserUpdate', 'name')"
            required
        ></v-text-field>

        <v-text-field
            v-model="selected.email"
            prepend-icon="mdi-email-seal-outline"
            label="Email"
            :rules="[v => !!v || 'E-mail is required', v => /.+@.+\..+/.test(v) || 'E-mail must be valid']"
            :counter="$apiStore.getMaxLength('UserUpdate', 'email')"
            required
        ></v-text-field>

        <v-select
            v-model="selected.member_of_static_ids"
            prepend-icon="mdi-account-group"
            :items="allUserGroups.filter(g => g.is_assignable)"
            label="Static user's groups"
            item-title="name"
            item-value="id"
            :return-object="false"
            :rules="[v => !!v || 'Please select a group']"
            chips
            multiple
        ></v-select>

        <v-select
            v-model="selected.member_of_dynamic_ids"
            :items="allUserGroups"
            prepend-icon="mdi-account-group"
            class="opacity-80"
            label="Dynamic user's groups (based on realm roles)"
            item-title="name"
            item-value="id"
            messages="This list is based on the last user login."
            readonly
            disabled
            chips
            multiple
        ></v-select>

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
      objectName="user"
      :name="selected?.name"
      @delete="doDelete"
  />
  <notification :notify-obj="notify"/>
</template>

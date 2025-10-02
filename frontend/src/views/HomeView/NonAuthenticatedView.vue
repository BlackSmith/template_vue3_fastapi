<script>
import {defineComponent} from "vue";
import api from "@/services/api";


export default defineComponent({
  name: 'NonAuthenticatedView',
  emits: ['notify'],
  props: {},
  methods: {
    login() {
      try{
        this.$auth.login()
      } catch (error) {
        console.error('Login failed:', error)
        this.$emit('notify', {
          text: 'There is a problem with the authentication server.',
          detail: 'Please try again later.',
          icon: 'mdi-alert-circle-outline',
          status: 'warn',
          timeout: 5000,
        })
      }
    },
  }
})
</script>

<template>
  <v-card flat>
    <template v-slot:title>
      <span class="text-h4"><v-icon icon="mdi-login" class="mr-3" style="font-size: 0.9em" />Login</span>
    </template>
    <template v-slot:subtitle>
      <span class="pl-16">Login</span>
    </template>
    <v-card-text>
      <v-divider theme="dark" class="mb-8"></v-divider>
      <v-sheet class="d-flex flex-wrap text-center">
        <v-sheet class="ma-2 pa-2">
          <v-card
              style="min-width: 300px; min-height: 167px"
              title="Login by KeyCloak"
              subtitle="Login by domain credentials."
              max-width="500"
          >
            <v-card-item v-if="$keycloakReady.value">
                  <v-btn prepend-icon="mdi-login"
                        color="primary"
                        @click="login()"
                        >
                    Login
                  </v-btn>
            </v-card-item>
            <v-card-text v-else>
              <p>Loading Keycloak configuration...</p>
              <br>
              <v-progress-circular color="blue-lighten-3" indeterminate></v-progress-circular>
            </v-card-text>
          </v-card>
        </v-sheet>
      </v-sheet>
    </v-card-text>
  </v-card>
</template>

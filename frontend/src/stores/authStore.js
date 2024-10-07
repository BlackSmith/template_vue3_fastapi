import { defineStore } from 'pinia'
import { ref } from 'vue'
import keycloakService from '@/services/keycloak';

export const useAuthStore = defineStore({
  id: "storeAuth",
  // persistent: true,
  state: () => {
    return {
      authenticated: false,
      user: {},
    }
  },
  getters: {},
  actions: {
    // Initialize Keycloak OAuth
    async initOauth(keycloak, clearData = true) {
      if (clearData) {
        await this.clearUserData();
      }
      this.authenticated = keycloak.authenticated;
      this.user.username = keycloak?.idTokenParsed?.preferred_username;
      this.user.info = keycloak?.idTokenParsed
      this.user.token = keycloak?.token;
      if (keycloak?.refreshToken) {
        localStorage.setItem('refreshToken', keycloak.refreshToken);
      }
      const roles = [];
      // Global roles
      if (keycloak.tokenParsed && keycloak.tokenParsed.realm_access) {
        roles.push(...keycloak.tokenParsed.realm_access.roles);
      }
      // Client roles
      if (keycloak.tokenParsed && keycloak.tokenParsed.resource_access) {
        const clientRoles = keycloak.tokenParsed.resource_access;
        for (const client in clientRoles) {
          roles.push(...clientRoles[client].roles);
        }
      }
      this.user.roles = roles;
      // console.log(await keycloak.loadUserProfile())
    },

    // Logout user
    async logout() {
      try {
        await keycloakService.CallLogout('');
        localStorage.removeItem('refreshToken');
        await this.clearUserData();
      } catch (error) {
        console.error(error);
      }
    },
    login(){
       return keycloakService.CallLogin()
    },
    // Refresh user's token
    async refreshUserToken() {
      // keycloak.isTokenExpired(180)
      try {
        const keycloak = await keycloakService.CallTokenRefresh();
        if (keycloak) {
          this.initOauth(keycloak, false);
        } else {
          this.login()
        }
      } catch (error) {
        console.error(error);
      }
    },
    // Clear user's store data
    clearUserData() {
      this.authenticated = false;
      this.user = {};
    },

    // return True if the role has been assigned to this user
    isRoleAssigned(role) {
       if (this?.user?.roles) {
         return this.user.roles.includes(role)
       }
       return false
    }
  }
});

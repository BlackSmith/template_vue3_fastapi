<script>
import {defineComponent, ref } from "vue";
import { checkRightToRoute } from './helpers';

export default defineComponent({
  data() {
    return {
      app_name: "Application",
      drawer: true,
    }
  },
  computed: {
    getMenuItems() {
      return this.$router.options.routes.filter(route => route.meta?.menu && checkRightToRoute(this.$auth, route))
    },
    appBarHeight() {
      return this.$vuetify.display.mobile ? 64 : 0;
    },
    navigationDrawerWidth() {
      return !this.$vuetify.display.mobile ? 256 : 0;
    },
    appBarHeightPx() {
      return this.appBarHeight + 'px';
    },
    navigationDrawerWidthPx() {
      return this.navigationDrawerWidth + 'px';
    }
  },
  methods: {
    async logout() {
      try {
        await this.$auth.logout()
        this.$router.push({path: '/'});
      } catch (error) {
        console.error('Logout failed:', error)
      }
    },
  },
})
</script>

<template>
  <v-app>
    <div v-if="$keycloakReady">
      <v-app-bar app
                v-if="$vuetify.display.mobile"
                class="bg-black"
                theme="dark"
                :height="appBarHeight">
        <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
        <v-toolbar-title >
          <img
              src="/logo.png"
              width="24"
              alt="Logo"
              style="vertical-align: middle; margin-right: 15px"
          />{{ app_name }}</v-toolbar-title>
      </v-app-bar>

        <!-- Sidebar navigace -->
      <v-navigation-drawer
          class="bg-black"
          theme="dark"
          v-model="drawer"
          :permanent="!$vuetify?.display?.mobile"
          :width="navigationDrawerWidth"
      >
        <v-img
            v-if="!$vuetify.display.mobile"
            src="/logo.png"
            max-width="150"
            class="mx-auto my-4"
            alt="Logo"
        />
        <v-list-item :title="app_name" style="text-align: center" ></v-list-item>

        <v-divider theme="dark"></v-divider>

        <v-list nav>
          <v-list-item
              v-for="page in getMenuItems"
              :prepend-icon="typeof page.meta.icon === 'function' ? page.meta.icon() : page.meta.icon"
              :title="typeof page.name === 'function' ? page.name() : page.name"
              :key="page.path"
              :to="page.path"
              link
          />
        </v-list>

        <template v-slot:append>
          <!-- Logout button -->
          <div class="pa-2" v-if="$auth.authenticated">
            <v-list-item
                :title="$auth.user.name"
                prepend-icon="mdi-account-box"
            >
            </v-list-item>
            <v-btn prepend-icon="mdi-logout"
                  block
                  @click="logout()"
            >Logout</v-btn>
          </div>
        </template>
      </v-navigation-drawer>

      <!--  Page content -->
      <v-main class="px-6 py-2 main-content">
        <router-view />
      </v-main>
    </div>
  </v-app>

</template>

<style scoped>
.main-content {
  overflow: hidden;
  position: relative;
  top: 0; left: 0;
  width: calc(100vw - v-bind(navigationDrawerWidthPx));
  height: calc(100vh - v-bind(appBarHeightPx));
  margin-left: v-bind(navigationDrawerWidthPx);
  margin-top: v-bind(appBarHeightPx);
}
</style>
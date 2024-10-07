<script>
import { RouterLink, RouterView } from 'vue-router'
import {defineComponent} from "vue";

export default defineComponent({
  props: {},
  data() {
    return {}
  },
  methods: {
    async test() {
      this.$socket.emit('test', {payload: 'AAA'})
    }
  }
})
</script>

<template>
  <header>

    <div class="wrapper">
      <h2>User: {{ $authStore.user?.info?.name }}
        ({{ $authStore.user?.info?.preferred_username }})</h2>
      <h2>Email: {{ $authStore.user?.info?.email }}</h2>
      <h2>Token: {{ $authStore.user?.token?.slice(0, 25) }}...</h2>
      <h2>Expire: {{
          new Date($authStore.user?.info?.exp * 1000).toLocaleString() }} </h2>
      <h2>Roles: {{ $authStore.user?.roles}}</h2>
      <h3>
        <button @click="$authStore.login()" v-if="!$authStore.authenticated">Login</button>
        <button @click="$authStore.logout()" v-if="$authStore.authenticated">Logout</button>
        <button @click="test()" v-if="$authStore.authenticated && !$SOCKET_DISABLED">
          Test Socket
        </button>
      </h3>
      <br>
      <h2>Info:</h2>
      {{ $authStore.user?.info }}
    </div>
  </header>

  <RouterView />
</template>

<style scoped>

</style>

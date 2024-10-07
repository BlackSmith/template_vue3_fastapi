<script>
import {defineComponent} from "vue";
import instance from "@/services/api"

export default defineComponent({
  props: {},
  data() {
    return {}
  },
  methods: {
    async get_info() {
      const res = await instance.get('/me')
      console.log(res)
      this.$refs.info.innerHTML = res.request.response.replaceAll(',', ',\n')
    }
  }
})
</script>

<template>
  <main>
    <button @click="get_info()" v-if="$authStore.authenticated">
      Test API
    </button>
    <pre ref="info"></pre>
  </main>
</template>

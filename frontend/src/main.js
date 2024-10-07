import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import keycloakService from '@/services/keycloak';

import App from '@/App.vue'
import router from '@/router'
import AuthStorePlugin from '@/plugins/authStore';
import WebSocketStorePlugin from '@/plugins/webSocket'

import './assets/main.css'

// Create Pinia instance
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate)

const renderApp = () => {
  const app = createApp(App)
  app.use(AuthStorePlugin, {pinia});
  app.config.globalProperties.$SOCKET_DISABLED = SOCKET_DISABLED;
  if (!SOCKET_DISABLED) {
    app.use(WebSocketStorePlugin, {pinia});
  }
  app.use(pinia);
  app.use(router)
  app.mount('#app')
}

keycloakService.CallInit(renderApp);

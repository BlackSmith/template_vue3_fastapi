import WebSocketService from "@/services/websocket";
import {useAuthStore} from "@/stores/authStore.js";

// Setup auth store as a plugin so it can be accessed globally in our FE
const webSocketPlugin = {
  install(app, option) {
    const store = useAuthStore(option.pinia);
    app.config.globalProperties.$socket = new WebSocketService(store)
  }
}

export default webSocketPlugin;

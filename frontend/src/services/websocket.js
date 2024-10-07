import {watch} from 'vue';
import {Manager} from "socket.io-client";

export default class WebSocketService {

  constructor(authStore) {
    this.client = null;
    this.disconnect_reason = null;
    this.manager = new Manager('/socket', {
      transports: ["websocket", "webtransport"],
      autoConnect: false,
    });
    this.authStore = authStore;
    this.token = this.authStore?.user.token
    watch(
      () => this.authStore.user.token,
      (newValue, oldValue) => {
        if (this.client && !this.token) {
           this.token = newValue
           console.info("Reconnect socket")
           this.disconnect()
           this.connect()
        }
      }
    );
    // window.setTimeout(() => {
    this.connect()
    // }, 1000)

  }

  connect() {
    if (this.client && typeof this.client === 'object') {
      return
    }

    this.client = this.manager.socket('/', {auth: {token: this.authStore?.user.token}});

    this.client.on('connect', () => {
      console.info('Public socket connected: ' + this.client.connected);
      this.client.io.engine.once("upgrade", () => {
        console.log(
          "Public socket upgrade to " + this.client.io.engine.transport.name
        );
      });
    });

    this.client.on('disconnect_reason', (reason) => {
      console.warn('Disconnect reason', reason)
      this.disconnect_reason = reason?.reason;
    })

    this.client.on('disconnect', async (reason) => {
      console.info('Public socket disconnected: ' + reason);
      if (reason === "io server disconnect") {
        // the disconnection was initiated by the server,
        // need to reconnect manually
        if (this.disconnect_reason === 'token-expired') {
          console.warn('Socket was disconnected because token expired.')
          await this.authStore.refreshUserToken()
        }
        this.client.connect();
      }
    });

    this.client.on("connect_error", (e) => {
      setTimeout(() => {
        this.disconnect()
        this.connect();
      }, SOCKET_RECONNECT * 1000);
    });
    this.client.connect()
  }

  disconnect() {
    this.client.disconnect();
    this.client = null;
  }

  emit(eventName, payload) {
    this.client.emit(eventName, payload)
  }

  request(eventName, payload, timeout = 30, client = null) {
    return new Promise((receiveCallback, rejectCallback) => {
      const callBack = (data) => {
        // console.warn(eventName, data)
        window.clearTimeout(timer);
        receiveCallback(data);
      }

      const timer = window.setTimeout(() => {
        console.error('The request "' + eventName + '" timeout. ', payload)
        rejectCallback()
        this.client.off(eventName, callBack);
      }, timeout * 1000)
      if (client === null) {
        client = this.client;
      }
      client.once(eventName, callBack)
      console.debug(eventName, payload)
      client.emit(eventName, payload)
    })
  }

}

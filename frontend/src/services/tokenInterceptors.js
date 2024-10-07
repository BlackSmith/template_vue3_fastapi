import axiosInstance from "@/services/api";
import WebSocketService from "@/services/websocket";

const setup = (authStore) => {
  axiosInstance.interceptors.request.use(
    (config) => {
      // If user is authenticated, place access token in request header.
      if (authStore.authenticated) {
        config.headers["Authorization"] = `bearer ${authStore.user.token}`;
      }

      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  axiosInstance.interceptors.response.use(
    (res) => {
      return res;
    },
    async (error) => {
      const oriConfig = error.config;

      if (error.response?.status === 401 && !oriConfig._retry) {
        oriConfig._retry = true;

        try {
          // Refresh token then retry once
          await authStore.refreshUserToken();

          // Place refreshed access token in the request header
          oriConfig.headers["Authorization"] = `bearer ${authStore.user.token}`;

          return axiosInstance(oriConfig);
        } catch (_error) {
          console.error("Refresh token failed");
          console.error(_error);

          return Promise.reject(_error);
        }
      }

      return Promise.reject(error);
    }
  );


  WebSocketService.authStore = authStore;
};

export default setup;

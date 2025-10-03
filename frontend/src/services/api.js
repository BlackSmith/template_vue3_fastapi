import axios from "axios";

// Creating an instance for axios to be used by the token interceptor service
const api = axios.create({
  baseURL: "",
  timeout: 10_000,
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;

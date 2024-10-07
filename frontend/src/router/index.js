import { createRouter, createWebHistory } from 'vue-router'

// Components
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: "/",
    name: "Home",
    component: HomeView
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes: routes
})

export default router

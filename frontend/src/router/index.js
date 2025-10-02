import { createRouter, createWebHistory } from 'vue-router'
import { useKeycloak }  from '@dsb-norge/vue-keycloak-js'
import { useAuthStore } from '../stores/authStore.js'
import { checkRightToRoute } from '../helpers.js'
import HomeView from '../views/HomeView/View.vue'
import UsersView from '../views/UsersView.vue'
import NotFound from '../views/NotFound.vue'


const permsContain = (text) => (perms) => perms.some(it => it === 'admin:all' || it.includes(text))

const keycloak = useKeycloak()

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: () => keycloak.authenticated ? "Home" : "Login",
      component: HomeView,
      meta: {
        icon: () => keycloak.authenticated ? 'mdi-view-dashboard' : 'mdi-login',
        menu: true,
      }
    }, {
      path: "/users",
      name: "Users",
      component: UsersView,
      meta: {
        permission: 'admin:all',
        icon: 'mdi-account-outline',
        menu: true,
      }
    }, {
      path: '/:pathMatch(.*)*', // Wildcard pro zachycení všech neexistujících tras
      component: NotFound
    }
  ],
})
router.beforeEach((to, from) => {
  if (!checkRightToRoute(useAuthStore(), to)) {
    return '/'
  }
})

export default router

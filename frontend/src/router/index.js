import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
  },
  {
    path: '/my-matchups',
    name: 'MyMatchups',
    component: () => import('../views/MyMatchups.vue'),
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/UserSettings.vue'),
  },
  {
    path: '/matchup/create',
    name: 'MatchupCreate',
    component: () => import('../views/MatchupCreate.vue'),
  },
  {
    path: '/matchup/:name',
    name: 'Matchup',
    component: () => import('../views/Matchup.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

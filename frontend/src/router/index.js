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
    path: '/oauth/callback',
    name: 'OAuthCallback',
    component: () => import('../views/OAuthCallback.vue'),
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
  // League routes
  {
    path: '/leagues',
    name: 'LeagueList',
    component: () => import('../views/LeagueList.vue'),
  },
  {
    path: '/league/create',
    name: 'LeagueCreate',
    component: () => import('../views/LeagueCreate.vue'),
  },
  {
    path: '/league/:id',
    name: 'LeagueDetail',
    component: () => import('../views/LeagueDetail.vue'),
  },
  // Admin routes
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('../views/AdminUsers.vue'),
  },
  {
    path: '/admin/settings',
    name: 'AdminSettings',
    component: () => import('../views/AdminSettings.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

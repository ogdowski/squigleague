import axios from 'axios'
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/LeagueList.vue'),
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
    path: '/matchups',
    name: 'MyMatchups',
    component: () => import('../views/MyMatchups.vue'),
  },
  // Redirect old URL
  {
    path: '/my-matchups',
    redirect: '/matchups',
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
    path: '/league/:id/:tab?',
    name: 'LeagueDetail',
    component: () => import('../views/LeagueDetail.vue'),
  },
  {
    path: '/league/:id/settings',
    name: 'LeagueSettings',
    component: () => import('../views/LeagueSettings.vue'),
  },
  {
    path: '/league/:leagueId/match/:matchId',
    name: 'MatchDetail',
    component: () => import('../views/MatchDetail.vue'),
  },
  // Rules routes (auth required)
  {
    path: '/rules',
    name: 'Rules',
    component: () => import('../views/Rules.vue'),
    meta: { requiresAuth: true, requiresRules: true },
  },
  {
    path: '/rules/:factionSlug',
    name: 'RulesFaction',
    component: () => import('../views/Rules.vue'),
    meta: { requiresAuth: true, requiresRules: true },
  },
  {
    path: '/rules/:factionSlug/:unitSlug',
    name: 'RulesUnit',
    component: () => import('../views/Rules.vue'),
    meta: { requiresAuth: true, requiresRules: true },
  },
  // Player routes
  {
    path: '/players',
    name: 'PlayerRanking',
    component: () => import('../views/PlayerRanking.vue'),
  },
  {
    path: '/player/:userId',
    name: 'PlayerProfile',
    component: () => import('../views/PlayerProfile.vue'),
  },
  // Admin routes
  {
    path: '/admin/:tab?',
    name: 'AdminPanel',
    component: () => import('../views/AdminPanel.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  if (to.meta.requiresAuth) {
    const authStore = useAuthStore()
    if (!authStore.isAuthenticated) {
      return { name: 'Login', query: { redirect: to.fullPath } }
    }
  }
  if (to.meta.requiresRules) {
    const authStore = useAuthStore()
    // On refresh, user may not be fetched yet — ensure it's loaded
    if (!authStore.user && authStore.token) {
      await authStore.fetchUser()
    }
    if (authStore.user?.role === 'admin') return
    try {
      const response = await axios.get(`${API_URL}/admin/settings/features`)
      if (!response.data.rules_enabled) {
        return { name: 'Home' }
      }
    } catch {
      // Don't redirect on network/auth errors — only block when
      // the API explicitly says rules are disabled
    }
  }
})

export default router

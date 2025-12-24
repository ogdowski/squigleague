import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/matchup'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/matchup',
      name: 'matchup',
      component: () => import('@/views/Matchup.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/matchup/:id',
      name: 'matchup-view',
      component: () => import('@/views/MatchupView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/leagues',
      name: 'leagues',
      component: () => import('@/views/Leagues.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/leagues/:id',
      name: 'league-detail',
      component: () => import('@/views/LeagueDetail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/leaderboard',
      name: 'leaderboard',
      component: () => import('@/views/Leaderboard.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/Settings.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (!authStore.user && authStore.token) {
    await authStore.fetchCurrentUser()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router

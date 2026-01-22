<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">{{ t('adminUsers.title') }}</h1>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-10 h-10 border-4 border-squig-yellow border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div v-else-if="error" class="card">
      <div class="bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ error }}
      </div>
    </div>

    <div v-else>
      <!-- Admin Navigation -->
      <div class="card mb-6">
        <h3 class="text-lg font-medium mb-3">{{ t('adminUsers.navigation') }}</h3>
        <div class="flex gap-4">
          <router-link to="/admin/settings" class="btn-secondary">
            {{ t('adminUsers.appSettings') }}
          </router-link>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid md:grid-cols-4 gap-4 mb-8">
        <div class="card">
          <h3 class="text-sm text-gray-400 mb-1">{{ t('adminUsers.totalUsers') }}</h3>
          <p class="text-2xl font-bold">{{ stats.total_users }}</p>
        </div>
        <div class="card">
          <h3 class="text-sm text-gray-400 mb-1">{{ t('adminUsers.players') }}</h3>
          <p class="text-2xl font-bold text-blue-400">{{ stats.players }}</p>
        </div>
        <div class="card">
          <h3 class="text-sm text-gray-400 mb-1">{{ t('adminUsers.organizers') }}</h3>
          <p class="text-2xl font-bold text-yellow-400">{{ stats.organizers }}</p>
        </div>
        <div class="card">
          <h3 class="text-sm text-gray-400 mb-1">{{ t('adminUsers.admins') }}</h3>
          <p class="text-2xl font-bold text-red-400">{{ stats.admins }}</p>
        </div>
      </div>

      <!-- Role Error -->
      <div v-if="roleError" class="mb-4 bg-red-900/30 border border-red-500 text-red-200 px-4 py-3 rounded">
        {{ roleError }}
      </div>

      <!-- Users Table -->
      <div class="card">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-gray-400 border-b border-gray-700">
                <th class="text-left py-3 px-4">{{ t('adminUsers.id') }}</th>
                <th class="text-left py-3 px-4">{{ t('adminUsers.email') }}</th>
                <th class="text-left py-3 px-4">{{ t('adminUsers.username') }}</th>
                <th class="text-center py-3 px-4">{{ t('adminUsers.role') }}</th>
                <th class="text-center py-3 px-4">{{ t('adminUsers.status') }}</th>
                <th class="text-right py-3 px-4">{{ t('adminUsers.created') }}</th>
                <th class="text-center py-3 px-4">{{ t('adminUsers.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="user in users"
                :key="user.id"
                class="border-b border-gray-800 hover:bg-gray-700/50"
              >
                <td class="py-3 px-4 text-gray-400">{{ user.id }}</td>
                <td class="py-3 px-4">{{ user.email }}</td>
                <td class="py-3 px-4">{{ user.username || '-' }}</td>
                <td class="py-3 px-4 text-center">
                  <select
                    v-model="user.role"
                    @change="updateRole(user)"
                    :disabled="user.updating"
                    class="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm focus:outline-none focus:border-squig-yellow"
                  >
                    <option value="player">{{ t('adminUsers.rolePlayer') }}</option>
                    <option value="organizer">{{ t('adminUsers.roleOrganizer') }}</option>
                    <option value="admin">{{ t('adminUsers.roleAdmin') }}</option>
                  </select>
                </td>
                <td class="py-3 px-4 text-center">
                  <span v-if="user.is_active" class="text-green-400">{{ t('adminUsers.active') }}</span>
                  <span v-else class="text-red-400">{{ t('adminUsers.inactive') }}</span>
                </td>
                <td class="py-3 px-4 text-right text-gray-400">{{ formatDate(user.created_at) }}</td>
                <td class="py-3 px-4 text-center">
                  <span v-if="user.updating" class="text-yellow-400">{{ t('adminUsers.saving') }}</span>
                  <span v-else-if="user.saved" class="text-green-400">{{ t('adminUsers.saved') }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const { t } = useI18n()
const API_URL = import.meta.env.VITE_API_URL || '/api'
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const roleError = ref('')
const users = ref([])
const stats = ref({
  total_users: 0,
  players: 0,
  organizers: 0,
  admins: 0,
})

const fetchData = async () => {
  try {
    const [usersRes, statsRes] = await Promise.all([
      axios.get(`${API_URL}/admin/users`),
      axios.get(`${API_URL}/admin/stats`),
    ])

    users.value = usersRes.data.map(u => ({
      ...u,
      updating: false,
      saved: false,
      originalRole: u.role,
    }))
    stats.value = statsRes.data
  } catch (err) {
    if (err.response?.status === 403) {
      error.value = t('adminUsers.accessDenied')
    } else {
      error.value = t('adminUsers.failedToLoad')
    }
  } finally {
    loading.value = false
  }
}

const updateRole = async (user) => {
  if (user.role === user.originalRole) return

  user.updating = true
  user.saved = false
  roleError.value = ''

  try {
    await axios.patch(`${API_URL}/admin/users/${user.id}/role`, {
      role: user.role,
    })
    user.originalRole = user.role
    user.saved = true

    // Refresh stats
    const statsRes = await axios.get(`${API_URL}/admin/stats`)
    stats.value = statsRes.data

    setTimeout(() => {
      user.saved = false
    }, 2000)
  } catch (err) {
    roleError.value = err.response?.data?.detail || t('adminUsers.failedToUpdateRole')
    user.role = user.originalRole
    setTimeout(() => {
      roleError.value = ''
    }, 5000)
  } finally {
    user.updating = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  fetchData()
})
</script>

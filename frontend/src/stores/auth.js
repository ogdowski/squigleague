import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  async function fetchCurrentUser() {
    if (!token.value) return
    
    try {
      const response = await axios.get('/api/users/me', {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      user.value = response.data
    } catch (error) {
      console.error('Failed to fetch user:', error)
      logout()
    }
  }

  async function login(credentials) {
    try {
      const formData = new FormData()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)

      const response = await axios.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })

      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
      
      await fetchCurrentUser()
      return { success: true }
    } catch (error) {
      console.error('Login failed:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      }
    }
  }

  async function register(userData) {
    try {
      await axios.post('/api/auth/register', userData)
      return { success: true }
    } catch (error) {
      console.error('Registration failed:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      }
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  async function handleOAuthCallback(provider, code) {
    try {
      const response = await axios.post(`/api/auth/oauth/${provider}/callback`, { code })
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
      await fetchCurrentUser()
      return { success: true }
    } catch (error) {
      console.error('OAuth callback failed:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'OAuth authentication failed' 
      }
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    logout,
    fetchCurrentUser,
    handleOAuthCallback
  }
})

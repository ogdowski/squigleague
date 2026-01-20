import { defineStore } from 'pinia'
import axios from 'axios'
import { useLanguageStore } from './language'

const API_URL = import.meta.env.VITE_API_URL || '/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    async register(email, username, password) {
      const response = await axios.post(`${API_URL}/auth/register`, {
        email,
        username,
        password,
      })
      this.token = response.data.access_token
      this.user = response.data.user
      localStorage.setItem('token', this.token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
    },

    async login(email, password) {
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        password,
      })
      this.token = response.data.access_token
      this.user = response.data.user
      localStorage.setItem('token', this.token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
    },

    async fetchUser() {
      if (!this.token) return
      try {
        const response = await axios.get(`${API_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${this.token}` },
        })
        this.user = response.data

        // Sync language preference from user data
        const languageStore = useLanguageStore()
        if (response.data.preferred_language) {
          languageStore.initFromUser(response.data.preferred_language)
        }
      } catch (error) {
        this.logout()
      }
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    },

    initAuth() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        this.fetchUser()
      }
    },
  },
})

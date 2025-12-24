<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import Navbar from '@/components/Navbar.vue'

const authStore = useAuthStore()
const themeStore = useThemeStore()

const displayName = ref('')
const email = ref('')
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const saving = ref(false)

onMounted(() => {
  if (authStore.user) {
    displayName.value = authStore.user.display_name || ''
    email.value = authStore.user.email || ''
  }
})

async function saveSettings() {
  saving.value = true
  
  setTimeout(() => {
    alert('Settings saved successfully!')
    saving.value = false
  }, 500)
}
</script>

<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark">
    <Navbar />
    
    <div class="max-w-4xl mx-auto px-4 py-8">
      <div class="card">
        <h1 class="text-3xl font-bold text-primary mb-6">Settings</h1>

        <div class="space-y-6">
          <div>
            <h2 class="text-xl font-semibold mb-4">Profile</h2>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium mb-2">Display Name</label>
                <input 
                  v-model="displayName" 
                  type="text" 
                  class="input-field w-full"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-2">Email</label>
                <input 
                  v-model="email" 
                  type="email" 
                  class="input-field w-full"
                  disabled
                />
              </div>
            </div>
          </div>

          <hr class="border-gray-300 dark:border-gray-600" />

          <div>
            <h2 class="text-xl font-semibold mb-4">Appearance</h2>
            <div class="flex items-center gap-4">
              <span class="text-sm font-medium">Theme:</span>
              <button 
                @click="themeStore.toggleTheme"
                class="btn-secondary"
              >
                {{ themeStore.isDark ? 'Dark Mode' : 'Light Mode' }}
              </button>
            </div>
          </div>

          <hr class="border-gray-300 dark:border-gray-600" />

          <div>
            <h2 class="text-xl font-semibold mb-4">Change Password</h2>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium mb-2">Current Password</label>
                <input 
                  v-model="currentPassword" 
                  type="password" 
                  class="input-field w-full"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-2">New Password</label>
                <input 
                  v-model="newPassword" 
                  type="password" 
                  class="input-field w-full"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-2">Confirm New Password</label>
                <input 
                  v-model="confirmPassword" 
                  type="password" 
                  class="input-field w-full"
                />
              </div>
            </div>
          </div>

          <div class="flex gap-4">
            <button 
              @click="saveSettings"
              :disabled="saving"
              class="btn-primary"
            >
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
            <button class="btn-secondary">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

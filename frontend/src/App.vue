<script setup>
import { RouterView } from 'vue-router'
import { useThemeStore } from './stores/theme'
import { onMounted } from 'vue'

const themeStore = useThemeStore()

onMounted(() => {
  themeStore.initTheme()
})
</script>

<template>
  <div :class="{ 'dark': themeStore.isDark }">
    <RouterView />
  </div>
</template>

<style scoped>
</style>

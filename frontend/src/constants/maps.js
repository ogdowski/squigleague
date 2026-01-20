// Maps data is fetched from backend API via /api/matchup/maps
// This file provides a composable for caching the maps data

import { ref } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

// Cached maps data
const mapsData = ref(null)
const loading = ref(false)

export async function fetchMapsData() {
  if (mapsData.value) return mapsData.value
  if (loading.value) {
    // Wait for existing request
    while (loading.value) {
      await new Promise(resolve => setTimeout(resolve, 50))
    }
    return mapsData.value
  }

  loading.value = true
  try {
    const response = await axios.get(`${API_URL}/matchup/maps`)
    mapsData.value = response.data
    return mapsData.value
  } catch (err) {
    console.error('Failed to fetch maps data:', err)
    return null
  } finally {
    loading.value = false
  }
}

export function useMaps() {
  return {
    mapsData,
    loading,
    fetchMapsData,
  }
}

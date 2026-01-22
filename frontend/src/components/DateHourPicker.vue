<template>
  <div class="flex flex-col sm:flex-row gap-3 sm:gap-2">
    <!-- Date input - large touch target on mobile -->
    <div class="flex-1">
      <label v-if="showLabels" class="block text-xs text-gray-400 mb-1 sm:hidden">{{ dateLabel }}</label>
      <input
        :value="dateValue"
        @input="updateDate($event.target.value)"
        type="date"
        :required="required"
        class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-base focus:outline-none focus:border-squig-yellow transition-colors"
        style="font-size: 16px; min-height: 48px;"
      />
    </div>
    <!-- Hour select - overlay menu on mobile, native select on desktop -->
    <div class="sm:w-28">
      <label v-if="showLabels" class="block text-xs text-gray-400 mb-1 sm:hidden">{{ hourLabel }}</label>
      <!-- Mobile: Button that opens overlay -->
      <button
        type="button"
        @click="showHourMenu = true"
        class="sm:hidden w-full flex items-center justify-between bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-base focus:outline-none focus:border-squig-yellow transition-colors"
        style="min-height: 48px;"
      >
        <span>{{ hourValue }}:00</span>
        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      <!-- Desktop: Native select -->
      <select
        :value="hourValue"
        @change="updateHour($event.target.value)"
        :required="required"
        class="hidden sm:block w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-base focus:outline-none focus:border-squig-yellow transition-colors appearance-none cursor-pointer"
        style="font-size: 16px; min-height: 48px;"
      >
        <option v-for="h in hours" :key="h" :value="h">{{ h }}:00</option>
      </select>
    </div>

    <!-- Hour selection overlay menu (mobile only) -->
    <Teleport to="body">
      <Transition name="hour-menu">
        <div v-if="showHourMenu" class="fixed inset-0 z-50 sm:hidden">
          <div class="fixed inset-0 bg-black/50" @click="showHourMenu = false"></div>
          <div class="fixed inset-x-4 top-1/4 bottom-1/4 bg-gray-800 border border-gray-700 rounded-xl shadow-xl overflow-hidden flex flex-col">
            <div class="px-4 py-3 border-b border-gray-700 flex-shrink-0">
              <p class="font-medium text-center">{{ hourLabel }}</p>
            </div>
            <div class="flex-1 overflow-y-auto p-2">
              <div class="grid grid-cols-4 gap-2">
                <button
                  v-for="h in hours"
                  :key="h"
                  type="button"
                  @click="selectHour(h)"
                  class="py-3 rounded-lg text-center font-medium transition-colors"
                  :class="hourValue === h ? 'bg-squig-yellow text-black' : 'bg-gray-700 hover:bg-gray-600 text-white'"
                >
                  {{ h }}:00
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const showHourMenu = ref(false)

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  showLabels: {
    type: Boolean,
    default: true
  },
  dateLabel: {
    type: String,
    default: 'Date'
  },
  hourLabel: {
    type: String,
    default: 'Hour'
  }
})

const emit = defineEmits(['update:modelValue'])

const hours = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'))

const dateValue = computed(() => {
  if (!props.modelValue) return ''
  // Handle both ISO string and datetime-local format
  const val = props.modelValue
  if (val.includes('T')) {
    return val.split('T')[0]
  }
  return val.slice(0, 10)
})

const hourValue = computed(() => {
  if (!props.modelValue) return '12'
  const val = props.modelValue
  if (val.includes('T')) {
    const timePart = val.split('T')[1]
    if (timePart) {
      return timePart.slice(0, 2)
    }
  }
  return '12'
})

const updateDate = (newDate) => {
  if (!newDate) {
    emit('update:modelValue', '')
    return
  }
  const hour = hourValue.value
  emit('update:modelValue', `${newDate}T${hour}:00`)
}

const updateHour = (newHour) => {
  const date = dateValue.value
  if (!date) return
  emit('update:modelValue', `${date}T${newHour}:00`)
}

const selectHour = (hour) => {
  updateHour(hour)
  showHourMenu.value = false
}
</script>

<style scoped>
.hour-menu-enter-active,
.hour-menu-leave-active {
  transition: opacity 0.15s ease;
}

.hour-menu-enter-from,
.hour-menu-leave-to {
  opacity: 0;
}

.hour-menu-enter-to,
.hour-menu-leave-from {
  opacity: 1;
}
</style>

<template>
  <div class="flex gap-2">
    <input
      :value="dateValue"
      @input="updateDate($event.target.value)"
      type="date"
      :required="required"
      class="flex-1 bg-gray-700 border border-gray-600 rounded px-4 py-2 focus:outline-none focus:border-squig-yellow"
    />
    <select
      :value="hourValue"
      @change="updateHour($event.target.value)"
      :required="required"
      class="w-24 bg-gray-700 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:border-squig-yellow"
    >
      <option v-for="h in hours" :key="h" :value="h">{{ h }}:00</option>
    </select>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
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
</script>

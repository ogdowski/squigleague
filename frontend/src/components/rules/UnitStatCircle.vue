<template>
  <div class="relative inline-flex items-center justify-center">
    <!-- Main circle -->
    <div class="w-28 h-28 rounded-full border-2 border-gray-600 relative bg-gray-800">
      <!-- Move (top) -->
      <div class="absolute top-2 left-1/2 -translate-x-1/2 text-center">
        <div class="text-xs text-gray-500 leading-none">M</div>
        <div class="text-lg font-bold leading-none">{{ move || '-' }}</div>
      </div>

      <!-- Health (left) -->
      <div class="absolute left-2 top-1/2 -translate-y-1/2 text-center">
        <div class="text-xs text-gray-500 leading-none">H</div>
        <div class="text-lg font-bold leading-none">{{ health || '-' }}</div>
      </div>

      <!-- Control (bottom) -->
      <div class="absolute bottom-2 left-1/2 -translate-x-1/2 text-center">
        <div class="text-lg font-bold leading-none">{{ control || '-' }}</div>
        <div class="text-xs text-gray-500 leading-none">C</div>
      </div>

      <!-- Save (right) - different color -->
      <div class="absolute right-2 top-1/2 -translate-y-1/2 text-center text-squig-yellow">
        <div class="text-xs text-squig-yellow/70 leading-none">Sv</div>
        <div class="text-lg font-bold leading-none">{{ save || '-' }}</div>
      </div>

      <!-- Divider lines (X shape - rotated 45 degrees) -->
      <svg class="absolute inset-0 w-full h-full" viewBox="0 0 112 112">
        <line x1="28" y1="28" x2="84" y2="84" stroke="currentColor" stroke-width="1" class="text-gray-700" />
        <line x1="84" y1="28" x2="28" y2="84" stroke="currentColor" stroke-width="1" class="text-gray-700" />
      </svg>
    </div>

    <!-- Ward circle (bottom-right) -->
    <div
      v-if="ward"
      class="absolute -bottom-1 -right-1 w-9 h-9 rounded-full bg-purple-900 border-2 border-purple-500 flex items-center justify-center"
    >
      <div class="text-center">
        <div class="text-[9px] text-purple-300 leading-none">W</div>
        <div class="text-sm font-bold text-purple-200 leading-none">{{ ward }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  move: {
    type: [String, Number],
    default: null
  },
  health: {
    type: [String, Number],
    default: null
  },
  save: {
    type: [String, Number],
    default: null
  },
  control: {
    type: [String, Number],
    default: null
  },
  ward: {
    type: [String, Number],
    default: null
  }
})
</script>

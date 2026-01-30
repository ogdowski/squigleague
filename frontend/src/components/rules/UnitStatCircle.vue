<template>
  <div class="relative inline-flex items-center justify-center">
    <!-- Main circle -->
    <div class="w-44 h-44 rounded-full border-2 border-gray-600 relative bg-gray-800">
      <!-- Move (top) -->
      <div class="absolute top-3 left-1/2 -translate-x-1/2 text-center">
        <div class="text-[10px] text-gray-500 leading-none">Move</div>
        <div class="text-3xl font-bold leading-none mt-0.5">{{ move || '-' }}</div>
      </div>

      <!-- Health (left) -->
      <div class="absolute left-3 top-1/2 -translate-y-1/2 text-center">
        <div class="text-[10px] text-gray-500 leading-none">Health</div>
        <div class="text-3xl font-bold leading-none mt-0.5">{{ health || '-' }}</div>
      </div>

      <!-- Bottom stat (Control or custom) -->
      <div class="absolute bottom-3 left-1/2 -translate-x-1/2 text-center">
        <div class="text-3xl font-bold leading-none">{{ control || '-' }}</div>
        <div class="text-[10px] text-gray-500 leading-none mt-0.5">{{ bottomLabel }}</div>
      </div>

      <!-- Save (right) - different color -->
      <div class="absolute right-3 top-1/2 -translate-y-1/2 text-center text-squig-yellow">
        <div class="text-[10px] text-squig-yellow/70 leading-none">Save</div>
        <div class="text-3xl font-bold leading-none mt-0.5">{{ save || '-' }}</div>
      </div>

      <!-- Divider lines (X shape - rotated 45 degrees) -->
      <svg class="absolute inset-0 w-full h-full" viewBox="0 0 176 176">
        <line x1="44" y1="44" x2="132" y2="132" stroke="currentColor" stroke-width="1" class="text-gray-700" />
        <line x1="132" y1="44" x2="44" y2="132" stroke="currentColor" stroke-width="1" class="text-gray-700" />
      </svg>
    </div>

    <!-- Ward circle (bottom-right) -->
    <div
      v-if="ward"
      class="absolute -bottom-2 -right-2 w-14 h-14 rounded-full bg-purple-900 border-2 border-purple-500 flex items-center justify-center"
    >
      <div class="text-center">
        <div class="text-[10px] text-purple-300 leading-none">Ward</div>
        <div class="text-lg font-bold text-purple-200 leading-none mt-0.5">{{ ward }}</div>
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
  },
  bottomLabel: {
    type: String,
    default: 'Control'
  }
})
</script>

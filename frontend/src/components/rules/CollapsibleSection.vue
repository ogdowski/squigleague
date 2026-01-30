<template>
  <div class="card">
    <button
      @click="$emit('toggle')"
      class="w-full flex items-center justify-between text-left"
    >
      <div class="flex items-center gap-2">
        <slot name="title-prefix"></slot>
        <h3 class="font-bold text-lg">{{ title }}</h3>
        <span v-if="count !== undefined" class="text-sm text-gray-500">({{ count }})</span>
      </div>
      <div class="flex items-center gap-2">
        <div v-if="loading" class="w-4 h-4 border-2 border-squig-yellow border-t-transparent rounded-full animate-spin"></div>
        <svg
          v-else
          :class="['w-5 h-5 transition-transform', expanded ? 'rotate-180' : '']"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </button>

    <div v-if="expanded && !loading" class="mt-4">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  count: {
    type: Number,
    default: undefined
  },
  expanded: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle'])
</script>

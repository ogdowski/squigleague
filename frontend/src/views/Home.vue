<template>
  <div class="max-w-4xl mx-auto">
    <div class="text-center mb-12">
      <h1 class="text-5xl font-bold text-squig-yellow mb-4">
        Squig League
      </h1>
      <p class="text-xl text-gray-300">
        Blind army list exchange for Age of Sigmar
      </p>
    </div>

    <div class="grid md:grid-cols-2 gap-8 mb-12">
      <div class="card">
        <h2 class="text-2xl font-bold mb-4">How It Works</h2>
        <ol class="space-y-3 text-gray-300">
          <li class="flex items-start">
            <span class="text-squig-yellow font-bold mr-2">1.</span>
            <span>First player uploads his list, he can't change it later</span>
          </li>
           <li class="flex items-start">
            <span class="text-squig-yellow font-bold mr-2">2.</span>
            <span>First player sends matchup link to second player</span>
          </li>
          <li class="flex items-start">
            <span class="text-squig-yellow font-bold mr-2">3.</span>
            <span>Second player submit their army list</span>
          </li>
          <li class="flex items-start">
            <span class="text-squig-yellow font-bold mr-2">4.</span>
            <span>Lists are revealed simultaneously with a random map</span>
          </li>
        </ol>
      </div>

      <div class="card">
        <h2 class="text-2xl font-bold mb-4">Features</h2>
        <ul class="space-y-3 text-gray-300">
          <li class="flex items-start">
            <span class="text-squig-yellow mr-2">✓</span>
            <span>Anonymous matchup creation (no account required)</span>
          </li>
          <li class="flex items-start">
            <span class="text-squig-yellow mr-2">✓</span>
            <span>Automatic map randomization</span>
          </li>
          <li class="flex items-start">
            <span class="text-squig-yellow mr-2">✓</span>
            <span>90-day matchup expiration</span>
          </li>
        </ul>
      </div>
    </div>

    <div class="text-center">
      <router-link to="/matchup/create" class="btn-primary text-xl px-8 py-4 inline-block">
        Create Your First Matchup
      </router-link>
    </div>
  </div>
</template>
<script setup lang="ts">
</script>
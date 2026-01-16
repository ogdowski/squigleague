<template>
  <div class="max-w-5xl mx-auto">
    <!-- Hero Section -->
    <div class="text-center mb-16">
      <h1 class="text-5xl font-bold text-squig-yellow mb-4">
        Squig League
      </h1>
      <p class="text-xl text-gray-300 max-w-2xl mx-auto">
        A toolset for Age of Sigmar players and tournament organizers.
        Manage leagues, exchange army lists safely, and more.
      </p>
    </div>

    <!-- Feature Cards -->
    <div class="grid md:grid-cols-3 gap-6 mb-12">
      <!-- Leagues Card -->
      <router-link to="/leagues" class="card hover:bg-gray-700 transition-colors group">
        <div class="text-4xl mb-4">
          <span class="text-squig-yellow">
            <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </span>
        </div>
        <h2 class="text-2xl font-bold mb-3 group-hover:text-squig-yellow transition-colors">Leagues</h2>
        <p class="text-gray-400 mb-4">
          Organize and manage competitive leagues with group phases, knockout brackets,
          and automated scoring. Track standings, schedule matches, and crown champions.
        </p>
        <span class="text-squig-yellow font-semibold inline-flex items-center">
          Browse Leagues
          <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </span>
      </router-link>

      <!-- Matchups Card -->
      <router-link to="/my-matchups" class="card hover:bg-gray-700 transition-colors group">
        <div class="text-4xl mb-4">
          <span class="text-squig-yellow">
            <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          </span>
        </div>
        <h2 class="text-2xl font-bold mb-3 group-hover:text-squig-yellow transition-colors">Matchups</h2>
        <p class="text-gray-400 mb-4">
          Safe blind army list exchange. Both players submit their lists secretly,
          then reveal simultaneously with a random map. No peeking, no cheating.
        </p>
        <span class="text-squig-yellow font-semibold inline-flex items-center">
          Create Matchup
          <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </span>
      </router-link>

      <!-- Coming Soon Card -->
      <div class="card bg-gray-800/50 border-dashed border-gray-600">
        <div class="text-4xl mb-4">
          <span class="text-gray-500">
            <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </span>
        </div>
        <h2 class="text-2xl font-bold mb-3 text-gray-500">Coming Soon</h2>
        <p class="text-gray-500 mb-4">
          Score tracker and game assistant for your Age of Sigmar battles.
        </p>
        <span class="text-gray-500 font-semibold">
          Stay Tuned
        </span>
      </div>
    </div>

    <!-- Quick Info Section -->
    <div class="card text-center">
      <h3 class="text-xl font-bold mb-4">Built for the Community</h3>
      <p class="text-gray-400 max-w-2xl mx-auto">
        Squig League is a free platform designed to make organizing and playing
        Age of Sigmar more enjoyable. Whether you're running a local league or
        just need a fair way to exchange lists before a game, we've got you covered.
      </p>
    </div>
  </div>
</template>

<script setup>
</script>

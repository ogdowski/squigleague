<template>
  <div
    ref="cardRef"
    class="share-card"
    :style="cardStyle"
  >
    <!-- Background -->
    <div class="card-bg"></div>

    <!-- Top accent line -->
    <div class="accent-line top" :style="{ height: scale(4) }"></div>
    <!-- Bottom accent line -->
    <div class="accent-line bottom" :style="{ height: scale(4) }"></div>

    <!-- Content -->
    <div class="card-content" :style="{ padding: scale(80) }">
      <!-- Header -->
      <div class="header" :style="{ marginBottom: scale(40) }">
        <div class="header-game" :style="{ fontSize: scale(44), marginBottom: scale(12) }">Age of Sigmar</div>
        <div class="header-label" :style="{ fontSize: scale(24), marginBottom: scale(4), letterSpacing: '0.15em' }">
          {{ t('matchups.battlePlan') }}
        </div>
        <div class="header-title" :style="{ fontSize: scale(48) }">{{ mapName }}</div>
      </div>

      <!-- VS Section -->
      <div class="vs-section" :style="{ gap: scale(40) }">
        <!-- Player 1 -->
        <div class="player">
          <div class="avatar-wrapper" :style="{ marginBottom: scale(20) }">
            <img
              v-if="player1Avatar"
              :src="player1Avatar"
              class="avatar"
              :style="{ width: scale(180), height: scale(180), borderWidth: scale(5) }"
              :alt="player1Name"
            />
            <div v-else class="avatar-placeholder" :style="{ width: scale(180), height: scale(180), borderWidth: scale(5) }">
              <svg class="avatar-icon" :style="{ width: scale(90), height: scale(90) }" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </div>
          </div>
          <div class="player-name" :style="{ fontSize: scale(48), marginBottom: scale(6), paddingBottom: scale(4) }">{{ player1Name }}</div>
          <div class="player-faction" :style="{ fontSize: scale(32), marginBottom: scale(20), paddingBottom: scale(4) }">{{ player1Faction }}</div>
          <div class="player-score" :class="{ winner: player1Score > player2Score }" :style="{ fontSize: scale(120) }">
            {{ player1Score }}
          </div>
        </div>

        <!-- VS divider -->
        <div class="vs-divider" :style="{ fontSize: scale(56) }">VS</div>

        <!-- Player 2 -->
        <div class="player">
          <div class="avatar-wrapper" :style="{ marginBottom: scale(20) }">
            <img
              v-if="player2Avatar"
              :src="player2Avatar"
              class="avatar"
              :style="{ width: scale(180), height: scale(180), borderWidth: scale(5) }"
              :alt="player2Name"
            />
            <div v-else class="avatar-placeholder" :style="{ width: scale(180), height: scale(180), borderWidth: scale(5) }">
              <svg class="avatar-icon" :style="{ width: scale(90), height: scale(90) }" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </div>
          </div>
          <div class="player-name" :style="{ fontSize: scale(48), marginBottom: scale(6), paddingBottom: scale(4) }">{{ player2Name }}</div>
          <div class="player-faction" :style="{ fontSize: scale(32), marginBottom: scale(20), paddingBottom: scale(4) }">{{ player2Faction }}</div>
          <div class="player-score" :class="{ winner: player2Score > player1Score }" :style="{ fontSize: scale(120) }">
            {{ player2Score }}
          </div>
        </div>
      </div>

      <!-- Footer with branding -->
      <div class="footer" :style="{ fontSize: scale(28), marginTop: scale(32) }">
        <span class="footer-squig">SQUIG</span> <span class="footer-league">LEAGUE</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  mapName: {
    type: String,
    required: true
  },
  player1Name: {
    type: String,
    required: true
  },
  player1Avatar: {
    type: String,
    default: null
  },
  player1Faction: {
    type: String,
    default: ''
  },
  player1Score: {
    type: Number,
    required: true
  },
  player2Name: {
    type: String,
    required: true
  },
  player2Avatar: {
    type: String,
    default: null
  },
  player2Faction: {
    type: String,
    default: ''
  },
  player2Score: {
    type: Number,
    required: true
  },
  size: {
    type: Number,
    default: 1080
  }
})

const cardRef = ref(null)

const scaleFactor = computed(() => props.size / 1080)

const scale = (value) => {
  return `${value * scaleFactor.value}px`
}

const cardStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`
}))

defineExpose({
  cardRef
})
</script>

<style scoped>
.share-card {
  position: relative;
  overflow: hidden;
  font-family: system-ui, -apple-system, sans-serif;
}

.card-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #111827 0%, #1f2937 50%, #111827 100%);
}

.accent-line {
  position: absolute;
  left: 0;
  width: 100%;
  background: linear-gradient(90deg, transparent 0%, #f59e0b 50%, transparent 100%);
}

.accent-line.top {
  top: 0;
}

.accent-line.bottom {
  bottom: 0;
}

.card-content {
  position: relative;
  z-index: 10;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
}

.header-game {
  color: #f59e0b;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.2em;
}

.header-label {
  color: #6b7280;
  font-weight: 500;
  text-transform: uppercase;
}

.header-title {
  color: #ffffff;
  font-weight: 700;
}

.vs-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.player {
  flex: 1;
  text-align: center;
  max-width: 42%;
}

.avatar-wrapper {
  display: flex;
  justify-content: center;
}

.avatar {
  border-radius: 50%;
  border-style: solid;
  border-color: #f59e0b;
  object-fit: cover;
}

.avatar-placeholder {
  border-radius: 50%;
  border-style: solid;
  border-color: #f59e0b;
  background-color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-icon {
  color: #6b7280;
}

.player-name {
  color: #ffffff;
  font-weight: 700;
  overflow: visible;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.2;
}

.player-faction {
  color: #f59e0b;
  font-weight: 500;
  overflow: visible;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.2;
}

.player-score {
  font-weight: 900;
  color: #ffffff;
  line-height: 1;
}

.player-score.winner {
  color: #4ade80;
}

.vs-divider {
  color: #6b7280;
  font-weight: 700;
}

.footer {
  text-align: center;
  font-weight: 700;
  letter-spacing: 0.1em;
}

.footer-squig {
  color: #f59e0b;
}

.footer-league {
  color: #ffffff;
}
</style>

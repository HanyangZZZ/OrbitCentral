<template>
  <section class="home-page-figma">
    <div class="home-top-bar">
      <div class="top-bar-left">
        <router-link to="/" class="brand-name">Orbit</router-link>
        <div class="location-chip">
          <span>Location</span>
          <svg class="location-pin-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z" stroke="#000" stroke-width="1.8" fill="none"/>
          </svg>
        </div>
      </div>
      <div class="top-bar-right">
        <router-link to="/leaderboard" class="nav-link">Leaderboard</router-link>
        <router-link to="/discover" class="nav-link">Discover</router-link>
        <router-link to="/settings/favorites" class="nav-link">Favorites</router-link>
        <div class="profile-wrapper" ref="profileWrapper">
          <div class="profile-icon" @click="profileOpen = !profileOpen">
            <img src="/figma-discovery-page/image_12_53x54.png" alt="" />
          </div>
          <div v-if="profileOpen" class="profile-dropdown">
            <router-link to="/settings" class="dropdown-item" @click="profileOpen = false">Account Settings</router-link>
          </div>
        </div>
      </div>
    </div>
    <div
      class="figma-frame-wrap"
      :style="{ height: (780 * figmaScale) + 'px' }"
    >
      <iframe
        class="figma-frame"
        src="/figma-home-page/index.html"
        title="Home page design"
        :style="{ transform: 'scale(' + figmaScale + ')' }"
      ></iframe>
    </div>

    <!-- ── Dynamic Gravity UI ── -->
    <section class="gravity-section">
      <div class="gravity-header">
        <h2 class="gravity-title">Nearby For You</h2>
        <p class="gravity-subtitle">✨ {{ aiSuggestion }}</p>
      </div>

      <div class="gravity-canvas" ref="gravityCanvas">
        <!-- Full orbit rings (circles) -->
        <svg class="orbit-rings" viewBox="-10 -10 520 520" preserveAspectRatio="xMidYMid meet">
          <circle v-for="i in orbitCount" :key="'ring-' + i"
            cx="250" cy="250"
            :r="55 + i * 40"
            class="orbit-ring"
          />
        </svg>

        <!-- User node at center -->
        <div class="gravity-user">
          <div class="user-glow"></div>
          <div class="user-dot">
            <span class="user-icon">📍</span>
          </div>
          <span class="user-label">You</span>
        </div>

        <!-- Businesses orbiting around -->
        <div class="orbit-items">
          <router-link
            v-for="biz in visibleBusinesses"
            :key="biz.id"
            :to="'/business/' + biz.slug"
            class="orbit-node"
            :style="biz.style"
            @mouseenter="pauseOrbit(biz)"
            @mouseleave="resumeOrbit(biz)"
          >
            <div class="orbit-dot" :style="{ width: biz.size + 'px', height: biz.size + 'px' }">
              <span class="orbit-emoji">{{ biz.emoji }}</span>
            </div>
            <span class="orbit-label">{{ biz.name }}</span>
          </router-link>
        </div>
      </div>

      <div class="gravity-context">
        <div class="context-chip">
          <span class="context-icon">🕐</span>
          <span>{{ currentTimeLabel }}</span>
        </div>
        <div class="context-chip">
          <span class="context-icon">📍</span>
          <span>{{ currentActivity }}</span>
        </div>
      </div>
    </section>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const profileOpen = ref(false)
const profileWrapper = ref(null)
const gravityCanvas = ref(null)

// ── Responsive iframe scaling ──
const figmaScale = ref(1)

function updateScale() {
  const vw = window.innerWidth
  figmaScale.value = vw < 1280 ? vw / 1280 : 1
}

function handleClickOutside(e) {
  if (profileWrapper.value && !profileWrapper.value.contains(e.target)) {
    profileOpen.value = false
  }
}

// ── Dynamic Gravity System ──
const currentHour = ref(new Date().getHours())
const orbitCount = 5

// Simulated business data pool
const allBusinesses = [
  // Morning (6-11): coffee, breakfast, bakeries
  { id: 1, name: 'Blue Bottle Coffee', slug: 'name-of-business', emoji: '☕', category: 'morning', weight: 0.95 },
  { id: 2, name: 'Sunrise Bakery', slug: 'name-of-business', emoji: '🥐', category: 'morning', weight: 0.88 },
  { id: 3, name: 'Matcha House', slug: 'name-of-business', emoji: '🍵', category: 'morning', weight: 0.82 },
  { id: 4, name: 'The Breakfast Club', slug: 'name-of-business', emoji: '🍳', category: 'morning', weight: 0.78 },
  { id: 5, name: 'Bean & Leaf', slug: 'name-of-business', emoji: '🫘', category: 'morning', weight: 0.70 },
  // Lunch (11-14): restaurants, delis
  { id: 6, name: 'Farm Table Bistro', slug: 'name-of-business', emoji: '🥗', category: 'lunch', weight: 0.94 },
  { id: 7, name: 'Poke Paradise', slug: 'name-of-business', emoji: '🍣', category: 'lunch', weight: 0.87 },
  { id: 8, name: 'Taco Loco', slug: 'name-of-business', emoji: '🌮', category: 'lunch', weight: 0.81 },
  { id: 9, name: 'Noodle Bar', slug: 'name-of-business', emoji: '🍜', category: 'lunch', weight: 0.75 },
  { id: 10, name: 'The Deli Counter', slug: 'name-of-business', emoji: '🥪', category: 'lunch', weight: 0.68 },
  // Afternoon (14-17): shopping, personal services
  { id: 11, name: 'Urban Outfitters', slug: 'name-of-business', emoji: '🛍️', category: 'afternoon', weight: 0.92 },
  { id: 12, name: 'Glow Spa', slug: 'name-of-business', emoji: '💆', category: 'afternoon', weight: 0.86 },
  { id: 13, name: 'Book Nook', slug: 'name-of-business', emoji: '📚', category: 'afternoon', weight: 0.79 },
  { id: 14, name: 'Plant Studio', slug: 'name-of-business', emoji: '🪴', category: 'afternoon', weight: 0.73 },
  { id: 15, name: 'Vintage Finds', slug: 'name-of-business', emoji: '🏺', category: 'afternoon', weight: 0.66 },
  // Evening (17-22): dinner, entertainment
  { id: 16, name: 'Ember Steakhouse', slug: 'name-of-business', emoji: '🥩', category: 'evening', weight: 0.96 },
  { id: 17, name: 'Moonlight Lounge', slug: 'name-of-business', emoji: '🍸', category: 'evening', weight: 0.89 },
  { id: 18, name: 'Regal Cinema', slug: 'name-of-business', emoji: '🎬', category: 'evening', weight: 0.83 },
  { id: 19, name: 'Pasta La Vista', slug: 'name-of-business', emoji: '🍝', category: 'evening', weight: 0.76 },
  { id: 20, name: 'Jazz Corner', slug: 'name-of-business', emoji: '🎷', category: 'evening', weight: 0.69 },
  // Night (22-6): late night
  { id: 21, name: '24hr Diner', slug: 'name-of-business', emoji: '🍔', category: 'night', weight: 0.91 },
  { id: 22, name: 'Night Owl Cafe', slug: 'name-of-business', emoji: '🦉', category: 'night', weight: 0.84 },
  { id: 23, name: 'Crescent Bar', slug: 'name-of-business', emoji: '🌙', category: 'night', weight: 0.77 },
  { id: 24, name: 'Late Bites', slug: 'name-of-business', emoji: '🌯', category: 'night', weight: 0.71 },
  { id: 25, name: 'Starlight Arcade', slug: 'name-of-business', emoji: '🕹️', category: 'night', weight: 0.64 },
]

const currentTimeCategory = computed(() => {
  const h = currentHour.value
  if (h >= 6 && h < 11) return 'morning'
  if (h >= 11 && h < 14) return 'lunch'
  if (h >= 14 && h < 17) return 'afternoon'
  if (h >= 17 && h < 22) return 'evening'
  return 'night'
})

const currentTimeLabel = computed(() => {
  const h = currentHour.value
  const ampm = h >= 12 ? 'PM' : 'AM'
  const h12 = h % 12 || 12
  const m = new Date().getMinutes().toString().padStart(2, '0')
  return `${h12}:${m} ${ampm}`
})

const currentActivity = computed(() => {
  const cat = currentTimeCategory.value
  if (cat === 'morning') return 'Morning commute'
  if (cat === 'lunch') return 'Lunch break'
  if (cat === 'afternoon') return 'Afternoon stroll'
  if (cat === 'evening') return 'Evening plans'
  return 'Late night'
})

// Proactive AI suggestion — context-aware, conversational
const aiSuggestion = computed(() => {
  const cat = currentTimeCategory.value
  const relevant = allBusinesses
    .filter(b => b.category === cat)
    .sort((a, b) => b.weight - a.weight)
  const top = relevant[0]?.name || 'a local spot'
  const second = relevant[1]?.name || 'somewhere new'

  if (cat === 'morning') {
    return `Good morning! ☀️ Looks like a great day to start with a warm drink at ${top} — and maybe a pastry from ${second} on the way?`
  }
  if (cat === 'lunch') {
    return `Hey, it's lunchtime! 🍽️ ${top} has been getting rave reviews lately. Or if you're in the mood for something lighter, ${second} is right nearby.`
  }
  if (cat === 'afternoon') {
    return `Good afternoon! It looks like it might rain later. 🌧️ How about visiting ${top}, followed by a relaxing stop at ${second}?`
  }
  if (cat === 'evening') {
    return `Good evening! 🌆 How about dinner at ${top}? You could follow it up with a visit to ${second} — perfect way to wind down.`
  }
  return `Still up? 🌙 ${top} is open late if you need a bite — or check out ${second} for some late-night vibes.`
})

// Position businesses on full circle orbits with rotation
const orbitAnimationOffset = ref(0)
const hoveredBizId = ref(null)
const frozenOffsets = ref({})       // animation offset at the moment of freeze
const angleAdjustments = ref({})    // cumulative base-angle shifts per biz id

const visibleBusinesses = computed(() => {
  const cat = currentTimeCategory.value
  const businesses = allBusinesses
    .filter(b => b.category === cat)
    .sort((a, b) => b.weight - a.weight)

  // Each business gets an orbit and starting angle
  const positions = [
    { orbitIdx: 1, baseAngle: 0 },    // closest orbit
    { orbitIdx: 2, baseAngle: 72 },   // second orbit
    { orbitIdx: 2, baseAngle: 216 },  // second orbit, opposite side
    { orbitIdx: 3, baseAngle: 144 },  // third orbit
    { orbitIdx: 3, baseAngle: 288 },  // third orbit, opposite side
  ]

  return businesses.slice(0, 5).map((biz, i) => {
    const pos = positions[i]
    const rotationSpeed = 1 / (pos.orbitIdx * 0.8 + 0.5)
    const adjust = angleAdjustments.value[biz.id] || 0

    let currentAngle
    if (hoveredBizId.value === biz.id && frozenOffsets.value[biz.id] !== undefined) {
      // Frozen: use the offset captured at hover time
      currentAngle = pos.baseAngle + adjust + (frozenOffsets.value[biz.id] * rotationSpeed)
    } else {
      // Moving: use the live animation offset
      currentAngle = pos.baseAngle + adjust + (orbitAnimationOffset.value * rotationSpeed)
    }

    const rad = (currentAngle * Math.PI) / 180
    const radius = 55 + pos.orbitIdx * 40
    const xPct = 50 + (radius * Math.cos(rad)) / 5
    const yPct = 50 + (radius * Math.sin(rad)) / 5

    const size = Math.round(52 - pos.orbitIdx * 6)

    return {
      ...biz,
      size,
      _i: i,
      orbitIdx: pos.orbitIdx,
      baseAngle: pos.baseAngle,
      style: {
        left: `${xPct}%`,
        top: `${yPct}%`,
        zIndex: 10 - pos.orbitIdx,
      }
    }
  })
})

// Handle category click from iframe
function handleCategoryMessage(e) {
  if (e.data && e.data.type === 'category-click' && e.data.category) {
    router.push({ path: '/discover', query: { category: e.data.category } })
  }
}

// Update time every minute
let timeInterval = null
let orbitAnimationFrame = null

function animateOrbits() {
  orbitAnimationOffset.value += 0.3
  orbitAnimationFrame = requestAnimationFrame(animateOrbits)
}

function pauseOrbit(biz) {
  // Snapshot the current animation offset so this icon stays put
  frozenOffsets.value[biz.id] = orbitAnimationOffset.value
  hoveredBizId.value = biz.id
}

function resumeOrbit(biz) {
  // Calculate how far the animation moved while this icon was frozen
  // and shift its base angle backwards by that amount so it resumes from here
  if (frozenOffsets.value[biz.id] !== undefined) {
    const rotationSpeed = 1 / (biz.orbitIdx * 0.8 + 0.5)
    const missedOffset = orbitAnimationOffset.value - frozenOffsets.value[biz.id]
    const missedAngle = missedOffset * rotationSpeed
    angleAdjustments.value[biz.id] = (angleAdjustments.value[biz.id] || 0) - missedAngle
  }
  delete frozenOffsets.value[biz.id]
  hoveredBizId.value = null
}

onMounted(() => {
  updateScale()
  window.addEventListener('resize', updateScale)
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('message', handleCategoryMessage)
  timeInterval = setInterval(() => {
    currentHour.value = new Date().getHours()
  }, 60000)
  // Start orbit animation
  animateOrbits()
})
onUnmounted(() => {
  window.removeEventListener('resize', updateScale)
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('message', handleCategoryMessage)
  if (timeInterval) clearInterval(timeInterval)
  if (orbitAnimationFrame) cancelAnimationFrame(orbitAnimationFrame)
})
</script>

<style scoped>
.home-page-figma {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  min-height: 100vh;
  padding: 0;
  background: white;
  overflow-x: hidden;
}

.home-top-bar {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1rem 0.75rem;
  gap: 0.75rem;
  position: relative;
  z-index: 2;
  flex-wrap: wrap;
  box-sizing: border-box;
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-name {
  font-family: 'Barlow', 'SF Pro', 'Inter', sans-serif;
  font-size: 1.125rem;
  font-weight: 500;
  color: #000;
  text-decoration: none;
  transition: font-weight 0.15s ease, text-shadow 0.15s ease;
}

.brand-name:hover {
  font-weight: 700;
  text-shadow: 0 1px 8px rgba(74, 112, 169, 0.3);
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.nav-link {
  display: none;
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 0.875rem;
  font-weight: 300;
  color: #000;
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
  transition: font-weight 0.15s ease, color 0.15s ease;
  padding-bottom: 2px;
  border-bottom: 2px solid transparent;
}

.nav-link:hover {
  font-weight: 600;
  color: #4a70a9;
  border-bottom-color: #4a70a9;
}

.location-chip {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 0.875rem;
  font-weight: 300;
  color: #000;
  white-space: nowrap;
}

.location-pin-icon {
  width: 1.125rem;
  height: 1.125rem;
  flex-shrink: 0;
}

.profile-wrapper {
  position: relative;
}

.profile-icon {
  cursor: pointer;
}

.profile-icon img {
  width: 2.25rem;
  height: 2.25rem;
  max-width: 100%;
  height: auto;
}

.profile-dropdown {
  position: absolute;
  top: calc(100% + 0.625rem);
  right: 0;
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.10);
  padding: 0.75rem 1.25rem;
  z-index: 100;
  white-space: nowrap;
  min-width: 10rem;
}

.dropdown-item {
  display: block;
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.8125rem;
  font-weight: 200;
  color: #000;
  text-decoration: none;
  cursor: pointer;
  transition: font-weight 0.15s ease, color 0.15s ease;
}

.dropdown-item:hover {
  font-weight: 500;
  color: #4a70a9;
}

.figma-frame-wrap {
  position: relative;
  width: 100%;
  max-width: 1280px;
  overflow: hidden;
  margin: 0 auto;
}

.figma-frame {
  width: 1280px;
  height: 780px;
  border: none;
  background: white;
  box-shadow: none;
  position: relative;
  z-index: 1;
  transform-origin: top left;
}

img {
  max-width: 100%;
  height: auto;
}

@media (min-width: 768px) {
  .nav-link { display: inline; }
  .home-top-bar {
    padding: 1.25rem 2rem 0.75rem;
    gap: 1rem;
    flex-wrap: nowrap;
  }
  .brand-name { font-size: 1.25rem; }
}

@media (min-width: 1024px) {
  .home-top-bar {
    padding: 1.5rem 5.25rem 0.75rem;
    gap: 1.5rem;
  }
  .brand-name { font-size: 1.375rem; }
  .top-bar-left { gap: 1.25rem; }
  .top-bar-right { gap: 1.5rem; }
}

/* ─── Dynamic Gravity Section ─── */
.gravity-section {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1.5rem 4rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: visible;
}

.gravity-header {
  text-align: center;
  margin-bottom: 2rem;
}

.gravity-title {
  font-family: 'Barlow', -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.75rem;
}

.gravity-subtitle {
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'Inter', sans-serif;
  font-size: 1rem;
  font-weight: 300;
  color: #64748b;
  line-height: 1.55;
  margin: 0;
  max-width: 520px;
}

.gravity-canvas {
  position: relative;
  width: 100%;
  max-width: 700px;
  aspect-ratio: 1 / 1;
  margin: 0 auto;
  overflow: visible;
}

.orbit-rings {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: visible;
  z-index: 1;
}

.orbit-ring {
  fill: none;
  stroke: #d4cfc5;
  stroke-width: 1.5;
  stroke-dasharray: 8 6;
  opacity: 0.85;
}

.orbit-items {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
  overflow: visible;
}

.orbit-node {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  text-decoration: none;
  cursor: pointer;
  transform: translate(-50%, -50%);
  transition: filter 0.3s ease;
}

.orbit-node:hover {
  filter: brightness(1.1);
  z-index: 50 !important;
}

.orbit-node:hover .orbit-dot {
  transform: scale(1.15);
}

.orbit-dot {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #efece3;
  border: 2px solid #d7d2c8;
  box-shadow: 0 4px 16px rgba(74, 112, 169, 0.15);
  transition: box-shadow 0.3s ease, border-color 0.3s ease, transform 0.3s ease;
}

.orbit-node:hover .orbit-dot {
  border-color: #4a70a9;
  box-shadow: 0 6px 24px rgba(74, 112, 169, 0.3);
}

.orbit-emoji {
  font-size: 1.5rem;
  line-height: 1;
}

.orbit-label {
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'Inter', sans-serif;
  font-size: 0.85rem;
  font-weight: 500;
  color: #0f172a;
  white-space: nowrap;
  text-align: center;
  max-width: 110px;
  overflow: hidden;
  text-overflow: ellipsis;
  background: rgba(255, 255, 255, 0.85);
  padding: 3px 8px;
  border-radius: 6px;
  backdrop-filter: blur(4px);
}

/* User node at center */
.gravity-user {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  z-index: 20;
}

.user-glow {
  position: absolute;
  width: 130px;
  height: 130px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(74, 112, 169, 0.3) 0%, transparent 70%);
  animation: pulse-glow 2.5s ease-in-out infinite;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

@keyframes pulse-glow {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.6; }
  50% { transform: translate(-50%, -50%) scale(1.4); opacity: 1; }
}

.user-dot {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #4a70a9;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(74, 112, 169, 0.4);
  position: relative;
  z-index: 2;
}

.user-icon {
  font-size: 1.5rem;
  filter: brightness(1.5);
}

.user-label {
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a70a9;
  letter-spacing: 0.03em;
}

/* Context chips */
.gravity-context {
  display: flex;
  gap: 0.75rem;
  margin-top: 2rem;
  flex-wrap: wrap;
  justify-content: center;
}

.context-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  background: #efece3;
  border-radius: 1.125rem;
  padding: 0.375rem 0.875rem;
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 0.8rem;
  font-weight: 400;
  color: #0f172a;
}

.context-icon {
  font-size: 0.9rem;
}

/* Transitions */
.gravity-fade-enter-active,
.gravity-fade-leave-active {
  transition: opacity 0.6s ease, transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
.gravity-fade-enter-from {
  opacity: 0;
  transform: translate(-50%, 0%) scale(0.5);
}
.gravity-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.3);
}

/* Responsive */
@media (max-width: 600px) {
  .gravity-title { font-size: 1.35rem; }
  .gravity-subtitle { font-size: 0.85rem; max-width: 320px; }
  .gravity-canvas { max-width: 380px; }
  .orbit-label { font-size: 0.65rem; max-width: 70px; padding: 2px 5px; }
  .orbit-emoji { font-size: 1.1rem; }
  .user-dot { width: 48px; height: 48px; }
  .user-glow { width: 90px; height: 90px; }
  .user-label { font-size: 0.75rem; }
}
</style>

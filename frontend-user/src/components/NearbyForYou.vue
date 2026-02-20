<!--
  NearbyForYou.vue — Personalised Recommendations Section
  ─────────────────────────────────────────────────────────────────────────────
  LARGEST COMPONENT (~780 lines). Shown on the Home page below the category
  grid. Combines an animated orbital visualisation with recommendation cards.

  DATA FLOW (see useNearbyForYou composable)
  1. Tries AI personalisation first → falls back to time-based search
  2. Detects user location (browser Geolocation API + reverse geocode)
  3. Displays "Why we picked these" context based on time of day

  VISUAL SECTIONS
  ┌──────────────────────────────────────────────────────────┐
  │  "Nearby For You"  header + location + refresh button    │
  ├──────────────────────────────────────────────────────────┤
  │  Orbital SVG animation       │  Recommendation cards     │
  │  (spinning ring of circles)  │  (swipeable card stack)   │
  ├──────────────────────────────────────────────────────────┤
  │  Loading skeleton (shown while fetching)                 │
  └──────────────────────────────────────────────────────────┘

  THE ORBIT ANIMATION
  • Animated with requestAnimationFrame (not CSS) for smooth 60fps.
  • Circles orbit an invisible centre; the featured business sits at centre.
  • Each circle represents a recommended business — clicking navigates there.

  MODULAR FLOW
    useNearbyForYou → businesses, location, loading, timeContext
    → this component animates + renders cards
    → clicking a card → router.push to /business/:id
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <section class="nearby-section">
    <div class="section-header">
      <div class="section-header-left">
        <h2 class="section-title">Nearby For You</h2>
        <span class="location-tag">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="location-icon">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
          {{ locationLabel || 'No Location Found' }}
        </span>
      </div>
      <button v-if="!loading" class="refresh-btn" @click="refresh" title="Refresh recommendations">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="23 4 23 10 17 10"></polyline>
          <polyline points="1 20 1 14 7 14"></polyline>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
        </svg>
      </button>
    </div>

    <!-- AI Message -->
    <div v-if="aiMessage && !loading" class="ai-message">
      <p class="message-text" v-html="formatMessage(aiMessage)"></p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="skeleton-message"></div>
      <div class="skeleton-orbit"></div>
      <div class="skeleton-grid">
        <div v-for="i in 3" :key="i" class="skeleton-card"></div>
      </div>
    </div>

    <!-- Location Prompt -->
    <div v-else-if="locationDenied && !hasRecommendations" class="location-prompt">
      <p>Enable location to get personalized recommendations near you</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="refresh">Try Again</button>
    </div>

    <!-- Orbit Visualization + Grid -->
    <template v-else-if="hasRecommendations">
      <!-- Semi-orbit visualization -->
      <div class="orbit-visualization">
        <svg :viewBox="`0 0 ${svgWidth} ${svgHeight}`" class="orbit-svg" preserveAspectRatio="xMidYMid meet">
          <defs>
            <clipPath :id="'avatar-clip'">
              <circle :cx="centerX" :cy="centerY" :r="avatarRadius - 2" />
            </clipPath>
          </defs>

          <!-- Concentric semi-circle arcs (dashed) — static -->
          <path
            v-for="(r, i) in orbitRadii"
            :key="'arc-' + i"
            :d="describeArc(centerX, centerY, r)"
            fill="none"
            :stroke="arcColors[i]"
            :stroke-width="1.2"
            stroke-dasharray="6 4"
            :opacity="0.35 + i * 0.1"
          />

          <!-- Business nodes — one per arc, inner = most recommended -->
          <g>
            <!-- Business nodes (3 max, one per orbit ring) -->
            <g
              v-for="(pos, i) in businessPositions"
              :key="'biz-' + i"
              class="orbit-node"
              :style="{ cursor: 'pointer', opacity: pos.opacity }"
              @click="goToBusiness(recommendations[i])"
            >
              <!-- Node circle (background / fallback color) -->
              <circle
                :cx="pos.x"
                :cy="pos.y"
                :r="nodeRadius"
                :fill="nodeColors[i]"
              />
              <!-- Inline clip path for this node -->
              <clipPath :id="'biz-clip-' + i">
                <circle :cx="pos.x" :cy="pos.y" :r="nodeRadius - 1" />
              </clipPath>
              <!-- Business photo (clipped) -->
              <image
                v-if="businessPhotoUrls[i]"
                :href="businessPhotoUrls[i]"
                :x="pos.x - nodeRadius + 1"
                :y="pos.y - nodeRadius + 1"
                :width="(nodeRadius - 1) * 2"
                :height="(nodeRadius - 1) * 2"
                :clip-path="`url(#biz-clip-${i})`"
                preserveAspectRatio="xMidYMid slice"
                class="biz-photo"
              />
              <!-- Subtle border ring -->
              <circle
                :cx="pos.x"
                :cy="pos.y"
                :r="nodeRadius"
                fill="none"
                stroke="white"
                stroke-width="2"
                opacity="0.7"
              />
              <!-- Fallback Initials (if no photo) -->
              <text
                v-if="!businessPhotoUrls[i]"
                :x="pos.x"
                :y="pos.y + 1"
                text-anchor="middle"
                dominant-baseline="central"
                fill="white"
                font-size="13"
                font-weight="700"
                font-family="var(--font-brand)"
              >{{ getInitials(recommendations[i]?.name) }}</text>

              <!-- Business name label -->
              <text
                :x="pos.x"
                :y="pos.y + nodeRadius + 16"
                text-anchor="middle"
                dominant-baseline="auto"
                fill="var(--color-text)"
                font-size="11.5"
                font-weight="600"
                font-family="var(--font-ui)"
                class="node-label"
              >{{ truncate(recommendations[i]?.name, 16) }}</text>

              <!-- Distance sub-label -->
              <text
                v-if="recommendations[i]?.distance_km"
                :x="pos.x"
                :y="pos.y + nodeRadius + 30"
                text-anchor="middle"
                dominant-baseline="auto"
                fill="var(--color-text-muted)"
                font-size="10"
                font-family="var(--font-ui)"
              >{{ formatDistance(recommendations[i].distance_km) }}</text>
            </g>
          </g>

          <!-- Center user avatar (stays fixed — not inside rotating group) -->
          <g class="user-node">
            <!-- Outer glow ring -->
            <circle
              :cx="centerX"
              :cy="centerY"
              :r="avatarRadius + 6"
              fill="none"
              stroke="var(--color-primary)"
              stroke-width="2"
              opacity="0.2"
            />
            <!-- Avatar background -->
            <circle
              :cx="centerX"
              :cy="centerY"
              :r="avatarRadius"
              fill="var(--color-primary)"
            />
            <!-- User photo (clipped) -->
            <image
              v-if="userAvatarUrl"
              :href="userAvatarUrl"
              :x="centerX - avatarRadius + 2"
              :y="centerY - avatarRadius + 2"
              :width="(avatarRadius - 2) * 2"
              :height="(avatarRadius - 2) * 2"
              :clip-path="'url(#avatar-clip)'"
              preserveAspectRatio="xMidYMid slice"
            />
            <!-- Fallback user icon -->
            <g v-else>
              <circle :cx="centerX" :cy="centerY - 4" r="8" fill="white" opacity="0.9" />
              <path
                :d="`M${centerX - 12},${centerY + 14} a16,16 0 0,1 24,0`"
                fill="white"
                opacity="0.9"
              />
            </g>
            <!-- "You" label -->
            <text
              :x="centerX"
              :y="centerY + avatarRadius + 18"
              text-anchor="middle"
              fill="var(--color-text)"
              font-size="12"
              font-weight="700"
              font-family="var(--font-brand)"
            >You</text>
          </g>
        </svg>
      </div>

      <!-- Recommendation Cards (top 3, matching orbit order) -->
      <div class="recommendations-grid">
        <router-link
          v-for="(biz, i) in recommendations.slice(0, 3)"
          :key="biz.id"
          :to="`/business/${biz.id}`"
          class="recommendation-card"
        >
          <div class="card-rank" :style="{ background: rankColors[i] }">{{ i + 1 }}</div>
          <div class="card-photo-wrapper">
            <img
              v-if="businessPhotoUrls[i]"
              :src="businessPhotoUrls[i]"
              :alt="biz.name"
              class="card-photo"
              @error="(e) => e.target.style.display = 'none'"
            />
            <div v-else class="card-photo-fallback" :style="{ background: rankColors[i] }">
              {{ getInitials(biz.name) }}
            </div>
          </div>
          <div class="card-content">
            <h3 class="card-name">{{ biz.name }}</h3>
            <div class="card-meta">
              <span v-if="biz.avg_rating" class="rating">
                {{ Number(biz.avg_rating).toFixed(1) }}
                <svg width="12" height="12" viewBox="0 0 24 24" fill="var(--color-primary)" stroke="none">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
              </span>
              <span v-if="biz.distance_km" class="distance">{{ formatDistance(biz.distance_km) }}</span>
              <span v-if="biz.category_name || biz.category_detail?.name" class="category">
                {{ biz.category_name || biz.category_detail?.name }}
              </span>
            </div>
            <p v-if="biz.description" class="card-desc">{{ truncate(biz.description, 80) }}</p>
          </div>
        </router-link>
      </div>
    </template>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>No recommendations available right now. Try again later!</p>
    </div>
  </section>
</template>

<script setup>
import { onMounted, onUnmounted, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useNearbyForYou } from '@/composables/useNearbyForYou'
import { getBusinessPhotoUrl } from '@/api/client'

const router = useRouter()

const {
  recommendations,
  aiMessage,
  locationLabel,
  loading,
  error,
  locationDenied,
  hasRecommendations,
  fetchRecommendations,
  user,
} = useNearbyForYou()

// ── SVG layout constants ─────────────────────────────────────────────────────
const svgWidth = 700
const svgHeight = 410
const centerX = svgWidth / 2
const centerY = svgHeight - 60  // user avatar near bottom, room for "You" label
const avatarRadius = 26
const nodeRadius = 22

// Three concentric arc radii
const orbitRadii = [120, 200, 280]
const arcColors = ['var(--color-primary)', 'var(--color-primary)', 'var(--color-primary)']

// Node colors for orbit visualization — subtle, professional tones
const nodeColors = ['#4a70a9', '#64748b', '#94a3b8']

// Rank badge colors — gold/silver/bronze inspired but UI-consistent
const rankColors = ['#4a70a9', '#64748b', '#94a3b8']

// ── Business photo URLs (from photo proxy API) ──────────────────────────────
const businessPhotoUrls = computed(() =>
  recommendations.value.slice(0, 3).map((biz) => {
    if (!biz?.id) return null
    return getBusinessPhotoUrl(biz.id, { maxHeight: 200 })
  })
)

// ── Animated positions — one business per arc ring ───────────────────────────
// Business 0 (most recommended) → inner arc (orbitRadii[0] = 120)
// Business 1                    → middle arc (orbitRadii[1] = 200)
// Business 2 (least)            → outer arc  (orbitRadii[2] = 280)
// Each node glides along its own semi-arc, fading at edges and teleporting.

const FADE_ZONE = 12 // degrees from each edge where fade begins
const MIN_ANGLE = 8
const MAX_ANGLE = 172

// One config per arc — arc index matches array index
const nodeConfigs = [
  { arc: 0, startAngle: 55,  speed: 4.2 },   // inner ring — #1 recommendation
  { arc: 1, startAngle: 95,  speed: 3.5 },   // middle ring — #2
  { arc: 2, startAngle: 130, speed: 2.8 },   // outer ring — #3
]

// Reactive animated state
const animatedNodes = ref(
  nodeConfigs.map(cfg => ({
    angle: cfg.startAngle,
    direction: 1,        // 1 = moving right (toward 170°), -1 = moving left
    opacity: 1,
  }))
)

let animFrameId = null
let lastTime = null

function animateOrbit(timestamp) {
  if (!lastTime) lastTime = timestamp
  const dt = (timestamp - lastTime) / 1000 // seconds
  lastTime = timestamp

  const count = Math.min(recommendations.value.length, 3)

  for (let i = 0; i < count; i++) {
    const cfg = nodeConfigs[i]
    const node = animatedNodes.value[i]

    // Advance angle
    node.angle += cfg.speed * node.direction * dt

    // Calculate opacity — fade near edges
    if (node.angle <= MIN_ANGLE + FADE_ZONE) {
      node.opacity = Math.max(0, (node.angle - MIN_ANGLE) / FADE_ZONE)
    } else if (node.angle >= MAX_ANGLE - FADE_ZONE) {
      node.opacity = Math.max(0, (MAX_ANGLE - node.angle) / FADE_ZONE)
    } else {
      node.opacity = 1
    }

    // When fully past the edge, teleport to the other side
    if (node.angle <= MIN_ANGLE) {
      node.angle = MAX_ANGLE
      node.opacity = 0
    } else if (node.angle >= MAX_ANGLE) {
      node.angle = MIN_ANGLE
      node.opacity = 0
    }
  }

  // Trigger reactivity
  animatedNodes.value = [...animatedNodes.value]
  animFrameId = requestAnimationFrame(animateOrbit)
}

// Compute pixel positions from animated angles
const businessPositions = computed(() => {
  const count = Math.min(recommendations.value.length, 3)
  if (count === 0) return []

  return animatedNodes.value.slice(0, count).map((node, i) => {
    const cfg = nodeConfigs[i]
    const rad = (node.angle * Math.PI) / 180
    const r = orbitRadii[cfg.arc]
    return {
      x: centerX - r * Math.cos(rad),
      y: centerY - r * Math.sin(rad),
      opacity: node.opacity,
    }
  })
})

// ── User avatar URL ──────────────────────────────────────────────────────────
const userAvatarUrl = computed(() => user.value?.avatar_url || null)

// ── Helpers ──────────────────────────────────────────────────────────────────
function describeArc(cx, cy, r) {
  // Semi-circle arc: from left to right above center
  const startX = cx - r
  const startY = cy
  const endX = cx + r
  const endY = cy
  return `M ${startX} ${startY} A ${r} ${r} 0 0 1 ${endX} ${endY}`
}

function getInitials(name) {
  if (!name) return '?'
  const words = name.trim().split(/\s+/)
  if (words.length === 1) return words[0].substring(0, 2).toUpperCase()
  return (words[0][0] + words[1][0]).toUpperCase()
}

function refresh() {
  fetchRecommendations()
}

function goToBusiness(biz) {
  if (biz?.id) router.push(`/business/${biz.id}`)
}

function formatDistance(km) {
  if (km < 1) return `${Math.round(km * 1000)}m`
  return `${km.toFixed(1)}km`
}

function truncate(text, len) {
  if (!text || text.length <= len) return text
  return text.slice(0, len).trim() + '…'
}

function formatMessage(msg) {
  return msg.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
}

onMounted(() => {
  fetchRecommendations()
  animFrameId = requestAnimationFrame(animateOrbit)
})

onUnmounted(() => {
  if (animFrameId) cancelAnimationFrame(animFrameId)
})
</script>

<style scoped>
.nearby-section {
  padding: 48px 24px 60px;
  max-width: 1200px;
  margin: 0 auto;
  border-top: 1px solid var(--color-border);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.location-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-muted);
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 20px;
  padding: 4px 12px 4px 8px;
}

.location-icon {
  flex-shrink: 0;
  color: var(--color-primary);
}

.refresh-btn {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.refresh-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

/* ── AI Message ── */
.ai-message {
  padding: 20px;
  background: linear-gradient(135deg, rgba(74, 112, 169, 0.06) 0%, rgba(67, 56, 202, 0.04) 100%);
  border: 1px solid var(--color-border-light, #c7d2fe);
  border-radius: 16px;
  margin-bottom: 32px;
}

.message-text {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
  color: var(--color-text);
}

.message-text :deep(strong) {
  color: var(--color-primary);
  font-weight: 600;
}

/* ── Orbit Visualization ── */
.orbit-visualization {
  display: flex;
  justify-content: center;
  margin-bottom: 36px;
  padding: 0 20px;
}

.orbit-svg {
  width: 100%;
  max-width: 700px;
  height: auto;
}

.orbit-node {
  transition: opacity 0.3s ease;
}

.orbit-node:hover circle {
  filter: brightness(1.15);
}

.orbit-node:hover .node-label {
  font-weight: 700;
}

.biz-photo {
  pointer-events: none;
}

.user-node circle {
  filter: drop-shadow(0 2px 8px rgba(74, 112, 169, 0.3));
}

/* ── Recommendation Cards (list style below orbit) ── */
.recommendations-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  text-decoration: none;
  color: inherit;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 16px 20px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.recommendation-card:hover {
  border-color: rgba(74, 112, 169, 0.4);
  box-shadow: var(--shadow-md);
}

.card-rank {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 700;
  font-family: var(--font-brand);
  margin-top: 14px;
}

.card-photo-wrapper {
  flex-shrink: 0;
  width: 52px;
  height: 52px;
  border-radius: 10px;
  overflow: hidden;
  background: var(--color-bg);
}

.card-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.card-photo-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-brand);
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 6px;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 6px;
}

.rating {
  display: flex;
  align-items: center;
  gap: 3px;
  font-weight: 600;
  color: var(--color-text);
}

.distance {
  color: var(--color-primary);
  font-weight: 500;
}

.category {
  opacity: 0.7;
}

.card-desc {
  font-size: 13px;
  color: var(--color-text-muted);
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ── Loading State ── */
.loading-state {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.skeleton-message {
  height: 80px;
  background: linear-gradient(90deg, var(--color-bg) 25%, var(--color-border) 50%, var(--color-bg) 75%);
  background-size: 200% 100%;
  border-radius: 16px;
  animation: shimmer 1.5s infinite;
}

.skeleton-orbit {
  height: 260px;
  max-width: 700px;
  margin: 0 auto;
  width: 100%;
  background: linear-gradient(90deg, var(--color-bg) 25%, var(--color-border) 50%, var(--color-bg) 75%);
  background-size: 200% 100%;
  border-radius: 16px;
  animation: shimmer 1.5s infinite;
}

.skeleton-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-card {
  height: 72px;
  background: linear-gradient(90deg, var(--color-bg) 25%, var(--color-border) 50%, var(--color-bg) 75%);
  background-size: 200% 100%;
  border-radius: 12px;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ── Other States ── */
.location-prompt,
.error-state,
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--color-text-muted);
}

.retry-btn {
  margin-top: 12px;
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.retry-btn:hover {
  background: var(--color-primary-hover);
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .section-header-left {
    flex-direction: column;
    gap: 2px;
  }

  .section-title {
    font-size: 20px;
  }

  .orbit-visualization {
    padding: 0;
  }

  .recommendation-card {
    padding: 14px 16px;
  }
}

@media (max-width: 480px) {
  .nearby-section {
    padding: 32px 16px 48px;
  }

  .recommendations-grid {
    gap: 10px;
  }

  .card-meta {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>

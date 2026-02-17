<template>
  <section class="business-details-figma">
    <TopBar :show-search="true" v-model:ai-enabled="aiEnabled">
      <template #right-extra>
        <!-- Mobile hamburger menu -->
        <button class="mobile-menu-btn" @click="mobileMenuOpen = !mobileMenuOpen" aria-label="Menu">
          <svg v-if="!mobileMenuOpen" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 6h18M3 12h18M3 18h18" stroke="#000" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M6 6l12 12M6 18L18 6" stroke="#000" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </template>
    </TopBar>

    <!-- Mobile dropdown menu -->
    <Transition name="mobile-menu">
      <div v-if="mobileMenuOpen" class="mobile-menu-dropdown">
        <router-link to="/leaderboard" class="mobile-menu-link" @click="mobileMenuOpen = false">Leaderboard</router-link>
        <router-link to="/discover" class="mobile-menu-link" @click="mobileMenuOpen = false">Discover</router-link>
        <router-link to="/settings/favorites" class="mobile-menu-link" @click="mobileMenuOpen = false">Favorites</router-link>
        <router-link to="/settings" class="mobile-menu-link" @click="mobileMenuOpen = false">Settings</router-link>
      </div>
    </Transition>

    <div
      class="figma-frame-wrap"
      ref="figmaWrapRef"
      :style="{ height: (1600 * figmaScale - 210) + 'px' }"
    >
      <div class="figma-inner" :style="{ transform: 'scale(' + figmaScale + ')', marginTop: (-100 * figmaScale) + 'px' }">
        <div class="figma-overlay" aria-hidden="true">
        <div class="business-name-overlay">Business Name</div>
        <div class="star-rating-overlay">
          <svg v-for="n in 5" :key="n" class="star-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill="#E8B931" stroke="#E8B931" stroke-width="0.5"/>
          </svg>
        </div>
        <!-- Clickable overlay on the iframe "Write a Review" button -->
        <button class="write-review-overlay-btn" @click="openReviewModal">
          Write a Review
        </button>
      </div>
      <iframe
        class="figma-frame"
        src="/figma-business-details-page/index.html"
        title="Business details design"
      ></iframe>
      </div><!-- .figma-inner -->
    </div>

    <!-- ─── Review Modal ─── -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="showModal" class="review-modal-backdrop" @click.self="closeModal">
          <div class="review-modal">
            <!-- Close button -->
            <button class="modal-close" @click="closeModal" aria-label="Close">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="#666" stroke-width="2" stroke-linecap="round"/></svg>
            </button>

            <!-- Step 1: Star Rating -->
            <div v-if="step === 1" class="modal-step">
              <div class="modal-header">
                <div class="modal-icon">
                  <svg width="32" height="32" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill="#E8B931" stroke="#E8B931" stroke-width="0.5"/></svg>
                </div>
                <h2 class="modal-title">How was your experience?</h2>
                <p class="modal-subtitle">Rate Business Name to get started</p>
              </div>
              <div class="star-selector">
                <svg
                  v-for="n in 5"
                  :key="n"
                  class="star-select"
                  :class="{ filled: n <= userRating, hover: n <= hoverRating }"
                  viewBox="0 0 24 24"
                  @mouseenter="hoverRating = n"
                  @mouseleave="hoverRating = 0"
                  @click="userRating = n"
                >
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </div>
              <p class="rating-label">{{ ratingLabel }}</p>
              <button class="modal-btn primary" :disabled="userRating === 0" @click="step = 2">Continue</button>
            </div>

            <!-- Step 2: AI Questions -->
            <div v-if="step === 2" class="modal-step">
              <div class="modal-header">
                <div class="modal-icon ai-icon">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none"><path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z" stroke="#4A70A9" stroke-width="1.8"/><path d="M9 21h6M10 17v2M14 17v2" stroke="#4A70A9" stroke-width="1.8" stroke-linecap="round"/></svg>
                </div>
                <h2 class="modal-title">Tell us more!</h2>
                <p class="modal-subtitle">Answer a few quick questions &mdash; our AI will craft your review.</p>
              </div>
              <div class="question-card">
                <p class="question-number">Question {{ currentQ + 1 }} of {{ questions.length }}</p>
                <p class="question-text">{{ questions[currentQ] }}</p>
                <textarea
                  v-model="answers[currentQ]"
                  class="answer-input"
                  :placeholder="placeholders[currentQ]"
                  rows="3"
                ></textarea>
              </div>
              <div class="question-nav">
                <button v-if="currentQ > 0" class="modal-btn secondary" @click="currentQ--">Back</button>
                <button
                  v-if="currentQ < questions.length - 1"
                  class="modal-btn primary"
                  :disabled="!answers[currentQ]?.trim()"
                  @click="currentQ++"
                >Next</button>
                <button
                  v-else
                  class="modal-btn primary"
                  :disabled="!answers[currentQ]?.trim()"
                  @click="generateReview"
                >
                  <span v-if="!generating">Generate Review</span>
                  <span v-else class="loading-dots">Generating<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></span>
                </button>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: ((currentQ + 1) / questions.length * 100) + '%' }"></div>
              </div>
            </div>

            <!-- Step 3: Generated Review + Edit -->
            <div v-if="step === 3" class="modal-step">
              <div class="modal-header">
                <div class="modal-icon">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="#4A70A9" stroke-width="1.8" stroke-linecap="round"/><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="#4A70A9" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </div>
                <h2 class="modal-title">Your AI-crafted review</h2>
                <p class="modal-subtitle">Feel free to edit before submitting.</p>
              </div>
              <textarea v-model="generatedReview" class="review-edit-area" rows="6"></textarea>
              <div class="vibe-tags-section">
                <p class="vibe-label">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" stroke="#4A70A9" stroke-width="2"/><circle cx="7" cy="7" r="1" fill="#4A70A9"/></svg>
                  Vibe Tags
                </p>
                <div class="vibe-tags">
                  <span v-for="tag in vibeTags" :key="tag" class="vibe-tag">{{ tag }}</span>
                </div>
              </div>
              <button class="modal-btn primary" @click="submitReview">Submit Review</button>
            </div>

            <!-- Step 4: Success + Points -->
            <div v-if="step === 4" class="modal-step success-step">
              <div class="success-icon-wrap">
                <svg width="56" height="56" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" fill="#4A70A9" opacity="0.1"/>
                  <circle cx="12" cy="12" r="10" stroke="#4A70A9" stroke-width="1.5"/>
                  <path d="M8 12l2.5 2.5L16 9" stroke="#4A70A9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <h2 class="modal-title">Review submitted!</h2>
              <p class="modal-subtitle">Thank you for sharing your experience.</p>
              <div class="points-card">
                <div class="points-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="#E8B931" stroke="#E8B931" stroke-width="0.5"/></svg>
                </div>
                <div class="points-info">
                  <span class="points-earned">+{{ pointsEarned }} Points</span>
                  <span class="points-desc">Earned for your review</span>
                </div>
              </div>
              <div v-if="vibeTags.length" class="vibe-tags-section">
                <p class="vibe-label">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" stroke="#4A70A9" stroke-width="2"/><circle cx="7" cy="7" r="1" fill="#4A70A9"/></svg>
                  Generated Vibe Tags
                </p>
                <div class="vibe-tags">
                  <span v-for="tag in vibeTags" :key="tag" class="vibe-tag">{{ tag }}</span>
                </div>
              </div>
              <button class="modal-btn primary" @click="closeModal">Done</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { TopBar } from '@/components'
import { useResponsiveScale } from '@/composables'

const aiEnabled = ref(false)

// ── Mobile menu ──
const mobileMenuOpen = ref(false)

// ── Responsive iframe scaling (via composable) ──
const figmaWrapRef = ref(null)
const { scale: figmaScale } = useResponsiveScale(1280)

// ── Modal state ──
const showModal = ref(false)
const step = ref(1)
const userRating = ref(0)
const hoverRating = ref(0)
const currentQ = ref(0)
const generating = ref(false)
const generatedReview = ref('')
const vibeTags = ref([])
const pointsEarned = ref(0)

const ratingLabels = ['', 'Terrible', 'Poor', 'Average', 'Good', 'Excellent']
const ratingLabel = computed(() => ratingLabels[userRating.value] || '')

// AI-style personalised questions
const questions = [
  'What brought you here and what did you enjoy most?',
  'How was the atmosphere and overall vibe?',
  'How would you describe the service or staff?',
  'Would you recommend this place? Who would love it?'
]
const placeholders = [
  'e.g. "Great coffee and the pastries were amazing"',
  'e.g. "Cozy, quiet, good for studying"',
  'e.g. "Super friendly, fast service"',
  'e.g. "Definitely! Perfect for remote workers and couples"'
]
const answers = ref(['', '', '', ''])

function openReviewModal() {
  showModal.value = true
  step.value = 1
  userRating.value = 0
  hoverRating.value = 0
  currentQ.value = 0
  generating.value = false
  generatedReview.value = ''
  vibeTags.value = []
  answers.value = ['', '', '', '']
  pointsEarned.value = 0
}

function closeModal() {
  showModal.value = false
}

function generateReview() {
  generating.value = true

  // Simulate AI processing delay
  setTimeout(() => {
    const [enjoy, vibe, service, recommend] = answers.value

    // ── Build a natural-sounding review from the answers ──
    const ratingAdj = ['', 'disappointing', 'below-average', 'decent', 'great', 'outstanding'][userRating.value]
    let review = `I had a${userRating.value >= 4 ? 'n ' + ratingAdj : ' ' + ratingAdj} experience at Business Name. `

    if (enjoy.trim()) {
      review += enjoy.trim().endsWith('.') ? enjoy.trim() + ' ' : enjoy.trim() + '. '
    }
    if (vibe.trim()) {
      review += `The atmosphere was ${vibe.trim().toLowerCase()}${vibe.trim().endsWith('.') ? ' ' : '. '}`
    }
    if (service.trim()) {
      review += `As for the service, ${service.trim().toLowerCase()}${service.trim().endsWith('.') ? ' ' : '. '}`
    }
    if (recommend.trim()) {
      review += recommend.trim().endsWith('.') ? recommend.trim() : recommend.trim() + '.'
    }

    generatedReview.value = review.trim()

    // ── Generate vibe tags from answers ──
    const allText = answers.value.join(' ').toLowerCase()
    const tagMap = {
      'Quiet': ['quiet', 'peaceful', 'calm', 'silent', 'chill', 'relaxing'],
      'Pet-Friendly': ['pet', 'dog', 'cat', 'animal'],
      'Cozy': ['cozy', 'cosy', 'warm', 'comfortable', 'homey', 'homely'],
      'Good for Groups': ['group', 'friends', 'party', 'family', 'families'],
      'Great Coffee': ['coffee', 'latte', 'espresso', 'cappuccino', 'brew'],
      'Outdoor Seating': ['outdoor', 'patio', 'terrace', 'outside', 'garden'],
      'Fast Service': ['fast', 'quick', 'speedy', 'efficient', 'prompt'],
      'Friendly Staff': ['friendly', 'nice', 'kind', 'welcoming', 'helpful', 'warm staff'],
      'Work-Friendly': ['work', 'laptop', 'wifi', 'remote', 'study', 'studying', 'productive'],
      'Romantic': ['date', 'romantic', 'couple', 'intimate', 'candlelit'],
      'Great Food': ['food', 'delicious', 'tasty', 'yummy', 'amazing food', 'pastry', 'pastries', 'meal'],
      'Affordable': ['affordable', 'cheap', 'value', 'budget', 'reasonable'],
      'Instagrammable': ['instagram', 'photo', 'aesthetic', 'pretty', 'beautiful', 'cute decor'],
      'Live Music': ['music', 'live', 'band', 'jazz', 'acoustic'],
      'Kid-Friendly': ['kid', 'child', 'children', 'family-friendly']
    }

    const tags = []
    for (const [tag, keywords] of Object.entries(tagMap)) {
      if (keywords.some(kw => allText.includes(kw))) {
        tags.push(tag)
      }
    }
    // Always add at least one tag based on rating
    if (tags.length === 0) {
      if (userRating.value >= 4) tags.push('Highly Rated')
      else if (userRating.value === 3) tags.push('Average')
      else tags.push('Needs Improvement')
    }

    vibeTags.value = tags.slice(0, 5)
    generating.value = false
    step.value = 3
  }, 1500)
}

function submitReview() {
  // Calculate points: base 50 + 10 per answer + 25 bonus if all answered
  let pts = 50
  answers.value.forEach(a => { if (a.trim()) pts += 10 })
  if (answers.value.every(a => a.trim())) pts += 25
  pointsEarned.value = pts
  step.value = 4
}
</script>

<style scoped>
/* ─── Base / Mobile-first ─── */
.business-details-figma {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  min-height: 100vh;
  padding: 0;
  background: white;
  overflow-x: hidden;
}

/* ─── Mobile Menu ─── */
.mobile-menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
}

.mobile-menu-btn svg {
  width: 1.5rem;
  height: 1.5rem;
}

@media (min-width: 768px) {
  .mobile-menu-btn { display: none; }
}

.mobile-menu-dropdown {
  width: 100%;
  background: #fff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  z-index: 100;
}

.mobile-menu-link {
  font-family: 'SF Pro', 'Inter', sans-serif;
  font-size: 1rem;
  font-weight: 400;
  color: #000;
  text-decoration: none;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  transition: background 0.15s ease;
}

.mobile-menu-link:hover {
  background: #f5f5f5;
}

/* Mobile menu transition */
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/*
  The iframe content is a fixed 1280×1600 Figma export.
  The wrapper is fluid; the inner container is scaled.
  Overlay elements are positioned in the same coordinate space
  so they scale together with the iframe.
*/
.figma-frame-wrap {
  position: relative;
  width: 100%;
  max-width: 1280px;
  overflow: hidden;
  margin: 0 auto;
}

.figma-inner {
  position: relative;
  width: 1280px;
  transform-origin: top left;
}

.figma-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 3;
}

.business-name-overlay {
  position: absolute;
  left: 228px;
  top: 197px;
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text',
    'Helvetica Neue', Arial, sans-serif;
  font-size: 24px;
  font-weight: 500;
  line-height: 16px;
  color: #000;
}

.star-rating-overlay {
  position: absolute;
  left: 228px;
  top: 225px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.star-icon {
  width: 28px;
  height: 28px;
}

/* Write a Review overlay button — positioned over the iframe button */
.write-review-overlay-btn {
  position: absolute;
  left: 739px;
  top: 293px;
  width: 239px;
  height: 54px;
  background: #4A70A9;
  border: none;
  border-radius: 9px;
  color: #fff;
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 20px;
  font-weight: 500;
  cursor: pointer;
  pointer-events: auto;
  z-index: 4;
  transition: background 0.2s ease, transform 0.15s ease;
}
.write-review-overlay-btn:hover {
  background: #3b5e94;
  transform: scale(1.02);
}
.write-review-overlay-btn:active {
  transform: scale(0.98);
}

.figma-frame {
  width: 1280px;
  height: 1600px;
  border: none;
  background: white;
  box-shadow: none;
  position: relative;
  z-index: 1;
}

/* ─── Modal Styles ─── */
.review-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  padding: 1rem;
}

.review-modal {
  position: relative;
  background: #fff;
  border-radius: 1.25rem;
  width: 100%;
  max-width: 32.5rem;
  max-height: 90vh;
  overflow-y: auto;
  padding: 2rem 1.5rem 1.5rem;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.18), 0 0 0 1px rgba(0, 0, 0, 0.04);
  animation: modal-pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modal-pop {
  0% { opacity: 0; transform: scale(0.92) translateY(16px); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: #f5f5f5;
  border: none;
  border-radius: 50%;
  width: 2.25rem;
  height: 2.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s;
}
.modal-close:hover {
  background: #e8e8e8;
}

.modal-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
}

.modal-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  text-align: center;
}

.modal-icon {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 1rem;
  background: #EFECE3;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.25rem;
}

.ai-icon {
  background: linear-gradient(135deg, #E8EEF6, #EFECE3);
}

.modal-title {
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.modal-subtitle {
  font-family: 'SF Pro', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
  font-size: 0.875rem;
  font-weight: 400;
  color: #888;
  margin: 0;
}

/* Star selector */
.star-selector {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem 0;
}

.star-select {
  width: 2.5rem;
  height: 2.5rem;
  cursor: pointer;
  fill: #ddd;
  stroke: #ccc;
  stroke-width: 0.5;
  transition: fill 0.15s, transform 0.15s;
}
.star-select.filled,
.star-select.hover {
  fill: #E8B931;
  stroke: #E8B931;
}
.star-select:hover {
  transform: scale(1.15);
}

.rating-label {
  font-family: 'SF Pro', sans-serif;
  font-size: 0.9375rem;
  font-weight: 500;
  color: #4A70A9;
  min-height: 1.375rem;
  margin: 0;
}

/* Question card */
.question-card {
  width: 100%;
  background: #FAFAF8;
  border-radius: 0.875rem;
  padding: 1.25rem;
  border: 1px solid #EFECE3;
  box-sizing: border-box;
}

.question-number {
  font-family: 'SF Pro', sans-serif;
  font-size: 0.75rem;
  font-weight: 500;
  color: #4A70A9;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  margin: 0 0 0.5rem;
}

.question-text {
  font-family: 'SF Pro', sans-serif;
  font-size: 1rem;
  font-weight: 500;
  color: #1a1a1a;
  margin: 0 0 0.875rem;
  line-height: 1.45;
}

.answer-input {
  width: 100%;
  border: 1.5px solid #e0ddd4;
  border-radius: 0.625rem;
  padding: 0.75rem 0.875rem;
  font-family: 'SF Pro', sans-serif;
  font-size: 0.875rem;
  color: #1a1a1a;
  background: #fff;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}
.answer-input:focus {
  border-color: #4A70A9;
}
.answer-input::placeholder {
  color: #bbb;
}

.question-nav {
  display: flex;
  gap: 0.75rem;
  width: 100%;
}

.progress-bar {
  width: 100%;
  height: 0.25rem;
  background: #EFECE3;
  border-radius: 0.25rem;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: #4A70A9;
  border-radius: 0.25rem;
  transition: width 0.3s ease;
}

/* Buttons */
.modal-btn {
  flex: 1;
  padding: 0.875rem 1.5rem;
  border-radius: 0.75rem;
  font-family: 'SF Pro', sans-serif;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: background 0.2s, opacity 0.2s, transform 0.15s;
}
.modal-btn:active {
  transform: scale(0.97);
}
.modal-btn.primary {
  background: #4A70A9;
  color: #fff;
}
.modal-btn.primary:hover:not(:disabled) {
  background: #3b5e94;
}
.modal-btn.primary:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.modal-btn.secondary {
  background: #EFECE3;
  color: #333;
}
.modal-btn.secondary:hover {
  background: #e4e0d6;
}

/* Review edit area */
.review-edit-area {
  width: 100%;
  border: 1.5px solid #e0ddd4;
  border-radius: 0.75rem;
  padding: 1rem;
  font-family: 'SF Pro', sans-serif;
  font-size: 0.875rem;
  line-height: 1.6;
  color: #1a1a1a;
  background: #FAFAF8;
  resize: vertical;
  outline: none;
  box-sizing: border-box;
}
.review-edit-area:focus {
  border-color: #4A70A9;
}

/* Vibe tags */
.vibe-tags-section {
  width: 100%;
}

.vibe-label {
  font-family: 'SF Pro', sans-serif;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #555;
  margin: 0 0 0.625rem;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.vibe-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.vibe-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.875rem;
  background: linear-gradient(135deg, #E8EEF6, #EFECE3);
  border-radius: 1.25rem;
  font-family: 'SF Pro', sans-serif;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #4A70A9;
  border: 1px solid rgba(74, 112, 169, 0.15);
}

/* Success step */
.success-step {
  gap: 1rem;
}

.success-icon-wrap {
  animation: pop-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes pop-in {
  0% { opacity: 0; transform: scale(0.5); }
  100% { opacity: 1; transform: scale(1); }
}

.points-card {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  background: linear-gradient(135deg, #FFF9E6, #FFF4CC);
  border: 1px solid #E8B931;
  border-radius: 0.875rem;
  padding: 1rem 1.25rem;
  width: 100%;
  animation: slide-up 0.4s ease;
  box-sizing: border-box;
}

@keyframes slide-up {
  0% { opacity: 0; transform: translateY(12px); }
  100% { opacity: 1; transform: translateY(0); }
}

.points-icon {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.75rem;
  background: rgba(232, 185, 49, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.points-info {
  display: flex;
  flex-direction: column;
}

.points-earned {
  font-family: 'SF Pro', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: #B8860B;
}

.points-desc {
  font-family: 'SF Pro', sans-serif;
  font-size: 0.8125rem;
  font-weight: 400;
  color: #997A1F;
}

/* Loading dots */
.loading-dots .dot {
  animation: blink 1.4s infinite;
}
.loading-dots .dot:nth-child(2) { animation-delay: 0.2s; }
.loading-dots .dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 20% { opacity: 1; }
  50% { opacity: 0; }
  100% { opacity: 1; }
}

/* Modal transitions */
.modal-fade-enter-active {
  transition: opacity 0.25s ease;
}
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* ─── Responsive images ─── */
img {
  max-width: 100%;
  height: auto;
}

/* ─── Desktop modal bump ─── */
@media (min-width: 768px) {
  .review-modal {
    padding: 2.5rem 2.25rem 2rem;
  }
  .modal-title {
    font-size: 1.375rem;
  }
}
</style>

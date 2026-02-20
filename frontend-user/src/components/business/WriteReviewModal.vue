<!--
  WriteReviewModal.vue — AI-Assisted Review Writing Modal
  ─────────────────────────────────────────────────────────────────────────────
  COMPLEX COMPONENT (~885 lines). Opens from the BusinessDetail page's
  "Write a Review" button. Guides users through writing a review via an
  AI chat conversation.

  STATE MACHINE FLOW
  ┌─────────┐   start   ┌──────────┐  messages  ┌──────────┐
  │  idle   │ ────────→ │  chat    │ ──────────→│ preview  │
  └─────────┘           └──────────┘             └──────────┘
                              ↕                       │
                         user sends messages      confirm → POST review
                         AI replies with           abandon → back to chat
                         follow-up questions

  AI REVIEW API SEQUENCE
  1. startAiReview(businessId)     → creates a session
  2. sendAiMessage(sessionId, msg) → AI responds with questions
  3. generateAiReview(sessionId)   → AI drafts a full review
  4. confirmAiReview(sessionId)    → saves the review to the backend
     OR abandonAiReview(sessionId) → discards the session

  VISUAL SECTIONS
  • Chat area with message bubbles (user = right, AI = left)
  • Star rating picker (StarRating component in interactive mode)
  • Photo upload with drag-and-drop support
  • Preview card showing the generated review before submission
  • Typing indicator animation while AI is responding

  MODULAR FLOW
    BusinessDetailPage opens modal via v-model → user interacts with chat
    → API calls to aiReviews module → on confirm, emits 'review-submitted'
    → BusinessDetailPage refreshes the reviews list.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <Transition name="modal-fade">
    <div v-if="modelValue" class="review-modal-backdrop" @click.self="handleClose">
      <div class="review-modal">
        <!-- Close Button -->
        <button class="modal-close" @click="handleClose">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2.5">
            <path d="M18 6 6 18M6 6l12 12"/>
          </svg>
        </button>

        <!-- ─── Compact header ─── -->
        <div class="modal-top">
          <div class="modal-icon ai-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4A70A9" stroke-width="2">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1.27c.34-.6.99-1 1.73-1a2 2 0 1 1 0 4c-.74 0-1.39-.4-1.73-1H21a7 7 0 0 1-7 7v1.27c.6.34 1 .99 1 1.73a2 2 0 1 1-4 0c0-.74.4-1.39 1-1.73V23a7 7 0 0 1-7-7H3.73c-.34.6-.99 1-1.73 1a2 2 0 1 1 0-4c.74 0 1.39.4 1.73 1H5a7 7 0 0 1 7-7V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"/>
            </svg>
          </div>
          <div>
            <h2 class="modal-title">Write a Review</h2>
            <p class="modal-subtitle">Chat with AI to craft your review</p>
          </div>
        </div>

        <!-- ─── Star rating bar (always visible until published) ─── -->
        <div v-if="!published" class="rating-bar">
          <span class="rating-bar-label">Your rating</span>
          <div class="star-selector">
            <svg
              v-for="n in 5" :key="n"
              class="star-select"
              :class="{ filled: n <= rating, hover: n <= hoverRating && hoverRating > 0 }"
              viewBox="0 0 24 24"
              @mouseenter="hoverRating = n"
              @mouseleave="hoverRating = 0"
              @click="selectRating(n)"
            >
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          </div>
          <span class="rating-label">{{ ratingLabel }}</span>
        </div>

        <!-- ─── Conversation area ─── -->
        <div class="chat-messages" ref="chatContainer">

          <!-- Placeholder before session starts -->
          <div v-if="!sessionId && !aiTyping" class="chat-empty">
            <p>Select a star rating above to begin chatting with our AI assistant.</p>
          </div>

          <!-- Chat bubbles -->
          <div
            v-for="(msg, i) in visibleMessages"
            :key="i"
            class="chat-bubble"
            :class="msg.role"
          >
            <div v-if="msg.role === 'assistant'" class="bubble-avatar">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4A70A9" stroke-width="2.5">
                <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1.27c.34-.6.99-1 1.73-1a2 2 0 1 1 0 4c-.74 0-1.39-.4-1.73-1H21a7 7 0 0 1-7 7v1.27c.6.34 1 .99 1 1.73a2 2 0 1 1-4 0c0-.74.4-1.39 1-1.73V23a7 7 0 0 1-7-7H3.73c-.34.6-.99 1-1.73 1a2 2 0 1 1 0-4c.74 0 1.39.4 1.73 1H5a7 7 0 0 1 7-7V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"/>
              </svg>
            </div>
            <div class="bubble-content">{{ msg.content }}</div>
          </div>

          <!-- Generated review card (inline in chat) -->
          <div v-if="generatedDescription" class="review-card-wrap">
            <div class="review-card">
              <div class="review-card-head">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4A70A9" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                <span>Your AI-crafted review</span>
              </div>
              <textarea
                v-model="generatedDescription"
                class="review-edit-area"
                rows="5"
              />
              <!-- Vibe Tags inside card -->
              <div v-if="tagsToAdd.length" class="vibe-tags">
                <span v-for="tag in tagsToAdd" :key="tag" class="vibe-tag">{{ tag }}</span>
              </div>

              <!-- Photo upload inside card -->
              <div class="photo-upload-section">
                <div v-if="!photoPreview"
                  class="photo-drop-zone"
                  :class="{ 'drag-over': isDragging }"
                  @click="triggerPhotoInput"
                  @dragover.prevent="isDragging = true"
                  @dragleave.prevent="isDragging = false"
                  @drop.prevent="handlePhotoDrop"
                >
                  <input
                    ref="photoInput"
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    class="photo-file-input"
                    @change="handlePhotoSelect"
                  />
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <polyline points="21 15 16 10 5 21"/>
                  </svg>
                  <span class="photo-drop-text">Add a photo <em>(optional)</em></span>
                  <span class="photo-drop-hint">JPG, PNG, or WebP · Max 5 MB</span>
                </div>

                <div v-else class="photo-preview-wrap">
                  <img :src="photoPreview" alt="Photo preview" class="photo-preview-img" />
                  <button class="photo-remove-btn" @click="removePhoto" title="Remove photo">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                  </button>
                </div>

                <p v-if="photoError" class="photo-error">{{ photoError }}</p>
              </div>
            </div>
          </div>

          <!-- Success card (inline in chat) -->
          <div v-if="published" class="success-card-wrap">
            <div class="success-card">
              <div class="success-icon-wrap">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 6 9 17l-5-5"/>
                </svg>
              </div>
              <h3 class="success-title">Review published!</h3>
              <p class="success-desc">Thanks for sharing your experience</p>
              <div class="points-card">
                <div class="points-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#B8860B" stroke-width="2">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                  </svg>
                </div>
                <div>
                  <p class="points-earned">+50 points</p>
                  <p class="points-desc">Earned for writing a review</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Typing indicator -->
          <div v-if="aiTyping" class="chat-bubble assistant">
            <div class="bubble-avatar">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4A70A9" stroke-width="2.5">
                <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1.27c.34-.6.99-1 1.73-1a2 2 0 1 1 0 4c-.74 0-1.39-.4-1.73-1H21a7 7 0 0 1-7 7v1.27c.6.34 1 .99 1 1.73a2 2 0 1 1-4 0c0-.74.4-1.39 1-1.73V23a7 7 0 0 1-7-7H3.73c-.34.6-.99 1-1.73 1a2 2 0 1 1 0-4c.74 0 1.39.4 1.73 1H5a7 7 0 0 1 7-7V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"/>
              </svg>
            </div>
            <div class="bubble-content">
              <span class="loading-dots">
                <span class="dot">●</span>
                <span class="dot">●</span>
                <span class="dot">●</span>
              </span>
            </div>
          </div>
        </div>

        <!-- ─── Error ─── -->
        <p v-if="chatError" class="chat-error">{{ chatError }}</p>

        <!-- ─── Bottom bar: input + actions ─── -->
        <div v-if="!published" class="chat-bottom">
          <!-- Vibe tags (shown during chat, before review generated) -->
          <div v-if="tagsToAdd.length && !generatedDescription" class="vibe-tags-bar">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#4A70A9" stroke-width="2"><path d="M12 2 2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
            <span v-for="tag in tagsToAdd" :key="tag" class="vibe-tag-sm">{{ tag }}</span>
          </div>

          <!-- Chat input (hidden once review is generated) -->
          <div v-if="sessionId && !generatedDescription" class="chat-input-row">
            <textarea
              ref="inputRef"
              v-model="userMessage"
              class="answer-input"
              placeholder="Type your reply…"
              rows="1"
              :disabled="aiTyping"
              @keydown.enter.exact.prevent="sendMessage"
              @input="autoGrow"
            />
            <button
              class="send-btn"
              :disabled="!userMessage.trim() || aiTyping"
              @click="sendMessage"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </button>
          </div>

          <!-- Action buttons -->
          <div class="action-row">
            <!-- Generate (only when chatting, no review yet) -->
            <button
              v-if="sessionId && !generatedDescription"
              class="modal-btn primary"
              :disabled="conversationTurns < 1 || generating || aiTyping"
              @click="generateReview"
            >
              <template v-if="generating">
                <span class="loading-dots"><span class="dot">●</span><span class="dot">●</span><span class="dot">●</span></span>
                Generating
              </template>
              <template v-else>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                Generate Review
              </template>
            </button>

            <!-- Rewrite + Publish (once review is generated) -->
            <template v-if="generatedDescription">
              <button class="modal-btn secondary" :disabled="generating" @click="rewriteReview">
                <template v-if="generating">
                  <span class="loading-dots"><span class="dot">●</span><span class="dot">●</span><span class="dot">●</span></span>
                  Rewriting
                </template>
                <template v-else>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
                  Rewrite
                </template>
              </button>
              <button
                class="modal-btn primary"
                :disabled="!generatedDescription.trim() || submitting"
                @click="confirmReview"
              >
                {{ submitting ? 'Publishing...' : 'Publish Review' }}
              </button>
            </template>
          </div>
        </div>

        <!-- Done button (after publish) -->
        <button v-if="published" class="modal-btn primary done-btn" @click="handleClose">
          Done
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import {
  startAIReview,
  sendAIReviewMessage,
  generateAIReview,
  confirmAIReview,
  abandonAIReview,
} from '@/api/client'

const props = defineProps({
  modelValue: Boolean,
  businessId: { type: [String, Number], required: true },
})

const emit = defineEmits(['update:modelValue', 'review-published'])

// ── State ──────────────────────────────────────────────────────────────
const rating = ref(0)
const hoverRating = ref(0)
const published = ref(false)

// AI chat
const sessionId = ref(null)
const conversation = ref([])
const userMessage = ref('')
const aiTyping = ref(false)
const generating = ref(false)
const submitting = ref(false)
const chatError = ref('')

// Tags & generated text
const tagsToAdd = ref([])
const generatedDescription = ref('')

// Photo upload
const photoBase64 = ref('')
const photoPreview = ref('')
const photoError = ref('')
const isDragging = ref(false)

// DOM refs
const chatContainer = ref(null)
const inputRef = ref(null)
const photoInput = ref(null)

// ── Computed ───────────────────────────────────────────────────────────
const ratingLabels = ['', 'Terrible', 'Poor', 'Okay', 'Great', 'Amazing!']
const ratingLabel = computed(() => {
  const active = hoverRating.value || rating.value
  return ratingLabels[active] || ''
})

const visibleMessages = computed(() =>
  conversation.value.filter(m => m.role === 'assistant' || m.role === 'user')
)

const conversationTurns = computed(() =>
  conversation.value.filter(m => m.role === 'user').length
)

// ── Reset on open ──────────────────────────────────────────────────────
watch(() => props.modelValue, (open) => {
  if (open) {
    rating.value = 0
    hoverRating.value = 0
    published.value = false
    sessionId.value = null
    conversation.value = []
    userMessage.value = ''
    aiTyping.value = false
    generating.value = false
    submitting.value = false
    chatError.value = ''
    tagsToAdd.value = []
    generatedDescription.value = ''
    photoBase64.value = ''
    photoPreview.value = ''
    photoError.value = ''
    isDragging.value = false
  }
})

// ── Helpers ────────────────────────────────────────────────────────────
function scrollChat() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

function autoGrow(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

// ── Photo upload helpers ───────────────────────────────────────────────
const MAX_PHOTO_SIZE = 5 * 1024 * 1024 // 5 MB

function triggerPhotoInput() {
  photoInput.value?.click()
}

function handlePhotoSelect(event) {
  const file = event.target.files?.[0]
  if (file) processPhotoFile(file)
  // reset so same file can be re-selected
  if (photoInput.value) photoInput.value.value = ''
}

function handlePhotoDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) processPhotoFile(file)
}

function processPhotoFile(file) {
  photoError.value = ''

  const allowed = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowed.includes(file.type)) {
    photoError.value = 'Only JPG, PNG, or WebP images are allowed.'
    return
  }
  if (file.size > MAX_PHOTO_SIZE) {
    photoError.value = 'Image must be under 5 MB.'
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    photoPreview.value = reader.result           // data:image/...;base64,...
    // Strip the data-URI prefix → send raw base64 to API
    photoBase64.value = reader.result.split(',')[1] || reader.result
  }
  reader.onerror = () => {
    photoError.value = 'Failed to read image. Please try again.'
  }
  reader.readAsDataURL(file)
}

function removePhoto() {
  photoBase64.value = ''
  photoPreview.value = ''
  photoError.value = ''
}

// ── Select rating → start session ──────────────────────────────────────
async function selectRating(n) {
  if (sessionId.value || aiTyping.value) return // already started
  rating.value = n
  chatError.value = ''
  aiTyping.value = true

  try {
    const { data } = await startAIReview(props.businessId, n)
    sessionId.value = data.id
    conversation.value = data.conversation || []
    tagsToAdd.value = data.tags_to_add || []
    scrollChat()
    nextTick(() => inputRef.value?.focus())
  } catch (err) {
    chatError.value = err.response?.data?.detail
      || err.response?.data?.non_field_errors?.[0]
      || 'Failed to start AI chat. Are you logged in with a verified email?'
  } finally {
    aiTyping.value = false
  }
}

// ── Send message ───────────────────────────────────────────────────────
async function sendMessage() {
  const msg = userMessage.value.trim()
  if (!msg || aiTyping.value || !sessionId.value) return

  chatError.value = ''
  conversation.value.push({ role: 'user', content: msg })
  userMessage.value = ''
  // Reset textarea height
  if (inputRef.value) inputRef.value.style.height = 'auto'
  aiTyping.value = true
  scrollChat()

  try {
    const { data } = await sendAIReviewMessage(sessionId.value, msg)
    conversation.value.push({ role: 'assistant', content: data.reply })

    if (data.tags_added?.length) {
      const existing = new Set(tagsToAdd.value)
      data.tags_added.forEach(t => existing.add(t))
      tagsToAdd.value = [...existing]
    }
    if (data.tags_removed?.length) {
      const removed = new Set(data.tags_removed)
      tagsToAdd.value = tagsToAdd.value.filter(t => !removed.has(t))
    }
    scrollChat()
  } catch (err) {
    chatError.value = err.response?.data?.detail || 'Failed to send message'
  } finally {
    aiTyping.value = false
    nextTick(() => inputRef.value?.focus())
  }
}

// ── Generate review ────────────────────────────────────────────────────
async function generateReview() {
  chatError.value = ''
  generating.value = true

  try {
    const { data } = await generateAIReview(sessionId.value)
    generatedDescription.value = data.generated_description
    if (data.session) {
      tagsToAdd.value = data.session.tags_to_add || tagsToAdd.value
    }
    scrollChat()
  } catch (err) {
    chatError.value = err.response?.data?.detail || 'Failed to generate review'
  } finally {
    generating.value = false
  }
}

// ── Rewrite ────────────────────────────────────────────────────────────
async function rewriteReview() {
  chatError.value = ''
  generating.value = true

  try {
    const { data } = await generateAIReview(sessionId.value)
    generatedDescription.value = data.generated_description
    if (data.session) {
      tagsToAdd.value = data.session.tags_to_add || tagsToAdd.value
    }
    scrollChat()
  } catch (err) {
    chatError.value = err.response?.data?.detail || 'Failed to rewrite review'
  } finally {
    generating.value = false
  }
}

// ── Confirm & publish ──────────────────────────────────────────────────
async function confirmReview() {
  chatError.value = ''
  submitting.value = true

  try {
    const payload = { description: generatedDescription.value }
    if (photoBase64.value) {
      payload.photo = photoBase64.value
    }
    await confirmAIReview(sessionId.value, payload)
    published.value = true
    emit('review-published')
    scrollChat()
  } catch (err) {
    chatError.value = err.response?.data?.detail
      || err.response?.data?.non_field_errors?.[0]
      || 'Failed to publish review. Please try again.'
  } finally {
    submitting.value = false
  }
}

// ── Close / abandon ────────────────────────────────────────────────────
function handleClose() {
  if (sessionId.value && !published.value) {
    abandonAIReview(sessionId.value).catch(() => {})
  }
  emit('update:modelValue', false)
}
</script>

<style scoped>
/* ─── Modal Backdrop ─── */
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

/* ─── Modal Container ─── */
.review-modal {
  position: relative;
  background: #fff;
  border-radius: 1.25rem;
  width: 100%;
  max-width: 32rem;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.18), 0 0 0 1px rgba(0, 0, 0, 0.04);
  animation: modal-pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  overflow: hidden;
}
@keyframes modal-pop {
  0% { opacity: 0; transform: scale(0.92) translateY(16px); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

/* ─── Close ─── */
.modal-close {
  position: absolute;
  top: 0.875rem;
  right: 0.875rem;
  background: #f5f5f5;
  border: none;
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s;
  z-index: 2;
}
.modal-close:hover { background: #e8e8e8; }

/* ─── Top header ─── */
.modal-top {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem 0;
  flex-shrink: 0;
}
.modal-icon {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 0.75rem;
  background: #EFECE3;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ai-icon { background: linear-gradient(135deg, #E8EEF6, #EFECE3); }
.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.3;
}
.modal-subtitle {
  font-size: 0.8125rem;
  font-weight: 400;
  color: #888;
  margin: 0;
}

/* ─── Rating bar ─── */
.rating-bar {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid #EFECE3;
  flex-shrink: 0;
}
.rating-bar-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #888;
  white-space: nowrap;
}
.star-selector {
  display: flex;
  gap: 0.25rem;
}
.star-select {
  width: 1.75rem;
  height: 1.75rem;
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
.star-select:hover { transform: scale(1.15); }
.rating-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #4A70A9;
  min-height: 1rem;
  margin: 0;
  white-space: nowrap;
}

/* ─── Conversation area ─── */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  padding: 1rem 1.25rem;
  min-height: 200px;
  max-height: 50vh;
  scroll-behavior: smooth;
}
.chat-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  text-align: center;
  color: #aaa;
  font-size: 0.875rem;
  padding: 2rem;
}
.chat-empty p { margin: 0; }

/* ─── Chat bubbles ─── */
.chat-bubble {
  display: flex;
  gap: 0.5rem;
  max-width: 88%;
  animation: slide-up 0.3s ease;
}
.chat-bubble.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}
.chat-bubble.assistant { align-self: flex-start; }
.bubble-avatar {
  width: 1.625rem;
  height: 1.625rem;
  border-radius: 50%;
  background: #E8EEF6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 0.125rem;
}
.bubble-content {
  padding: 0.5rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  line-height: 1.55;
  color: #1a1a1a;
}
.chat-bubble.assistant .bubble-content {
  background: #FAFAF8;
  border: 1px solid #EFECE3;
  border-top-left-radius: 0.25rem;
}
.chat-bubble.user .bubble-content {
  background: #4A70A9;
  color: #fff;
  border-top-right-radius: 0.25rem;
}

/* ─── Review card (inline) ─── */
.review-card-wrap {
  width: 100%;
  animation: slide-up 0.35s ease;
}
.review-card {
  background: #FAFAF8;
  border: 1.5px solid #e0ddd4;
  border-radius: 0.875rem;
  padding: 0.875rem;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}
.review-card-head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #4A70A9;
}
.review-edit-area {
  width: 100%;
  border: 1.5px solid #e0ddd4;
  border-radius: 0.625rem;
  padding: 0.75rem;
  font-size: 0.8125rem;
  line-height: 1.6;
  color: #1a1a1a;
  background: #fff;
  resize: vertical;
  outline: none;
  font-family: inherit;
}
.review-edit-area:focus { border-color: #4A70A9; }

/* ─── Success card (inline) ─── */
.success-card-wrap {
  width: 100%;
  animation: slide-up 0.35s ease;
}
.success-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.625rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 0.875rem;
  padding: 1.25rem;
  text-align: center;
}
.success-icon-wrap {
  animation: pop-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.success-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}
.success-desc {
  font-size: 0.8125rem;
  color: #666;
  margin: 0;
}

/* ─── Points card ─── */
.points-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: linear-gradient(135deg, #FFF9E6, #FFF4CC);
  border: 1px solid #E8B931;
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  width: 100%;
  animation: slide-up 0.4s ease;
}
.points-icon {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.625rem;
  background: rgba(232, 185, 49, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.points-earned {
  font-size: 1rem;
  font-weight: 700;
  color: #B8860B;
  margin: 0;
}
.points-desc {
  font-size: 0.75rem;
  font-weight: 400;
  color: #997A1F;
  margin: 0;
}

/* ─── Vibe tags (in chat) ─── */
.vibe-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}
.vibe-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.625rem;
  background: linear-gradient(135deg, #E8EEF6, #EFECE3);
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #4A70A9;
  border: 1px solid rgba(74, 112, 169, 0.12);
}

/* ─── Photo upload ─── */
.photo-upload-section {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.photo-drop-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem;
  border: 1.5px dashed #d0cdc4;
  border-radius: 0.625rem;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}
.photo-drop-zone:hover {
  border-color: #4A70A9;
  background: #f8f9fc;
}
.photo-drop-zone.drag-over {
  border-color: #4A70A9;
  background: #eef2f8;
}
.photo-file-input {
  display: none;
}
.photo-drop-text {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #555;
}
.photo-drop-text em {
  font-style: italic;
  font-weight: 400;
  color: #999;
}
.photo-drop-hint {
  font-size: 0.6875rem;
  color: #aaa;
}
.photo-preview-wrap {
  position: relative;
  display: inline-block;
  align-self: flex-start;
}
.photo-preview-img {
  max-height: 140px;
  max-width: 100%;
  border-radius: 0.5rem;
  border: 1px solid #e0ddd4;
  object-fit: cover;
}
.photo-remove-btn {
  position: absolute;
  top: -0.375rem;
  right: -0.375rem;
  width: 1.375rem;
  height: 1.375rem;
  border-radius: 50%;
  background: #ef4444;
  color: #fff;
  border: 2px solid #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s, transform 0.15s;
  padding: 0;
}
.photo-remove-btn:hover {
  background: #dc2626;
  transform: scale(1.1);
}
.photo-error {
  font-size: 0.75rem;
  color: #ef4444;
  margin: 0;
}

/* ─── Vibe tags bar (above input) ─── */
.vibe-tags-bar {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  flex-wrap: wrap;
  padding: 0 0.25rem;
}
.vibe-tag-sm {
  font-size: 0.6875rem;
  font-weight: 500;
  color: #4A70A9;
  background: rgba(74, 112, 169, 0.08);
  padding: 0.125rem 0.5rem;
  border-radius: 0.75rem;
}

/* ─── Chat error ─── */
.chat-error {
  color: #ef4444;
  font-size: 0.8125rem;
  text-align: center;
  margin: 0;
  padding: 0 1.5rem 0.5rem;
  flex-shrink: 0;
}

/* ─── Bottom bar ─── */
.chat-bottom {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  padding: 0.75rem 1.25rem 1rem;
  border-top: 1px solid #EFECE3;
  flex-shrink: 0;
}
.chat-input-row {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
}
.answer-input {
  flex: 1;
  border: 1.5px solid #e0ddd4;
  border-radius: 0.75rem;
  padding: 0.625rem 0.75rem;
  font-size: 0.875rem;
  color: #1a1a1a;
  background: #fff;
  resize: none;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
  min-height: 2.5rem;
  max-height: 7.5rem;
  overflow-y: auto;
}
.answer-input:focus { border-color: #4A70A9; }
.answer-input::placeholder { color: #bbb; }
.answer-input:disabled { opacity: 0.5; }

.send-btn {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  background: #4A70A9;
  color: #fff;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s, transform 0.15s;
}
.send-btn:hover:not(:disabled) { background: #3b5e94; }
.send-btn:active { transform: scale(0.93); }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* ─── Action row ─── */
.action-row {
  display: flex;
  gap: 0.5rem;
}

/* ─── Buttons ─── */
.modal-btn {
  flex: 1;
  padding: 0.75rem 1.25rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: background 0.2s, opacity 0.2s, transform 0.15s;
}
.modal-btn:active { transform: scale(0.97); }
.modal-btn.primary {
  background: #4A70A9;
  color: #fff;
}
.modal-btn.primary:hover:not(:disabled) { background: #3b5e94; }
.modal-btn.primary:disabled { opacity: 0.45; cursor: not-allowed; }
.modal-btn.secondary {
  background: #EFECE3;
  color: #333;
}
.modal-btn.secondary:hover:not(:disabled) { background: #e4e0d6; }
.modal-btn.secondary:disabled { opacity: 0.45; cursor: not-allowed; }

.done-btn {
  margin: 0 1.25rem 1rem;
  flex: none;
}

/* ─── Animations ─── */
@keyframes slide-up {
  0% { opacity: 0; transform: translateY(12px); }
  100% { opacity: 1; transform: translateY(0); }
}
@keyframes pop-in {
  0% { opacity: 0; transform: scale(0.5); }
  100% { opacity: 1; transform: scale(1); }
}
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

/* ─── Vue transition ─── */
.modal-fade-enter-active { transition: opacity 0.25s ease; }
.modal-fade-leave-active { transition: opacity 0.2s ease; }
.modal-fade-enter-from,
.modal-fade-leave-to { opacity: 0; }

/* ─── Desktop ─── */
@media (min-width: 768px) {
  .review-modal { max-width: 34rem; }
  .modal-title { font-size: 1.25rem; }
}
</style>

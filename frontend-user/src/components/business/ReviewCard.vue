<!--
  ReviewCard.vue — Individual Review Display
  ─────────────────────────────────────────────────────────────────────────────
  Renders a single review inside ReviewsSection.

  LAYOUT
  ┌─────────────────────────────────────────────────┐
  │  [A]  ★★★★☆  Author Name  · Dec 15, 2024       │
  │  "The food was amazing and the staff was…"       │
  │  [photo if any]                                  │
  │  [👍 useful 3] [😄 funny 1] [😎 cool]           │
  └─────────────────────────────────────────────────┘

  • Avatar shows the author's first initial with a coloured background
    (gold for Google reviews, blue for user reviews).
  • Vote buttons use SVG icons from VOTE_ICONS (config/businessDetail.js).
  • A `.voted` class highlights buttons the current user has voted on.

  EVENTS
  • @vote(reviewId, voteType) — emitted when a vote button is clicked.
  • @delete(reviewId) — emitted when the delete button is clicked (own reviews only).
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="review-card">
    <div class="review-card-header">
      <div class="reviewer-avatar" :class="review.source">
        {{ review.author.charAt(0).toUpperCase() }}
      </div>
      <div class="reviewer-info">
        <div class="reviewer-stars">
          <svg v-for="n in 5" :key="n" width="13" height="13" viewBox="0 0 24 24" :fill="n <= review.rating ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        </div>
        <span class="reviewer-name">{{ review.author }}</span>
        <span v-if="review.date" class="review-date">{{ formattedDate }}</span>
        <span v-if="review.source === 'google'" class="source-badge">Google</span>
        <button
          v-if="isOwn"
          class="delete-btn"
          title="Delete your review"
          @click="confirmDelete"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
        </button>
      </div>
    </div>
    <p v-if="review.text" class="review-body">{{ review.text }}</p>
    <img v-if="review.imageUrl" :src="review.imageUrl" alt="Review photo" class="review-photo" />
    <div v-if="review.voteCounts" class="vote-bar">
      <button
        v-for="vt in voteTypes" :key="vt"
        class="vote-btn" :class="{ voted: review.userVotes?.includes(vt) }"
        @click="$emit('vote', review.id, vt)"
      >
        <span class="vote-icon" v-html="VOTE_ICONS[vt]"></span> {{ vt }} {{ review.voteCounts[vt] || '' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { VOTE_ICONS } from '@/config/businessDetail'

const props = defineProps({
  review: { type: Object, required: true },
  currentUserId: { type: [Number, String], default: null }
})

const emit = defineEmits(['vote', 'delete'])

const voteTypes = ['useful', 'funny', 'cool']

/** True when this review belongs to the logged-in user. */
const isOwn = computed(() => {
  return (
    props.currentUserId != null &&
    props.review.userId != null &&
    String(props.review.userId) === String(props.currentUserId)
  )
})

function confirmDelete() {
  if (window.confirm('Delete your review? This cannot be undone.')) {
    emit('delete', props.review.id)
  }
}

const formattedDate = computed(() => {
  if (!props.review.date) return ''
  return props.review.date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
})
</script>

<style scoped>
.review-card {
  padding: 18px; border-radius: 10px;
  background: var(--color-surface); border: 1px solid var(--color-border);
}
.review-card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.reviewer-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 16px;
}
.reviewer-avatar.google { background: rgba(245,158,11,0.1); color: var(--color-accent-gold, #f59e0b); }
.reviewer-avatar.user { background: rgba(74,112,169,0.1); color: var(--color-primary); }
.reviewer-info { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; flex: 1; }
.reviewer-stars { color: var(--color-accent-gold, #f59e0b); display: flex; align-items: center; gap: 1px; }
.reviewer-name { font-weight: 600; font-size: 14px; color: var(--color-text); }
.review-date { font-size: 12px; color: var(--color-text-muted); }
.source-badge {
  font-size: 10px; padding: 1px 8px; border-radius: 999px;
  background: rgba(245,158,11,0.08); color: var(--color-accent-gold, #f59e0b); font-weight: 600;
}
.delete-btn {
  margin-left: auto; padding: 4px 8px; border-radius: 6px; cursor: pointer;
  background: none; border: 1px solid transparent;
  color: var(--color-text-muted); transition: all 0.15s;
}
.delete-btn:hover {
  background: rgba(239,68,68,0.08); border-color: #ef4444; color: #ef4444;
}
.review-body { font-size: 14px; line-height: 1.6; color: var(--color-text-light, #475569); margin: 0; }
.review-photo { margin-top: 12px; max-height: 200px; border-radius: 8px; }
.vote-bar { display: flex; gap: 8px; margin-top: 12px; }
.vote-btn {
  padding: 4px 12px; font-size: 12px; border-radius: 999px; cursor: pointer;
  background: rgba(0,0,0,0.03); border: 1px solid var(--color-border);
  color: var(--color-text-muted); transition: all 0.15s;
}
.vote-btn:hover { border-color: var(--color-primary); color: var(--color-text); }
.vote-btn.voted { background: rgba(74,112,169,0.1); border-color: var(--color-primary); color: var(--color-primary); }
.vote-icon { display: inline-flex; align-items: center; vertical-align: middle; }
</style>

<!--
  StarRating.vue — Star Display / Picker Component
  ─────────────────────────────────────────────────────────────────────────────
  Renders 1-to-5 star SVGs. Has two modes controlled by the `interactive` prop:

  • DISPLAY MODE (default) — small 14px filled/empty stars, read-only.
    Used in review cards, hero ratings, search results.
  • PICKER MODE (interactive=true) — larger 20px clickable stars.
    Used in WriteReviewModal so users can select their rating.

  v-model binding: `modelValue` is the current rating (Number, 0–5).
  In picker mode, clicking a star emits `update:modelValue` with that star's
  number, making it work seamlessly with Vue's v-model syntax.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <span class="stars" :class="{ picker: interactive }">
    <template v-if="interactive">
      <button
        v-for="n in max"
        :key="n"
        class="star-pick"
        :class="{ filled: n <= modelValue }"
        @click="$emit('update:modelValue', n)"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" :fill="n <= modelValue ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
      </button>
    </template>
    <template v-else>
      <svg v-for="n in max" :key="n" class="star-display" width="14" height="14" viewBox="0 0 24 24" :fill="n <= roundedValue ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
    </template>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 0 },
  max: { type: Number, default: 5 },
  interactive: Boolean
})

defineEmits(['update:modelValue'])

const roundedValue = computed(() => Math.round(props.modelValue))
</script>

<style scoped>
.stars { color: var(--color-accent-gold, #f59e0b); display: inline-flex; align-items: center; gap: 1px; }
.picker { gap: 6px; }
.star-pick {
  background: none; border: none; cursor: pointer;
  color: var(--color-border); transition: color 0.1s;
  display: flex; align-items: center;
}
.star-pick.filled { color: var(--color-accent-gold, #f59e0b); }
.star-display { flex-shrink: 0; }
</style>

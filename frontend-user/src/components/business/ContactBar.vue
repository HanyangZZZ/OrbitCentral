<!--
  ContactBar.vue — Business Contact Info + Action Buttons
  ─────────────────────────────────────────────────────────────────────────────
  Horizontal bar below the hero on the Business Detail page.

  LEFT SIDE — clickable contact links (each wrapped in an <a>):
    📍 Address (opens Google Maps)  ✉ Email  📞 Phone  🌐 Website

  RIGHT SIDE — action buttons:
    [Write a Review] [Vote for Activities] [View Coupons]

  The website URL is cleaned for display (strips protocol + trailing slash)
  via the `websiteDisplay` computed.

  EVENTS
  • @write-review, @vote-activities, @view-coupons — passed up to
    BusinessDetailPage which opens the corresponding modal.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <section class="contact-bar">
    <div class="contact-items">
      <a v-if="address" :href="mapsUri || '#'" target="_blank" class="contact-item">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
        <span>{{ address }}</span>
      </a>
      <a v-if="email" :href="`mailto:${email}`" class="contact-item">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
        <span>{{ email }}</span>
      </a>
      <a v-if="phone" :href="`tel:${phone}`" class="contact-item">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
        <span>{{ phone }}</span>
      </a>
      <a v-if="website" :href="website" target="_blank" class="contact-item website-link">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
        <span>{{ websiteDisplay }}</span>
        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
      </a>
    </div>
    <div class="action-buttons">
      <button class="action-btn primary" @click="$emit('write-review')">Write a Review</button>
      <button class="action-btn accent-secondary" @click="$emit('vote-activities')">Vote for Activities</button>
      <button class="action-btn accent-secondary" @click="$emit('view-coupons')">View Coupons</button>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  address: String,
  mapsUri: String,
  email: String,
  phone: String,
  website: String
})

defineEmits(['write-review', 'vote-activities', 'view-coupons'])

const websiteDisplay = computed(() => props.website?.replace(/^https?:\/\//, '').replace(/\/$/, '') || '')
</script>

<style scoped>
.contact-bar {
  max-width: 900px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 12px; padding: 16px 32px;
  border-bottom: 1px solid var(--color-border);
}
.contact-items { display: flex; flex-wrap: wrap; gap: 16px; }
.contact-item {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 13px; color: var(--color-text-muted);
  text-decoration: none; transition: color 0.15s;
}
.contact-item:hover { color: var(--color-text); }
.website-link { color: var(--color-primary) !important; font-weight: 500; }
.website-link:hover { color: var(--color-primary-hover) !important; }
.action-buttons { display: flex; gap: 8px; flex-wrap: wrap; }
.action-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 18px; border-radius: 8px; font-size: 13px; font-weight: 500;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', system-ui, sans-serif;
  cursor: pointer; border: none; transition: background 0.15s;
}
.action-btn.primary { background: var(--color-primary); color: #fff; }
.action-btn.primary:hover { background: var(--color-primary-hover); }
.action-btn.accent-secondary {
  background: rgba(67,56,202,0.06); color: var(--color-accent, #4338ca);
  border: 1px solid var(--color-border-light, #c7d2fe);
}
.action-btn.accent-secondary:hover {
  background: rgba(67,56,202,0.12); border-color: var(--color-accent);
}
</style>

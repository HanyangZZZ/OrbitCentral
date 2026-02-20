<!--
  CookieConsent.vue — One-time cookie permission banner
  ─────────────────────────────────────────────────────────────────────────────
  Shows a bottom-of-screen banner asking the user to allow a single
  auth cookie used for login / logout functionality.

  RULES
  • User accepts  → store flag in localStorage, never show again.
  • User declines → don't persist anything, banner reappears on the
    next page visit so they can change their mind later.

  Other components can check consent with:
    import { hasCookieConsent } from '@/components/CookieConsent.vue'
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <Transition name="consent-slide">
    <div v-if="visible" class="consent-backdrop">
      <div class="consent-box">
        <p class="consent-text">
          <strong>Cookie Notice</strong> — We use a single cookie solely to keep
          you logged in. No tracking, no ads, no third parties.
        </p>
        <div class="consent-actions">
          <button class="btn-consent btn-accept" @click="accept">Accept</button>
          <button class="btn-consent btn-decline" @click="decline">Decline</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const STORAGE_KEY = 'cookie_consent'
const visible = ref(false)

onMounted(() => {
  // Only hide when the user has explicitly accepted
  if (localStorage.getItem(STORAGE_KEY) !== 'accepted') {
    visible.value = true
  }
})

function accept() {
  localStorage.setItem(STORAGE_KEY, 'accepted')
  visible.value = false
}

function decline() {
  // Don't persist — banner will reappear on next visit
  localStorage.removeItem(STORAGE_KEY)
  visible.value = false
}

/**
 * Utility readable by any module:
 *   import { hasCookieConsent } from '@/components/CookieConsent.vue'
 */
export function hasCookieConsent() {
  return localStorage.getItem(STORAGE_KEY) === 'accepted'
}
</script>

<style scoped>
.consent-backdrop {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  display: flex;
  justify-content: center;
  padding: 16px;
  pointer-events: none;
}

.consent-box {
  pointer-events: auto;
  max-width: 560px;
  width: 100%;
  background: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 12px;
  box-shadow: 0 -2px 20px rgba(0, 0, 0, 0.12);
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.consent-text {
  margin: 0;
  font-size: 0.92rem;
  line-height: 1.5;
  color: var(--color-text, #0f172a);
}

.consent-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn-consent {
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: background 0.15s, transform 0.1s;
}
.btn-consent:active { transform: scale(0.97); }

.btn-accept {
  background: var(--color-primary, #4a70a9);
  color: #fff;
}
.btn-accept:hover { background: var(--color-primary-hover, #1e3a8a); }

.btn-decline {
  background: transparent;
  color: var(--color-text-muted, #64748b);
  border: 1px solid var(--color-border, #e2e8f0);
}
.btn-decline:hover { background: var(--color-bg, #f8fafc); }

/* Slide-up / slide-down transition */
.consent-slide-enter-active,
.consent-slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.consent-slide-enter-from,
.consent-slide-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>

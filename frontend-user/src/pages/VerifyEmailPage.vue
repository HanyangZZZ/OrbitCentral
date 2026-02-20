<!--
  VerifyEmailPage.vue — Email Verification (route: /verify-email)
  ─────────────────────────────────────────────────────────────────────────────
  Shown after registration or when a user tries to log in with an unverified
  email address.

  SCENARIOS
  1. URL has ?token=… → auto-verifies by calling verifyEmail(token).
     On success shows a green checkmark + "Verified!" message.
  2. No token in URL → shows "Check your inbox" message with a
     "Resend verification email" button.

  FLOW
    ?token → verifyEmail() API → success → auto-login → redirect to Home
    No token → user clicks Resend → resendVerify(email) API → cooldown timer
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="auth-page">
    <div class="auth-card">
      <!-- Logo -->
      <router-link to="/" class="auth-logo">Orbit</router-link>

      <!-- Loading state -->
      <div v-if="verifying" class="verify-state">
        <div class="spinner"></div>
        <h1 class="auth-title">Verifying your email…</h1>
        <p class="auth-subtitle">Hang tight while we confirm your address.</p>
      </div>

      <!-- Success state -->
      <div v-else-if="success" class="verify-state">
        <div class="status-icon success-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 6 9 17l-5-5"/>
          </svg>
        </div>
        <h1 class="auth-title">Email verified! ✓</h1>
        <p class="auth-subtitle">Your email address has been confirmed. You're all set to use Orbit.</p>
        <router-link to="/login" class="btn btn-primary btn-full">
          Log In
        </router-link>
      </div>

      <!-- Error state -->
      <div v-else class="verify-state">
        <div class="status-icon error-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
        </div>
        <h1 class="auth-title">Verification failed</h1>
        <p class="auth-subtitle">{{ error }}</p>
        <div class="verify-actions">
          <button
            v-if="canResend"
            class="btn btn-primary btn-full"
            :disabled="resending"
            @click="handleResend"
          >
            {{ resending ? 'Sending…' : 'Resend Verification Email' }}
          </button>
          <p v-if="resendSuccess" class="success-msg resend-msg">✓ New verification email sent! Check your inbox.</p>
          <router-link to="/login" class="btn btn-outline btn-full">
            Go to Login
          </router-link>
        </div>
      </div>

      <div class="auth-footer">
        <router-link to="/" class="auth-link">← Back to home</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { verifyEmail, resendVerify } from '@/api/client'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const { isLoggedIn } = useAuth()

const verifying     = ref(true)
const success       = ref(false)
const error         = ref('')
const canResend     = ref(false)
const resending     = ref(false)
const resendSuccess = ref(false)

onMounted(async () => {
  const token = route.query.token

  if (!token) {
    verifying.value = false
    error.value = 'No verification token found. Please check the link in your email.'
    return
  }

  try {
    await verifyEmail(token)
    success.value = true
  } catch (err) {
    const detail = err.response?.data?.detail
      || err.response?.data?.non_field_errors?.[0]
      || 'This verification link is invalid or has expired.'
    error.value = detail
    // If the user is logged in, they can request a new verification email
    canResend.value = isLoggedIn.value
  } finally {
    verifying.value = false
  }
})

async function handleResend() {
  resending.value = true
  resendSuccess.value = false

  try {
    await resendVerify()
    resendSuccess.value = true
  } catch {
    error.value = 'Could not resend verification email. Please try again later.'
  } finally {
    resending.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh; background: var(--color-bg); padding: 24px;
}
.auth-card {
  width: 100%; max-width: 420px;
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 16px; padding: 40px 32px;
  animation: fade-up 0.35s ease;
}
.auth-logo {
  display: block; text-align: center;
  font-family: var(--font-brand, 'Barlow', sans-serif);
  font-size: 30px; font-weight: 800; letter-spacing: -0.5px;
  color: var(--color-primary); text-decoration: none; margin-bottom: 24px;
}
.auth-title { font-size: 22px; font-weight: 700; color: var(--color-text); text-align: center; margin: 0 0 8px; }
.auth-subtitle { font-size: 14px; color: var(--color-text-muted); text-align: center; margin: 0 0 24px; line-height: 1.5; }
.auth-footer { margin-top: 24px; text-align: center; }
.auth-link { font-size: 14px; color: var(--color-text-muted); text-decoration: none; }
.auth-link:hover { color: var(--color-primary); }

.verify-state {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
}

.status-icon {
  width: 64px; height: 64px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 8px;
  animation: pop-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.success-icon { background: #f0fdf4; }
.error-icon   { background: #fef2f2; }

.verify-actions {
  display: flex; flex-direction: column; gap: 10px; width: 100%; margin-top: 8px;
}

.resend-msg { text-align: center; margin-top: 4px; }

@keyframes fade-up {
  0%   { opacity: 0; transform: translateY(16px); }
  100% { opacity: 1; transform: translateY(0); }
}
@keyframes pop-in {
  0%   { opacity: 0; transform: scale(0.5); }
  100% { opacity: 1; transform: scale(1); }
}
</style>

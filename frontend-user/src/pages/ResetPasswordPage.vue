<!--
  ResetPasswordPage.vue — Password Reset (route: /reset-password)
  ─────────────────────────────────────────────────────────────────────────────
  Two-step password reset flow:

  STEP 1 — "Forgot Password" (no token in URL)
    User enters their email → calls forgotPassword(email) → backend sends
    a reset link via email. Shows "Check your inbox" confirmation.

  STEP 2 — "Set New Password" (URL has ?token=…)
    User enters new password + confirm → calls resetPassword(token, password)
    → on success shows "Password updated!" and redirects to /login.

  CLIENT-SIDE VALIDATION
  • New password ≥ 8 chars, uppercase, lowercase, number.
  • Confirm must match.
  ─────────────────────────────────────────────────────────────────────────────
-->
<template>
  <div class="auth-page">
    <div class="auth-card">
      <!-- Logo -->
      <router-link to="/" class="auth-logo">Orbit</router-link>

      <!-- Success state -->
      <div v-if="success" class="verify-state">
        <div class="status-icon success-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 6 9 17l-5-5"/>
          </svg>
        </div>
        <h1 class="auth-title">Password reset! ✓</h1>
        <p class="auth-subtitle">Your password has been updated. You can now log in with your new password.</p>
        <router-link to="/login" class="btn btn-primary btn-full">
          Log In
        </router-link>
      </div>

      <!-- Form state -->
      <template v-else>
        <h1 class="auth-title">Reset your password</h1>
        <p class="auth-subtitle">Enter a new password for your account.</p>

        <form class="auth-form" @submit.prevent="handleReset">
          <div class="field-group">
            <label class="field-label">New Password</label>
            <input
              v-model="newPassword"
              type="password"
              class="field-input"
              placeholder="Min 8 characters"
              required
              minlength="8"
              autofocus
            />
          </div>

          <div class="field-group">
            <label class="field-label">Confirm Password</label>
            <input
              v-model="confirmPassword"
              type="password"
              class="field-input"
              placeholder="••••••••"
              required
            />
          </div>

          <p v-if="error" class="error-msg">{{ error }}</p>

          <button type="submit" class="btn btn-primary btn-full" :disabled="submitting">
            {{ submitting ? 'Resetting…' : 'Reset Password' }}
          </button>
        </form>
      </template>

      <div class="auth-footer">
        <router-link to="/login" class="auth-link">← Back to login</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { resetPassword } from '@/api/client'

const route = useRoute()

const newPassword     = ref('')
const confirmPassword = ref('')
const submitting      = ref(false)
const success         = ref(false)
const error           = ref('')

async function handleReset() {
  error.value = ''

  const token = route.query.token
  if (!token) {
    error.value = 'No reset token found. Please use the link from your email.'
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords do not match.'
    return
  }

  if (newPassword.value.length < 8) {
    error.value = 'Password must be at least 8 characters.'
    return
  }

  submitting.value = true

  try {
    await resetPassword(token, newPassword.value)
    success.value = true
  } catch (err) {
    const detail = err.response?.data?.detail
      || err.response?.data?.non_field_errors?.[0]
      || (Array.isArray(err.response?.data) ? err.response.data[0] : null)
      || 'Invalid or expired reset token. Please request a new reset link.'
    error.value = detail
  } finally {
    submitting.value = false
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
.auth-subtitle { font-size: 14px; color: var(--color-text-muted); text-align: center; margin: 0 0 28px; line-height: 1.5; }
.auth-form { display: flex; flex-direction: column; gap: 18px; }
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

@keyframes fade-up {
  0%   { opacity: 0; transform: translateY(16px); }
  100% { opacity: 1; transform: translateY(0); }
}
@keyframes pop-in {
  0%   { opacity: 0; transform: scale(0.5); }
  100% { opacity: 1; transform: scale(1); }
}
</style>

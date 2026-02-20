<template>
  <!-- Email verification landing page -->
  <div v-if="route === 'verify-email'" class="landing-page">
    <div class="landing-card">
      <h1>Orbit — Email Verification</h1>
      <div v-if="verifyState === 'loading'" class="status loading">Verifying your email…</div>
      <div v-else-if="verifyState === 'success'" class="status success">
        ✅ Email verified successfully! You can close this page.
      </div>
      <div v-else class="status error">
        ❌ {{ verifyError }}
        <p style="margin-top:12px;font-size:13px;color:#94a3b8;">
          Token may have expired. Request a new one from the app.
        </p>
      </div>
    </div>
  </div>

  <!-- Password reset landing page -->
  <div v-else-if="route === 'reset-password'" class="landing-page">
    <div class="landing-card">
      <h1>Orbit — Reset Password</h1>
      <div v-if="resetState === 'form'">
        <input v-model="newPassword" type="password" placeholder="New password" class="landing-input" />
        <input v-model="confirmPassword" type="password" placeholder="Confirm password" class="landing-input" />
        <button @click="doReset" class="landing-btn" :disabled="!newPassword || newPassword !== confirmPassword">
          Reset Password
        </button>
        <p v-if="newPassword && confirmPassword && newPassword !== confirmPassword" class="status error" style="margin-top:8px;">
          Passwords do not match.
        </p>
      </div>
      <div v-else-if="resetState === 'loading'" class="status loading">Resetting password…</div>
      <div v-else-if="resetState === 'success'" class="status success">
        ✅ Password reset! You can now log in with your new password.
      </div>
      <div v-else class="status error">❌ {{ resetError }}</div>
    </div>
  </div>

  <!-- Default: API demo page -->
  <HomePage v-else />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import HomePage from './pages/HomePage.vue'
import { verifyEmail, resetPassword } from './api/client.js'

const route = ref('home')

// ── Verify email state ──
const verifyState = ref('loading')
const verifyError = ref('')

// ── Reset password state ──
const resetState = ref('form')
const resetError = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
let resetToken = ''

onMounted(async () => {
  const path = window.location.pathname
  const params = new URLSearchParams(window.location.search)
  const token = params.get('token')

  if (path === '/verify-email' && token) {
    route.value = 'verify-email'
    try {
      await verifyEmail(token)
      verifyState.value = 'success'
    } catch (e) {
      verifyState.value = 'error'
      verifyError.value = e.response?.data?.detail || e.message || 'Verification failed.'
    }
  } else if (path === '/reset-password' && token) {
    route.value = 'reset-password'
    resetToken = token
  }
})

async function doReset() {
  resetState.value = 'loading'
  try {
    await resetPassword(resetToken, newPassword.value)
    resetState.value = 'success'
  } catch (e) {
    resetState.value = 'error'
    resetError.value = e.response?.data?.detail || e.message || 'Reset failed.'
  }
}
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f172a;
  color: #e2e8f0;
  font-family: system-ui, -apple-system, sans-serif;
}
.landing-card {
  background: #1e293b;
  border-radius: 16px;
  padding: 48px 40px;
  max-width: 420px;
  width: 90%;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0,0,0,.4);
}
.landing-card h1 {
  font-size: 20px;
  margin-bottom: 24px;
  color: #f1f5f9;
}
.status { padding: 16px; border-radius: 8px; font-size: 15px; }
.status.loading { color: #93c5fd; }
.status.success { color: #86efac; background: #052e16; }
.status.error   { color: #fca5a5; background: #450a0a; }
.landing-input {
  display: block;
  width: 100%;
  padding: 12px 16px;
  margin-bottom: 12px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 15px;
  box-sizing: border-box;
}
.landing-btn {
  width: 100%;
  padding: 12px;
  background: #6366f1;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}
.landing-btn:disabled { opacity: 0.4; cursor: not-allowed; }
</style>

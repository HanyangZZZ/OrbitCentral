<template>
  <div class="auth-page">
    <div class="auth-card">
      <a href="/" class="auth-logo">Orbit</a>

      <!-- Success -->
      <div v-if="success" class="verify-state">
        <div class="status-icon success-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 6 9 17l-5-5"/>
          </svg>
        </div>
        <h1 class="auth-title">Password reset! ✓</h1>
        <p class="auth-subtitle">Your password has been updated. You can now log in with your new password.</p>
        <a href="/" class="btn btn-primary btn-full">Go to Home</a>
      </div>

      <!-- Form -->
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
        <a href="/" class="auth-link">← Back to home</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { resetPassword } from '../api/client'

const newPassword     = ref('')
const confirmPassword = ref('')
const submitting      = ref(false)
const success         = ref(false)
const error           = ref('')

async function handleReset() {
  error.value = ''

  const params = new URLSearchParams(window.location.search)
  const token  = params.get('token')

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
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f8fafc;
  padding: 24px;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
}
.auth-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 40px 32px;
  animation: fade-up 0.35s ease;
}
.auth-logo {
  display: block;
  text-align: center;
  font-family: 'Barlow', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: #4a70a9;
  text-decoration: none;
  margin-bottom: 24px;
}
.auth-title {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  text-align: center;
  margin: 0 0 8px;
}
.auth-subtitle {
  font-size: 14px;
  color: #64748b;
  text-align: center;
  margin: 0 0 28px;
  line-height: 1.5;
}
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.auth-footer {
  margin-top: 24px;
  text-align: center;
}
.auth-link {
  font-size: 14px;
  color: #64748b;
  text-decoration: none;
}
.auth-link:hover { color: #4a70a9; }

.field-group { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 13px; font-weight: 500; color: #64748b; }
.field-input {
  background: #fafaf8;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 11px 14px;
  color: #0f172a;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.field-input:focus {
  border-color: #4a70a9;
  box-shadow: 0 0 0 3px rgba(74, 112, 169, 0.12);
}
.field-input::placeholder { color: #94a3b8; }

.error-msg { font-size: 13px; color: #ef4444; text-align: center; margin: 0; }

.verify-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.status-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  animation: pop-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.success-icon { background: #f0fdf4; }

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 11px 18px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  text-decoration: none;
  transition: background 0.2s, opacity 0.2s;
  margin-top: 8px;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-full { width: 100%; }
.btn-primary { background: #4a70a9; color: #fff; }
.btn-primary:hover:not(:disabled) { background: #3b5e94; }

@keyframes fade-up {
  0%   { opacity: 0; transform: translateY(16px); }
  100% { opacity: 1; transform: translateY(0); }
}
@keyframes pop-in {
  0%   { opacity: 0; transform: scale(0.5); }
  100% { opacity: 1; transform: scale(1); }
}
</style>

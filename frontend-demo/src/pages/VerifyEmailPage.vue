<template>
  <div class="auth-page">
    <div class="auth-card">
      <a href="/" class="auth-logo">Orbit</a>

      <!-- Loading -->
      <div v-if="verifying" class="verify-state">
        <div class="spinner"></div>
        <h1 class="auth-title">Verifying your email…</h1>
        <p class="auth-subtitle">Hang tight while we confirm your address.</p>
      </div>

      <!-- Success -->
      <div v-else-if="success" class="verify-state">
        <div class="status-icon success-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 6 9 17l-5-5"/>
          </svg>
        </div>
        <h1 class="auth-title">Email verified! ✓</h1>
        <p class="auth-subtitle">Your email address has been confirmed. You're all set to use Orbit.</p>
        <a href="/login" class="btn btn-primary btn-full">Log In</a>
      </div>

      <!-- Error -->
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
        <a href="/" class="btn btn-outline btn-full">Go to Home</a>
      </div>

      <div class="auth-footer">
        <a href="/" class="auth-link">← Back to home</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { verifyEmail } from '../api/client'

const verifying = ref(true)
const success   = ref(false)
const error     = ref('')

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const token  = params.get('token')

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
  } finally {
    verifying.value = false
  }
})
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
  margin: 0 0 24px;
  line-height: 1.5;
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
.auth-link:hover {
  color: #4a70a9;
}

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
.error-icon   { background: #fef2f2; }

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #e2e8f0;
  border-top-color: #4a70a9;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  margin-bottom: 12px;
}

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
.btn-full { width: 100%; }
.btn-primary {
  background: #4a70a9;
  color: #fff;
}
.btn-primary:hover { background: #3b5e94; }
.btn-outline {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #64748b;
}
.btn-outline:hover {
  border-color: #4a70a9;
  color: #4a70a9;
}

@keyframes fade-up {
  0%   { opacity: 0; transform: translateY(16px); }
  100% { opacity: 1; transform: translateY(0); }
}
@keyframes pop-in {
  0%   { opacity: 0; transform: scale(0.5); }
  100% { opacity: 1; transform: scale(1); }
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
